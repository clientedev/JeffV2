from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.database import get_db
from app.models.models import LinhaTecnologia, Usuario
from app.auth import get_current_user
from decimal import Decimal

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

class EtapaUpdate(BaseModel):
    campo: str
    valor: Optional[str] = None

class ProjetoResponse(BaseModel):
    id: int
    empresa: str
    tipo_programa: Optional[str]
    status_etapa: Optional[str]
    situacao: Optional[str]
    numero_proposta: Optional[str]
    valor_proposta: Optional[Decimal]
    data_inicio: Optional[date]
    data_termino: Optional[date]
    
    # Campos de controle
    dados_socios_informados: Optional[str]
    contrato_enviado_empresa: Optional[str]
    contrato_assinado_empresa: Optional[str]
    data_contrato_assinado_senai: Optional[date]
    data_cadastro_sgt: Optional[date]
    data_upload_sgt: Optional[date]
    data_aceite_sgt: Optional[date]
    data_envio_relatorio_t1: Optional[date]
    data_cobranca_empresa: Optional[date]
    cadastro_plataforma_ok: Optional[str]
    data_cobranca_sebrae: Optional[date]
    contrato_sebrae_enviado: Optional[str]
    data_resposta_sebrae: Optional[date]
    requisicao_grm: Optional[str]
    reuniao_kickoff_confirmada: Optional[str]
    reuniao_final_agendada: Optional[str]
    presencial: Optional[str]
    gratuidade: Optional[str]
    numero_demanda: Optional[str]
    codigo_rae: Optional[str]
    mov_1_1_57: Optional[str]
    relatorio_priorizacao_enviado: Optional[str]
    relatorio_smart_factory: Optional[str]
    relatorio_final_enviado: Optional[str]
    relatorio_educacional_enviado: Optional[str]
    data_conclusao_sgt: Optional[date]
    envio_auditoria: Optional[str]
    retorno_auditoria: Optional[str]
    data_prestacao_contas: Optional[date]
    data_pesquisa_satisfacao: Optional[date]
    observacoes: Optional[str]
    
    class Config:
        from_attributes = True

@router.get("/", response_class=HTMLResponse)
async def pagina_gerenciar_etapas(request: Request):
    """Página principal de gerenciamento de etapas"""
    return templates.TemplateResponse("gerenciar_etapas.html", {"request": request})

@router.get("/meus-projetos")
async def listar_meus_projetos(
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    status_etapa: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista projetos do consultor logado"""
    query = db.query(LinhaTecnologia).filter(
        LinhaTecnologia.consultor.ilike(f"%{current_user.nome}%")
    )
    
    if search:
        query = query.filter(
            or_(
                LinhaTecnologia.empresa.ilike(f"%{search}%"),
                LinhaTecnologia.numero_proposta.ilike(f"%{search}%")
            )
        )
    
    if status_etapa:
        query = query.filter(LinhaTecnologia.status_etapa == status_etapa)
    
    total = query.count()
    offset = (page - 1) * page_size
    projetos = query.order_by(LinhaTecnologia.criado_em.desc()).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": [ProjetoResponse.from_orm(p) for p in projetos]
    }

@router.get("/projeto/{projeto_id}")
async def obter_projeto(
    projeto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém detalhes completos de um projeto"""
    projeto = db.query(LinhaTecnologia).filter(LinhaTecnologia.id == projeto_id).first()
    
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Verifica se o consultor tem acesso ao projeto
    if current_user.nivel != "admin" and not (projeto.consultor and current_user.nome in projeto.consultor):
        raise HTTPException(status_code=403, detail="Acesso negado a este projeto")
    
    return ProjetoResponse.from_orm(projeto)

@router.put("/projeto/{projeto_id}/atualizar-campo")
async def atualizar_campo_projeto(
    projeto_id: int,
    update: EtapaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza um campo específico do projeto"""
    projeto = db.query(LinhaTecnologia).filter(LinhaTecnologia.id == projeto_id).first()
    
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Verifica se o consultor tem acesso ao projeto
    if current_user.nivel != "admin" and not (projeto.consultor and current_user.nome in projeto.consultor):
        raise HTTPException(status_code=403, detail="Acesso negado a este projeto")
    
    # Protege dados iniciais de edição completa (apenas atualiza campos de controle)
    campos_permitidos = [
        'status_etapa', 'situacao', 'dados_socios_informados', 'contrato_enviado_empresa',
        'contrato_assinado_empresa', 'data_contrato_assinado_senai', 'data_cadastro_sgt',
        'data_upload_sgt', 'data_aceite_sgt', 'data_envio_relatorio_t1', 'data_cobranca_empresa',
        'cadastro_plataforma_ok', 'data_cobranca_sebrae', 'contrato_sebrae_enviado',
        'data_resposta_sebrae', 'requisicao_grm', 'reuniao_kickoff_confirmada',
        'reuniao_final_agendada', 'presencial', 'gratuidade', 'numero_demanda', 'codigo_rae',
        'mov_1_1_57', 'relatorio_priorizacao_enviado', 'relatorio_smart_factory',
        'relatorio_final_enviado', 'relatorio_educacional_enviado', 'data_conclusao_sgt',
        'envio_auditoria', 'retorno_auditoria', 'data_prestacao_contas', 'data_pesquisa_satisfacao',
        'observacoes', 'data_inicio', 'data_termino'
    ]
    
    if update.campo not in campos_permitidos:
        raise HTTPException(status_code=400, detail=f"Campo '{update.campo}' não pode ser editado")
    
    # Atualiza o campo
    setattr(projeto, update.campo, update.valor)
    
    db.commit()
    db.refresh(projeto)
    
    return {"message": "Campo atualizado com sucesso", "campo": update.campo, "valor": update.valor}

@router.get("/estatisticas")
async def estatisticas_consultor(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna estatísticas dos projetos do consultor"""
    query = db.query(LinhaTecnologia).filter(
        LinhaTecnologia.consultor.ilike(f"%{current_user.nome}%")
    )
    
    total_projetos = query.count()
    
    # Por status
    por_status = db.query(
        LinhaTecnologia.status_etapa,
        func.count(LinhaTecnologia.id).label('quantidade')
    ).filter(
        LinhaTecnologia.consultor.ilike(f"%{current_user.nome}%")
    ).group_by(LinhaTecnologia.status_etapa).all()
    
    # Por situação
    por_situacao = db.query(
        LinhaTecnologia.situacao,
        func.count(LinhaTecnologia.id).label('quantidade')
    ).filter(
        LinhaTecnologia.consultor.ilike(f"%{current_user.nome}%")
    ).group_by(LinhaTecnologia.situacao).all()
    
    # Valor total
    valor_total = query.with_entities(func.sum(LinhaTecnologia.valor_proposta)).scalar() or 0
    
    return {
        "total_projetos": total_projetos,
        "valor_total": float(valor_total),
        "por_status": [{"status": s[0] or "Sem status", "quantidade": s[1]} for s in por_status],
        "por_situacao": [{"situacao": s[0] or "Sem situação", "quantidade": s[1]} for s in por_situacao]
    }
