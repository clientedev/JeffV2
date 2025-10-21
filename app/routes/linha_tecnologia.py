from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_, extract
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.database import get_db
from app.models.models import LinhaTecnologia
from app.auth import get_current_user
from fastapi.responses import StreamingResponse
import io
import pandas as pd
from decimal import Decimal

router = APIRouter()

class LinhaTecnologiaCreate(BaseModel):
    linha: Optional[str] = None
    tipo_programa: Optional[str] = None
    cnpj: Optional[str] = None
    empresa: Optional[str] = None
    porte: Optional[str] = None
    er: Optional[str] = None
    sigla: Optional[str] = None
    t3: Optional[str] = None
    status_etapa: Optional[str] = None
    numero_proposta: Optional[str] = None
    consultor: Optional[str] = None
    valor_proposta: Optional[Decimal] = None
    situacao: Optional[str] = None
    solucao: Optional[str] = None
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    observacoes: Optional[str] = None
    ano: Optional[int] = None
    mes: Optional[str] = None

class LinhaTecnologiaResponse(BaseModel):
    id: int
    linha: Optional[str]
    tipo_programa: Optional[str]
    cnpj: Optional[str]
    empresa: Optional[str]
    porte: Optional[str]
    er: Optional[str]
    sigla: Optional[str]
    t3: Optional[str]
    status_etapa: Optional[str]
    oportunidade: Optional[str]
    numero_proposta: Optional[str]
    ordem_venda: Optional[str]
    emissor_proposta: Optional[str]
    cfp_parceiro: Optional[str]
    consultor: Optional[str]
    valor_proposta: Optional[Decimal]
    situacao: Optional[str]
    solucao: Optional[str]
    ch: Optional[str]
    dados_socios_informados: Optional[str]
    contrato_enviado_empresa: Optional[str]
    contrato_assinado_empresa: Optional[str]
    data_contrato_assinado_senai: Optional[date]
    data_cadastro_sgt: Optional[date]
    data_upload_sgt: Optional[date]
    data_aceite_sgt: Optional[date]
    data_envio_relatorio_t1: Optional[date]
    data_cobranca_empresa: Optional[date]
    cadastro_plataforma_ok: Optional[str]
    data_cobranca_sebrae: Optional[date]
    contrato_sebrae_enviado: Optional[str]
    data_resposta_sebrae: Optional[date]
    requisicao_grm: Optional[str]
    data_inicio: Optional[date]
    data_termino: Optional[date]
    reuniao_kickoff_confirmada: Optional[str]
    reuniao_final_agendada: Optional[str]
    presencial: Optional[str]
    gratuidade: Optional[str]
    numero_demanda: Optional[str]
    codigo_rae: Optional[str]
    mov_1_1_57: Optional[str]
    relatorio_priorizacao_enviado: Optional[str]
    relatorio_smart_factory: Optional[str]
    relatorio_final_enviado: Optional[str]
    relatorio_educacional_enviado: Optional[str]
    data_conclusao_sgt: Optional[date]
    envio_auditoria: Optional[str]
    retorno_auditoria: Optional[str]
    data_prestacao_contas: Optional[date]
    data_pesquisa_satisfacao: Optional[date]
    observacoes: Optional[str]
    especifico_saldo: Optional[str]
    passou_ali_2023: Optional[str]
    ali_2024_convidar: Optional[str]
    t3_solucao_1_2024: Optional[str]
    t3_solucao_2_2024: Optional[str]
    aceitou: Optional[str]
    qual_3_etapa: Optional[str]
    t4_proposto_2024: Optional[str]
    aceitou_2: Optional[str]
    follow_2024: Optional[str]
    continuidade: Optional[str]
    etapa_5_ou_6: Optional[str]
    fez_efici_energ: Optional[str]
    obs2: Optional[str]
    ano: Optional[int]
    mes: Optional[str]
    inu: Optional[str]
    hubspot: Optional[str]
    nova_proposta: Optional[str]
    valor_sap: Optional[Decimal]
    dados_iniciais: bool
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True

class ListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[LinhaTecnologiaResponse]

@router.get("/", response_model=ListResponse)
async def listar(
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    situacao: Optional[str] = None,
    status_etapa: Optional[str] = None,
    ano: Optional[int] = None,
    mes: Optional[str] = None,
    tipo_programa: Optional[str] = None,
    porte: Optional[str] = None,
    er: Optional[str] = None,
    consultor: Optional[str] = None,
    t3: Optional[str] = None,
    data_inicio_de: Optional[date] = None,
    data_inicio_ate: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(LinhaTecnologia)
    
    # Filtro de busca geral
    if search:
        query = query.filter(
            or_(
                LinhaTecnologia.empresa.ilike(f"%{search}%"),
                LinhaTecnologia.numero_proposta.ilike(f"%{search}%"),
                LinhaTecnologia.consultor.ilike(f"%{search}%"),
                LinhaTecnologia.cnpj.ilike(f"%{search}%"),
                LinhaTecnologia.sigla.ilike(f"%{search}%")
            )
        )
    
    # Filtros específicos
    if situacao:
        query = query.filter(LinhaTecnologia.situacao == situacao)
    
    if status_etapa:
        query = query.filter(LinhaTecnologia.status_etapa == status_etapa)
    
    if ano:
        query = query.filter(LinhaTecnologia.ano == ano)
    
    if mes:
        query = query.filter(LinhaTecnologia.mes == mes)
    
    if tipo_programa:
        query = query.filter(LinhaTecnologia.tipo_programa == tipo_programa)
    
    if porte:
        query = query.filter(LinhaTecnologia.porte == porte)
    
    if er:
        query = query.filter(LinhaTecnologia.er == er)
    
    if consultor:
        query = query.filter(LinhaTecnologia.consultor.ilike(f"%{consultor}%"))
    
    if t3:
        query = query.filter(LinhaTecnologia.t3 == t3)
    
    if data_inicio_de:
        query = query.filter(LinhaTecnologia.data_inicio >= data_inicio_de)
    
    if data_inicio_ate:
        query = query.filter(LinhaTecnologia.data_inicio <= data_inicio_ate)
    
    # Contagem total
    total = query.count()
    
    # Paginação
    offset = (page - 1) * page_size
    registros = query.order_by(LinhaTecnologia.criado_em.desc()).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": registros
    }

@router.get("/filtros")
async def obter_filtros(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Retorna valores únicos para cada campo de filtro"""
    situacoes = db.query(LinhaTecnologia.situacao).distinct().filter(LinhaTecnologia.situacao.isnot(None)).all()
    status_etapas = db.query(LinhaTecnologia.status_etapa).distinct().filter(LinhaTecnologia.status_etapa.isnot(None)).all()
    anos = db.query(LinhaTecnologia.ano).distinct().filter(LinhaTecnologia.ano.isnot(None)).all()
    meses = db.query(LinhaTecnologia.mes).distinct().filter(LinhaTecnologia.mes.isnot(None)).all()
    tipos_programa = db.query(LinhaTecnologia.tipo_programa).distinct().filter(LinhaTecnologia.tipo_programa.isnot(None)).all()
    portes = db.query(LinhaTecnologia.porte).distinct().filter(LinhaTecnologia.porte.isnot(None)).all()
    ers = db.query(LinhaTecnologia.er).distinct().filter(LinhaTecnologia.er.isnot(None)).all()
    consultores = db.query(LinhaTecnologia.consultor).distinct().filter(LinhaTecnologia.consultor.isnot(None)).all()
    t3s = db.query(LinhaTecnologia.t3).distinct().filter(LinhaTecnologia.t3.isnot(None)).all()
    
    return {
        "situacoes": sorted([s[0] for s in situacoes if s[0]]),
        "status_etapas": sorted([s[0] for s in status_etapas if s[0]]),
        "anos": sorted([a[0] for a in anos if a[0]], reverse=True),
        "meses": [m[0] for m in meses if m[0]],
        "tipos_programa": sorted([t[0] for t in tipos_programa if t[0]]),
        "portes": sorted([p[0] for p in portes if p[0]]),
        "ers": sorted([e[0] for e in ers if e[0]]),
        "consultores": sorted([c[0] for c in consultores if c[0]]),
        "t3s": sorted([t[0] for t in t3s if t[0]])
    }

@router.get("/estatisticas")
async def obter_estatisticas(
    ano: Optional[int] = None,
    mes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Retorna estatísticas agregadas da linha tecnologia"""
    query = db.query(LinhaTecnologia)
    
    if ano:
        query = query.filter(LinhaTecnologia.ano == ano)
    
    if mes:
        query = query.filter(LinhaTecnologia.mes == mes)
    
    # Estatísticas gerais
    total_registros = query.count()
    total_valor = query.with_entities(func.sum(LinhaTecnologia.valor_proposta)).scalar() or 0
    
    # Por status etapa
    por_status = db.query(
        LinhaTecnologia.status_etapa,
        func.count(LinhaTecnologia.id).label('quantidade'),
        func.sum(LinhaTecnologia.valor_proposta).label('valor_total')
    ).filter(
        and_(
            LinhaTecnologia.ano == ano if ano else True,
            LinhaTecnologia.mes == mes if mes else True
        )
    ).group_by(LinhaTecnologia.status_etapa).all()
    
    # Por tipo de programa
    por_tipo_programa = db.query(
        LinhaTecnologia.tipo_programa,
        func.count(LinhaTecnologia.id).label('quantidade')
    ).filter(
        and_(
            LinhaTecnologia.ano == ano if ano else True,
            LinhaTecnologia.mes == mes if mes else True
        )
    ).group_by(LinhaTecnologia.tipo_programa).all()
    
    # Por porte
    por_porte = db.query(
        LinhaTecnologia.porte,
        func.count(LinhaTecnologia.id).label('quantidade')
    ).filter(
        and_(
            LinhaTecnologia.ano == ano if ano else True,
            LinhaTecnologia.mes == mes if mes else True
        )
    ).group_by(LinhaTecnologia.porte).all()
    
    # Por consultor
    por_consultor = db.query(
        LinhaTecnologia.consultor,
        func.count(LinhaTecnologia.id).label('quantidade'),
        func.sum(LinhaTecnologia.valor_proposta).label('valor_total')
    ).filter(
        and_(
            LinhaTecnologia.ano == ano if ano else True,
            LinhaTecnologia.mes == mes if mes else True
        )
    ).group_by(LinhaTecnologia.consultor).order_by(func.count(LinhaTecnologia.id).desc()).limit(10).all()
    
    return {
        "total_registros": total_registros,
        "total_valor": float(total_valor),
        "por_status_etapa": [
            {"status": s[0], "quantidade": s[1], "valor_total": float(s[2] or 0)}
            for s in por_status if s[0]
        ],
        "por_tipo_programa": [
            {"tipo": t[0], "quantidade": t[1]}
            for t in por_tipo_programa if t[0]
        ],
        "por_porte": [
            {"porte": p[0], "quantidade": p[1]}
            for p in por_porte if p[0]
        ],
        "por_consultor": [
            {"consultor": c[0], "quantidade": c[1], "valor_total": float(c[2] or 0)}
            for c in por_consultor if c[0]
        ]
    }

@router.get("/{id}", response_model=LinhaTecnologiaResponse)
async def obter(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    registro = db.query(LinhaTecnologia).filter(LinhaTecnologia.id == id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return registro

@router.post("/", response_model=LinhaTecnologiaResponse)
async def criar(
    data: LinhaTecnologiaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    registro = LinhaTecnologia(**data.dict(), dados_iniciais=False)
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro

@router.put("/{id}", response_model=LinhaTecnologiaResponse)
async def atualizar(
    id: int,
    data: LinhaTecnologiaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    registro = db.query(LinhaTecnologia).filter(LinhaTecnologia.id == id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    
    if registro.dados_iniciais:
        raise HTTPException(status_code=403, detail="Dados iniciais não podem ser modificados")
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(registro, key, value)
    
    db.commit()
    db.refresh(registro)
    return registro

@router.delete("/{id}")
async def deletar(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    registro = db.query(LinhaTecnologia).filter(LinhaTecnologia.id == id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    
    if registro.dados_iniciais:
        raise HTTPException(status_code=403, detail="Dados iniciais não podem ser deletados")
    
    db.delete(registro)
    db.commit()
    return {"message": "Registro deletado com sucesso"}

@router.get("/exportar/excel")
async def exportar_excel(
    search: Optional[str] = None,
    situacao: Optional[str] = None,
    ano: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(LinhaTecnologia)
    
    if search:
        query = query.filter(
            or_(
                LinhaTecnologia.empresa.ilike(f"%{search}%"),
                LinhaTecnologia.numero_proposta.ilike(f"%{search}%")
            )
        )
    
    if situacao:
        query = query.filter(LinhaTecnologia.situacao == situacao)
    
    if ano:
        query = query.filter(LinhaTecnologia.ano == ano)
    
    registros = query.all()
    
    data = []
    for r in registros:
        data.append({
            "ID": r.id,
            "Linha": r.linha,
            "Tipo Programa": r.tipo_programa,
            "CNPJ": r.cnpj,
            "Empresa": r.empresa,
            "Porte": r.porte,
            "ER": r.er,
            "Sigla": r.sigla,
            "T3": r.t3,
            "Status Etapa": r.status_etapa,
            "Nº Proposta": r.numero_proposta,
            "Consultor": r.consultor,
            "Solução": r.solucao,
            "Valor Proposta": float(r.valor_proposta) if r.valor_proposta else None,
            "Situação": r.situacao,
            "Data Início": r.data_inicio,
            "Data Término": r.data_termino,
            "Ano": r.ano,
            "Mês": r.mes,
            "Observações": r.observacoes
        })
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    df.to_excel(output, index=False, sheet_name='Linha Tecnologia', engine='openpyxl')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=linha_tecnologia_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )
