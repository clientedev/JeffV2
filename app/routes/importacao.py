from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import io
from datetime import datetime

from app.database import get_db
from app.models.models import Empresa, Consultor, Proposta, Cronograma, Contrato, Usuario
from app.schemas import ImportacaoResponse
from app.auth import get_current_user, require_role

router = APIRouter()

@router.post("/empresas", response_model=ImportacaoResponse)
async def importar_empresas(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Admin"))
):
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Use .xlsx, .xls ou .csv")
    
    try:
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        registros_importados = 0
        erros = []
        
        for index, row in df.iterrows():
            try:
                cnpj = str(row.get('CNPJ', '')).strip()
                if not cnpj or cnpj == 'nan':
                    continue
                
                empresa_existente = db.query(Empresa).filter(Empresa.cnpj == cnpj).first()
                if empresa_existente:
                    continue
                
                empresa = Empresa(
                    cnpj=cnpj,
                    nome=str(row.get('EMPRESA', row.get('NOME', ''))),
                    segmento=str(row.get('SEGMENTO', '')) if pd.notna(row.get('SEGMENTO')) else None,
                    regiao=str(row.get('REGIAO', '')) if pd.notna(row.get('REGIAO')) else None,
                    er=str(row.get('ER', '')) if pd.notna(row.get('ER')) else None
                )
                db.add(empresa)
                registros_importados += 1
            except Exception as e:
                erros.append(f"Linha {index + 2}: {str(e)}")
        
        db.commit()
        return ImportacaoResponse(
            sucesso=True,
            registros_importados=registros_importados,
            erros=erros
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

@router.post("/propostas", response_model=ImportacaoResponse)
async def importar_propostas(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Admin"))
):
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido")
    
    try:
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        registros_importados = 0
        erros = []
        
        for index, row in df.iterrows():
            try:
                numero_proposta = str(row.get('Nº PROPOSTA', row.get('NUMERO_PROPOSTA', ''))).strip()
                if not numero_proposta or numero_proposta == 'nan':
                    continue
                
                proposta_existente = db.query(Proposta).filter(
                    Proposta.numero_proposta == numero_proposta
                ).first()
                if proposta_existente:
                    continue
                
                cnpj = str(row.get('CNPJ', '')).strip()
                empresa = db.query(Empresa).filter(Empresa.cnpj == cnpj).first()
                if not empresa:
                    empresa = Empresa(
                        cnpj=cnpj,
                        nome=str(row.get('EMPRESA', ''))
                    )
                    db.add(empresa)
                    db.flush()
                
                consultor_nome = str(row.get('CONSULTOR', ''))
                consultor = None
                if consultor_nome and consultor_nome != 'nan':
                    consultor = db.query(Consultor).filter(Consultor.nome == consultor_nome).first()
                
                proposta = Proposta(
                    numero_proposta=numero_proposta,
                    empresa_id=empresa.id,
                    consultor_id=consultor.id if consultor else None,
                    solucao=str(row.get('SOLUÇÃO', row.get('SOLUCAO', ''))) if pd.notna(row.get('SOLUÇÃO', row.get('SOLUCAO'))) else None,
                    status=str(row.get('STATUS', 'Em andamento'))
                )
                
                if pd.notna(row.get('DATA_PROPOSTA')):
                    proposta.data_proposta = pd.to_datetime(row['DATA_PROPOSTA']).date()
                if pd.notna(row.get('VALOR_PROPOSTA')):
                    proposta.valor_proposta = float(row['VALOR_PROPOSTA'])
                
                db.add(proposta)
                registros_importados += 1
            except Exception as e:
                erros.append(f"Linha {index + 2}: {str(e)}")
        
        db.commit()
        return ImportacaoResponse(
            sucesso=True,
            registros_importados=registros_importados,
            erros=erros
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

@router.post("/cronogramas", response_model=ImportacaoResponse)
async def importar_cronogramas(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Admin"))
):
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido")
    
    try:
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        registros_importados = 0
        erros = []
        
        for index, row in df.iterrows():
            try:
                numero_proposta = str(row.get('Nº PROPOSTA', row.get('NUMERO_PROPOSTA', ''))).strip()
                if not numero_proposta or numero_proposta == 'nan':
                    continue
                
                proposta = db.query(Proposta).filter(
                    Proposta.numero_proposta == numero_proposta
                ).first()
                
                if not proposta:
                    erros.append(f"Linha {index + 2}: Proposta {numero_proposta} não encontrada")
                    continue
                
                cronograma = Cronograma(
                    proposta_id=proposta.id,
                    status=str(row.get('STATUS', 'Não iniciado'))
                )
                
                if pd.notna(row.get('DATA_INÍCIO', row.get('DATA_INICIO'))):
                    cronograma.data_inicio = pd.to_datetime(row.get('DATA_INÍCIO', row.get('DATA_INICIO'))).date()
                if pd.notna(row.get('DATA_TÉRMINO', row.get('DATA_TERMINO'))):
                    cronograma.data_termino = pd.to_datetime(row.get('DATA_TÉRMINO', row.get('DATA_TERMINO'))).date()
                if pd.notna(row.get('HORAS_PREVISTAS')):
                    cronograma.horas_previstas = float(row['HORAS_PREVISTAS'])
                if pd.notna(row.get('HORAS_EXECUTADAS')):
                    cronograma.horas_executadas = float(row['HORAS_EXECUTADAS'])
                
                db.add(cronograma)
                registros_importados += 1
            except Exception as e:
                erros.append(f"Linha {index + 2}: {str(e)}")
        
        db.commit()
        return ImportacaoResponse(
            sucesso=True,
            registros_importados=registros_importados,
            erros=erros
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")
