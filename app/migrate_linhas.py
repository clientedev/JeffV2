import logging
from app.database import engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_linha_tecnologia():
    """Adiciona novas colunas à tabela linha_tecnologia"""
    
    alteracoes = [
        "ALTER TABLE linha_tecnologia ALTER COLUMN solucao TYPE TEXT",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS dados_socios_informados VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS contrato_enviado_empresa VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS contrato_assinado_empresa VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS data_contrato_assinado_senai DATE",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS data_cadastro_sgt DATE",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS data_upload_sgt DATE",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS data_aceite_sgt DATE",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS data_envio_relatorio_t1 DATE",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS data_cobranca_empresa DATE",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS cadastro_plataforma_ok VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS data_cobranca_sebrae DATE",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS contrato_sebrae_enviado VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS data_resposta_sebrae DATE",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS requisicao_grm VARCHAR(100)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS reuniao_kickoff_confirmada VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS reuniao_final_agendada VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS mov_1_1_57 VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS relatorio_priorizacao_enviado VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS relatorio_smart_factory VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS relatorio_final_enviado VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS relatorio_educacional_enviado VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS data_conclusao_sgt DATE",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS envio_auditoria VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS retorno_auditoria VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS data_prestacao_contas DATE",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS data_pesquisa_satisfacao DATE",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS especifico_saldo VARCHAR(255)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS passou_ali_2023 VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS ali_2024_convidar VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS t3_solucao_1_2024 TEXT",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS t3_solucao_2_2024 TEXT",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS aceitou VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS qual_3_etapa TEXT",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS t4_proposto_2024 TEXT",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS aceitou_2 VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS follow_2024 VARCHAR(255)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS continuidade VARCHAR(255)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS etapa_5_ou_6 VARCHAR(255)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS fez_efici_energ VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS obs2 TEXT",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS inu VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS hubspot VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS nova_proposta VARCHAR(50)",
        "ALTER TABLE linha_tecnologia ADD COLUMN IF NOT EXISTS valor_sap NUMERIC(12, 2)"
    ]
    
    with engine.connect() as conn:
        for sql in alteracoes:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                logger.warning(f"Aviso ao executar {sql[:50]}... : {e}")
    
    logger.info("✅ Migração de linha_tecnologia concluída")

def migrate_linha_educacional():
    """Adiciona novas colunas à tabela linha_educacional"""
    
    alteracoes = [
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS tipo_programa CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS empresa CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS porte CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS er CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS sigla CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS status_etapa CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS oportunidade CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS ordem_venda CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS emissor_proposta CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS solucao CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS consultor CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS presencial CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS gratuidade CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS valor_proposta CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS numero_demanda CASCADE",
        "ALTER TABLE linha_educacional DROP COLUMN IF EXISTS codigo_rae CASCADE",
        
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS cliente VARCHAR(255)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS estabelecimento VARCHAR(255)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS numero_cotacao VARCHAR(50)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS data_envio_cotacao DATE",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS data_follow DATE",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS status_cotacao VARCHAR(100)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS motivo VARCHAR(255)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS programa VARCHAR(255)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS tipo VARCHAR(100)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS cfp_proposta VARCHAR(100)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS cfp_parceiro VARCHAR(100)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS modalidade VARCHAR(100)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS turno VARCHAR(50)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS numero_ordem_venda VARCHAR(50)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS valor NUMERIC(12, 2)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS status_proposta VARCHAR(100)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS receita_espelhada NUMERIC(12, 2)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS solicitacao_mdi DATE",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS follow_mdi DATE",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS recebimento_mdi DATE",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS turma VARCHAR(100)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS instrutor_1 VARCHAR(255)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS ch_c1 VARCHAR(50)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS instrutor_2 VARCHAR(255)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS ch_c2 VARCHAR(50)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS status_servico VARCHAR(100)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS emissao_certificados DATE",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS assinatura_certificados DATE",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS data_entrega_certificados DATE",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS pesquisa_satisfacao VARCHAR(10)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS codigo_material VARCHAR(100)",
        "ALTER TABLE linha_educacional ADD COLUMN IF NOT EXISTS quantidade_estoque_atual INTEGER"
    ]
    
    with engine.connect() as conn:
        for sql in alteracoes:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                logger.warning(f"Aviso ao executar {sql[:50]}... : {e}")
    
    logger.info("✅ Migração de linha_educacional concluída")

def run_migrations():
    """Executa todas as migrações"""
    logger.info("🔄 Iniciando migrações...")
    migrate_linha_tecnologia()
    migrate_linha_educacional()
    logger.info("✅ Todas as migrações concluídas!")

if __name__ == "__main__":
    run_migrations()
