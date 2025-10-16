from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta

from app.database import get_db
from app.models.models import Cronograma, Tarefa, Usuario
from app.schemas import CronogramaCreate, CronogramaUpdate, CronogramaResponse, TarefaCreate, TarefaResponse
from app.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=CronogramaResponse, status_code=status.HTTP_201_CREATED)
async def criar_cronograma(
    cronograma: CronogramaCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    new_cronograma = Cronograma(**cronograma.model_dump())
    db.add(new_cronograma)
    db.commit()
    db.refresh(new_cronograma)
    return new_cronograma

@router.get("/", response_model=List[CronogramaResponse])
async def listar_cronogramas(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    cronogramas = db.query(Cronograma).offset(skip).limit(limit).all()
    return cronogramas

@router.get("/alertas", response_model=List[CronogramaResponse])
async def cronogramas_alertas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    hoje = date.today()
    sete_dias = hoje + timedelta(days=7)
    
    cronogramas = db.query(Cronograma).filter(
        Cronograma.data_termino <= sete_dias,
        Cronograma.data_termino >= hoje,
        Cronograma.status != "Concluído"
    ).all()
    
    atrasados = db.query(Cronograma).filter(
        Cronograma.data_termino < hoje,
        Cronograma.status != "Concluído"
    ).all()
    
    return cronogramas + atrasados

@router.get("/{cronograma_id}", response_model=CronogramaResponse)
async def obter_cronograma(
    cronograma_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    cronograma = db.query(Cronograma).filter(Cronograma.id == cronograma_id).first()
    if not cronograma:
        raise HTTPException(status_code=404, detail="Cronograma não encontrado")
    return cronograma

@router.put("/{cronograma_id}", response_model=CronogramaResponse)
async def atualizar_cronograma(
    cronograma_id: int,
    cronograma_data: CronogramaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    cronograma = db.query(Cronograma).filter(Cronograma.id == cronograma_id).first()
    if not cronograma:
        raise HTTPException(status_code=404, detail="Cronograma não encontrado")
    
    for key, value in cronograma_data.model_dump(exclude_unset=True).items():
        setattr(cronograma, key, value)
    
    _atualizar_status_cronograma(cronograma, db)
    
    db.commit()
    db.refresh(cronograma)
    return cronograma

@router.post("/{cronograma_id}/calcular-progresso")
async def calcular_progresso_cronograma(
    cronograma_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    cronograma = db.query(Cronograma).filter(Cronograma.id == cronograma_id).first()
    if not cronograma:
        raise HTTPException(status_code=404, detail="Cronograma não encontrado")
    
    tarefas = db.query(Tarefa).filter(Tarefa.cronograma_id == cronograma_id).all()
    
    if tarefas:
        total_tarefas = len(tarefas)
        tarefas_concluidas = sum(1 for t in tarefas if t.concluida)
        percentual = (tarefas_concluidas / total_tarefas) * 100
        cronograma.percentual_conclusao = round(percentual, 2)
    
    _atualizar_status_cronograma(cronograma, db)
    
    db.commit()
    db.refresh(cronograma)
    
    return {
        "cronograma_id": cronograma.id,
        "percentual_conclusao": float(cronograma.percentual_conclusao),
        "status": cronograma.status,
        "total_tarefas": len(tarefas) if tarefas else 0,
        "tarefas_concluidas": sum(1 for t in tarefas if t.concluida) if tarefas else 0
    }

def _atualizar_status_cronograma(cronograma: Cronograma, db: Session):
    hoje = date.today()
    
    if cronograma.percentual_conclusao >= 100:
        cronograma.status = "Concluído"
    elif cronograma.data_termino and cronograma.data_termino < hoje and cronograma.percentual_conclusao < 100:
        cronograma.status = "Atrasado"
    elif cronograma.data_inicio and cronograma.data_inicio <= hoje:
        cronograma.status = "Em andamento"
    else:
        cronograma.status = "Não iniciado"

@router.delete("/{cronograma_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_cronograma(
    cronograma_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    cronograma = db.query(Cronograma).filter(Cronograma.id == cronograma_id).first()
    if not cronograma:
        raise HTTPException(status_code=404, detail="Cronograma não encontrado")
    
    db.delete(cronograma)
    db.commit()
    return None

@router.post("/{cronograma_id}/tarefas", response_model=TarefaResponse, status_code=status.HTTP_201_CREATED)
async def adicionar_tarefa(
    cronograma_id: int,
    tarefa: TarefaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    cronograma = db.query(Cronograma).filter(Cronograma.id == cronograma_id).first()
    if not cronograma:
        raise HTTPException(status_code=404, detail="Cronograma não encontrado")
    
    new_tarefa = Tarefa(**tarefa.model_dump())
    db.add(new_tarefa)
    db.commit()
    db.refresh(new_tarefa)
    return new_tarefa

@router.get("/{cronograma_id}/tarefas", response_model=List[TarefaResponse])
async def listar_tarefas(
    cronograma_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    tarefas = db.query(Tarefa).filter(Tarefa.cronograma_id == cronograma_id).order_by(Tarefa.ordem).all()
    return tarefas
