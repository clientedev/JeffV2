from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

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
    limit: int = 1000,
    busca: Optional[str] = None,
    porte: Optional[str] = None,
    er: Optional[str] = None,
    zona: Optional[str] = None,
    municipio: Optional[str] = None,
    estado: Optional[str] = None,
    area: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Empresa)
    
    if busca:
        query = query.filter(
            (Empresa.nome.ilike(f"%{busca}%")) |
            (Empresa.cnpj.ilike(f"%{busca}%")) |
            (Empresa.sigla.ilike(f"%{busca}%"))
        )
    
    if porte:
        query = query.filter(Empresa.porte == porte)
    if er:
        query = query.filter(Empresa.er == er)
    if zona:
        query = query.filter(Empresa.zona == zona)
    if municipio:
        query = query.filter(Empresa.municipio == municipio)
    if estado:
        query = query.filter(Empresa.estado == estado)
    if area:
        query = query.filter(Empresa.area.ilike(f"%{area}%"))
    
    empresas = query.offset(skip).limit(limit).all()
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

@router.get("/filtros/valores")
async def obter_valores_filtros(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    portes = db.query(Empresa.porte).distinct().filter(Empresa.porte.isnot(None)).all()
    ers = db.query(Empresa.er).distinct().filter(Empresa.er.isnot(None)).all()
    zonas = db.query(Empresa.zona).distinct().filter(Empresa.zona.isnot(None)).all()
    municipios = db.query(Empresa.municipio).distinct().filter(Empresa.municipio.isnot(None)).all()
    estados = db.query(Empresa.estado).distinct().filter(Empresa.estado.isnot(None)).all()
    areas = db.query(Empresa.area).distinct().filter(Empresa.area.isnot(None)).all()
    
    return {
        "portes": sorted([p[0] for p in portes if p[0]]),
        "ers": sorted([e[0] for e in ers if e[0]]),
        "zonas": sorted([z[0] for z in zonas if z[0]]),
        "municipios": sorted([m[0] for m in municipios if m[0]]),
        "estados": sorted([e[0] for e in estados if e[0]]),
        "areas": sorted([a[0] for a in areas if a[0]])
    }

@router.get("/exportar/excel")
async def exportar_excel(
    busca: Optional[str] = None,
    porte: Optional[str] = None,
    er: Optional[str] = None,
    zona: Optional[str] = None,
    municipio: Optional[str] = None,
    estado: Optional[str] = None,
    area: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Empresa)
    
    if busca:
        query = query.filter(
            (Empresa.nome.ilike(f"%{busca}%")) |
            (Empresa.cnpj.ilike(f"%{busca}%")) |
            (Empresa.sigla.ilike(f"%{busca}%"))
        )
    if porte:
        query = query.filter(Empresa.porte == porte)
    if er:
        query = query.filter(Empresa.er == er)
    if zona:
        query = query.filter(Empresa.zona == zona)
    if municipio:
        query = query.filter(Empresa.municipio == municipio)
    if estado:
        query = query.filter(Empresa.estado == estado)
    if area:
        query = query.filter(Empresa.area.ilike(f"%{area}%"))
    
    empresas = query.all()
    
    data = []
    for emp in empresas:
        data.append({
            "CNPJ": emp.cnpj,
            "Empresa": emp.nome,
            "Sigla": emp.sigla,
            "Porte": emp.porte,
            "ER": emp.er,
            "Carteira": emp.carteira,
            "Endereço": emp.endereco,
            "Bairro": emp.bairro,
            "Zona": emp.zona,
            "Município": emp.municipio,
            "Estado": emp.estado,
            "País": emp.pais,
            "Área": emp.area,
            "CNAE Principal": emp.cnae_principal,
            "Descrição CNAE": emp.descricao_cnae,
            "Tipo Empresa": emp.tipo_empresa,
            "Nº Funcionários": emp.num_funcionarios,
            "Observação": emp.observacao
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Empresas')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=empresas.xlsx"}
    )

@router.get("/exportar/pdf")
async def exportar_pdf(
    busca: Optional[str] = None,
    porte: Optional[str] = None,
    er: Optional[str] = None,
    zona: Optional[str] = None,
    municipio: Optional[str] = None,
    estado: Optional[str] = None,
    area: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Empresa)
    
    if busca:
        query = query.filter(
            (Empresa.nome.ilike(f"%{busca}%")) |
            (Empresa.cnpj.ilike(f"%{busca}%")) |
            (Empresa.sigla.ilike(f"%{busca}%"))
        )
    if porte:
        query = query.filter(Empresa.porte == porte)
    if er:
        query = query.filter(Empresa.er == er)
    if zona:
        query = query.filter(Empresa.zona == zona)
    if municipio:
        query = query.filter(Empresa.municipio == municipio)
    if estado:
        query = query.filter(Empresa.estado == estado)
    if area:
        query = query.filter(Empresa.area.ilike(f"%{area}%"))
    
    empresas = query.all()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=landscape(letter))
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("<b>Relatório de Empresas</b>", styles['Title'])
        elements.append(title)
        
        data = [['CNPJ', 'Empresa', 'Município', 'Estado', 'Zona', 'Área']]
        
        for emp in empresas:
            data.append([
                emp.cnpj or '',
                emp.nome[:30] if emp.nome else '',
                emp.municipio or '',
                emp.estado or '',
                emp.zona or '',
                emp.area[:20] if emp.area else ''
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
        
        return FileResponse(tmp.name, media_type="application/pdf", filename="empresas.pdf")
