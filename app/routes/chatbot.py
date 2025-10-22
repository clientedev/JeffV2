from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
import os

from app.database import get_db
from app.models.models import Proposta, Cronograma, Contrato, Consultor, Empresa, Usuario
from app.auth import get_current_user

router = APIRouter()

class ChatRequest(BaseModel):
    pergunta: Optional[str] = None
    mensagem: Optional[str] = None  # Mantém compatibilidade com frontend existente

class ChatResponse(BaseModel):
    resposta: str
    dados: dict = {}

# Tentar importar Groq AI se disponível
try:
    from groq import Groq
    AI_DISPONIVEL = True
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except (ImportError, Exception):
    AI_DISPONIVEL = False
    client = None

@router.post("/perguntar", response_model=ChatResponse)
async def chat_perguntar(
    chat: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Aceita tanto 'pergunta' quanto 'mensagem' para compatibilidade
    pergunta = chat.pergunta or chat.mensagem
    if not pergunta:
        raise HTTPException(status_code=400, detail="Pergunta ou mensagem é obrigatória")
    mensagem = pergunta.lower()
    
    if "contrato" in mensagem and ("venc" in mensagem or "próximo" in mensagem or "semana" in mensagem):
        hoje = date.today()
        sete_dias = hoje + timedelta(days=7)
        
        contratos = db.query(Contrato).filter(
            Contrato.data_vencimento <= sete_dias,
            Contrato.data_vencimento >= hoje,
            Contrato.status_pagamento.in_(["Pendente", "Vencido"])
        ).all()
        
        if not contratos:
            return ChatResponse(
                resposta="Não há contratos vencendo nos próximos 7 dias.",
                dados={"contratos": []}
            )
        
        lista_contratos = []
        for c in contratos:
            proposta = db.query(Proposta).filter(Proposta.id == c.proposta_id).first()
            empresa = db.query(Empresa).filter(Empresa.id == proposta.empresa_id).first() if proposta else None
            
            lista_contratos.append({
                "numero": c.numero_contrato,
                "empresa": empresa.nome if empresa else "N/A",
                "vencimento": str(c.data_vencimento),
                "valor": float(c.valor or 0)
            })
        
        return ChatResponse(
            resposta=f"Encontrei {len(contratos)} contrato(s) vencendo nos próximos 7 dias.",
            dados={"contratos": lista_contratos}
        )
    
    elif "projeto" in mensagem and ("ativo" in mensagem or "andamento" in mensagem):
        cronogramas = db.query(Cronograma).filter(
            Cronograma.status == "Em andamento"
        ).all()
        
        lista_projetos = []
        for cron in cronogramas:
            proposta = db.query(Proposta).filter(Proposta.id == cron.proposta_id).first()
            empresa = db.query(Empresa).filter(Empresa.id == proposta.empresa_id).first() if proposta else None
            
            lista_projetos.append({
                "numero_proposta": proposta.numero_proposta if proposta else "N/A",
                "empresa": empresa.nome if empresa else "N/A",
                "percentual": float(cron.percentual_conclusao or 0),
                "termino_previsto": str(cron.data_termino) if cron.data_termino else "N/A"
            })
        
        return ChatResponse(
            resposta=f"Há {len(cronogramas)} projeto(s) em andamento.",
            dados={"projetos": lista_projetos}
        )
    
    elif "proposta" in mensagem and ("parada" in mensagem or "pendente" in mensagem):
        hoje = date.today()
        trinta_dias = hoje - timedelta(days=30)
        
        propostas = db.query(Proposta).filter(
            Proposta.status == "Em andamento",
            Proposta.data_proposta <= trinta_dias
        ).all()
        
        lista_propostas = []
        for p in propostas:
            empresa = db.query(Empresa).filter(Empresa.id == p.empresa_id).first()
            consultor = db.query(Consultor).filter(Consultor.id == p.consultor_id).first()
            
            dias_parada = (hoje - p.data_proposta).days if p.data_proposta else 0
            
            lista_propostas.append({
                "numero": p.numero_proposta,
                "empresa": empresa.nome if empresa else "N/A",
                "consultor": consultor.nome if consultor else "N/A",
                "dias_parada": dias_parada
            })
        
        return ChatResponse(
            resposta=f"Encontrei {len(propostas)} proposta(s) parada(s) há mais de 30 dias.",
            dados={"propostas": lista_propostas}
        )
    
    elif "receita" in mensagem or "faturamento" in mensagem:
        from sqlalchemy import func
        
        receita_total = db.query(func.sum(Contrato.valor)).filter(
            Contrato.status_pagamento == "Pago"
        ).scalar() or 0
        
        hoje = date.today()
        receita_mes = db.query(func.sum(Contrato.valor)).filter(
            Contrato.status_pagamento == "Pago",
            func.extract('month', Contrato.data_assinatura) == hoje.month,
            func.extract('year', Contrato.data_assinatura) == hoje.year
        ).scalar() or 0
        
        return ChatResponse(
            resposta=f"Receita total: R$ {float(receita_total):,.2f} | Receita este mês: R$ {float(receita_mes):,.2f}",
            dados={
                "receita_total": float(receita_total),
                "receita_mes": float(receita_mes)
            }
        )
    
    else:
        # Se Groq AI estiver disponível, usar para responder perguntas mais complexas
        if AI_DISPONIVEL and client and os.getenv("GROQ_API_KEY"):
            try:
                # Coletar contexto do banco de dados
                total_propostas = db.query(Proposta).count()
                total_empresas = db.query(Empresa).count()
                total_consultores = db.query(Consultor).count()
                
                contexto = f"""
                Você é um assistente de um sistema de gestão industrial chamado "Núcleo de Tecnologia". 
                O sistema atualmente possui:
                - {total_propostas} propostas cadastradas
                - {total_empresas} empresas
                - {total_consultores} consultores ativos
                
                Responda de forma objetiva e útil à seguinte pergunta do usuário:
                {pergunta}
                
                Se a pergunta não for relacionada ao sistema, responda educadamente que você só pode ajudar com questões do sistema de gestão.
                """
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Você é um assistente útil e prestativo para um sistema de gestão industrial brasileiro. Responda sempre em português brasileiro de forma clara e profissional."},
                        {"role": "user", "content": contexto}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                
                resposta_ai = response.choices[0].message.content
                
                return ChatResponse(
                    resposta=resposta_ai,
                    dados={
                        "total_propostas": total_propostas,
                        "total_empresas": total_empresas,
                        "total_consultores": total_consultores
                    }
                )
            except Exception as e:
                print(f"Erro ao consultar Groq AI: {e}")
                # Fallback para resposta padrão
                pass
        
        return ChatResponse(
            resposta="Desculpe, não entendi sua pergunta. Tente perguntar sobre: contratos vencendo, projetos ativos, propostas paradas ou receita.",
            dados={}
        )
