from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import Empresa, Usuario
from app.schemas import EmpresaCreate, EmpresaResponse
from app.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
async def criar_empresa(
    empresa: EmpresaCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    db_empresa = db.query(Empresa).filter(Empresa.cnpj == empresa.cnpj).first()
    if db_empresa:
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
    
    new_empresa = Empresa(**empresa.model_dump())
    db.add(new_empresa)
    db.commit()
    db.refresh(new_empresa)
    return new_empresa

@router.get("/", response_model=List[EmpresaResponse])
async def listar_empresas(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    empresas = db.query(Empresa).offset(skip).limit(limit).all()
    return empresas

@router.get("/{empresa_id}", response_model=EmpresaResponse)
async def obter_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa

@router.put("/{empresa_id}", response_model=EmpresaResponse)
async def atualizar_empresa(
    empresa_id: int,
    empresa_data: EmpresaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    for key, value in empresa_data.model_dump().items():
        setattr(empresa, key, value)
    
    db.commit()
    db.refresh(empresa)
    return empresa

@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    db.delete(empresa)
    db.commit()
    return None
