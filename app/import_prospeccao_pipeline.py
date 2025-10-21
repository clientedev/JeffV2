"""
Script para importar dados das planilhas de Linha Tecnologia e Linha Educacional
para as tabelas de Prospecção e Pipeline Kanban
"""
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.models import (
    CompanyPipeline, Stage, Prospeccao, LinhaTecnologia, LinhaEducacional,
    Empresa
)

def safe_str(value, max_length=None):
    """Converte valor para string de forma segura"""
    if pd.isna(value) or value is None or value == '':
        return None
    result = str(value).strip()
    if max_length and len(result) > max_length:
        result = result[:max_length]
    return result if result else None

def safe_date(value):
    """Converte valor para data de forma segura"""
    if pd.isna(value) or value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    try:
        return pd.to_datetime(value, dayfirst=True).date()
    except:
        return None

def safe_decimal(value):
    """Converte valor para decimal de forma segura"""
    if pd.isna(value) or value is None or value == '':
        return None
    try:
        return float(str(value).replace(',', '.').replace('R$', '').replace(' ', '').strip())
    except:
        return None

def criar_stages_padrao(db: Session):
    """Cria os stages padrão do pipeline se não existirem"""
    stages_padrao = [
        {"nome": "Prospecção", "ordem": 1, "cor": "#3b82f6"},
        {"nome": "Proposta Enviada", "ordem": 2, "cor": "#8b5cf6"},
        {"nome": "Negociação", "ordem": 3, "cor": "#f59e0b"},
        {"nome": "Contrato Assinado", "ordem": 4, "cor": "#10b981"},
        {"nome": "Em Execução", "ordem": 5, "cor": "#06b6d4"},
        {"nome": "Concluído", "ordem": 6, "cor": "#22c55e"},
        {"nome": "Perdido", "ordem": 7, "cor": "#ef4444"},
    ]
    
    for stage_data in stages_padrao:
        existing = db.query(Stage).filter(Stage.nome == stage_data["nome"]).first()
        if not existing:
            stage = Stage(**stage_data)
            db.add(stage)
    
    db.commit()
    print(f"✅ Stages criados/verificados")

def mapear_situacao_para_stage(situacao: str) -> str:
    """Mapeia a situação da planilha para um stage do pipeline"""
    if not situacao:
        return "Prospecção"
    
    situacao_lower = situacao.lower().strip()
    
    # Mapeamento de situações
    if any(x in situacao_lower for x in ['concluído', 'finalizado', 'entregue']):
        return "Concluído"
    elif any(x in situacao_lower for x in ['execução', 'andamento', 'em curso']):
        return "Em Execução"
    elif any(x in situacao_lower for x in ['assinado', 'contratado']):
        return "Contrato Assinado"
    elif any(x in situacao_lower for x in ['negociação', 'negociando']):
        return "Negociação"
    elif any(x in situacao_lower for x in ['proposta', 'enviada', 'aguardando']):
        return "Proposta Enviada"
    elif any(x in situacao_lower for x in ['perdido', 'cancelado', 'recusado']):
        return "Perdido"
    else:
        return "Prospecção"

def importar_para_pipeline(db: Session):
    """Importa dados das linhas tecnologia e educacional para o pipeline"""
    
    print("\n" + "="*80)
    print("📊 IMPORTAÇÃO PARA PIPELINE KANBAN")
    print("="*80 + "\n")
    
    # Garantir que stages existem
    criar_stages_padrao(db)
    
    # Carregar stages
    stages = {stage.nome: stage for stage in db.query(Stage).all()}
    
    # Importar Linha Tecnologia
    print("📁 Lendo arquivo: linha tecnologia_1761065276454.xlsx")
    df_tech = pd.read_excel('attached_assets/linha tecnologia_1761065276454.xlsx')
    
    tech_count = 0
    tech_skip = 0
    
    for idx, row in df_tech.iterrows():
        cnpj = safe_str(row.get('CNPJ'), 18)
        empresa = safe_str(row.get('EMPRESA'), 255)
        
        if not cnpj or not empresa:
            tech_skip += 1
            continue
        
        # Determinar stage baseado na situação
        situacao = safe_str(row.get('SITUAÇÃO'))
        stage_nome = mapear_situacao_para_stage(situacao)
        stage = stages.get(stage_nome)
        
        if not stage:
            tech_skip += 1
            continue
        
        # Verificar se já existe
        existing = db.query(CompanyPipeline).filter(
            CompanyPipeline.cnpj == cnpj,
            CompanyPipeline.linha == "TECNOLOGIA"
        ).first()
        
        if existing:
            tech_skip += 1
            continue
        
        # Criar novo registro no pipeline
        pipeline_entry = CompanyPipeline(
            cnpj=cnpj,
            nome_empresa=empresa,
            linha="TECNOLOGIA",
            tipo_programa=safe_str(row.get('TIPO DE PROGRAMA'), 100),
            porte=safe_str(row.get('PORTE'), 50),
            er_regiao=safe_str(row.get('ER'), 100),
            consultor_responsavel=safe_str(row.get('CONSULTOR'), 255),
            stage_id=stage.id,
            numero_proposta=safe_str(row.get('Nº PROPOSTA'), 50),
            valor_proposta=safe_decimal(row.get('VALOR DA PROPOSTA')),
            observacoes=safe_str(row.get('OBSERVAÇÕES'))
        )
        
        db.add(pipeline_entry)
        tech_count += 1
        
        if tech_count % 100 == 0:
            db.commit()
            print(f"   ✓ {tech_count} registros de tecnologia importados...")
    
    db.commit()
    print(f"\n✅ Linha Tecnologia: {tech_count} registros importados, {tech_skip} ignorados")
    
    # Importar Linha Educacional
    print("\n📁 Lendo arquivo: linha educacional_1761065289005.xlsx")
    df_edu = pd.read_excel('attached_assets/linha educacional_1761065289005.xlsx')
    
    edu_count = 0
    edu_skip = 0
    
    for idx, row in df_edu.iterrows():
        cnpj = safe_str(row.get('CNPJ'), 18)
        empresa = safe_str(row.get('CLIENTE'), 255)
        
        if not cnpj or not empresa:
            edu_skip += 1
            continue
        
        # Determinar stage baseado na situação
        situacao = safe_str(row.get('SITUAÇÃO'))
        stage_nome = mapear_situacao_para_stage(situacao)
        stage = stages.get(stage_nome)
        
        if not stage:
            edu_skip += 1
            continue
        
        # Verificar se já existe
        existing = db.query(CompanyPipeline).filter(
            CompanyPipeline.cnpj == cnpj,
            CompanyPipeline.linha == "EDUCACIONAL"
        ).first()
        
        if existing:
            edu_skip += 1
            continue
        
        # Criar novo registro no pipeline
        pipeline_entry = CompanyPipeline(
            cnpj=cnpj,
            nome_empresa=empresa,
            linha="EDUCACIONAL",
            tipo_programa=safe_str(row.get('PROGRAMA'), 100),
            porte=None,  # Não tem na planilha educacional
            er_regiao=None,
            consultor_responsavel=None,
            stage_id=stage.id,
            numero_proposta=safe_str(row.get('Nº PROPOSTA'), 50),
            valor_proposta=safe_decimal(row.get('VALOR')),
            observacoes=safe_str(row.get('Obs.'))
        )
        
        db.add(pipeline_entry)
        edu_count += 1
        
        if edu_count % 50 == 0:
            db.commit()
            print(f"   ✓ {edu_count} registros educacionais importados...")
    
    db.commit()
    print(f"\n✅ Linha Educacional: {edu_count} registros importados, {edu_skip} ignorados")
    
    print("\n" + "="*80)
    print(f"✅ IMPORTAÇÃO CONCLUÍDA: {tech_count + edu_count} registros no pipeline")
    print("="*80 + "\n")

def importar_para_prospeccao(db: Session):
    """Importa empresas das planilhas que ainda não têm proposta para prospecção"""
    
    print("\n" + "="*80)
    print("📊 IMPORTAÇÃO PARA PROSPECÇÃO")
    print("="*80 + "\n")
    
    # Importar da Linha Tecnologia
    print("📁 Processando linha tecnologia...")
    df_tech = pd.read_excel('attached_assets/linha tecnologia_1761065276454.xlsx')
    
    prosp_count = 0
    prosp_skip = 0
    
    for idx, row in df_tech.iterrows():
        empresa = safe_str(row.get('EMPRESA'), 255)
        cnpj = safe_str(row.get('CNPJ'), 18)
        
        if not empresa:
            prosp_skip += 1
            continue
        
        # Verificar se já existe na prospecção
        existing = db.query(Prospeccao).filter(
            Prospeccao.empresa == empresa
        ).first()
        
        if existing:
            prosp_skip += 1
            continue
        
        # Criar registro de prospecção
        prospeccao = Prospeccao(
            empresa=empresa,
            cnpj=cnpj,
            porte=safe_str(row.get('PORTE'), 50),
            er=safe_str(row.get('ER'), 100),
            tipo_programa=safe_str(row.get('TIPO DE PROGRAMA'), 100),
            status='Novo',
            responsavel=safe_str(row.get('CONSULTOR'), 255),
            oportunidade=safe_str(row.get('OPORTUNIDADE'), 255),
            observacoes=safe_str(row.get('OBSERVAÇÕES'))
        )
        
        db.add(prospeccao)
        prosp_count += 1
        
        if prosp_count % 100 == 0:
            db.commit()
            print(f"   ✓ {prosp_count} prospecções criadas...")
    
    db.commit()
    print(f"\n✅ {prosp_count} empresas adicionadas à prospecção, {prosp_skip} ignoradas")
    
    print("\n" + "="*80)
    print(f"✅ IMPORTAÇÃO DE PROSPECÇÃO CONCLUÍDA")
    print("="*80 + "\n")

def main():
    """Função principal de importação"""
    db = SessionLocal()
    
    try:
        print("\n🚀 Iniciando importação de dados para Prospecção e Pipeline Kanban\n")
        
        # Importar para pipeline
        importar_para_pipeline(db)
        
        # Importar para prospecção
        importar_para_prospeccao(db)
        
        print("\n🎉 IMPORTAÇÃO COMPLETA!")
        
    except Exception as e:
        print(f"\n❌ Erro durante importação: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
