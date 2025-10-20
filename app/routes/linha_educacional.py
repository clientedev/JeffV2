from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.database import get_db
from app.models.models import LinhaEducacional
from app.auth import get_current_user
from fastapi.responses import StreamingResponse
import io
import pandas as pd
from decimal import Decimal

router = APIRouter()

class LinhaEducacionalCreate(BaseModel):
    linha: Optional[str] = None
    cliente: Optional[str] = None
    cnpj: Optional[str] = None
    estabelecimento: Optional[str] = None
    numero_proposta: Optional[str] = None
    programa: Optional[str] = None
    tipo: Optional[str] = None
    modalidade: Optional[str] = None
    valor: Optional[Decimal] = None
    situacao: Optional[str] = None
    status_proposta: Optional[str] = None
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    observacoes: Optional[str] = None
    ano: Optional[int] = None
    mes: Optional[str] = None

class LinhaEducacionalResponse(BaseModel):
    id: int
    linha: Optional[str]
    cliente: Optional[str]
    cnpj: Optional[str]
    estabelecimento: Optional[str]
    numero_proposta: Optional[str]
    programa: Optional[str]
    tipo: Optional[str]
    modalidade: Optional[str]
    ch: Optional[str]
    valor: Optional[Decimal]
    situacao: Optional[str]
    status_proposta: Optional[str]
    data_inicio: Optional[date]
    data_termino: Optional[date]
    observacoes: Optional[str]
    ano: Optional[int]
    mes: Optional[str]
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
    data: List[LinhaEducacionalResponse]

@router.get("/", response_model=ListResponse)
async def listar(
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    situacao: Optional[str] = None,
    status_proposta: Optional[str] = None,
    ano: Optional[int] = None,
    mes: Optional[str] = None,
    tipo: Optional[str] = None,
    programa: Optional[str] = None,
    modalidade: Optional[str] = None,
    data_inicio_de: Optional[date] = None,
    data_inicio_ate: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(LinhaEducacional)
    
    # Filtro de busca geral
    if search:
        query = query.filter(
            or_(
                LinhaEducacional.cliente.ilike(f"%{search}%"),
                LinhaEducacional.estabelecimento.ilike(f"%{search}%"),
                LinhaEducacional.numero_proposta.ilike(f"%{search}%"),
                LinhaEducacional.cnpj.ilike(f"%{search}%"),
                LinhaEducacional.programa.ilike(f"%{search}%")
            )
        )
    
    # Filtros específicos
    if situacao:
        query = query.filter(LinhaEducacional.situacao == situacao)
    
    if status_proposta:
        query = query.filter(LinhaEducacional.status_proposta == status_proposta)
    
    if ano:
        query = query.filter(LinhaEducacional.ano == ano)
    
    if mes:
        query = query.filter(LinhaEducacional.mes == mes)
    
    if tipo:
        query = query.filter(LinhaEducacional.tipo == tipo)
    
    if programa:
        query = query.filter(LinhaEducacional.programa.ilike(f"%{programa}%"))
    
    if modalidade:
        query = query.filter(LinhaEducacional.modalidade == modalidade)
    
    if data_inicio_de:
        query = query.filter(LinhaEducacional.data_inicio >= data_inicio_de)
    
    if data_inicio_ate:
        query = query.filter(LinhaEducacional.data_inicio <= data_inicio_ate)
    
    # Contagem total
    total = query.count()
    
    # Paginação
    offset = (page - 1) * page_size
    registros = query.order_by(LinhaEducacional.criado_em.desc()).offset(offset).limit(page_size).all()
    
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
    situacoes = db.query(LinhaEducacional.situacao).distinct().filter(LinhaEducacional.situacao.isnot(None)).all()
    status_propostas = db.query(LinhaEducacional.status_proposta).distinct().filter(LinhaEducacional.status_proposta.isnot(None)).all()
    anos = db.query(LinhaEducacional.ano).distinct().filter(LinhaEducacional.ano.isnot(None)).all()
    meses = db.query(LinhaEducacional.mes).distinct().filter(LinhaEducacional.mes.isnot(None)).all()
    tipos = db.query(LinhaEducacional.tipo).distinct().filter(LinhaEducacional.tipo.isnot(None)).all()
    programas = db.query(LinhaEducacional.programa).distinct().filter(LinhaEducacional.programa.isnot(None)).all()
    modalidades = db.query(LinhaEducacional.modalidade).distinct().filter(LinhaEducacional.modalidade.isnot(None)).all()
    
    return {
        "situacoes": sorted([s[0] for s in situacoes if s[0]]),
        "status_propostas": sorted([s[0] for s in status_propostas if s[0]]),
        "anos": sorted([a[0] for a in anos if a[0]], reverse=True),
        "meses": [m[0] for m in meses if m[0]],
        "tipos": sorted([t[0] for t in tipos if t[0]]),
        "programas": sorted([p[0] for p in programas if p[0]]),
        "modalidades": sorted([m[0] for m in modalidades if m[0]])
    }

@router.get("/estatisticas")
async def obter_estatisticas(
    ano: Optional[int] = None,
    mes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Retorna estatísticas agregadas da linha educacional"""
    query = db.query(LinhaEducacional)
    
    if ano:
        query = query.filter(LinhaEducacional.ano == ano)
    
    if mes:
        query = query.filter(LinhaEducacional.mes == mes)
    
    # Estatísticas gerais
    total_registros = query.count()
    total_valor = query.with_entities(func.sum(LinhaEducacional.valor)).scalar() or 0
    
    # Por status proposta
    por_status = db.query(
        LinhaEducacional.status_proposta,
        func.count(LinhaEducacional.id).label('quantidade'),
        func.sum(LinhaEducacional.valor).label('valor_total')
    ).filter(
        and_(
            LinhaEducacional.ano == ano if ano else True,
            LinhaEducacional.mes == mes if mes else True
        )
    ).group_by(LinhaEducacional.status_proposta).all()
    
    # Por tipo
    por_tipo = db.query(
        LinhaEducacional.tipo,
        func.count(LinhaEducacional.id).label('quantidade')
    ).filter(
        and_(
            LinhaEducacional.ano == ano if ano else True,
            LinhaEducacional.mes == mes if mes else True
        )
    ).group_by(LinhaEducacional.tipo).all()
    
    # Por modalidade
    por_modalidade = db.query(
        LinhaEducacional.modalidade,
        func.count(LinhaEducacional.id).label('quantidade')
    ).filter(
        and_(
            LinhaEducacional.ano == ano if ano else True,
            LinhaEducacional.mes == mes if mes else True
        )
    ).group_by(LinhaEducacional.modalidade).all()
    
    # Por programa (top 10)
    por_programa = db.query(
        LinhaEducacional.programa,
        func.count(LinhaEducacional.id).label('quantidade'),
        func.sum(LinhaEducacional.valor).label('valor_total')
    ).filter(
        and_(
            LinhaEducacional.ano == ano if ano else True,
            LinhaEducacional.mes == mes if mes else True
        )
    ).group_by(LinhaEducacional.programa).order_by(func.count(LinhaEducacional.id).desc()).limit(10).all()
    
    return {
        "total_registros": total_registros,
        "total_valor": float(total_valor),
        "por_status_proposta": [
            {"status": s[0], "quantidade": s[1], "valor_total": float(s[2] or 0)}
            for s in por_status if s[0]
        ],
        "por_tipo": [
            {"tipo": t[0], "quantidade": t[1]}
            for t in por_tipo if t[0]
        ],
        "por_modalidade": [
            {"modalidade": m[0], "quantidade": m[1]}
            for m in por_modalidade if m[0]
        ],
        "por_programa": [
            {"programa": p[0], "quantidade": p[1], "valor_total": float(p[2] or 0)}
            for p in por_programa if p[0]
        ]
    }

@router.get("/{id}", response_model=LinhaEducacionalResponse)
async def obter(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    registro = db.query(LinhaEducacional).filter(LinhaEducacional.id == id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return registro

@router.post("/", response_model=LinhaEducacionalResponse)
async def criar(
    data: LinhaEducacionalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    registro = LinhaEducacional(**data.dict(), dados_iniciais=False)
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro

@router.put("/{id}", response_model=LinhaEducacionalResponse)
async def atualizar(
    id: int,
    data: LinhaEducacionalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    registro = db.query(LinhaEducacional).filter(LinhaEducacional.id == id).first()
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
    registro = db.query(LinhaEducacional).filter(LinhaEducacional.id == id).first()
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
    query = db.query(LinhaEducacional)
    
    if search:
        query = query.filter(
            or_(
                LinhaEducacional.cliente.ilike(f"%{search}%"),
                LinhaEducacional.numero_proposta.ilike(f"%{search}%")
            )
        )
    
    if situacao:
        query = query.filter(LinhaEducacional.situacao == situacao)
    
    if ano:
        query = query.filter(LinhaEducacional.ano == ano)
    
    registros = query.all()
    
    data = []
    for r in registros:
        data.append({
            "ID": r.id,
            "Linha": r.linha,
            "Cliente": r.cliente,
            "CNPJ": r.cnpj,
            "Estabelecimento": r.estabelecimento,
            "Nº Proposta": r.numero_proposta,
            "Programa": r.programa,
            "Tipo": r.tipo,
            "Modalidade": r.modalidade,
            "CH": r.ch,
            "Valor": float(r.valor) if r.valor else None,
            "Situação": r.situacao,
            "Status Proposta": r.status_proposta,
            "Data Início": r.data_inicio,
            "Data Término": r.data_termino,
            "Ano": r.ano,
            "Mês": r.mes,
            "Observações": r.observacoes
        })
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    df.to_excel(output, index=False, sheet_name='Linha Educacional', engine='openpyxl')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=linha_educacional_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )
