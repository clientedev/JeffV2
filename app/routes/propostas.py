from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.models import Proposta, Usuario
from app.schemas import PropostaCreate, PropostaUpdate, PropostaResponse
from app.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=PropostaResponse, status_code=status.HTTP_201_CREATED)
async def criar_proposta(
    proposta: PropostaCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    db_proposta = db.query(Proposta).filter(Proposta.numero_proposta == proposta.numero_proposta).first()
    if db_proposta:
        raise HTTPException(status_code=400, detail="Número de proposta já existe")
    
    new_proposta = Proposta(**proposta.model_dump())
    db.add(new_proposta)
    db.commit()
    db.refresh(new_proposta)
    return new_proposta

@router.get("/", response_model=List[PropostaResponse])
async def listar_propostas(
    skip: int = 0, 
    limit: int = 100,
    status_filter: Optional[str] = None,
    consultor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Proposta)
    
    if current_user.funcao == "Consultor" and current_user.consultor_id:
        query = query.filter(Proposta.consultor_id == current_user.consultor_id)
    
    if status_filter:
        query = query.filter(Proposta.status == status_filter)
    
    if consultor_id:
        query = query.filter(Proposta.consultor_id == consultor_id)
    
    propostas = query.offset(skip).limit(limit).all()
    return propostas

@router.get("/{proposta_id}", response_model=PropostaResponse)
async def obter_proposta(
    proposta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    proposta = db.query(Proposta).filter(Proposta.id == proposta_id).first()
    if not proposta:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    return proposta

@router.put("/{proposta_id}", response_model=PropostaResponse)
async def atualizar_proposta(
    proposta_id: int,
    proposta_data: PropostaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    proposta = db.query(Proposta).filter(Proposta.id == proposta_id).first()
    if not proposta:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    
    for key, value in proposta_data.model_dump(exclude_unset=True).items():
        setattr(proposta, key, value)
    
    db.commit()
    db.refresh(proposta)
    return proposta

@router.delete("/{proposta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_proposta(
    proposta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    proposta = db.query(Proposta).filter(Proposta.id == proposta_id).first()
    if not proposta:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    
    db.delete(proposta)
    db.commit()
    return None
