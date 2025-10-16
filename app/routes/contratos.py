from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta

from app.database import get_db
from app.models.models import Contrato, Usuario
from app.schemas import ContratoCreate, ContratoUpdate, ContratoResponse
from app.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ContratoResponse, status_code=status.HTTP_201_CREATED)
async def criar_contrato(
    contrato: ContratoCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    db_contrato = db.query(Contrato).filter(Contrato.numero_contrato == contrato.numero_contrato).first()
    if db_contrato:
        raise HTTPException(status_code=400, detail="Número de contrato já existe")
    
    new_contrato = Contrato(**contrato.model_dump())
    db.add(new_contrato)
    db.commit()
    db.refresh(new_contrato)
    return new_contrato

@router.get("/", response_model=List[ContratoResponse])
async def listar_contratos(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    contratos = db.query(Contrato).offset(skip).limit(limit).all()
    return contratos

@router.get("/alertas", response_model=List[ContratoResponse])
async def contratos_vencendo(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    hoje = date.today()
    sete_dias = hoje + timedelta(days=7)
    
    contratos = db.query(Contrato).filter(
        Contrato.data_vencimento <= sete_dias,
        Contrato.data_vencimento >= hoje,
        Contrato.status_pagamento.in_(["Pendente", "Vencido"])
    ).all()
    
    vencidos = db.query(Contrato).filter(
        Contrato.data_vencimento < hoje,
        Contrato.status_pagamento == "Pendente"
    ).all()
    
    for vencido in vencidos:
        vencido.status_pagamento = "Vencido"
    
    db.commit()
    
    return contratos + vencidos

@router.get("/{contrato_id}", response_model=ContratoResponse)
async def obter_contrato(
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return contrato

@router.put("/{contrato_id}", response_model=ContratoResponse)
async def atualizar_contrato(
    contrato_id: int,
    contrato_data: ContratoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    
    for key, value in contrato_data.model_dump(exclude_unset=True).items():
        setattr(contrato, key, value)
    
    db.commit()
    db.refresh(contrato)
    return contrato

@router.delete("/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_contrato(
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    
    db.delete(contrato)
    db.commit()
    return None
