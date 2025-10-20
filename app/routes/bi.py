from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, timedelta
from decimal import Decimal

from app.database import get_db
from app.models.models import Proposta, Cronograma, Contrato, Consultor, Usuario, LinhaTecnologia, LinhaEducacional
from app.auth import get_current_user

router = APIRouter()

@router.get("/linhas/consolidado")
async def get_linhas_consolidado(
    ano: int = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna estatísticas consolidadas das linhas tecnologia e educacional"""
    hoje = date.today()
    ano_atual = ano or hoje.year
    
    # Estatísticas Linha Tecnologia
    query_tec = db.query(LinhaTecnologia)
    if ano:
        query_tec = query_tec.filter(LinhaTecnologia.ano == ano)
    
    total_tec = query_tec.count()
    valor_total_tec = query_tec.with_entities(func.sum(LinhaTecnologia.valor_proposta)).scalar() or 0
    
    # Por status etapa - Tecnologia
    tec_por_status = db.query(
        LinhaTecnologia.status_etapa,
        func.count(LinhaTecnologia.id).label('quantidade')
    ).filter(
        LinhaTecnologia.ano == ano if ano else True
    ).group_by(LinhaTecnologia.status_etapa).all()
    
    # Estatísticas Linha Educacional
    query_edu = db.query(LinhaEducacional)
    if ano:
        query_edu = query_edu.filter(LinhaEducacional.ano == ano)
    
    total_edu = query_edu.count()
    valor_total_edu = query_edu.with_entities(func.sum(LinhaEducacional.valor)).scalar() or 0
    
    # Por status proposta - Educacional
    edu_por_status = db.query(
        LinhaEducacional.status_proposta,
        func.count(LinhaEducacional.id).label('quantidade')
    ).filter(
        LinhaEducacional.ano == ano if ano else True
    ).group_by(LinhaEducacional.status_proposta).all()
    
    # Distribuição por mês - Tecnologia
    tec_por_mes = db.query(
        LinhaTecnologia.mes,
        func.count(LinhaTecnologia.id).label('quantidade'),
        func.sum(LinhaTecnologia.valor_proposta).label('valor')
    ).filter(
        LinhaTecnologia.ano == ano if ano else True
    ).group_by(LinhaTecnologia.mes).all()
    
    # Distribuição por mês - Educacional
    edu_por_mes = db.query(
        LinhaEducacional.mes,
        func.count(LinhaEducacional.id).label('quantidade'),
        func.sum(LinhaEducacional.valor).label('valor')
    ).filter(
        LinhaEducacional.ano == ano if ano else True
    ).group_by(LinhaEducacional.mes).all()
    
    # Top consultores - Tecnologia
    top_consultores_tec = db.query(
        LinhaTecnologia.consultor,
        func.count(LinhaTecnologia.id).label('quantidade')
    ).filter(
        LinhaTecnologia.ano == ano if ano else True,
        LinhaTecnologia.consultor.isnot(None)
    ).group_by(LinhaTecnologia.consultor).order_by(func.count(LinhaTecnologia.id).desc()).limit(10).all()
    
    return {
        "ano": ano_atual,
        "tecnologia": {
            "total_registros": total_tec,
            "valor_total": float(valor_total_tec),
            "por_status": [
                {"status": s[0], "quantidade": s[1]}
                for s in tec_por_status if s[0]
            ],
            "por_mes": [
                {"mes": m[0], "quantidade": m[1], "valor": float(m[2] or 0)}
                for m in tec_por_mes if m[0]
            ],
            "top_consultores": [
                {"consultor": c[0], "quantidade": c[1]}
                for c in top_consultores_tec if c[0]
            ]
        },
        "educacional": {
            "total_registros": total_edu,
            "valor_total": float(valor_total_edu),
            "por_status": [
                {"status": s[0], "quantidade": s[1]}
                for s in edu_por_status if s[0]
            ],
            "por_mes": [
                {"mes": m[0], "quantidade": m[1], "valor": float(m[2] or 0)}
                for m in edu_por_mes if m[0]
            ]
        },
        "consolidado": {
            "total_geral": total_tec + total_edu,
            "valor_total_geral": float(valor_total_tec + valor_total_edu),
            "percentual_tecnologia": round((total_tec / (total_tec + total_edu) * 100) if (total_tec + total_edu) > 0 else 0, 2),
            "percentual_educacional": round((total_edu / (total_tec + total_edu) * 100) if (total_tec + total_edu) > 0 else 0, 2)
        }
    }

@router.get("/dashboard")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    hoje = date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    total_propostas = db.query(func.count(Proposta.id)).scalar()
    
    propostas_ativas = db.query(func.count(Proposta.id)).filter(
        Proposta.status == "Em andamento"
    ).scalar()
    
    propostas_fechadas_mes = db.query(func.count(Proposta.id)).filter(
        Proposta.status == "Fechado",
        extract('month', Proposta.data_fechamento) == mes_atual,
        extract('year', Proposta.data_fechamento) == ano_atual
    ).scalar()
    
    projetos_concluidos_mes = db.query(func.count(Cronograma.id)).filter(
        Cronograma.status == "Concluído",
        extract('month', Cronograma.atualizado_em) == mes_atual,
        extract('year', Cronograma.atualizado_em) == ano_atual
    ).scalar()
    
    total_horas_executadas = db.query(func.sum(Cronograma.horas_executadas)).scalar() or 0
    
    receita_total = db.query(func.sum(Contrato.valor)).filter(
        Contrato.status_pagamento == "Pago"
    ).scalar() or Decimal(0)
    
    receita_mes = db.query(func.sum(Contrato.valor)).filter(
        Contrato.status_pagamento == "Pago",
        extract('month', Contrato.data_assinatura) == mes_atual,
        extract('year', Contrato.data_assinatura) == ano_atual
    ).scalar() or Decimal(0)
    
    total_propostas_fechadas = db.query(func.count(Proposta.id)).filter(
        Proposta.status == "Fechado"
    ).scalar()
    
    taxa_conversao = 0
    if total_propostas > 0:
        taxa_conversao = round((total_propostas_fechadas / total_propostas) * 100, 2)
    
    contratos_vencidos = db.query(func.count(Contrato.id)).filter(
        Contrato.data_vencimento < hoje,
        Contrato.status_pagamento.in_(["Pendente", "Vencido"])
    ).scalar()
    
    return {
        "total_propostas": total_propostas,
        "propostas_ativas": propostas_ativas,
        "propostas_fechadas_mes": propostas_fechadas_mes,
        "projetos_concluidos_mes": projetos_concluidos_mes,
        "total_horas_executadas": float(total_horas_executadas),
        "receita_total": float(receita_total),
        "receita_mes": float(receita_mes),
        "taxa_conversao": taxa_conversao,
        "contratos_vencidos": contratos_vencidos
    }

@router.get("/propostas-por-status")
async def propostas_por_status(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    resultados = db.query(
        Proposta.status, 
        func.count(Proposta.id).label('total')
    ).group_by(Proposta.status).all()
    
    return [{"status": r.status, "total": r.total} for r in resultados]

@router.get("/propostas-por-consultor")
async def propostas_por_consultor(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    resultados = db.query(
        Consultor.nome,
        func.count(Proposta.id).label('total')
    ).join(Proposta, Proposta.consultor_id == Consultor.id).group_by(Consultor.nome).all()
    
    return [{"consultor": r.nome, "total": r.total} for r in resultados]

@router.get("/receita-mensal")
async def receita_mensal(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    resultados = db.query(
        extract('month', Contrato.data_assinatura).label('mes'),
        extract('year', Contrato.data_assinatura).label('ano'),
        func.sum(Contrato.valor).label('receita')
    ).filter(
        Contrato.status_pagamento == "Pago"
    ).group_by('mes', 'ano').order_by('ano', 'mes').limit(12).all()
    
    meses = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
             7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
    
    return [{
        "mes": f"{meses[int(r.mes)]}/{int(r.ano)}", 
        "receita": float(r.receita or 0)
    } for r in resultados]

@router.get("/produtividade-consultores")
async def produtividade_consultores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    resultados = db.query(
        Consultor.nome,
        func.sum(Cronograma.horas_executadas).label('horas')
    ).join(Proposta, Proposta.consultor_id == Consultor.id)\
     .join(Cronograma, Cronograma.proposta_id == Proposta.id)\
     .group_by(Consultor.nome).all()
    
    return [{"consultor": r.nome, "horas": float(r.horas or 0)} for r in resultados]
