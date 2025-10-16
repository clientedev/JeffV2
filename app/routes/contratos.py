from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
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
    status_pagamento: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Contrato)
    
    if status_pagamento:
        query = query.filter(Contrato.status_pagamento == status_pagamento)
    
    if data_inicio:
        query = query.filter(Contrato.data_vencimento >= data_inicio)
    
    if data_fim:
        query = query.filter(Contrato.data_vencimento <= data_fim)
    
    contratos = query.offset(skip).limit(limit).all()
    return contratos

@router.get("/faturamento")
async def obter_faturamento(
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Contrato)
    
    if ano and mes:
        query = query.filter(
            func.extract('year', Contrato.data_assinatura) == ano,
            func.extract('month', Contrato.data_assinatura) == mes
        )
    elif ano:
        query = query.filter(func.extract('year', Contrato.data_assinatura) == ano)
    
    total_contratos = query.count()
    contratos_pagos = query.filter(Contrato.status_pagamento == "Pago").count()
    contratos_pendentes = query.filter(Contrato.status_pagamento == "Pendente").count()
    contratos_vencidos = query.filter(Contrato.status_pagamento == "Vencido").count()
    
    valor_total = db.query(func.sum(Contrato.valor)).filter(
        Contrato.id.in_([c.id for c in query.all()])
    ).scalar() or 0
    
    valor_pago = db.query(func.sum(Contrato.valor)).filter(
        Contrato.id.in_([c.id for c in query.all()]),
        Contrato.status_pagamento == "Pago"
    ).scalar() or 0
    
    valor_pendente = db.query(func.sum(Contrato.valor)).filter(
        Contrato.id.in_([c.id for c in query.all()]),
        Contrato.status_pagamento.in_(["Pendente", "Vencido"])
    ).scalar() or 0
    
    return {
        "periodo": f"{ano}/{mes:02d}" if ano and mes else str(ano) if ano else "Total",
        "total_contratos": total_contratos,
        "contratos_pagos": contratos_pagos,
        "contratos_pendentes": contratos_pendentes,
        "contratos_vencidos": contratos_vencidos,
        "valor_total": float(valor_total),
        "valor_pago": float(valor_pago),
        "valor_pendente": float(valor_pendente),
        "taxa_pagamento": round((contratos_pagos / total_contratos * 100) if total_contratos > 0 else 0, 2)
    }

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
