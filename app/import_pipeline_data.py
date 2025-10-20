import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import SessionLocal, engine
from app.models.models import Stage, CompanyPipeline, CompanyStageHistory, LinhaTecnologia, LinhaEducacional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STAGES_CONFIG = [
    {"ordem": 1, "nome": "Prospecção", "descricao": "Identificação e qualificação de oportunidades", "cor": "#8b5cf6"},
    {"ordem": 2, "nome": "Reunião de Diagnóstico", "descricao": "Análise detalhada das necessidades do cliente", "cor": "#3b82f6"},
    {"ordem": 3, "nome": "Proposta / Adesão", "descricao": "Elaboração e apresentação da proposta", "cor": "#06b6d4"},
    {"ordem": 4, "nome": "Execução", "descricao": "Implementação da solução", "cor": "#10b981"},
    {"ordem": 5, "nome": "Entregas", "descricao": "Conclusão e entrega dos resultados", "cor": "#f59e0b"},
    {"ordem": 6, "nome": "Certificação", "descricao": "Processo de certificação e validação", "cor": "#f97316"},
    {"ordem": 7, "nome": "Finalizado", "descricao": "Projeto concluído com sucesso", "cor": "#22c55e"}
]

STATUS_TO_STAGE_MAP = {
    'prospecção': 1,
    'prospecçao': 1,
    'diagnostico': 2,
    'diagnóstico': 2,
    'reunião': 2,
    'reuniao': 2,
    'proposta': 3,
    'adesão': 3,
    'adesao': 3,
    'execução': 4,
    'execucao': 4,
    'em execução': 4,
    'em execucao': 4,
    'andamento': 4,
    'entrega': 5,
    'entregas': 5,
    'concluído': 5,
    'concluido': 5,
    'certificação': 6,
    'certificacao': 6,
    'finalizado': 7,
    'finalizada': 7,
    'encerrado': 7,
    'concluído': 7
}

def criar_stages(db: Session):
    logger.info("Criando etapas do pipeline...")
    
    existing_stages = db.query(Stage).all()
    if existing_stages:
        logger.info(f"✓ {len(existing_stages)} etapas já existem")
        return
    
    for config in STAGES_CONFIG:
        stage = Stage(**config)
        db.add(stage)
    
    db.commit()
    logger.info(f"✓ Criadas {len(STAGES_CONFIG)} etapas do pipeline")

def mapear_status_para_stage(status_str: str) -> int:
    if pd.isna(status_str):
        return 1
    
    status_lower = str(status_str).lower().strip()
    
    for keyword, stage_id in STATUS_TO_STAGE_MAP.items():
        if keyword in status_lower:
            return stage_id
    
    return 1

def importar_linha_tecnologia(db: Session, arquivo_excel: str):
    logger.info(f"Importando dados de Linha Tecnologia de {arquivo_excel}...")
    
    try:
        df = pd.read_excel(arquivo_excel)
        logger.info(f"Lidas {len(df)} linhas do arquivo")
        
        importados = 0
        for _, row in df.iterrows():
            cnpj = str(row.get('CNPJ', '')).strip() if pd.notna(row.get('CNPJ')) else None
            empresa = str(row.get('EMPRESA', '')).strip() if pd.notna(row.get('EMPRESA')) else None
            
            if not cnpj or not empresa or cnpj == 'nan':
                continue
            
            existing = db.query(CompanyPipeline).filter(
                CompanyPipeline.cnpj == cnpj,
                CompanyPipeline.linha == 'TECNOLOGIA'
            ).first()
            
            if existing:
                continue
            
            status_etapa = row.get('STATUS DA ETAPA', '')
            stage_id = mapear_status_para_stage(status_etapa)
            
            valor_proposta = row.get('VALOR DA PROPOSTA')
            if pd.notna(valor_proposta):
                try:
                    valor_proposta = float(valor_proposta)
                except:
                    valor_proposta = None
            else:
                valor_proposta = None
            
            company = CompanyPipeline(
                cnpj=cnpj,
                nome_empresa=empresa,
                linha='TECNOLOGIA',
                tipo_programa=str(row.get('TIPO DE PROGRAMA', '')).strip() if pd.notna(row.get('TIPO DE PROGRAMA')) else None,
                porte=str(row.get('PORTE', '')).strip() if pd.notna(row.get('PORTE')) else None,
                er_regiao=str(row.get('ER', '')).strip() if pd.notna(row.get('ER')) else None,
                consultor_responsavel=str(row.get('CONSULTOR', '')).strip() if pd.notna(row.get('CONSULTOR')) else None,
                stage_id=stage_id,
                numero_proposta=str(row.get('Nº PROPOSTA', '')).strip() if pd.notna(row.get('Nº PROPOSTA')) else None,
                valor_proposta=valor_proposta,
                observacoes=str(row.get('OBSERVAÇÕES', '')).strip() if pd.notna(row.get('OBSERVAÇÕES')) else None
            )
            db.add(company)
            
            history = CompanyStageHistory(
                company_pipeline=company,
                stage_id=stage_id,
                data_entrada=datetime.utcnow(),
                observacao=f"Importado automaticamente - Status original: {status_etapa}"
            )
            db.add(history)
            
            importados += 1
            
            if importados % 100 == 0:
                db.commit()
                logger.info(f"Importadas {importados} empresas...")
        
        db.commit()
        logger.info(f"✓ Importadas {importados} empresas de Linha Tecnologia")
        
    except Exception as e:
        logger.error(f"Erro ao importar Linha Tecnologia: {e}")
        db.rollback()

def importar_linha_educacional(db: Session, arquivo_excel: str):
    logger.info(f"Importando dados de Linha Educacional de {arquivo_excel}...")
    
    try:
        df = pd.read_excel(arquivo_excel)
        logger.info(f"Lidas {len(df)} linhas do arquivo")
        
        importados = 0
        for _, row in df.iterrows():
            cnpj = str(row.get('CNPJ', '')).strip() if pd.notna(row.get('CNPJ')) else None
            empresa = str(row.get('CLIENTE', '')).strip() if pd.notna(row.get('CLIENTE')) else None
            
            if not cnpj or not empresa or cnpj == 'nan':
                continue
            
            existing = db.query(CompanyPipeline).filter(
                CompanyPipeline.cnpj == cnpj,
                CompanyPipeline.linha == 'EDUCACIONAL'
            ).first()
            
            if existing:
                continue
            
            status_proposta = row.get('STATUS DA PROPOSTA', '')
            stage_id = mapear_status_para_stage(status_proposta)
            
            valor = row.get('VALOR')
            if pd.notna(valor):
                try:
                    valor = float(valor)
                except:
                    valor = None
            else:
                valor = None
            
            company = CompanyPipeline(
                cnpj=cnpj,
                nome_empresa=empresa,
                linha='EDUCACIONAL',
                tipo_programa=str(row.get('PROGRAMA', '')).strip() if pd.notna(row.get('PROGRAMA')) else None,
                porte=None,
                er_regiao=str(row.get('ESTABELECIMENTO', '')).strip() if pd.notna(row.get('ESTABELECIMENTO')) else None,
                consultor_responsavel=None,
                stage_id=stage_id,
                numero_proposta=str(row.get('Nº PROPOSTA', '')).strip() if pd.notna(row.get('Nº PROPOSTA')) else None,
                valor_proposta=valor,
                observacoes=str(row.get('Obs.', '')).strip() if pd.notna(row.get('Obs.')) else None
            )
            db.add(company)
            
            history = CompanyStageHistory(
                company_pipeline=company,
                stage_id=stage_id,
                data_entrada=datetime.utcnow(),
                observacao=f"Importado automaticamente - Status original: {status_proposta}"
            )
            db.add(history)
            
            importados += 1
            
            if importados % 100 == 0:
                db.commit()
                logger.info(f"Importadas {importados} empresas...")
        
        db.commit()
        logger.info(f"✓ Importadas {importados} empresas de Linha Educacional")
        
    except Exception as e:
        logger.error(f"Erro ao importar Linha Educacional: {e}")
        db.rollback()

def importar_todos_dados():
    db = SessionLocal()
    try:
        criar_stages(db)
        
        importar_linha_tecnologia(db, 'attached_assets/linha tecnologia_1760989195244.xlsx')
        importar_linha_educacional(db, 'attached_assets/linha educacional_1760989195245.xlsx')
        
        total = db.query(CompanyPipeline).count()
        logger.info(f"\n✓ IMPORTAÇÃO CONCLUÍDA - Total de {total} empresas no pipeline")
        
    finally:
        db.close()

if __name__ == "__main__":
    importar_todos_dados()
