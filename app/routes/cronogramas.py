from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta, datetime
from pydantic import BaseModel
import pandas as pd
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

from app.database import get_db
from app.models.models import Cronograma, Tarefa, Usuario, AlocacaoCronograma, Consultor
from app.schemas import CronogramaCreate, CronogramaUpdate, CronogramaResponse, TarefaCreate, TarefaResponse
from app.auth import get_current_user
from sqlalchemy import func

class AlocacaoCreate(BaseModel):
    consultor_id: int
    data: str
    periodo: str
    codigo_projeto: Optional[str] = None
    observacao: Optional[str] = None

class AlocacaoUpdate(BaseModel):
    codigo_projeto: Optional[str] = None
    observacao: Optional[str] = None

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

@router.get("/alocacoes/listar")
async def listar_alocacoes(
    data_inicio: str = None,
    data_fim: str = None,
    consultor_id: int = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(AlocacaoCronograma).join(Consultor)
    
    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(AlocacaoCronograma.data >= data_inicio_obj)
    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(AlocacaoCronograma.data <= data_fim_obj)
    if consultor_id:
        query = query.filter(AlocacaoCronograma.consultor_id == consultor_id)
    
    alocacoes = query.order_by(AlocacaoCronograma.data, AlocacaoCronograma.periodo).all()
    
    resultado = []
    for alocacao in alocacoes:
        resultado.append({
            "id": alocacao.id,
            "consultor_id": alocacao.consultor_id,
            "consultor_nome": alocacao.consultor.nome,
            "nif": alocacao.nif,
            "data": str(alocacao.data),
            "periodo": alocacao.periodo,
            "codigo_projeto": alocacao.codigo_projeto,
            "observacao": alocacao.observacao
        })
    
    return resultado

@router.get("/alocacoes/gantt")
async def obter_dados_gantt(
    data_inicio: str = None,
    data_fim: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(AlocacaoCronograma).join(Consultor)
    
    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(AlocacaoCronograma.data >= data_inicio_obj)
    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(AlocacaoCronograma.data <= data_fim_obj)
    
    alocacoes = query.order_by(Consultor.nome, AlocacaoCronograma.data).all()
    
    tarefas_gantt = []
    for alocacao in alocacoes:
        tarefas_gantt.append({
            "Task": f"{alocacao.consultor.nome} - {alocacao.periodo}",
            "Start": str(alocacao.data),
            "Finish": str(alocacao.data),
            "Resource": alocacao.codigo_projeto or "Sem projeto",
            "Consultor": alocacao.consultor.nome,
            "Periodo": alocacao.periodo
        })
    
    return tarefas_gantt

@router.get("/alocacoes/estatisticas")
async def obter_estatisticas(
    data_inicio: str = None,
    data_fim: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(AlocacaoCronograma)
    
    data_inicio_obj = None
    data_fim_obj = None
    
    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(AlocacaoCronograma.data >= data_inicio_obj)
    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(AlocacaoCronograma.data <= data_fim_obj)
    
    total_alocacoes = query.count()
    
    query_consultor = db.query(
        Consultor.nome,
        func.count(AlocacaoCronograma.id).label('total')
    ).join(AlocacaoCronograma)
    
    if data_inicio_obj:
        query_consultor = query_consultor.filter(AlocacaoCronograma.data >= data_inicio_obj)
    if data_fim_obj:
        query_consultor = query_consultor.filter(AlocacaoCronograma.data <= data_fim_obj)
    
    alocacoes_por_consultor = query_consultor.group_by(Consultor.nome).all()
    
    query_projeto = db.query(
        AlocacaoCronograma.codigo_projeto,
        func.count(AlocacaoCronograma.id).label('total')
    ).filter(AlocacaoCronograma.codigo_projeto != None)
    
    if data_inicio_obj:
        query_projeto = query_projeto.filter(AlocacaoCronograma.data >= data_inicio_obj)
    if data_fim_obj:
        query_projeto = query_projeto.filter(AlocacaoCronograma.data <= data_fim_obj)
    
    alocacoes_por_projeto = query_projeto.group_by(
        AlocacaoCronograma.codigo_projeto
    ).order_by(func.count(AlocacaoCronograma.id).desc()).limit(10).all()
    
    return {
        "total_alocacoes": total_alocacoes,
        "por_consultor": [{"nome": c[0], "total": c[1]} for c in alocacoes_por_consultor],
        "top_projetos": [{"projeto": p[0], "total": p[1]} for p in alocacoes_por_projeto]
    }

@router.post("/alocacoes/criar")
async def criar_alocacao(
    alocacao_data: AlocacaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    consultor = db.query(Consultor).filter(Consultor.id == alocacao_data.consultor_id).first()
    if not consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")
    
    data_obj = datetime.strptime(alocacao_data.data, '%Y-%m-%d').date()
    
    nova_alocacao = AlocacaoCronograma(
        consultor_id=alocacao_data.consultor_id,
        data=data_obj,
        periodo=alocacao_data.periodo,
        codigo_projeto=alocacao_data.codigo_projeto,
        nif=consultor.nif,
        observacao=alocacao_data.observacao
    )
    
    db.add(nova_alocacao)
    db.commit()
    db.refresh(nova_alocacao)
    
    return {
        "id": nova_alocacao.id,
        "consultor_nome": consultor.nome,
        "data": str(nova_alocacao.data),
        "periodo": nova_alocacao.periodo,
        "codigo_projeto": nova_alocacao.codigo_projeto
    }

@router.put("/alocacoes/{alocacao_id}")
async def atualizar_alocacao(
    alocacao_id: int,
    alocacao_data: AlocacaoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    alocacao = db.query(AlocacaoCronograma).filter(AlocacaoCronograma.id == alocacao_id).first()
    if not alocacao:
        raise HTTPException(status_code=404, detail="Alocação não encontrada")
    
    if alocacao_data.codigo_projeto is not None:
        alocacao.codigo_projeto = alocacao_data.codigo_projeto
    if alocacao_data.observacao is not None:
        alocacao.observacao = alocacao_data.observacao
    
    db.commit()
    db.refresh(alocacao)
    
    return {"message": "Alocação atualizada com sucesso", "id": alocacao.id}

@router.delete("/alocacoes/{alocacao_id}")
async def deletar_alocacao(
    alocacao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    alocacao = db.query(AlocacaoCronograma).filter(AlocacaoCronograma.id == alocacao_id).first()
    if not alocacao:
        raise HTTPException(status_code=404, detail="Alocação não encontrada")
    
    db.delete(alocacao)
    db.commit()
    
    return {"message": "Alocação deletada com sucesso"}

@router.get("/alocacoes/exportar/excel")
async def exportar_alocacoes_excel(
    data_inicio: str = None,
    data_fim: str = None,
    consultor_id: int = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(AlocacaoCronograma).join(Consultor)
    
    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(AlocacaoCronograma.data >= data_inicio_obj)
    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(AlocacaoCronograma.data <= data_fim_obj)
    if consultor_id:
        query = query.filter(AlocacaoCronograma.consultor_id == consultor_id)
    
    alocacoes = query.order_by(AlocacaoCronograma.data, AlocacaoCronograma.periodo).all()
    
    data = []
    for alocacao in alocacoes:
        data.append({
            "Data": str(alocacao.data),
            "Consultor": alocacao.consultor.nome,
            "NIF": alocacao.nif or '',
            "Período": alocacao.periodo,
            "Código Projeto": alocacao.codigo_projeto or '',
            "Observação": alocacao.observacao or ''
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Cronograma')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=cronograma.xlsx"}
    )

@router.get("/alocacoes/exportar/pdf")
async def exportar_alocacoes_pdf(
    data_inicio: str = None,
    data_fim: str = None,
    consultor_id: int = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(AlocacaoCronograma).join(Consultor)
    
    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(AlocacaoCronograma.data >= data_inicio_obj)
    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(AlocacaoCronograma.data <= data_fim_obj)
    if consultor_id:
        query = query.filter(AlocacaoCronograma.consultor_id == consultor_id)
    
    alocacoes = query.order_by(AlocacaoCronograma.data, AlocacaoCronograma.periodo).all()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=landscape(letter))
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("<b>Relatório de Cronograma de Alocações</b>", styles['Title'])
        elements.append(title)
        
        data = [['Data', 'Consultor', 'NIF', 'Período', 'Código Projeto']]
        
        for alocacao in alocacoes:
            data.append([
                str(alocacao.data),
                alocacao.consultor.nome[:25] if alocacao.consultor.nome else '',
                alocacao.nif or '',
                alocacao.periodo,
                alocacao.codigo_projeto[:20] if alocacao.codigo_projeto else ''
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        return FileResponse(tmp.name, media_type="application/pdf", filename="cronograma.pdf")
