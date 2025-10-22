from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
import os
import shutil

from app.database import get_db
from app.models.models import (
    EmailContato, CampanhaEmail, CampanhaDestinatario, 
    AnexoEmail, Usuario
)
from app.auth import get_current_user

router = APIRouter()

@router.get("/email-contatos")
async def listar_email_contatos(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    apenas_ativos: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(EmailContato)
    
    if apenas_ativos:
        query = query.filter(EmailContato.ativo == True)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                EmailContato.nome.ilike(search_filter),
                EmailContato.email.ilike(search_filter),
                EmailContato.empresa.ilike(search_filter)
            )
        )
    
    total = query.count()
    contatos = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "contatos": [
            {
                "id": c.id,
                "nome": c.nome,
                "email": c.email,
                "empresa": c.empresa,
                "cargo": c.cargo,
                "telefone": c.telefone,
                "ativo": c.ativo,
                "observacoes": c.observacoes,
                "criado_em": c.criado_em.isoformat() if c.criado_em else None
            }
            for c in contatos
        ]
    }

@router.post("/email-contatos")
async def criar_email_contato(
    nome: str,
    email: str,
    empresa: str = None,
    cargo: str = None,
    telefone: str = None,
    observacoes: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    contato_existente = db.query(EmailContato).filter(
        EmailContato.email == email
    ).first()
    
    if contato_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    novo_contato = EmailContato(
        nome=nome,
        email=email,
        empresa=empresa,
        cargo=cargo,
        telefone=telefone,
        observacoes=observacoes
    )
    
    db.add(novo_contato)
    db.commit()
    db.refresh(novo_contato)
    
    return {
        "id": novo_contato.id,
        "nome": novo_contato.nome,
        "email": novo_contato.email,
        "message": "Contato criado com sucesso"
    }

@router.put("/email-contatos/{contato_id}")
async def atualizar_email_contato(
    contato_id: int,
    nome: str = None,
    email: str = None,
    empresa: str = None,
    cargo: str = None,
    telefone: str = None,
    ativo: bool = None,
    observacoes: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    contato = db.query(EmailContato).filter(EmailContato.id == contato_id).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    if nome is not None:
        contato.nome = nome
    if email is not None:
        contato.email = email
    if empresa is not None:
        contato.empresa = empresa
    if cargo is not None:
        contato.cargo = cargo
    if telefone is not None:
        contato.telefone = telefone
    if ativo is not None:
        contato.ativo = ativo
    if observacoes is not None:
        contato.observacoes = observacoes
    
    contato.atualizado_em = datetime.utcnow()
    
    db.commit()
    db.refresh(contato)
    
    return {"message": "Contato atualizado com sucesso"}

@router.delete("/email-contatos/{contato_id}")
async def deletar_email_contato(
    contato_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    contato = db.query(EmailContato).filter(EmailContato.id == contato_id).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    db.delete(contato)
    db.commit()
    
    return {"message": "Contato deletado com sucesso"}

@router.get("/campanhas")
async def listar_campanhas(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(CampanhaEmail)
    
    if status:
        query = query.filter(CampanhaEmail.status == status)
    
    query = query.order_by(CampanhaEmail.criado_em.desc())
    
    total = query.count()
    campanhas = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "campanhas": [
            {
                "id": c.id,
                "titulo": c.titulo,
                "assunto": c.assunto,
                "status": c.status,
                "total_destinatarios": c.total_destinatarios,
                "total_enviados": c.total_enviados,
                "total_falhas": c.total_falhas,
                "data_agendamento": c.data_agendamento.isoformat() if c.data_agendamento else None,
                "data_envio": c.data_envio.isoformat() if c.data_envio else None,
                "criado_em": c.criado_em.isoformat() if c.criado_em else None
            }
            for c in campanhas
        ]
    }

@router.get("/campanhas/{campanha_id}")
async def obter_campanha(
    campanha_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    campanha = db.query(CampanhaEmail).filter(CampanhaEmail.id == campanha_id).first()
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    destinatarios = db.query(CampanhaDestinatario).filter(
        CampanhaDestinatario.campanha_id == campanha_id
    ).all()
    
    anexos = db.query(AnexoEmail).filter(
        AnexoEmail.campanha_id == campanha_id
    ).all()
    
    return {
        "id": campanha.id,
        "titulo": campanha.titulo,
        "assunto": campanha.assunto,
        "corpo_email": campanha.corpo_email,
        "remetente_nome": campanha.remetente_nome,
        "remetente_email": campanha.remetente_email,
        "status": campanha.status,
        "data_agendamento": campanha.data_agendamento.isoformat() if campanha.data_agendamento else None,
        "data_envio": campanha.data_envio.isoformat() if campanha.data_envio else None,
        "total_destinatarios": campanha.total_destinatarios,
        "total_enviados": campanha.total_enviados,
        "total_falhas": campanha.total_falhas,
        "destinatarios": [
            {
                "id": d.id,
                "email": d.email,
                "nome": d.nome,
                "status_envio": d.status_envio,
                "data_envio": d.data_envio.isoformat() if d.data_envio else None,
                "mensagem_erro": d.mensagem_erro
            }
            for d in destinatarios
        ],
        "anexos": [
            {
                "id": a.id,
                "nome_arquivo": a.nome_arquivo,
                "tipo_arquivo": a.tipo_arquivo,
                "tamanho_bytes": a.tamanho_bytes
            }
            for a in anexos
        ]
    }

@router.post("/campanhas")
async def criar_campanha(
    titulo: str,
    assunto: str,
    corpo_email: str,
    remetente_nome: str = None,
    remetente_email: str = None,
    destinatarios_ids: List[int] = [],
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    nova_campanha = CampanhaEmail(
        titulo=titulo,
        assunto=assunto,
        corpo_email=corpo_email,
        remetente_nome=remetente_nome,
        remetente_email=remetente_email,
        usuario_id=current_user.id,
        status='Rascunho'
    )
    
    db.add(nova_campanha)
    db.commit()
    db.refresh(nova_campanha)
    
    if destinatarios_ids:
        for contato_id in destinatarios_ids:
            contato = db.query(EmailContato).filter(EmailContato.id == contato_id).first()
            if contato:
                destinatario = CampanhaDestinatario(
                    campanha_id=nova_campanha.id,
                    email_contato_id=contato.id,
                    email=contato.email,
                    nome=contato.nome
                )
                db.add(destinatario)
        
        nova_campanha.total_destinatarios = len(destinatarios_ids)
        db.commit()
    
    return {
        "id": nova_campanha.id,
        "titulo": nova_campanha.titulo,
        "message": "Campanha criada com sucesso"
    }

@router.put("/campanhas/{campanha_id}")
async def atualizar_campanha(
    campanha_id: int,
    titulo: str = None,
    assunto: str = None,
    corpo_email: str = None,
    remetente_nome: str = None,
    remetente_email: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    campanha = db.query(CampanhaEmail).filter(CampanhaEmail.id == campanha_id).first()
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    if campanha.status != 'Rascunho':
        raise HTTPException(
            status_code=400, 
            detail="Apenas campanhas em rascunho podem ser editadas"
        )
    
    if titulo is not None:
        campanha.titulo = titulo
    if assunto is not None:
        campanha.assunto = assunto
    if corpo_email is not None:
        campanha.corpo_email = corpo_email
    if remetente_nome is not None:
        campanha.remetente_nome = remetente_nome
    if remetente_email is not None:
        campanha.remetente_email = remetente_email
    
    campanha.atualizado_em = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Campanha atualizada com sucesso"}

@router.post("/campanhas/{campanha_id}/destinatarios")
async def adicionar_destinatarios(
    campanha_id: int,
    destinatarios_ids: List[int],
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    campanha = db.query(CampanhaEmail).filter(CampanhaEmail.id == campanha_id).first()
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    if campanha.status != 'Rascunho':
        raise HTTPException(
            status_code=400,
            detail="Não é possível adicionar destinatários a campanhas já enviadas"
        )
    
    adicionados = 0
    for contato_id in destinatarios_ids:
        contato = db.query(EmailContato).filter(EmailContato.id == contato_id).first()
        if contato:
            ja_existe = db.query(CampanhaDestinatario).filter(
                CampanhaDestinatario.campanha_id == campanha_id,
                CampanhaDestinatario.email == contato.email
            ).first()
            
            if not ja_existe:
                destinatario = CampanhaDestinatario(
                    campanha_id=campanha.id,
                    email_contato_id=contato.id,
                    email=contato.email,
                    nome=contato.nome
                )
                db.add(destinatario)
                adicionados += 1
    
    campanha.total_destinatarios = db.query(CampanhaDestinatario).filter(
        CampanhaDestinatario.campanha_id == campanha_id
    ).count()
    
    db.commit()
    
    return {
        "message": f"{adicionados} destinatários adicionados com sucesso",
        "total_destinatarios": campanha.total_destinatarios
    }

@router.delete("/campanhas/{campanha_id}/destinatarios/{destinatario_id}")
async def remover_destinatario(
    campanha_id: int,
    destinatario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    campanha = db.query(CampanhaEmail).filter(CampanhaEmail.id == campanha_id).first()
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    if campanha.status != 'Rascunho':
        raise HTTPException(
            status_code=400,
            detail="Não é possível remover destinatários de campanhas já enviadas"
        )
    
    destinatario = db.query(CampanhaDestinatario).filter(
        CampanhaDestinatario.id == destinatario_id,
        CampanhaDestinatario.campanha_id == campanha_id
    ).first()
    
    if not destinatario:
        raise HTTPException(status_code=404, detail="Destinatário não encontrado")
    
    db.delete(destinatario)
    
    campanha.total_destinatarios = db.query(CampanhaDestinatario).filter(
        CampanhaDestinatario.campanha_id == campanha_id
    ).count()
    
    db.commit()
    
    return {"message": "Destinatário removido com sucesso"}

@router.post("/campanhas/{campanha_id}/anexos")
async def adicionar_anexo(
    campanha_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    campanha = db.query(CampanhaEmail).filter(CampanhaEmail.id == campanha_id).first()
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    if campanha.status != 'Rascunho':
        raise HTTPException(
            status_code=400,
            detail="Não é possível adicionar anexos a campanhas já enviadas"
        )
    
    upload_dir = "app/static/uploads/email_anexos"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{campanha_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = os.path.getsize(file_path)
    
    anexo = AnexoEmail(
        campanha_id=campanha_id,
        nome_arquivo=file.filename,
        tipo_arquivo=file.content_type,
        tamanho_bytes=file_size,
        caminho_arquivo=file_path
    )
    
    db.add(anexo)
    db.commit()
    db.refresh(anexo)
    
    return {
        "id": anexo.id,
        "nome_arquivo": anexo.nome_arquivo,
        "message": "Anexo adicionado com sucesso"
    }

@router.delete("/campanhas/{campanha_id}/anexos/{anexo_id}")
async def remover_anexo(
    campanha_id: int,
    anexo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    campanha = db.query(CampanhaEmail).filter(CampanhaEmail.id == campanha_id).first()
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    anexo = db.query(AnexoEmail).filter(
        AnexoEmail.id == anexo_id,
        AnexoEmail.campanha_id == campanha_id
    ).first()
    
    if not anexo:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")
    
    if os.path.exists(anexo.caminho_arquivo):
        os.remove(anexo.caminho_arquivo)
    
    db.delete(anexo)
    db.commit()
    
    return {"message": "Anexo removido com sucesso"}

@router.post("/campanhas/{campanha_id}/enviar")
async def enviar_campanha(
    campanha_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    campanha = db.query(CampanhaEmail).filter(CampanhaEmail.id == campanha_id).first()
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    if campanha.status != 'Rascunho':
        raise HTTPException(
            status_code=400,
            detail="Esta campanha já foi enviada"
        )
    
    if campanha.total_destinatarios == 0:
        raise HTTPException(
            status_code=400,
            detail="A campanha precisa ter ao menos um destinatário"
        )
    
    campanha.status = 'Pronta para Envio'
    campanha.data_agendamento = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Campanha marcada para envio. Configure a integração de email para enviar.",
        "status": campanha.status
    }

@router.delete("/campanhas/{campanha_id}")
async def deletar_campanha(
    campanha_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    campanha = db.query(CampanhaEmail).filter(CampanhaEmail.id == campanha_id).first()
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    anexos = db.query(AnexoEmail).filter(AnexoEmail.campanha_id == campanha_id).all()
    for anexo in anexos:
        if os.path.exists(anexo.caminho_arquivo):
            os.remove(anexo.caminho_arquivo)
    
    db.delete(campanha)
    db.commit()
    
    return {"message": "Campanha deletada com sucesso"}
