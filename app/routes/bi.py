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
    
    # Dados das Linhas Tecnologia e Educacional
    total_tec = db.query(func.count(LinhaTecnologia.id)).scalar() or 0
    total_edu = db.query(func.count(LinhaEducacional.id)).scalar() or 0
    total_propostas = total_tec + total_edu
    
    # Propostas ativas (PREVISTO para tecnologia, todas não FATURADO/CANCELADO para educacional)
    propostas_ativas_tec = db.query(func.count(LinhaTecnologia.id)).filter(
        LinhaTecnologia.ano == ano_atual,
        LinhaTecnologia.situacao == 'PREVISTO'
    ).scalar() or 0
    
    propostas_ativas_edu = db.query(func.count(LinhaEducacional.id)).filter(
        LinhaEducacional.ano == ano_atual,
        LinhaEducacional.situacao.notin_(['FATURADO', 'CANCELADO'])
    ).scalar() or 0
    
    propostas_ativas = propostas_ativas_tec + propostas_ativas_edu
    
    # Propostas fechadas no mês (FATURADO)
    propostas_fechadas_mes_tec = db.query(func.count(LinhaTecnologia.id)).filter(
        LinhaTecnologia.mes == str(mes_atual),
        LinhaTecnologia.ano == ano_atual,
        LinhaTecnologia.situacao == 'FATURADO'
    ).scalar() or 0
    
    propostas_fechadas_mes_edu = db.query(func.count(LinhaEducacional.id)).filter(
        LinhaEducacional.mes == str(mes_atual),
        LinhaEducacional.ano == ano_atual,
        LinhaEducacional.situacao == 'FATURADO'
    ).scalar() or 0
    
    propostas_fechadas_mes = propostas_fechadas_mes_tec + propostas_fechadas_mes_edu
    
    # Receita total
    receita_total_tec = db.query(func.sum(LinhaTecnologia.valor_proposta)).scalar() or 0
    receita_total_edu = db.query(func.sum(LinhaEducacional.valor)).scalar() or 0
    receita_total = float(receita_total_tec) + float(receita_total_edu)
    
    # Receita do mês
    receita_mes_tec = db.query(func.sum(LinhaTecnologia.valor_proposta)).filter(
        LinhaTecnologia.mes == str(mes_atual),
        LinhaTecnologia.ano == ano_atual
    ).scalar() or 0
    
    receita_mes_edu = db.query(func.sum(LinhaEducacional.valor)).filter(
        LinhaEducacional.mes == str(mes_atual),
        LinhaEducacional.ano == ano_atual
    ).scalar() or 0
    
    receita_mes = float(receita_mes_tec) + float(receita_mes_edu)
    
    # Taxa de conversão (FATURADO)
    total_propostas_fechadas_tec = db.query(func.count(LinhaTecnologia.id)).filter(
        LinhaTecnologia.situacao == 'FATURADO'
    ).scalar() or 0
    
    total_propostas_fechadas_edu = db.query(func.count(LinhaEducacional.id)).filter(
        LinhaEducacional.situacao == 'FATURADO'
    ).scalar() or 0
    
    total_propostas_fechadas = total_propostas_fechadas_tec + total_propostas_fechadas_edu
    
    taxa_conversao = 0
    if total_propostas > 0:
        taxa_conversao = round((total_propostas_fechadas / total_propostas) * 100, 2)
    
    return {
        "total_propostas": total_propostas,
        "propostas_ativas": propostas_ativas,
        "propostas_fechadas_mes": propostas_fechadas_mes,
        "projetos_concluidos_mes": total_propostas_fechadas,
        "total_horas_executadas": 0,
        "receita_total": receita_total,
        "receita_mes": receita_mes,
        "taxa_conversao": taxa_conversao,
        "contratos_vencidos": 0
    }

@router.get("/propostas-por-status")
async def propostas_por_status(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Combinar dados de Linha Tecnologia e Linha Educacional
    resultados_tec = db.query(
        LinhaTecnologia.situacao, 
        func.count(LinhaTecnologia.id).label('total')
    ).filter(LinhaTecnologia.situacao.isnot(None)).group_by(LinhaTecnologia.situacao).all()
    
    resultados_edu = db.query(
        LinhaEducacional.situacao, 
        func.count(LinhaEducacional.id).label('total')
    ).filter(LinhaEducacional.situacao.isnot(None)).group_by(LinhaEducacional.situacao).all()
    
    # Consolidar resultados
    status_dict = {}
    for r in resultados_tec:
        status_dict[r.situacao] = status_dict.get(r.situacao, 0) + r.total
    for r in resultados_edu:
        status_dict[r.situacao] = status_dict.get(r.situacao, 0) + r.total
    
    return [{"status": status, "total": total} for status, total in status_dict.items()]

@router.get("/propostas-por-consultor")
async def propostas_por_consultor(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Dados de Linha Tecnologia
    resultados_tec = db.query(
        LinhaTecnologia.consultor,
        func.count(LinhaTecnologia.id).label('total')
    ).filter(LinhaTecnologia.consultor.isnot(None)).group_by(LinhaTecnologia.consultor).all()
    
    # Dados de Linha Educacional (usa instrutor_1)
    resultados_edu = db.query(
        LinhaEducacional.instrutor_1,
        func.count(LinhaEducacional.id).label('total')
    ).filter(LinhaEducacional.instrutor_1.isnot(None)).group_by(LinhaEducacional.instrutor_1).all()
    
    # Consolidar resultados
    consultor_dict = {}
    for r in resultados_tec:
        consultor_dict[r.consultor] = consultor_dict.get(r.consultor, 0) + r.total
    for r in resultados_edu:
        consultor_dict[r.instrutor_1] = consultor_dict.get(r.instrutor_1, 0) + r.total
    
    # Retornar top 10 consultores
    consultores_sorted = sorted(consultor_dict.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return [{"consultor": consultor, "total": total} for consultor, total in consultores_sorted]

@router.get("/receita-mensal")
async def receita_mensal(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    hoje = date.today()
    ano_atual = hoje.year
    
    # Dados de Linha Tecnologia
    resultados_tec = db.query(
        LinhaTecnologia.mes,
        LinhaTecnologia.ano,
        func.sum(LinhaTecnologia.valor_proposta).label('receita')
    ).filter(
        LinhaTecnologia.ano == ano_atual,
        LinhaTecnologia.mes.isnot(None)
    ).group_by(LinhaTecnologia.mes, LinhaTecnologia.ano).all()
    
    # Dados de Linha Educacional
    resultados_edu = db.query(
        LinhaEducacional.mes,
        LinhaEducacional.ano,
        func.sum(LinhaEducacional.valor).label('receita')
    ).filter(
        LinhaEducacional.ano == ano_atual,
        LinhaEducacional.mes.isnot(None)
    ).group_by(LinhaEducacional.mes, LinhaEducacional.ano).all()
    
    # Consolidar por mês
    receita_dict = {}
    for r in resultados_tec:
        if r.mes and r.mes.isdigit():
            mes_key = int(r.mes)
            receita_dict[mes_key] = receita_dict.get(mes_key, 0) + float(r.receita or 0)
    for r in resultados_edu:
        if r.mes and r.mes.isdigit():
            mes_key = int(r.mes)
            receita_dict[mes_key] = receita_dict.get(mes_key, 0) + float(r.receita or 0)
    
    meses = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
             7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
    
    # Criar lista de meses ordenada
    resultado_final = []
    for mes_num in sorted(receita_dict.keys()):
        resultado_final.append({
            "mes": f"{meses[mes_num]}/{ano_atual}",
            "receita": receita_dict[mes_num]
        })
    
    return resultado_final

@router.get("/produtividade-consultores")
async def produtividade_consultores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Usar dados das linhas para produtividade
    # Conta a quantidade de propostas por consultor como métrica de produtividade
    resultados_tec = db.query(
        LinhaTecnologia.consultor,
        func.count(LinhaTecnologia.id).label('quantidade')
    ).filter(LinhaTecnologia.consultor.isnot(None)).group_by(LinhaTecnologia.consultor).all()
    
    resultados_edu = db.query(
        LinhaEducacional.instrutor_1,
        func.count(LinhaEducacional.id).label('quantidade')
    ).filter(LinhaEducacional.instrutor_1.isnot(None)).group_by(LinhaEducacional.instrutor_1).all()
    
    # Consolidar
    consultor_dict = {}
    for r in resultados_tec:
        consultor_dict[r.consultor] = consultor_dict.get(r.consultor, 0) + r.quantidade
    for r in resultados_edu:
        consultor_dict[r.instrutor_1] = consultor_dict.get(r.instrutor_1, 0) + r.quantidade
    
    # Retornar top 10
    consultores_sorted = sorted(consultor_dict.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return [{"consultor": consultor, "horas": total * 10} for consultor, total in consultores_sorted]
