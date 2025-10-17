from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.database import get_db
from app.models.models import Contato
from app.auth import get_current_user
from fastapi.responses import StreamingResponse
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import pandas as pd

router = APIRouter()

class ContatoCreate(BaseModel):
    empresa: Optional[str] = None
    cnpj: Optional[str] = None
    carteira: Optional[str] = None
    porte: Optional[str] = None
    er: Optional[str] = None
    contato: Optional[str] = None
    ponto_focal: Optional[str] = None
    cargo: Optional[str] = None
    proprietario_socio: Optional[str] = None
    telefone_fixo: Optional[str] = None
    celular: Optional[str] = None
    celular2: Optional[str] = None
    email: Optional[str] = None
    emails_voltaram: Optional[str] = None
    observacoes: Optional[str] = None
    atualizacao: Optional[date] = None

class ContatoUpdate(BaseModel):
    empresa: Optional[str] = None
    cnpj: Optional[str] = None
    carteira: Optional[str] = None
    porte: Optional[str] = None
    er: Optional[str] = None
    contato: Optional[str] = None
    ponto_focal: Optional[str] = None
    cargo: Optional[str] = None
    proprietario_socio: Optional[str] = None
    telefone_fixo: Optional[str] = None
    celular: Optional[str] = None
    celular2: Optional[str] = None
    email: Optional[str] = None
    emails_voltaram: Optional[str] = None
    observacoes: Optional[str] = None
    atualizacao: Optional[date] = None

class ContatoResponse(BaseModel):
    id: int
    empresa: Optional[str]
    cnpj: Optional[str]
    carteira: Optional[str]
    porte: Optional[str]
    er: Optional[str]
    contato: Optional[str]
    ponto_focal: Optional[str]
    cargo: Optional[str]
    proprietario_socio: Optional[str]
    telefone_fixo: Optional[str]
    celular: Optional[str]
    celular2: Optional[str]
    email: Optional[str]
    emails_voltaram: Optional[str]
    observacoes: Optional[str]
    atualizacao: Optional[date]
    dados_iniciais: bool
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ContatoResponse])
async def listar_contatos(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    empresa: Optional[str] = None,
    porte: Optional[str] = None,
    er: Optional[str] = None,
    carteira: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Contato)
    
    # Aplicar filtros
    if search:
        query = query.filter(
            or_(
                Contato.empresa.ilike(f"%{search}%"),
                Contato.cnpj.ilike(f"%{search}%"),
                Contato.contato.ilike(f"%{search}%"),
                Contato.email.ilike(f"%{search}%")
            )
        )
    
    if empresa:
        query = query.filter(Contato.empresa.ilike(f"%{empresa}%"))
    
    if porte:
        query = query.filter(Contato.porte == porte)
    
    if er:
        query = query.filter(Contato.er == er)
    
    if carteira:
        query = query.filter(Contato.carteira == carteira)
    
    contatos = query.order_by(Contato.empresa).offset(skip).limit(limit).all()
    return contatos

@router.get("/filtros")
async def obter_filtros(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Retorna valores únicos para os filtros"""
    portes = db.query(Contato.porte).distinct().filter(Contato.porte.isnot(None)).all()
    ers = db.query(Contato.er).distinct().filter(Contato.er.isnot(None)).all()
    carteiras = db.query(Contato.carteira).distinct().filter(Contato.carteira.isnot(None)).all()
    
    return {
        "portes": sorted([p[0] for p in portes if p[0]]),
        "ers": sorted([e[0] for e in ers if e[0]]),
        "carteiras": sorted([c[0] for c in carteiras if c[0]])
    }

@router.get("/{contato_id}", response_model=ContatoResponse)
async def obter_contato(
    contato_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    contato = db.query(Contato).filter(Contato.id == contato_id).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    return contato

@router.post("/", response_model=ContatoResponse)
async def criar_contato(
    contato_data: ContatoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    contato = Contato(**contato_data.dict(), dados_iniciais=False)
    db.add(contato)
    db.commit()
    db.refresh(contato)
    return contato

@router.put("/{contato_id}", response_model=ContatoResponse)
async def atualizar_contato(
    contato_id: int,
    contato_data: ContatoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    contato = db.query(Contato).filter(Contato.id == contato_id).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    if contato.dados_iniciais:
        raise HTTPException(status_code=403, detail="Dados iniciais não podem ser modificados")
    
    for key, value in contato_data.dict(exclude_unset=True).items():
        setattr(contato, key, value)
    
    db.commit()
    db.refresh(contato)
    return contato

@router.delete("/{contato_id}")
async def deletar_contato(
    contato_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    contato = db.query(Contato).filter(Contato.id == contato_id).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    if contato.dados_iniciais:
        raise HTTPException(status_code=403, detail="Dados iniciais não podem ser deletados")
    
    db.delete(contato)
    db.commit()
    return {"message": "Contato deletado com sucesso"}

@router.get("/exportar/excel")
async def exportar_excel(
    search: Optional[str] = None,
    empresa: Optional[str] = None,
    porte: Optional[str] = None,
    er: Optional[str] = None,
    carteira: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Contato)
    
    # Aplicar mesmos filtros
    if search:
        query = query.filter(
            or_(
                Contato.empresa.ilike(f"%{search}%"),
                Contato.cnpj.ilike(f"%{search}%"),
                Contato.contato.ilike(f"%{search}%"),
                Contato.email.ilike(f"%{search}%")
            )
        )
    
    if empresa:
        query = query.filter(Contato.empresa.ilike(f"%{empresa}%"))
    
    if porte:
        query = query.filter(Contato.porte == porte)
    
    if er:
        query = query.filter(Contato.er == er)
    
    if carteira:
        query = query.filter(Contato.carteira == carteira)
    
    contatos = query.all()
    
    # Criar DataFrame
    data = []
    for c in contatos:
        data.append({
            "ID": c.id,
            "Empresa": c.empresa,
            "CNPJ": c.cnpj,
            "Carteira": c.carteira,
            "Porte": c.porte,
            "ER": c.er,
            "Contato": c.contato,
            "Ponto Focal": c.ponto_focal,
            "Cargo": c.cargo,
            "Proprietário/Sócio": c.proprietario_socio,
            "Telefone Fixo": c.telefone_fixo,
            "Celular": c.celular,
            "Celular 2": c.celular2,
            "Email": c.email,
            "E-mails Voltaram": c.emails_voltaram,
            "Observações": c.observacoes,
            "Atualização": c.atualizacao
        })
    
    df = pd.DataFrame(data)
    
    # Criar arquivo Excel em memória
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Contatos')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=contatos_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )

@router.get("/exportar/pdf")
async def exportar_pdf(
    search: Optional[str] = None,
    empresa: Optional[str] = None,
    porte: Optional[str] = None,
    er: Optional[str] = None,
    carteira: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Contato)
    
    # Aplicar mesmos filtros
    if search:
        query = query.filter(
            or_(
                Contato.empresa.ilike(f"%{search}%"),
                Contato.cnpj.ilike(f"%{search}%"),
                Contato.contato.ilike(f"%{search}%"),
                Contato.email.ilike(f"%{search}%")
            )
        )
    
    if empresa:
        query = query.filter(Contato.empresa.ilike(f"%{empresa}%"))
    
    if porte:
        query = query.filter(Contato.porte == porte)
    
    if er:
        query = query.filter(Contato.er == er)
    
    if carteira:
        query = query.filter(Contato.carteira == carteira)
    
    contatos = query.all()
    
    # Criar PDF em memória
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    title = Paragraph("Relatório de Contatos", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Dados da tabela
    data = [["Empresa", "CNPJ", "Contato", "Cargo", "Telefone", "Email"]]
    for c in contatos[:50]:  # Limitar a 50 registros para PDF
        data.append([
            c.empresa[:30] if c.empresa else "",
            c.cnpj if c.cnpj else "",
            c.contato[:25] if c.contato else "",
            c.cargo[:20] if c.cargo else "",
            c.celular if c.celular else c.telefone_fixo if c.telefone_fixo else "",
            c.email[:30] if c.email else ""
        ])
    
    # Criar tabela
    table = Table(data, colWidths=[2*inch, 1.2*inch, 1.5*inch, 1.2*inch, 1*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=contatos_{datetime.now().strftime('%Y%m%d')}.pdf"}
    )
