from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from app.database import get_db
from app.models.models import Prospeccao, FollowUp, Usuario, CompanyPipeline, Stage
from app.auth import get_current_user

router = APIRouter()

class ProspeccaoCreate(BaseModel):
    empresa: str
    cnpj: Optional[str] = None
    porte: Optional[str] = None
    er: Optional[str] = None
    contato: Optional[str] = None
    cargo: Optional[str] = None
    email: Optional[str] = None
    celular: Optional[str] = None
    telefone: Optional[str] = None
    tipo_programa: Optional[str] = None
    status: str = 'Novo'
    responsavel: Optional[str] = None
    data_ligacao: Optional[date] = None
    oportunidade: Optional[str] = None
    observacoes: Optional[str] = None

class ProspeccaoUpdate(BaseModel):
    empresa: Optional[str] = None
    cnpj: Optional[str] = None
    porte: Optional[str] = None
    er: Optional[str] = None
    contato: Optional[str] = None
    cargo: Optional[str] = None
    email: Optional[str] = None
    celular: Optional[str] = None
    telefone: Optional[str] = None
    tipo_programa: Optional[str] = None
    status: Optional[str] = None
    responsavel: Optional[str] = None
    data_ligacao: Optional[date] = None
    oportunidade: Optional[str] = None
    observacoes: Optional[str] = None

class ProspeccaoResponse(BaseModel):
    id: int
    empresa: str
    cnpj: Optional[str]
    porte: Optional[str]
    er: Optional[str]
    contato: Optional[str]
    cargo: Optional[str]
    email: Optional[str]
    celular: Optional[str]
    telefone: Optional[str]
    tipo_programa: Optional[str]
    status: str
    responsavel: Optional[str]
    data_ligacao: Optional[date]
    oportunidade: Optional[str]
    observacoes: Optional[str]
    
    class Config:
        from_attributes = True

class FollowUpCreate(BaseModel):
    prospeccao_id: int
    responsavel: Optional[str] = None
    tipo: str  # Ligação, Email, Reunião, WhatsApp
    descricao: Optional[str] = None
    proximo_contato: Optional[date] = None

class FollowUpResponse(BaseModel):
    id: int
    prospeccao_id: int
    responsavel: Optional[str]
    tipo: str
    descricao: Optional[str]
    proximo_contato: Optional[date]
    
    class Config:
        from_attributes = True

@router.post("/", response_model=ProspeccaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_prospeccao(
    prospeccao: ProspeccaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    new_prospeccao = Prospeccao(**prospeccao.model_dump())
    db.add(new_prospeccao)
    db.commit()
    db.refresh(new_prospeccao)
    return new_prospeccao

@router.get("/", response_model=List[ProspeccaoResponse])
async def listar_prospeccao(
    skip: int = 0,
    limit: int = 1000,
    status: Optional[str] = None,
    responsavel: Optional[str] = None,
    busca: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Prospeccao)
    
    if status:
        query = query.filter(Prospeccao.status == status)
    
    if responsavel:
        query = query.filter(Prospeccao.responsavel.ilike(f"%{responsavel}%"))
    
    if busca:
        query = query.filter(
            (Prospeccao.empresa.ilike(f"%{busca}%")) |
            (Prospeccao.cnpj.ilike(f"%{busca}%")) |
            (Prospeccao.contato.ilike(f"%{busca}%"))
        )
    
    prospeccoes = query.order_by(desc(Prospeccao.criado_em)).offset(skip).limit(limit).all()
    return prospeccoes

@router.get("/pipeline")
async def get_prospeccao_pipeline(
    linha: Optional[str] = None,
    incluir_fases_iniciais: bool = False,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna empresas do pipeline em fase de prospecção (ou opcionalmente fases iniciais)"""
    from sqlalchemy.orm import selectinload
    
    if incluir_fases_iniciais:
        prospeccao_stages = db.query(Stage).filter(
            Stage.nome.in_(["Prospecção", "Proposta Enviada", "Negociação"])
        ).all()
    else:
        prospeccao_stages = db.query(Stage).filter(Stage.nome == "Prospecção").all()
    
    stage_ids = [s.id for s in prospeccao_stages]
    
    query = db.query(CompanyPipeline).options(
        selectinload(CompanyPipeline.stage)
    ).filter(CompanyPipeline.stage_id.in_(stage_ids))
    
    if linha:
        query = query.filter(CompanyPipeline.linha == linha)
    
    companies = query.order_by(CompanyPipeline.ultima_atualizacao.desc()).limit(100).all()
    
    return [{
        "id": c.id,
        "empresa": c.nome_empresa,
        "cnpj": c.cnpj,
        "linha": c.linha,
        "tipo_programa": c.tipo_programa,
        "porte": c.porte,
        "consultor": c.consultor_responsavel,
        "numero_proposta": c.numero_proposta,
        "valor_proposta": float(c.valor_proposta) if c.valor_proposta else None,
        "stage": c.stage.nome if c.stage else None,
        "stage_cor": c.stage.cor if c.stage else None
    } for c in companies]

@router.get("/dados-linhas")
async def obter_dados_linhas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from app.models.models import LinhaEducacional, LinhaTecnologia

    dados_educacional = db.query(LinhaEducacional).all()
    dados_tecnologia = db.query(LinhaTecnologia).all()

    resultado = []

    for item in dados_educacional:
        resultado.append({
            "id": f"edu_{item.id}",
            "linha": "Educacional",
            "empresa": item.cliente or "N/A",
            "cnpj": item.cnpj,
            "numero_proposta": item.numero_proposta,
            "programa": item.programa,
            "tipo": item.tipo,
            "valor": float(item.valor) if item.valor else None,
            "situacao": item.situacao,
            "status": item.status_proposta,
            "data_inicio": str(item.data_inicio) if item.data_inicio else None,
            "observacoes": item.observacoes
        })

    for item in dados_tecnologia:
        resultado.append({
            "id": f"tec_{item.id}",
            "linha": "Tecnologia",
            "empresa": item.empresa or "N/A",
            "cnpj": item.cnpj,
            "numero_proposta": item.numero_proposta,
            "tipo_programa": item.tipo_programa,
            "consultor": item.consultor,
            "valor": float(item.valor_proposta) if item.valor_proposta else None,
            "situacao": item.situacao,
            "status": item.status_etapa,
            "data_inicio": str(item.data_inicio) if item.data_inicio else None,
            "solucao": item.solucao,
            "observacoes": item.observacoes
        })

    return resultado

@router.get("/kanban")
async def get_kanban_data(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    novos = db.query(Prospeccao).filter(Prospeccao.status == "Novo").all()
    em_andamento = db.query(Prospeccao).filter(Prospeccao.status == "Em andamento").all()
    fechados = db.query(Prospeccao).filter(Prospeccao.status == "Fechado").all()
    perdidos = db.query(Prospeccao).filter(Prospeccao.status == "Perdido").all()

    return {
        "Novo": [{"id": p.id, "empresa": p.empresa, "contato": p.contato, "responsavel": p.responsavel} for p in novos],
        "Em andamento": [{"id": p.id, "empresa": p.empresa, "contato": p.contato, "responsavel": p.responsavel} for p in em_andamento],
        "Fechado": [{"id": p.id, "empresa": p.empresa, "contato": p.contato, "responsavel": p.responsavel} for p in fechados],
        "Perdido": [{"id": p.id, "empresa": p.empresa, "contato": p.contato, "responsavel": p.responsavel} for p in perdidos]
    }

@router.get("/{prospeccao_id}", response_model=ProspeccaoResponse)
async def obter_prospeccao(
    prospeccao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    prospeccao = db.query(Prospeccao).filter(Prospeccao.id == prospeccao_id).first()
    if not prospeccao:
        raise HTTPException(status_code=404, detail="Prospecção não encontrada")
    return prospeccao

@router.put("/{prospeccao_id}", response_model=ProspeccaoResponse)
async def atualizar_prospeccao(
    prospeccao_id: int,
    prospeccao_data: ProspeccaoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    prospeccao = db.query(Prospeccao).filter(Prospeccao.id == prospeccao_id).first()
    if not prospeccao:
        raise HTTPException(status_code=404, detail="Prospecção não encontrada")
    
    for key, value in prospeccao_data.model_dump(exclude_unset=True).items():
        setattr(prospeccao, key, value)
    
    db.commit()
    db.refresh(prospeccao)
    return prospeccao

@router.delete("/{prospeccao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_prospeccao(
    prospeccao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    prospeccao = db.query(Prospeccao).filter(Prospeccao.id == prospeccao_id).first()
    if not prospeccao:
        raise HTTPException(status_code=404, detail="Prospecção não encontrada")
    
    db.delete(prospeccao)
    db.commit()
    return None

# Rotas para Follow-ups
@router.post("/followups", response_model=FollowUpResponse, status_code=status.HTTP_201_CREATED)
async def criar_followup(
    followup: FollowUpCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    new_followup = FollowUp(**followup.model_dump())
    db.add(new_followup)
    db.commit()
    db.refresh(new_followup)
    return new_followup

@router.get("/{prospeccao_id}/followups", response_model=List[FollowUpResponse])
async def listar_followups(
    prospeccao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    followups = db.query(FollowUp).filter(
        FollowUp.prospeccao_id == prospeccao_id
    ).order_by(desc(FollowUp.data)).all()
    return followups

@router.delete("/followups/{followup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_followup(
    followup_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    followup = db.query(FollowUp).filter(FollowUp.id == followup_id).first()
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up não encontrado")
    
    db.delete(followup)
    db.commit()
    return None
