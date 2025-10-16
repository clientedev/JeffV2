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
    
    contratos_vencidos = db.query(Contrato).filter(
        Contrato.data_vencimento < hoje,
        Contrato.status_pagamento.in_(["Pendente", "Vencido"])
    ).all()
    
    contratos_vencendo = db.query(Contrato).filter(
        Contrato.data_vencimento <= sete_dias,
        Contrato.data_vencimento >= hoje,
        Contrato.status_pagamento == "Pendente"
    ).all()
    
    cronogramas_atrasados = db.query(Cronograma).filter(
        Cronograma.data_termino < hoje,
        Cronograma.status != "Concluído"
    ).all()
    
    cronogramas_vencendo = db.query(Cronograma).filter(
        Cronograma.data_termino <= sete_dias,
        Cronograma.data_termino >= hoje,
        Cronograma.status != "Concluído"
    ).all()
    
    propostas_paradas = db.query(Proposta).filter(
        Proposta.status == "Em andamento",
        Proposta.atualizado_em < trinta_dias_atras
    ).all()
    
    tarefas_criticas = db.query(Cronograma).filter(
        Cronograma.percentual_conclusao < 30,
        Cronograma.data_termino <= sete_dias,
        Cronograma.status != "Concluído"
    ).all()
    
    alertas = {
        "resumo": {
            "total_alertas": (
                len(contratos_vencidos) + len(contratos_vencendo) + 
                len(cronogramas_atrasados) + len(cronogramas_vencendo) + 
                len(propostas_paradas) + len(tarefas_criticas)
            ),
            "contratos_criticos": len(contratos_vencidos) + len(contratos_vencendo),
            "cronogramas_criticos": len(cronogramas_atrasados) + len(cronogramas_vencendo),
            "propostas_paradas": len(propostas_paradas),
            "tarefas_criticas": len(tarefas_criticas)
        },
        "contratos": {
            "vencidos": [
                {
                    "id": c.id,
                    "numero": c.numero_contrato,
                    "data_vencimento": str(c.data_vencimento),
                    "valor": float(c.valor) if c.valor else 0,
                    "status": c.status_pagamento,
                    "tipo_alerta": "CRÍTICO",
                    "mensagem": f"Contrato {c.numero_contrato} vencido há {(hoje - c.data_vencimento).days} dias"
                } for c in contratos_vencidos
            ],
            "vencendo": [
                {
                    "id": c.id,
                    "numero": c.numero_contrato,
                    "data_vencimento": str(c.data_vencimento),
                    "valor": float(c.valor) if c.valor else 0,
                    "status": c.status_pagamento,
                    "tipo_alerta": "ATENÇÃO",
                    "mensagem": f"Contrato {c.numero_contrato} vence em {(c.data_vencimento - hoje).days} dias"
                } for c in contratos_vencendo
            ]
        },
        "cronogramas": {
            "atrasados": [
                {
                    "id": cr.id,
                    "proposta_id": cr.proposta_id,
                    "data_termino": str(cr.data_termino),
                    "percentual_conclusao": float(cr.percentual_conclusao),
                    "status": cr.status,
                    "tipo_alerta": "CRÍTICO",
                    "mensagem": f"Projeto atrasado há {(hoje - cr.data_termino).days} dias - {cr.percentual_conclusao}% concluído"
                } for cr in cronogramas_atrasados
            ],
            "vencendo": [
                {
                    "id": cr.id,
                    "proposta_id": cr.proposta_id,
                    "data_termino": str(cr.data_termino),
                    "percentual_conclusao": float(cr.percentual_conclusao),
                    "status": cr.status,
                    "tipo_alerta": "ATENÇÃO",
                    "mensagem": f"Projeto vence em {(cr.data_termino - hoje).days} dias - {cr.percentual_conclusao}% concluído"
                } for cr in cronogramas_vencendo
            ]
        },
        "propostas": {
            "paradas": [
                {
                    "id": p.id,
                    "numero": p.numero_proposta,
                    "ultima_atualizacao": str(p.atualizado_em),
                    "dias_parado": (datetime.now() - p.atualizado_em).days,
                    "status": p.status,
                    "tipo_alerta": "AVISO",
                    "mensagem": f"Proposta {p.numero_proposta} sem atualização há {(datetime.now() - p.atualizado_em).days} dias"
                } for p in propostas_paradas
            ]
        },
        "tarefas_criticas": [
            {
                "id": cr.id,
                "proposta_id": cr.proposta_id,
                "data_termino": str(cr.data_termino),
                "percentual_conclusao": float(cr.percentual_conclusao),
                "tipo_alerta": "URGENTE",
                "mensagem": f"Projeto crítico com apenas {cr.percentual_conclusao}% concluído e vencimento próximo"
            } for cr in tarefas_criticas
        ]
    }
    
    return alertas

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
