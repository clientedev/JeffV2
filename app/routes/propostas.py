from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta, datetime

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
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
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
    
    if data_inicio:
        query = query.filter(Proposta.data_proposta >= data_inicio)
    
    if data_fim:
        query = query.filter(Proposta.data_proposta <= data_fim)
    
    propostas = query.offset(skip).limit(limit).all()
    return propostas

@router.get("/estatisticas")
async def obter_estatisticas_propostas(
    consultor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Proposta)
    
    if current_user.funcao == "Consultor" and current_user.consultor_id:
        query = query.filter(Proposta.consultor_id == current_user.consultor_id)
    elif consultor_id:
        query = query.filter(Proposta.consultor_id == consultor_id)
    
    total_propostas = query.count()
    propostas_fechadas = query.filter(Proposta.status == "Fechado").count()
    propostas_em_andamento = query.filter(Proposta.status == "Em andamento").count()
    propostas_perdidas = query.filter(Proposta.status == "Perdido").count()
    
    taxa_conversao = (propostas_fechadas / total_propostas * 100) if total_propostas > 0 else 0
    
    propostas_paradas = query.filter(
        Proposta.status == "Em andamento",
        Proposta.atualizado_em < datetime.now() - timedelta(days=30)
    ).count()
    
    valor_total = db.query(func.sum(Proposta.valor_proposta)).filter(
        Proposta.id.in_([p.id for p in query.all()]),
        Proposta.status == "Fechado"
    ).scalar() or 0
    
    return {
        "total_propostas": total_propostas,
        "propostas_fechadas": propostas_fechadas,
        "propostas_em_andamento": propostas_em_andamento,
        "propostas_perdidas": propostas_perdidas,
        "propostas_paradas": propostas_paradas,
        "taxa_conversao": round(taxa_conversao, 2),
        "valor_total_fechado": float(valor_total)
    }

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
