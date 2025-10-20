import logging
import pandas as pd
from datetime import datetime
from decimal import Decimal
from app.database import SessionLocal
from app.models.models import LinhaTecnologia, LinhaEducacional
from sqlalchemy import delete

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_date(value):
    """Converte valor para data"""
    if pd.isna(value) or value == '' or value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    try:
        return pd.to_datetime(value, dayfirst=True).date()
    except:
        return None

def parse_decimal(value):
    """Converte valor para decimal"""
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        return Decimal(str(value).replace(',', '.'))
    except:
        return None

def parse_int(value):
    """Converte valor para inteiro"""
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        return int(float(value))
    except:
        return None

def parse_string(value):
    """Converte valor para string"""
    if pd.isna(value) or value == '' or value is None:
        return None
    return str(value).strip()

def importar_linha_tecnologia(arquivo_path):
    """Importa dados da planilha de linha tecnologia"""
    logger.info("Importando linha tecnologia...")
    
    df = pd.read_excel(arquivo_path)
    logger.info(f"Planilha carregada: {len(df)} registros")
    
    db = SessionLocal()
    try:
        # Remove dados anteriores não iniciais
        db.execute(delete(LinhaTecnologia).where(LinhaTecnologia.dados_iniciais == False))
        db.commit()
        
        count = 0
        for _, row in df.iterrows():
            try:
                registro = LinhaTecnologia(
                    linha=parse_string(row.get('LINHA')),
                    tipo_programa=parse_string(row.get('TIPO DE PROGRAMA')),
                    cnpj=parse_string(row.get('CNPJ')),
                    empresa=parse_string(row.get('EMPRESA')),
                    porte=parse_string(row.get('PORTE')),
                    er=parse_string(row.get('ER')),
                    sigla=parse_string(row.get('SIGLA')),
                    t3=parse_string(row.get('T3')),
                    status_etapa=parse_string(row.get('STATUS DA ETAPA')),
                    oportunidade=parse_string(row.get('OPORTUNIDADE')),
                    numero_proposta=parse_string(row.get('Nº PROPOSTA')),
                    ordem_venda=parse_string(row.get('ORDEM DE VENDA')),
                    emissor_proposta=parse_string(row.get('EMISSOR DA PROPOSTA')),
                    cfp_parceiro=parse_string(row.get('CFP PARCEIRO')),
                    solucao=parse_string(row.get('SOLUÇÃO')),
                    ch=parse_string(row.get('CH')),
                    consultor=parse_string(row.get('CONSULTOR')),
                    dados_socios_informados=parse_string(row.get('DADOS SOCIOS INFORMADOS')),
                    contrato_enviado_empresa=parse_string(row.get('S/N            ')),
                    contrato_assinado_empresa=parse_string(row.get('S/N           ')),
                    data_contrato_assinado_senai=parse_date(row.get('DATA DO CONTRATO ASSINADO SENAI')),
                    data_cadastro_sgt=parse_date(row.get('DATA CADASTRO SGT')),
                    data_upload_sgt=parse_date(row.get('DATA UPLOAD SGT')),
                    data_aceite_sgt=parse_date(row.get('DATA ACEITE SGT')),
                    data_envio_relatorio_t1=parse_date(row.get('DATA DO ENVIO DO RELATÓRIO T1')),
                    data_cobranca_empresa=parse_date(row.get('DATA DE COBRANÇA DA EMPRESA')),
                    cadastro_plataforma_ok=parse_string(row.get('CADASTRO PLATAFORMA PRODUTIVIDADE OK?')),
                    data_cobranca_sebrae=parse_date(row.get('DATA COBRANÇA SEBRAE ')),
                    contrato_sebrae_enviado=parse_string(row.get('Contrato SEBRAE Enviado?')),
                    data_resposta_sebrae=parse_date(row.get('DATA RESPOSTA SEBRAE')),
                    requisicao_grm=parse_string(row.get('REQUISIÇÃO GRM')),
                    data_inicio=parse_date(row.get('DATA INÍCIO')),
                    data_termino=parse_date(row.get('DATA TÉRMINO')),
                    reuniao_kickoff_confirmada=parse_string(row.get('REUNIÃO KICK-OFF CONFIRMADA')),
                    reuniao_final_agendada=parse_string(row.get('REUNIÃO FINAL AGENDADA')),
                    presencial=parse_string(row.get('PRESENCIAL')),
                    gratuidade=parse_string(row.get('GRATUIDADE?')),
                    valor_proposta=parse_decimal(row.get('VALOR DA PROPOSTA')),
                    situacao=parse_string(row.get('SITUAÇÃO')),
                    numero_demanda=parse_string(row.get('Nº DEMANDA ou                       Nº ID')),
                    codigo_rae=parse_string(row.get('CÓDIGO RAE ')),
                    mov_1_1_57=parse_string(row.get('MOV. 1.1.57')),
                    relatorio_priorizacao_enviado=parse_string(row.get('RELATÓRIO DE PRIORIZAÇÃO ENVIADO')),
                    relatorio_smart_factory=parse_string(row.get('RELATÓRIO SMART FACTORY')),
                    relatorio_final_enviado=parse_string(row.get('RELATÓRIO FINAL ENVIADO')),
                    relatorio_educacional_enviado=parse_string(row.get('RELATÓRIO EDUCACIONAL ENVIADO')),
                    data_conclusao_sgt=parse_date(row.get('DATA DE CONCLUSÃO SGT')),
                    envio_auditoria=parse_string(row.get('ENVIO AUDITORIA (ER/GIT)')),
                    retorno_auditoria=parse_string(row.get('RETORNO AUDITORIA')),
                    data_prestacao_contas=parse_date(row.get('DATA PRESTAÇÃO DE CONTAS')),
                    data_pesquisa_satisfacao=parse_date(row.get('DATA PESQUISA DE SATISFAÇÃO RESPONDIDA')),
                    observacoes=parse_string(row.get('OBSERVAÇÕES')),
                    especifico_saldo=parse_string(row.get('ESPECÍFICO (SALDO SGSET AGOSTO)')),
                    passou_ali_2023=parse_string(row.get('Passou no ALI em 2023 ? ')),
                    ali_2024_convidar=parse_string(row.get('ALI 2024 - Convidar ?')),
                    t3_solucao_1_2024=parse_string(row.get('T 3 (1ª  Solução Proposta para 2024 )')),
                    t3_solucao_2_2024=parse_string(row.get('T 3 (2ª  Solução Proposta para 2024 )')),
                    aceitou=parse_string(row.get('ACEITOU ?')),
                    qual_3_etapa=parse_string(row.get('QUAL ? (           3ª ETAPA)')),
                    t4_proposto_2024=parse_string(row.get('T4 Proposto para 2024 ')),
                    aceitou_2=parse_string(row.get('ACEITOU ?2')),
                    follow_2024=parse_string(row.get('FOLLOW 2024')),
                    continuidade=parse_string(row.get('CONTINUIDADE')),
                    etapa_5_ou_6=parse_string(row.get('5ª ou 6ª etapa')),
                    fez_efici_energ=parse_string(row.get('FEZ EFICI ENERG ?')),
                    obs2=parse_string(row.get('OBS2')),
                    ano=parse_int(row.get('ANO')),
                    mes=parse_string(row.get('MÊS')),
                    inu=parse_string(row.get('INU')),
                    hubspot=parse_string(row.get('HUBSPOT')),
                    nova_proposta=parse_string(row.get('NOVA PROPOSTA')),
                    valor_sap=parse_decimal(row.get('VALOR SAP')),
                    dados_iniciais=False
                )
                db.add(registro)
                count += 1
                
                if count % 100 == 0:
                    logger.info(f"{count} registros importados...")
                    
            except Exception as e:
                logger.error(f"Erro ao importar registro: {e}")
                continue
        
        db.commit()
        logger.info(f"✅ {count} registros de linha tecnologia importados com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao importar linha tecnologia: {e}")
        db.rollback()
    finally:
        db.close()

def importar_linha_educacional(arquivo_path):
    """Importa dados da planilha de linha educacional"""
    logger.info("Importando linha educacional...")
    
    df = pd.read_excel(arquivo_path)
    logger.info(f"Planilha carregada: {len(df)} registros")
    
    db = SessionLocal()
    try:
        # Remove dados anteriores não iniciais
        db.execute(delete(LinhaEducacional).where(LinhaEducacional.dados_iniciais == False))
        db.commit()
        
        count = 0
        for _, row in df.iterrows():
            try:
                registro = LinhaEducacional(
                    linha=parse_string(row.get('LINHA')),
                    cliente=parse_string(row.get('CLIENTE')),
                    cnpj=parse_string(row.get('CNPJ')),
                    estabelecimento=parse_string(row.get('ESTABELECIMENTO')),
                    numero_cotacao=parse_string(row.get('Nº COTAÇÃO')),
                    data_envio_cotacao=parse_date(row.get('DT ENVIO COTAÇÃO')),
                    data_follow=parse_date(row.get('DATA\nFOLLOW')),
                    status_cotacao=parse_string(row.get('STATUS COTAÇÃO')),
                    motivo=parse_string(row.get('MOTIVO')),
                    programa=parse_string(row.get('PROGRAMA')),
                    tipo=parse_string(row.get('TIPO')),
                    cfp_proposta=parse_string(row.get('CFP PROPOSTA')),
                    cfp_parceiro=parse_string(row.get('CFP PARCEIRO')),
                    modalidade=parse_string(row.get('MODALIDADE')),
                    ch=parse_string(row.get('CH')),
                    turno=parse_string(row.get('TURNO')),
                    data_inicio=parse_date(row.get('INÍCIO')),
                    data_termino=parse_date(row.get('TÉRMINO')),
                    numero_proposta=parse_string(row.get('Nº PROPOSTA')),
                    numero_ordem_venda=parse_string(row.get('Nº ORDEM DE VENDA')),
                    valor=parse_decimal(row.get('VALOR')),
                    situacao=parse_string(row.get('SITUAÇÃO')),
                    status_proposta=parse_string(row.get('STATUS DA PROPOSTA')),
                    receita_espelhada=parse_decimal(row.get('RECEITA ESPELHADA')),
                    solicitacao_mdi=parse_date(row.get('SOLICITAÇÃO DE MDI')),
                    follow_mdi=parse_date(row.get('FOLLOW MDI')),
                    recebimento_mdi=parse_date(row.get('RECEBIMENTO MDI')),
                    turma=parse_string(row.get('TURMA')),
                    instrutor_1=parse_string(row.get('INSTRUTOR 1')),
                    ch_c1=parse_string(row.get('CH C1')),
                    instrutor_2=parse_string(row.get('INSTRUTOR 2')),
                    ch_c2=parse_string(row.get('CH C2')),
                    status_servico=parse_string(row.get('STATUS DO SERVIÇO')),
                    emissao_certificados=parse_date(row.get('EMISSÃO CERTIFICADOS')),
                    assinatura_certificados=parse_date(row.get('ASSINATURA CERTIFICADOS')),
                    data_entrega_certificados=parse_date(row.get('DATA ENTREGA CERTIFICADOS')),
                    pesquisa_satisfacao=parse_string(row.get('PESQUISA DE SATISFAÇÃO')),
                    codigo_material=parse_string(row.get('CÓDIGO MATERIAL')),
                    quantidade_estoque_atual=parse_int(row.get('QUANTIDADE ESTOQUE ATUAL')),
                    observacoes=parse_string(row.get('Obs.')),
                    ano=parse_int(datetime.now().year),
                    mes=parse_string(datetime.now().strftime('%B')),
                    dados_iniciais=False
                )
                db.add(registro)
                count += 1
                
                if count % 50 == 0:
                    logger.info(f"{count} registros importados...")
                    
            except Exception as e:
                logger.error(f"Erro ao importar registro: {e}")
                continue
        
        db.commit()
        logger.info(f"✅ {count} registros de linha educacional importados com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao importar linha educacional: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python import_novas_planilhas.py <arquivo_tecnologia.xlsx> <arquivo_educacional.xlsx>")
        sys.exit(1)
    
    importar_linha_tecnologia(sys.argv[1])
    importar_linha_educacional(sys.argv[2])
    logger.info("✅ Importação concluída!")
