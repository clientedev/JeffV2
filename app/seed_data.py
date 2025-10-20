import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import Contato, LinhaTecnologia, LinhaEducacional, Empresa, Consultor, AlocacaoCronograma
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
        
        df = pd.read_excel('attached_assets/linha educacional_1760980473345.xlsx')
        
        registros_adicionados = 0
        for _, row in df.iterrows():
            try:
                # Mapear as colunas corretamente da nova planilha
                registro = LinhaEducacional(
                    linha=safe_str(row.get('LINHA'), 100),
                    tipo_programa=safe_str(row.get('TIPO'), 100),
                    cnpj=safe_str(row.get('CNPJ'), 18),
                    empresa=safe_str(row.get('CLIENTE'), 255),
                    porte=safe_str(row.get('PORTE') if 'PORTE' in row else None, 50),
                    er=safe_str(row.get('ER') if 'ER' in row else None, 100),
                    sigla=safe_str(row.get('SIGLA') if 'SIGLA' in row else None, 50),
                    status_etapa=safe_str(row.get('STATUS COTAÇÃO'), 100),
                    oportunidade=safe_str(row.get('Nº COTAÇÃO'), 100),
                    numero_proposta=safe_str(row.get('Nº PROPOSTA'), 50),
                    ordem_venda=safe_str(row.get('Nº ORDEM DE VENDA'), 50),
                    emissor_proposta=safe_str(row.get('CFP PROPOSTA'), 255),
                    solucao=safe_str(row.get('PROGRAMA'), 500),
                    ch=safe_str(row.get('CH'), 50),
                    consultor=safe_str(row.get('INSTRUTOR 1'), 255),
                    data_inicio=safe_date(row.get('INÍCIO')),
                    data_termino=safe_date(row.get('TÉRMINO')),
                    presencial=safe_str(row.get('MODALIDADE'), 50),
                    gratuidade=None,
                    valor_proposta=safe_numeric(row.get('VALOR')),
                    situacao=safe_str(row.get('SITUAÇÃO'), 100),
                    numero_demanda=None,
                    codigo_rae=safe_str(row.get('CÓDIGO MATERIAL'), 100),
                    observacoes=safe_str(row.get('Obs.')),
                    ano=None,
                    mes=None,
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

def importar_empresas(db: Session):
    """Importa empresas da planilha Excel"""
    try:
        logger.info("Importando empresas...")
        
        # Verifica se já existem empresas
        if db.query(Empresa).first():
            logger.info("Empresas já foram importadas anteriormente. Pulando...")
            return
        
        df = pd.read_excel('attached_assets/empresas_1760980485597.xlsx')
        
        empresas_adicionadas = 0
        for _, row in df.iterrows():
            try:
                cnpj = safe_str(row.get('CNPJ'), 18)
                if not cnpj:
                    continue
                    
                empresa = Empresa(
                    cnpj=cnpj,
                    nome=safe_str(row.get('EMPRESA'), 255) or 'Sem nome',
                    sigla=safe_str(row.get('SIGLA'), 50),
                    porte=safe_str(row.get('PORTE'), 50),
                    er=safe_str(row.get('ER'), 100),
                    carteira=safe_str(row.get('CARTEIRA22'), 100),
                    endereco=safe_str(row.get('ENDEREÇO'), 500),
                    bairro=safe_str(row.get('BAIRRO'), 100),
                    zona=safe_str(row.get('ZONA'), 50),
                    municipio=safe_str(row.get('MUNICÍPIO'), 100),
                    estado=safe_str(row.get('ESTADO'), 2),
                    pais=safe_str(row.get('PAÍS'), 100),
                    area=safe_str(row.get('ÁREA'), 255),
                    cnae_principal=safe_str(row.get('CNAE PRINCIPAL'), 50),
                    descricao_cnae=safe_str(row.get('DESCRIÇÃO CNAE')),
                    tipo_empresa=safe_str(row.get('TIPO DE EMPRESA'), 100),
                    cadastro_atualizacao=safe_date(row.get('CADASTRO / ATUALIZAÇÃO')),
                    num_funcionarios=safe_int(row.get('Nº FUNC.')),
                    observacao=safe_str(row.get('Observação'))
                )
                db.add(empresa)
                empresas_adicionadas += 1
            except Exception as e:
                logger.error(f"Erro ao importar empresa: {e}")
                continue
        
        db.commit()
        logger.info(f"{empresas_adicionadas} empresas importadas com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao importar empresas: {e}")
        db.rollback()

def importar_consultores(db: Session):
    """Extrai e importa consultores do cronograma"""
    try:
        logger.info("Importando consultores...")
        
        # Verifica se já existem consultores
        if db.query(Consultor).first():
            logger.info("Consultores já foram importados anteriormente. Pulando...")
            return
        
        df = pd.read_excel('attached_assets/crnograma principal jef_1760980381606.xlsx')
        
        # Consultores estão na coluna 1 (Unnamed: 1), a partir da linha 11
        consultores_unicos = set()
        for i in range(11, len(df)):
            nome = df.iloc[i, 1]
            if pd.notna(nome) and isinstance(nome, str) and nome != 'CONSULTORES':
                consultores_unicos.add(nome.strip())
        
        consultores_adicionados = 0
        for idx, nome in enumerate(sorted(consultores_unicos), start=1):
            try:
                # Criar email fictício baseado no nome
                email_base = nome.lower().replace(' ', '.').replace('ç', 'c').replace('ã', 'a')
                email = f"{email_base}@empresa.com"
                nif = f"NIF{idx:04d}"
                
                consultor = Consultor(
                    nome=nome,
                    email=email,
                    nif=nif,
                    cargo="Consultor",
                    ativo=True
                )
                db.add(consultor)
                consultores_adicionados += 1
            except Exception as e:
                logger.error(f"Erro ao importar consultor {nome}: {e}")
                continue
        
        db.commit()
        logger.info(f"{consultores_adicionados} consultores importados com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao importar consultores: {e}")
        db.rollback()

def importar_alocacoes_cronograma(db: Session):
    """Importa alocações do cronograma"""
    try:
        logger.info("Importando alocações do cronograma...")
        
        # Verifica se já existem alocações
        if db.query(AlocacaoCronograma).first():
            logger.info("Alocações já foram importadas anteriormente. Pulando...")
            return
        
        df = pd.read_excel('attached_assets/crnograma principal jef_1760980381606.xlsx')
        
        # Criar mapeamento de consultores por nome
        consultores_map = {}
        consultores = db.query(Consultor).all()
        for c in consultores:
            consultores_map[c.nome] = c.id
        
        alocacoes_adicionadas = 0
        
        # Processar linhas a partir da linha 11
        # Cada consultor tem 2 linhas: uma para manhã (M) e outra para tarde (T)
        for i in range(11, len(df), 2):
            nome_consultor = df.iloc[i, 1]
            if pd.isna(nome_consultor) or not isinstance(nome_consultor, str):
                continue
                
            nome_consultor = nome_consultor.strip()
            consultor_id = consultores_map.get(nome_consultor)
            
            if not consultor_id:
                logger.warning(f"Consultor não encontrado: {nome_consultor}")
                continue
            
            # Processar colunas de datas (a partir da coluna 4)
            for col_idx in range(4, len(df.columns)):
                # Pegar a data do header (linha 2)
                data = df.iloc[2, col_idx]
                if pd.isna(data):
                    continue
                    
                try:
                    data_obj = pd.to_datetime(data).date()
                except:
                    continue
                
                # Manhã (linha i, coluna col_idx)
                codigo_manha = df.iloc[i, col_idx]
                if pd.notna(codigo_manha) and str(codigo_manha).strip():
                    try:
                        alocacao = AlocacaoCronograma(
                            consultor_id=consultor_id,
                            data=data_obj,
                            periodo='M',
                            codigo_projeto=safe_str(codigo_manha, 100),
                            nif=None
                        )
                        db.add(alocacao)
                        alocacoes_adicionadas += 1
                    except Exception as e:
                        logger.error(f"Erro ao adicionar alocação manhã: {e}")
                
                # Tarde (linha i+1, coluna col_idx) - se existir
                if i + 1 < len(df):
                    codigo_tarde = df.iloc[i + 1, col_idx]
                    if pd.notna(codigo_tarde) and str(codigo_tarde).strip():
                        try:
                            alocacao = AlocacaoCronograma(
                                consultor_id=consultor_id,
                                data=data_obj,
                                periodo='T',
                                codigo_projeto=safe_str(codigo_tarde, 100),
                                nif=None
                            )
                            db.add(alocacao)
                            alocacoes_adicionadas += 1
                        except Exception as e:
                            logger.error(f"Erro ao adicionar alocação tarde: {e}")
        
        db.commit()
        logger.info(f"{alocacoes_adicionadas} alocações de cronograma importadas com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao importar alocações: {e}")
        db.rollback()

def seed_all_data():
    """Executa todas as importações de dados iniciais"""
    db = SessionLocal()
    try:
        logger.info("Iniciando importação de dados iniciais...")
        importar_contatos(db)
        importar_empresas(db)
        importar_consultores(db)
        importar_linha_tecnologia(db)
        importar_linha_educacional(db)
        importar_alocacoes_cronograma(db)
        logger.info("Importação de dados iniciais concluída!")
    except Exception as e:
        logger.error(f"Erro durante importação: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_all_data()
