from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import Consultor, Usuario
from app.schemas import ConsultorCreate, ConsultorResponse
from app.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ConsultorResponse, status_code=status.HTTP_201_CREATED)
async def criar_consultor(
    consultor: ConsultorCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    db_consultor = db.query(Consultor).filter(Consultor.email == consultor.email).first()
    if db_consultor:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    new_consultor = Consultor(**consultor.model_dump())
    db.add(new_consultor)
    db.commit()
    db.refresh(new_consultor)
    return new_consultor

@router.get("/", response_model=List[ConsultorResponse])
async def listar_consultores(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    consultores = db.query(Consultor).filter(Consultor.ativo == True).offset(skip).limit(limit).all()
    return consultores

@router.get("/{consultor_id}", response_model=ConsultorResponse)
async def obter_consultor(
    consultor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    consultor = db.query(Consultor).filter(Consultor.id == consultor_id).first()
    if not consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")
    return consultor

@router.put("/{consultor_id}", response_model=ConsultorResponse)
async def atualizar_consultor(
    consultor_id: int,
    consultor_data: ConsultorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    consultor = db.query(Consultor).filter(Consultor.id == consultor_id).first()
    if not consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")
    
    for key, value in consultor_data.model_dump().items():
        setattr(consultor, key, value)
    
    db.commit()
    db.refresh(consultor)
    return consultor

@router.delete("/{consultor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_consultor(
    consultor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    consultor = db.query(Consultor).filter(Consultor.id == consultor_id).first()
    if not consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")
    
    consultor.ativo = False
    db.commit()
    return None
