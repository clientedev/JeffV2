import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import Contato, LinhaTecnologia, LinhaEducacional, Empresa
from app.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_str(value, max_length=None):
    """Converte valor para string de forma segura"""
    if pd.isna(value):
        return None
    result = str(value).strip()
    if max_length and len(result) > max_length:
        result = result[:max_length]
    return result if result else None

def safe_date(value):
    """Converte valor para data de forma segura"""
    if pd.isna(value):
        return None
    try:
        if isinstance(value, datetime):
            return value.date()
        return pd.to_datetime(value).date()
    except:
        return None

def safe_numeric(value):
    """Converte valor para numérico de forma segura"""
    if pd.isna(value):
        return None
    try:
        return float(value)
    except:
        return None

def safe_int(value):
    """Converte valor para inteiro de forma segura"""
    if pd.isna(value):
        return None
    try:
        return int(float(value))
    except:
        return None

def importar_contatos(db: Session):
    """Importa contatos da planilha Excel"""
    try:
        logger.info("Importando contatos...")
        
        # Verifica se já existem dados iniciais
        if db.query(Contato).filter(Contato.dados_iniciais == True).first():
            logger.info("Contatos já foram importados anteriormente. Pulando...")
            return
        
        df = pd.read_excel('attached_assets/contats_1760739018153.xlsx')
        
        contatos_adicionados = 0
        for _, row in df.iterrows():
            try:
                contato = Contato(
                    empresa=safe_str(row.get('EMPRESA'), 255),
                    cnpj=safe_str(row.get('CNPJ'), 18),
                    carteira=safe_str(row.get('CARTEIRA'), 100),
                    porte=safe_str(row.get('PORTE'), 50),
                    er=safe_str(row.get('ER'), 100),
                    contato=safe_str(row.get('CONTATO'), 255),
                    ponto_focal=safe_str(row.get('PONTO FOCAL'), 255),
                    cargo=safe_str(row.get('CARGO'), 100),
                    proprietario_socio=safe_str(row.get('PROPRIETÁRIO / SÓCIO'), 255),
                    telefone_fixo=safe_str(row.get('TELEFONE FIXO'), 20),
                    celular=safe_str(row.get('CELULAR'), 20),
                    celular2=safe_str(row.get('CELULAR2'), 20),
                    email=safe_str(row.get('EMAIL'), 255),
                    emails_voltaram=safe_str(row.get('E-MAILS VOLTARAM'), 255),
                    observacoes=safe_str(row.get('OBS')),
                    atualizacao=safe_date(row.get('ATUALIZAÇÃO')),
                    dados_iniciais=True
                )
                db.add(contato)
                contatos_adicionados += 1
            except Exception as e:
                logger.error(f"Erro ao importar contato: {e}")
                continue
        
        db.commit()
        logger.info(f"{contatos_adicionados} contatos importados com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao importar contatos: {e}")
        db.rollback()

def importar_linha_tecnologia(db: Session):
    """Importa linha tecnologia da planilha Excel"""
    try:
        logger.info("Importando linha tecnologia...")
        
        # Verifica se já existem dados iniciais
        if db.query(LinhaTecnologia).filter(LinhaTecnologia.dados_iniciais == True).first():
            logger.info("Linha tecnologia já foi importada anteriormente. Pulando...")
            return
        
        df = pd.read_excel('attached_assets/linha tecnologia_1760739169405.xlsx')
        
        registros_adicionados = 0
        for _, row in df.iterrows():
            try:
                registro = LinhaTecnologia(
                    linha=safe_str(row.get('LINHA'), 100),
                    tipo_programa=safe_str(row.get('TIPO DE PROGRAMA'), 100),
                    cnpj=safe_str(row.get('CNPJ'), 18),
                    empresa=safe_str(row.get('EMPRESA'), 255),
                    porte=safe_str(row.get('PORTE'), 50),
                    er=safe_str(row.get('ER'), 100),
                    sigla=safe_str(row.get('SIGLA'), 50),
                    t3=safe_str(row.get('T3'), 100),
                    status_etapa=safe_str(row.get('STATUS DA ETAPA'), 100),
                    oportunidade=safe_str(row.get('OPORTUNIDADE'), 100),
                    numero_proposta=safe_str(row.get('Nº PROPOSTA'), 50),
                    ordem_venda=safe_str(row.get('ORDEM DE VENDA'), 50),
                    emissor_proposta=safe_str(row.get('EMISSOR DA PROPOSTA'), 255),
                    cfp_parceiro=safe_str(row.get('CFP PARCEIRO'), 100),
                    solucao=safe_str(row.get('SOLUÇÃO'), 500),
                    ch=safe_str(row.get('CH'), 50),
                    consultor=safe_str(row.get('CONSULTOR'), 255),
                    data_inicio=safe_date(row.get('DATA INÍCIO')),
                    data_termino=safe_date(row.get('DATA TÉRMINO')),
                    presencial=safe_str(row.get('PRESENCIAL'), 50),
                    gratuidade=safe_str(row.get('GRATUIDADE?'), 50),
                    valor_proposta=safe_numeric(row.get('VALOR DA PROPOSTA')),
                    situacao=safe_str(row.get('SITUAÇÃO'), 100),
                    numero_demanda=safe_str(row.get('Nº DEMANDA ou                       Nº ID'), 100),
                    codigo_rae=safe_str(row.get('CÓDIGO RAE '), 100),
                    observacoes=safe_str(row.get('OBSERVAÇÕES')),
                    ano=safe_int(row.get('ANO')),
                    mes=safe_str(row.get('MÊS'), 20),
                    dados_iniciais=True
                )
                db.add(registro)
                registros_adicionados += 1
            except Exception as e:
                logger.error(f"Erro ao importar registro de linha tecnologia: {e}")
                continue
        
        db.commit()
        logger.info(f"{registros_adicionados} registros de linha tecnologia importados com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao importar linha tecnologia: {e}")
        db.rollback()

def importar_linha_educacional(db: Session):
    """Importa linha educacional da planilha Excel"""
    try:
        logger.info("Importando linha educacional...")
        
        # Verifica se já existem dados iniciais
        if db.query(LinhaEducacional).filter(LinhaEducacional.dados_iniciais == True).first():
            logger.info("Linha educacional já foi importada anteriormente. Pulando...")
            return
        
        df = pd.read_excel('attached_assets/linha educacional_1760739298496.xlsx')
        
        registros_adicionados = 0
        for _, row in df.iterrows():
            try:
                registro = LinhaEducacional(
                    linha=safe_str(row.get('LINHA'), 100),
                    tipo_programa=safe_str(row.get('TIPO DE PROGRAMA'), 100),
                    cnpj=safe_str(row.get('CNPJ'), 18),
                    empresa=safe_str(row.get('EMPRESA'), 255),
                    porte=safe_str(row.get('PORTE'), 50),
                    er=safe_str(row.get('ER'), 100),
                    sigla=safe_str(row.get('SIGLA'), 50),
                    status_etapa=safe_str(row.get('STATUS DA ETAPA'), 100),
                    oportunidade=safe_str(row.get('OPORTUNIDADE'), 100),
                    numero_proposta=safe_str(row.get('Nº PROPOSTA'), 50),
                    ordem_venda=safe_str(row.get('ORDEM DE VENDA'), 50),
                    emissor_proposta=safe_str(row.get('EMISSOR DA PROPOSTA'), 255),
                    solucao=safe_str(row.get('SOLUÇÃO'), 500),
                    ch=safe_str(row.get('CH'), 50),
                    consultor=safe_str(row.get('CONSULTOR'), 255),
                    data_inicio=safe_date(row.get('DATA INÍCIO')),
                    data_termino=safe_date(row.get('DATA TÉRMINO')),
                    presencial=safe_str(row.get('PRESENCIAL'), 50),
                    gratuidade=safe_str(row.get('GRATUIDADE?'), 50),
                    valor_proposta=safe_numeric(row.get('VALOR DA PROPOSTA')),
                    situacao=safe_str(row.get('SITUAÇÃO'), 100),
                    numero_demanda=safe_str(row.get('Nº DEMANDA'), 100),
                    codigo_rae=safe_str(row.get('CÓDIGO RAE'), 100),
                    observacoes=safe_str(row.get('OBSERVAÇÕES')),
                    ano=safe_int(row.get('ANO')),
                    mes=safe_str(row.get('MÊS'), 20),
                    dados_iniciais=True
                )
                db.add(registro)
                registros_adicionados += 1
            except Exception as e:
                logger.error(f"Erro ao importar registro de linha educacional: {e}")
                continue
        
        db.commit()
        logger.info(f"{registros_adicionados} registros de linha educacional importados com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao importar linha educacional: {e}")
        db.rollback()

def seed_all_data():
    """Executa todas as importações de dados iniciais"""
    db = SessionLocal()
    try:
        logger.info("Iniciando importação de dados iniciais...")
        importar_contatos(db)
        importar_linha_tecnologia(db)
        importar_linha_educacional(db)
        logger.info("Importação de dados iniciais concluída!")
    except Exception as e:
        logger.error(f"Erro durante importação: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_all_data()
