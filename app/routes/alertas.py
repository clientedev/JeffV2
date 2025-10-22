from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from typing import List, Dict, Any

from app.database import get_db
from app.models.models import Contrato, Cronograma, Proposta, Usuario
from app.auth import get_current_user

router = APIRouter()

@router.get("/todos")
async def obter_todos_alertas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Dict[str, Any]:
    hoje = date.today()
    sete_dias = hoje + timedelta(days=7)
    trinta_dias_atras = hoje - timedelta(days=30)
    
    contratos_vencendo_list = db.query(Contrato).filter(
        Contrato.data_vencimento <= sete_dias,
        Contrato.data_vencimento >= hoje
    ).all()
    
    cronogramas_proximos_list = db.query(Cronograma).filter(
        Cronograma.data_termino <= sete_dias,
        Cronograma.data_termino >= hoje,
        Cronograma.status != "Concluído"
    ).all()
    
    propostas_paradas_list = db.query(Proposta).filter(
        Proposta.status == "Em andamento",
        Proposta.data_proposta < trinta_dias_atras
    ).all()
    
    from app.models.models import Empresa, Consultor
    
    contratos_vencendo = []
    for c in contratos_vencendo_list:
        empresa_nome = "N/A"
        proposta = db.query(Proposta).filter(Proposta.id == c.proposta_id).first()
        if proposta:
            empresa = db.query(Empresa).filter(Empresa.id == proposta.empresa_id).first()
            if empresa:
                empresa_nome = empresa.nome_fantasia
        
        contratos_vencendo.append({
            "numero_contrato": c.numero_contrato if c.numero_contrato else "N/A",
            "empresa_nome": empresa_nome,
            "valor": float(c.valor) if c.valor is not None else 0,
            "data_vencimento": str(c.data_vencimento)
        })
    
    cronogramas_proximos = []
    for cr in cronogramas_proximos_list:
        empresa_nome = "N/A"
        proposta_numero = "N/A"
        
        proposta = db.query(Proposta).filter(Proposta.id == cr.proposta_id).first()
        if proposta:
            if proposta.numero_proposta:
                proposta_numero = proposta.numero_proposta
            empresa = db.query(Empresa).filter(Empresa.id == proposta.empresa_id).first()
            if empresa:
                empresa_nome = empresa.nome_fantasia
        
        cronogramas_proximos.append({
            "proposta_numero": proposta_numero,
            "empresa_nome": empresa_nome,
            "data_termino": str(cr.data_termino),
            "percentual_conclusao": float(cr.percentual_conclusao) if cr.percentual_conclusao is not None else 0
        })
    
    propostas_paradas = []
    for p in propostas_paradas_list:
        empresa_nome = "N/A"
        consultor_nome = "N/A"
        
        empresa = db.query(Empresa).filter(Empresa.id == p.empresa_id).first()
        if empresa:
            empresa_nome = empresa.nome_fantasia
            
        consultor = db.query(Consultor).filter(Consultor.id == p.consultor_id).first()
        if consultor:
            consultor_nome = consultor.nome
        
        data_proposta_str = str(p.criado_em.date())
        if p.data_proposta is not None:
            data_proposta_str = str(p.data_proposta)
        
        propostas_paradas.append({
            "numero_proposta": p.numero_proposta if p.numero_proposta else "N/A",
            "empresa_nome": empresa_nome,
            "consultor_nome": consultor_nome,
            "data_proposta": data_proposta_str
        })
    
    return {
        "contratos_vencendo": contratos_vencendo,
        "cronogramas_proximos": cronogramas_proximos,
        "propostas_paradas": propostas_paradas
    }

@router.get("/resumo")
async def obter_resumo_alertas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    hoje = date.today()
    sete_dias = hoje + timedelta(days=7)
    trinta_dias_atras = hoje - timedelta(days=30)
    
    total_contratos_vencidos = db.query(Contrato).filter(
        Contrato.data_vencimento < hoje,
        Contrato.status_pagamento.in_(["Pendente", "Vencido"])
    ).count()
    
    total_cronogramas_atrasados = db.query(Cronograma).filter(
        Cronograma.data_termino < hoje,
        Cronograma.status != "Concluído"
    ).count()
    
    total_propostas_paradas = db.query(Proposta).filter(
        Proposta.status == "Em andamento",
        Proposta.atualizado_em < trinta_dias_atras
    ).count()
    
    return {
        "total_alertas_criticos": total_contratos_vencidos + total_cronogramas_atrasados,
        "contratos_vencidos": total_contratos_vencidos,
        "projetos_atrasados": total_cronogramas_atrasados,
        "propostas_paradas": total_propostas_paradas,
        "requer_atencao": total_contratos_vencidos + total_cronogramas_atrasados + total_propostas_paradas > 0
    }
