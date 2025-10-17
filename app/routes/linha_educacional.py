from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
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
    tipo_programa: Optional[str] = None
    cnpj: Optional[str] = None
    empresa: Optional[str] = None
    porte: Optional[str] = None
    er: Optional[str] = None
    sigla: Optional[str] = None
    status_etapa: Optional[str] = None
    numero_proposta: Optional[str] = None
    consultor: Optional[str] = None
    valor_proposta: Optional[Decimal] = None
    situacao: Optional[str] = None
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    observacoes: Optional[str] = None
    ano: Optional[int] = None
    mes: Optional[str] = None

class LinhaEducacionalResponse(BaseModel):
    id: int
    linha: Optional[str]
    tipo_programa: Optional[str]
    cnpj: Optional[str]
    empresa: Optional[str]
    porte: Optional[str]
    er: Optional[str]
    sigla: Optional[str]
    status_etapa: Optional[str]
    numero_proposta: Optional[str]
    consultor: Optional[str]
    valor_proposta: Optional[Decimal]
    situacao: Optional[str]
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

@router.get("/", response_model=List[LinhaEducacionalResponse])
async def listar(
    skip: int = 0,
    limit: int = 100,
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
                LinhaEducacional.empresa.ilike(f"%{search}%"),
                LinhaEducacional.numero_proposta.ilike(f"%{search}%"),
                LinhaEducacional.consultor.ilike(f"%{search}%")
            )
        )
    
    if situacao:
        query = query.filter(LinhaEducacional.situacao == situacao)
    
    if ano:
        query = query.filter(LinhaEducacional.ano == ano)
    
    registros = query.order_by(LinhaEducacional.empresa).offset(skip).limit(limit).all()
    return registros

@router.get("/filtros")
async def obter_filtros(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    situacoes = db.query(LinhaEducacional.situacao).distinct().filter(LinhaEducacional.situacao.isnot(None)).all()
    anos = db.query(LinhaEducacional.ano).distinct().filter(LinhaEducacional.ano.isnot(None)).all()
    
    return {
        "situacoes": sorted([s[0] for s in situacoes if s[0]]),
        "anos": sorted([a[0] for a in anos if a[0]], reverse=True)
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
                LinhaEducacional.empresa.ilike(f"%{search}%"),
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
            "Tipo Programa": r.tipo_programa,
            "CNPJ": r.cnpj,
            "Empresa": r.empresa,
            "Porte": r.porte,
            "ER": r.er,
            "Nº Proposta": r.numero_proposta,
            "Consultor": r.consultor,
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
    df.to_excel(output, index=False, sheet_name='Linha Educacional', engine='openpyxl')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=linha_educacional_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )
