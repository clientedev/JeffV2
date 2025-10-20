from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import date

from app.database import get_db
from app.models.models import Consultor, Proposta, Cronograma, Empresa, Usuario
from app.auth import get_current_user

router = APIRouter()

@router.get("/{consultor_id}/detalhes")
async def obter_detalhes_consultor(
    consultor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    consultor = db.query(Consultor).filter(Consultor.id == consultor_id).first()
    if not consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")
    
    # Estatísticas do consultor
    total_propostas = db.query(func.count(Proposta.id)).filter(
        Proposta.consultor_id == consultor_id
    ).scalar() or 0
    
    propostas_abertas = db.query(func.count(Proposta.id)).filter(
        Proposta.consultor_id == consultor_id,
        Proposta.status == "Em andamento"
    ).scalar() or 0
    
    propostas_concluidas = db.query(func.count(Proposta.id)).filter(
        Proposta.consultor_id == consultor_id,
        Proposta.status == "Fechado"
    ).scalar() or 0
    
    taxa_conversao = 0
    if total_propostas > 0:
        taxa_conversao = round((propostas_concluidas / total_propostas) * 100, 2)
    
    # Receita gerada
    receita_total = db.query(func.sum(Proposta.valor_proposta)).filter(
        Proposta.consultor_id == consultor_id,
        Proposta.status == "Fechado"
    ).scalar() or Decimal(0)
    
    # Horas trabalhadas
    horas_trabalhadas = db.query(func.sum(Cronograma.horas_executadas)).join(
        Proposta, Proposta.id == Cronograma.proposta_id
    ).filter(
        Proposta.consultor_id == consultor_id
    ).scalar() or Decimal(0)
    
    # Empresas sob responsabilidade
    empresas = db.query(Empresa).join(
        Proposta, Proposta.empresa_id == Empresa.id
    ).filter(
        Proposta.consultor_id == consultor_id
    ).distinct().all()
    
    # Propostas recentes
    propostas_recentes = db.query(Proposta).filter(
        Proposta.consultor_id == consultor_id
    ).order_by(Proposta.criado_em.desc()).limit(10).all()
    
    return {
        "consultor": {
            "id": consultor.id,
            "nome": consultor.nome,
            "email": consultor.email,
            "cargo": consultor.cargo,
            "ativo": consultor.ativo
        },
        "estatisticas": {
            "total_propostas": total_propostas,
            "propostas_abertas": propostas_abertas,
            "propostas_concluidas": propostas_concluidas,
            "taxa_conversao": taxa_conversao,
            "receita_gerada": float(receita_total),
            "horas_trabalhadas": float(horas_trabalhadas)
        },
        "empresas": [{"id": e.id, "nome": e.nome, "cnpj": e.cnpj} for e in empresas],
        "propostas_recentes": [
            {
                "id": p.id,
                "numero_proposta": p.numero_proposta,
                "status": p.status,
                "valor": float(p.valor_proposta) if p.valor_proposta else 0,
                "data_proposta": str(p.data_proposta) if p.data_proposta else None
            } for p in propostas_recentes
        ]
    }
