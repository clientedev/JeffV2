from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.models.models import (
    CompanyPipeline, Stage, CompanyStageHistory, Note, Attachment, Activity, Usuario
)
from app.auth import get_current_user, require_role

router = APIRouter()

class StageResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    ordem: int
    cor: str
    ativo: bool
    
    class Config:
        from_attributes = True

class CompanyPipelineCreate(BaseModel):
    cnpj: str
    nome_empresa: str
    linha: str
    tipo_programa: Optional[str] = None
    porte: Optional[str] = None
    er_regiao: Optional[str] = None
    consultor_responsavel: Optional[str] = None
    stage_id: int
    numero_proposta: Optional[str] = None
    valor_proposta: Optional[float] = None
    observacoes: Optional[str] = None

class CompanyPipelineUpdate(BaseModel):
    nome_empresa: Optional[str] = None
    linha: Optional[str] = None
    tipo_programa: Optional[str] = None
    porte: Optional[str] = None
    er_regiao: Optional[str] = None
    consultor_responsavel: Optional[str] = None
    numero_proposta: Optional[str] = None
    valor_proposta: Optional[float] = None
    observacoes: Optional[str] = None

class CompanyPipelineResponse(BaseModel):
    id: int
    cnpj: str
    nome_empresa: str
    linha: str
    tipo_programa: Optional[str]
    porte: Optional[str]
    er_regiao: Optional[str]
    consultor_responsavel: Optional[str]
    stage_id: int
    stage: StageResponse
    numero_proposta: Optional[str]
    valor_proposta: Optional[float]
    data_cadastro: datetime
    ultima_atualizacao: datetime
    observacoes: Optional[str]
    dias_na_etapa: int
    
    class Config:
        from_attributes = True

class MoveStageRequest(BaseModel):
    stage_id: int
    observacao: Optional[str] = None

class NoteCreate(BaseModel):
    titulo: Optional[str] = None
    conteudo: str
    privada: bool = False

class NoteResponse(BaseModel):
    id: int
    titulo: Optional[str]
    conteudo: str
    privada: bool
    criado_em: datetime
    atualizado_em: datetime
    usuario_nome: str
    
    class Config:
        from_attributes = True

@router.get("/stages", response_model=List[StageResponse])
async def listar_stages(db: Session = Depends(get_db)):
    stages = db.query(Stage).filter(Stage.ativo == True).order_by(Stage.ordem).all()
    return stages

@router.get("/companies", response_model=List[CompanyPipelineResponse])
async def listar_companies(
    linha: Optional[str] = None,
    stage_id: Optional[int] = None,
    consultor: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(CompanyPipeline)
    
    if linha:
        query = query.filter(CompanyPipeline.linha == linha)
    
    if stage_id:
        query = query.filter(CompanyPipeline.stage_id == stage_id)
    
    if consultor:
        query = query.filter(CompanyPipeline.consultor_responsavel.ilike(f"%{consultor}%"))
    
    if current_user.funcao == "Consultor":
        query = query.filter(
            or_(
                CompanyPipeline.consultor_responsavel.ilike(f"%{current_user.nome}%"),
                CompanyPipeline.consultor_responsavel == None
            )
        )
    
    companies = query.order_by(CompanyPipeline.ultima_atualizacao.desc()).all()
    
    result = []
    for company in companies:
        history = db.query(CompanyStageHistory).filter(
            and_(
                CompanyStageHistory.company_pipeline_id == company.id,
                CompanyStageHistory.stage_id == company.stage_id,
                CompanyStageHistory.data_saida == None
            )
        ).first()
        
        dias_na_etapa = 0
        if history:
            dias_na_etapa = (datetime.utcnow() - history.data_entrada).days
        
        company_dict = {
            "id": company.id,
            "cnpj": company.cnpj,
            "nome_empresa": company.nome_empresa,
            "linha": company.linha,
            "tipo_programa": company.tipo_programa,
            "porte": company.porte,
            "er_regiao": company.er_regiao,
            "consultor_responsavel": company.consultor_responsavel,
            "stage_id": company.stage_id,
            "stage": company.stage,
            "numero_proposta": company.numero_proposta,
            "valor_proposta": company.valor_proposta,
            "data_cadastro": company.data_cadastro,
            "ultima_atualizacao": company.ultima_atualizacao,
            "observacoes": company.observacoes,
            "dias_na_etapa": dias_na_etapa
        }
        result.append(CompanyPipelineResponse(**company_dict))
    
    return result

@router.post("/companies", response_model=CompanyPipelineResponse, status_code=status.HTTP_201_CREATED)
async def criar_company(
    company_data: CompanyPipelineCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Admin", "Consultor"))
):
    existing = db.query(CompanyPipeline).filter(
        CompanyPipeline.cnpj == company_data.cnpj,
        CompanyPipeline.linha == company_data.linha
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Empresa já cadastrada nesta linha")
    
    company = CompanyPipeline(**company_data.model_dump())
    db.add(company)
    db.flush()
    
    history = CompanyStageHistory(
        company_pipeline_id=company.id,
        stage_id=company_data.stage_id,
        data_entrada=datetime.utcnow(),
        usuario_id=current_user.id,
        observacao="Cadastro inicial"
    )
    db.add(history)
    
    activity = Activity(
        company_pipeline_id=company.id,
        usuario_id=current_user.id,
        tipo="CADASTRO",
        descricao=f"Empresa {company.nome_empresa} cadastrada no pipeline",
        entidade="CompanyPipeline",
        entidade_id=company.id
    )
    db.add(activity)
    
    db.commit()
    db.refresh(company)
    
    company_dict = {
        "id": company.id,
        "cnpj": company.cnpj,
        "nome_empresa": company.nome_empresa,
        "linha": company.linha,
        "tipo_programa": company.tipo_programa,
        "porte": company.porte,
        "er_regiao": company.er_regiao,
        "consultor_responsavel": company.consultor_responsavel,
        "stage_id": company.stage_id,
        "stage": company.stage,
        "numero_proposta": company.numero_proposta,
        "valor_proposta": company.valor_proposta,
        "data_cadastro": company.data_cadastro,
        "ultima_atualizacao": company.ultima_atualizacao,
        "observacoes": company.observacoes,
        "dias_na_etapa": 0
    }
    
    return CompanyPipelineResponse(**company_dict)

@router.put("/companies/{company_id}", response_model=CompanyPipelineResponse)
async def atualizar_company(
    company_id: int,
    company_data: CompanyPipelineUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Admin", "Consultor"))
):
    company = db.query(CompanyPipeline).filter(CompanyPipeline.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    update_data = company_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(company, key, value)
    
    activity = Activity(
        company_pipeline_id=company.id,
        usuario_id=current_user.id,
        tipo="ATUALIZACAO",
        descricao=f"Dados da empresa {company.nome_empresa} atualizados",
        entidade="CompanyPipeline",
        entidade_id=company.id
    )
    db.add(activity)
    
    db.commit()
    db.refresh(company)
    
    history = db.query(CompanyStageHistory).filter(
        and_(
            CompanyStageHistory.company_pipeline_id == company.id,
            CompanyStageHistory.stage_id == company.stage_id,
            CompanyStageHistory.data_saida == None
        )
    ).first()
    
    dias_na_etapa = 0
    if history:
        dias_na_etapa = (datetime.utcnow() - history.data_entrada).days
    
    company_dict = {
        "id": company.id,
        "cnpj": company.cnpj,
        "nome_empresa": company.nome_empresa,
        "linha": company.linha,
        "tipo_programa": company.tipo_programa,
        "porte": company.porte,
        "er_regiao": company.er_regiao,
        "consultor_responsavel": company.consultor_responsavel,
        "stage_id": company.stage_id,
        "stage": company.stage,
        "numero_proposta": company.numero_proposta,
        "valor_proposta": company.valor_proposta,
        "data_cadastro": company.data_cadastro,
        "ultima_atualizacao": company.ultima_atualizacao,
        "observacoes": company.observacoes,
        "dias_na_etapa": dias_na_etapa
    }
    
    return CompanyPipelineResponse(**company_dict)

@router.post("/companies/{company_id}/move", response_model=CompanyPipelineResponse)
async def mover_stage(
    company_id: int,
    move_data: MoveStageRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Admin", "Consultor"))
):
    company = db.query(CompanyPipeline).filter(CompanyPipeline.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    stage = db.query(Stage).filter(Stage.id == move_data.stage_id).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    
    old_stage_id = company.stage_id
    
    current_history = db.query(CompanyStageHistory).filter(
        and_(
            CompanyStageHistory.company_pipeline_id == company.id,
            CompanyStageHistory.stage_id == old_stage_id,
            CompanyStageHistory.data_saida == None
        )
    ).first()
    
    if current_history:
        current_history.data_saida = datetime.utcnow()
    
    company.stage_id = move_data.stage_id
    
    new_history = CompanyStageHistory(
        company_pipeline_id=company.id,
        stage_id=move_data.stage_id,
        data_entrada=datetime.utcnow(),
        usuario_id=current_user.id,
        observacao=move_data.observacao
    )
    db.add(new_history)
    
    old_stage = db.query(Stage).filter(Stage.id == old_stage_id).first()
    activity = Activity(
        company_pipeline_id=company.id,
        usuario_id=current_user.id,
        tipo="MUDANCA_ETAPA",
        descricao=f"Empresa {company.nome_empresa} movida de '{old_stage.nome}' para '{stage.nome}'",
        entidade="CompanyPipeline",
        entidade_id=company.id,
        dados_antes=f"Stage ID: {old_stage_id}",
        dados_depois=f"Stage ID: {move_data.stage_id}"
    )
    db.add(activity)
    
    db.commit()
    db.refresh(company)
    
    company_dict = {
        "id": company.id,
        "cnpj": company.cnpj,
        "nome_empresa": company.nome_empresa,
        "linha": company.linha,
        "tipo_programa": company.tipo_programa,
        "porte": company.porte,
        "er_regiao": company.er_regiao,
        "consultor_responsavel": company.consultor_responsavel,
        "stage_id": company.stage_id,
        "stage": company.stage,
        "numero_proposta": company.numero_proposta,
        "valor_proposta": company.valor_proposta,
        "data_cadastro": company.data_cadastro,
        "ultima_atualizacao": company.ultima_atualizacao,
        "observacoes": company.observacoes,
        "dias_na_etapa": 0
    }
    
    return CompanyPipelineResponse(**company_dict)

@router.delete("/companies/{company_id}")
async def deletar_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Admin"))
):
    company = db.query(CompanyPipeline).filter(CompanyPipeline.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    db.delete(company)
    db.commit()
    
    return {"message": "Empresa deletada com sucesso"}

@router.get("/companies/{company_id}/history")
async def listar_historico(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    company = db.query(CompanyPipeline).filter(CompanyPipeline.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    history = db.query(CompanyStageHistory).filter(
        CompanyStageHistory.company_pipeline_id == company_id
    ).order_by(CompanyStageHistory.data_entrada.desc()).all()
    
    result = []
    for h in history:
        dias_na_etapa = None
        if h.data_saida:
            dias_na_etapa = (h.data_saida - h.data_entrada).days
        else:
            dias_na_etapa = (datetime.utcnow() - h.data_entrada).days
        
        result.append({
            "id": h.id,
            "stage": {"id": h.stage.id, "nome": h.stage.nome, "cor": h.stage.cor},
            "data_entrada": h.data_entrada,
            "data_saida": h.data_saida,
            "dias_na_etapa": dias_na_etapa,
            "usuario": h.usuario.nome if h.usuario else None,
            "observacao": h.observacao
        })
    
    return result

@router.post("/companies/{company_id}/notes", status_code=status.HTTP_201_CREATED)
async def criar_nota(
    company_id: int,
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Admin", "Consultor"))
):
    company = db.query(CompanyPipeline).filter(CompanyPipeline.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    note = Note(
        company_pipeline_id=company_id,
        usuario_id=current_user.id,
        titulo=note_data.titulo,
        conteudo=note_data.conteudo,
        privada=note_data.privada
    )
    db.add(note)
    
    activity = Activity(
        company_pipeline_id=company_id,
        usuario_id=current_user.id,
        tipo="NOTA_CRIADA",
        descricao=f"Nova nota adicionada à empresa {company.nome_empresa}",
        entidade="Note",
        entidade_id=None
    )
    db.add(activity)
    
    db.commit()
    db.refresh(note)
    
    return {
        "id": note.id,
        "titulo": note.titulo,
        "conteudo": note.conteudo,
        "privada": note.privada,
        "criado_em": note.criado_em,
        "atualizado_em": note.atualizado_em,
        "usuario_nome": current_user.nome
    }

@router.get("/companies/{company_id}/notes")
async def listar_notas(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    company = db.query(CompanyPipeline).filter(CompanyPipeline.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    query = db.query(Note).filter(Note.company_pipeline_id == company_id)
    
    if current_user.funcao != "Admin":
        query = query.filter(
            or_(
                Note.privada == False,
                Note.usuario_id == current_user.id
            )
        )
    
    notes = query.order_by(Note.criado_em.desc()).all()
    
    result = []
    for note in notes:
        result.append({
            "id": note.id,
            "titulo": note.titulo,
            "conteudo": note.conteudo,
            "privada": note.privada,
            "criado_em": note.criado_em,
            "atualizado_em": note.atualizado_em,
            "usuario_nome": note.usuario.nome
        })
    
    return result

class ImportarLinhasRequest(BaseModel):
    linha: str

@router.post("/importar-de-linhas")
async def importar_de_linhas(
    request: ImportarLinhasRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Admin", "Consultor"))
):
    linha = request.linha
    from app.models.models import LinhaEducacional, LinhaTecnologia

    stage_prospeccao = db.query(Stage).filter(Stage.nome == "Prospecção").first()
    if not stage_prospeccao:
        raise HTTPException(status_code=404, detail="Etapa de prospecção não encontrada")

    importados = 0
    erros = []

    if linha.upper() == "EDUCACIONAL":
        registros = db.query(LinhaEducacional).filter(
            LinhaEducacional.cnpj.isnot(None),
            LinhaEducacional.cliente.isnot(None)
        ).all()

        for reg in registros:
            try:
                existing = db.query(CompanyPipeline).filter(
                    CompanyPipeline.cnpj == reg.cnpj,
                    CompanyPipeline.linha == "EDUCACIONAL"
                ).first()

                if not existing:
                    company = CompanyPipeline(
                        cnpj=reg.cnpj,
                        nome_empresa=reg.cliente,
                        linha="EDUCACIONAL",
                        tipo_programa=reg.tipo,
                        stage_id=stage_prospeccao.id,
                        numero_proposta=reg.numero_proposta,
                        valor_proposta=reg.valor,
                        observacoes=reg.observacoes
                    )
                    db.add(company)
                    db.flush()

                    history = CompanyStageHistory(
                        company_pipeline_id=company.id,
                        stage_id=stage_prospeccao.id,
                        data_entrada=datetime.utcnow(),
                        usuario_id=current_user.id,
                        observacao="Importado da Linha Educacional"
                    )
                    db.add(history)
                    importados += 1
            except Exception as e:
                erros.append(f"Erro ao importar {reg.cliente}: {str(e)}")

    elif linha.upper() == "TECNOLOGIA":
        registros = db.query(LinhaTecnologia).filter(
            LinhaTecnologia.cnpj.isnot(None),
            LinhaTecnologia.empresa.isnot(None)
        ).all()

        for reg in registros:
            try:
                existing = db.query(CompanyPipeline).filter(
                    CompanyPipeline.cnpj == reg.cnpj,
                    CompanyPipeline.linha == "TECNOLOGIA"
                ).first()

                if not existing:
                    company = CompanyPipeline(
                        cnpj=reg.cnpj,
                        nome_empresa=reg.empresa,
                        linha="TECNOLOGIA",
                        tipo_programa=reg.tipo_programa,
                        porte=reg.porte,
                        er_regiao=reg.er,
                        consultor_responsavel=reg.consultor,
                        stage_id=stage_prospeccao.id,
                        numero_proposta=reg.numero_proposta,
                        valor_proposta=reg.valor_proposta,
                        observacoes=reg.observacoes
                    )
                    db.add(company)
                    db.flush()

                    history = CompanyStageHistory(
                        company_pipeline_id=company.id,
                        stage_id=stage_prospeccao.id,
                        data_entrada=datetime.utcnow(),
                        usuario_id=current_user.id,
                        observacao="Importado da Linha Tecnologia"
                    )
                    db.add(history)
                    importados += 1
            except Exception as e:
                erros.append(f"Erro ao importar {reg.empresa}: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Linha inválida")

    db.commit()

    return {
        "importados": importados,
        "erros": erros
    }

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(CompanyPipeline)
    
    if current_user.funcao == "Consultor":
        query = query.filter(CompanyPipeline.consultor_responsavel.ilike(f"%{current_user.nome}%"))
    
    total_empresas = query.count()
    
    programas_andamento = query.filter(
        CompanyPipeline.stage_id.in_([3, 4, 5])
    ).count()
    
    stages = db.query(Stage).order_by(Stage.ordem).all()
    empresas_por_etapa = []
    
    for stage in stages:
        stage_query = query.filter(CompanyPipeline.stage_id == stage.id)
        count = stage_query.count()
        percentual = (count / total_empresas * 100) if total_empresas > 0 else 0
        
        empresas_por_etapa.append({
            "stage_id": stage.id,
            "stage_nome": stage.nome,
            "stage_cor": stage.cor,
            "count": count,
            "percentual": round(percentual, 1)
        })
    
    empresas_por_consultor = db.query(
        CompanyPipeline.consultor_responsavel,
        func.count(CompanyPipeline.id).label('count')
    ).filter(
        CompanyPipeline.consultor_responsavel != None,
        CompanyPipeline.consultor_responsavel != ''
    )
    
    if current_user.funcao == "Consultor":
        empresas_por_consultor = empresas_por_consultor.filter(
            CompanyPipeline.consultor_responsavel.ilike(f"%{current_user.nome}%")
        )
    
    empresas_por_consultor = empresas_por_consultor.group_by(
        CompanyPipeline.consultor_responsavel
    ).all()
    
    consultor_stats = [
        {"consultor": c[0], "count": c[1]}
        for c in empresas_por_consultor
    ]
    
    data_limite = datetime.utcnow() - timedelta(days=7)
    empresas_paradas = db.query(CompanyPipeline).join(
        CompanyStageHistory,
        and_(
            CompanyStageHistory.company_pipeline_id == CompanyPipeline.id,
            CompanyStageHistory.stage_id == CompanyPipeline.stage_id,
            CompanyStageHistory.data_saida == None,
            CompanyStageHistory.data_entrada < data_limite
        )
    )
    
    if current_user.funcao == "Consultor":
        empresas_paradas = empresas_paradas.filter(
            CompanyPipeline.consultor_responsavel.ilike(f"%{current_user.nome}%")
        )
    
    empresas_paradas = empresas_paradas.all()
    
    pendencias = []
    for empresa in empresas_paradas:
        history = db.query(CompanyStageHistory).filter(
            and_(
                CompanyStageHistory.company_pipeline_id == empresa.id,
                CompanyStageHistory.stage_id == empresa.stage_id,
                CompanyStageHistory.data_saida == None
            )
        ).first()
        
        if history:
            dias_parada = (datetime.utcnow() - history.data_entrada).days
            pendencias.append({
                "id": empresa.id,
                "nome_empresa": empresa.nome_empresa,
                "stage_nome": empresa.stage.nome,
                "dias_parada": dias_parada,
                "consultor": empresa.consultor_responsavel
            })
    
    return {
        "total_empresas": total_empresas,
        "programas_andamento": programas_andamento,
        "empresas_por_etapa": empresas_por_etapa,
        "empresas_por_consultor": consultor_stats,
        "pendencias": sorted(pendencias, key=lambda x: x['dias_parada'], reverse=True)
    }
