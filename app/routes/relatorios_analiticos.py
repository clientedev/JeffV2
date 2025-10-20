from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.database import get_db
from app.models.models import (
    PesquisaSatisfacao, CarteiraGRM, LinhaTecnologia, LinhaEducacional, Usuario
)
from app.auth import get_current_user

router = APIRouter()

@router.get("/pesquisa-satisfacao/estatisticas")
async def estatisticas_pesquisa_satisfacao(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    total_respostas = db.query(func.count(PesquisaSatisfacao.id)).scalar() or 0
    
    media_geral = db.query(func.avg(PesquisaSatisfacao.nota_geral)).scalar() or 0
    media_consultoria = db.query(func.avg(PesquisaSatisfacao.nota_consultoria)).scalar() or 0
    media_consultor = db.query(func.avg(PesquisaSatisfacao.nota_consultor)).scalar() or 0
    
    recomendaria_sim = db.query(func.count(PesquisaSatisfacao.id)).filter(
        PesquisaSatisfacao.recomendaria == "Sim"
    ).scalar() or 0
    
    taxa_recomendacao = 0
    if total_respostas > 0:
        taxa_recomendacao = round((recomendaria_sim / total_respostas) * 100, 2)
    
    return {
        "total_respostas": total_respostas,
        "media_geral": float(media_geral),
        "media_consultoria": float(media_consultoria),
        "media_consultor": float(media_consultor),
        "taxa_recomendacao": taxa_recomendacao,
        "recomendaria_sim": recomendaria_sim
    }

@router.get("/carteira-grm/resumo")
async def resumo_carteira_grm(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    total_projetos = db.query(func.count(CarteiraGRM.id)).scalar() or 0
    
    valor_total = db.query(func.sum(CarteiraGRM.valor)).scalar() or Decimal(0)
    
    # Agrupa por status
    por_status = db.query(
        CarteiraGRM.status,
        func.count(CarteiraGRM.id).label('total'),
        func.sum(CarteiraGRM.valor).label('valor_total')
    ).group_by(CarteiraGRM.status).all()
    
    # Agrupa por consultor
    por_consultor = db.query(
        CarteiraGRM.consultor,
        func.count(CarteiraGRM.id).label('total'),
        func.sum(CarteiraGRM.valor).label('valor_total')
    ).group_by(CarteiraGRM.consultor).all()
    
    return {
        "total_projetos": total_projetos,
        "valor_total": float(valor_total),
        "por_status": [
            {
                "status": s.status or "Sem status",
                "total": s.total,
                "valor": float(s.valor_total or 0)
            } for s in por_status
        ],
        "por_consultor": [
            {
                "consultor": c.consultor or "Sem consultor",
                "total": c.total,
                "valor": float(c.valor_total or 0)
            } for c in por_consultor
        ]
    }

@router.get("/linha-tecnologia/resumo")
async def resumo_linha_tecnologia(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    total_projetos = db.query(func.count(LinhaTecnologia.id)).scalar() or 0
    
    valor_total = db.query(func.sum(LinhaTecnologia.valor_proposta)).scalar() or Decimal(0)
    
    # Por situação
    por_situacao = db.query(
        LinhaTecnologia.situacao,
        func.count(LinhaTecnologia.id).label('total'),
        func.sum(LinhaTecnologia.valor_proposta).label('valor')
    ).group_by(LinhaTecnologia.situacao).all()
    
    # Por tipo de programa
    por_tipo = db.query(
        LinhaTecnologia.tipo_programa,
        func.count(LinhaTecnologia.id).label('total')
    ).group_by(LinhaTecnologia.tipo_programa).all()
    
    # Por consultor
    por_consultor = db.query(
        LinhaTecnologia.consultor,
        func.count(LinhaTecnologia.id).label('total'),
        func.sum(LinhaTecnologia.valor_proposta).label('valor')
    ).group_by(LinhaTecnologia.consultor).all()
    
    return {
        "total_projetos": total_projetos,
        "valor_total": float(valor_total),
        "por_situacao": [
            {
                "situacao": s.situacao or "Sem situação",
                "total": s.total,
                "valor": float(s.valor or 0)
            } for s in por_situacao
        ],
        "por_tipo_programa": [
            {
                "tipo": t.tipo_programa or "Sem tipo",
                "total": t.total
            } for t in por_tipo
        ],
        "por_consultor": [
            {
                "consultor": c.consultor or "Sem consultor",
                "total": c.total,
                "valor": float(c.valor or 0)
            } for c in por_consultor
        ]
    }

@router.get("/linha-educacional/resumo")
async def resumo_linha_educacional(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    total_projetos = db.query(func.count(LinhaEducacional.id)).scalar() or 0
    
    valor_total = db.query(func.sum(LinhaEducacional.valor_proposta)).scalar() or Decimal(0)
    
    # Por situação
    por_situacao = db.query(
        LinhaEducacional.situacao,
        func.count(LinhaEducacional.id).label('total'),
        func.sum(LinhaEducacional.valor_proposta).label('valor')
    ).group_by(LinhaEducacional.situacao).all()
    
    # Por tipo de programa
    por_tipo = db.query(
        LinhaEducacional.tipo_programa,
        func.count(LinhaEducacional.id).label('total')
    ).group_by(LinhaEducacional.tipo_programa).all()
    
    # Por consultor
    por_consultor = db.query(
        LinhaEducacional.consultor,
        func.count(LinhaEducacional.id).label('total'),
        func.sum(LinhaEducacional.valor_proposta).label('valor')
    ).group_by(LinhaEducacional.consultor).all()
    
    return {
        "total_projetos": total_projetos,
        "valor_total": float(valor_total),
        "por_situacao": [
            {
                "situacao": s.situacao or "Sem situação",
                "total": s.total,
                "valor": float(s.valor or 0)
            } for s in por_situacao
        ],
        "por_tipo_programa": [
            {
                "tipo": t.tipo_programa or "Sem tipo",
                "total": t.total
            } for t in por_tipo
        ],
        "por_consultor": [
            {
                "consultor": c.consultor or "Sem consultor",
                "total": c.total,
                "valor": float(c.valor or 0)
            } for c in por_consultor
        ]
    }

@router.get("/consolidado")
async def relatorio_consolidado(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Chama todos os relatórios
    satisfacao = await estatisticas_pesquisa_satisfacao(db, current_user)
    grm = await resumo_carteira_grm(db, current_user)
    tecnologia = await resumo_linha_tecnologia(db, current_user)
    educacional = await resumo_linha_educacional(db, current_user)
    
    return {
        "pesquisa_satisfacao": satisfacao,
        "carteira_grm": grm,
        "linha_tecnologia": tecnologia,
        "linha_educacional": educacional
    }
