import pandas as pd
from app.database import get_db
from app.models.models import Stage, CompanyPipeline, CompanyStageHistory
from datetime import datetime
import sys

def criar_stages():
    """Cria as etapas do pipeline Kanban"""
    db = next(get_db())
    
    try:
        stages_data = [
            {"nome": "Prospecção", "descricao": "Empresas em prospecção inicial", "ordem": 1, "cor": "#94a3b8", "ativo": True},
            {"nome": "Proposta Enviada", "descricao": "Proposta comercial enviada", "ordem": 2, "cor": "#3b82f6", "ativo": True},
            {"nome": "Negociação", "descricao": "Em negociação com o cliente", "ordem": 3, "cor": "#f59e0b", "ativo": True},
            {"nome": "Contrato Assinado", "descricao": "Contrato assinado, aguardando início", "ordem": 4, "cor": "#8b5cf6", "ativo": True},
            {"nome": "Em Andamento", "descricao": "Programa em execução", "ordem": 5, "cor": "#10b981", "ativo": True},
            {"nome": "Concluído", "descricao": "Programa finalizado", "ordem": 6, "cor": "#06b6d4", "ativo": True},
            {"nome": "Cancelado", "descricao": "Não convertido ou cancelado", "ordem": 7, "cor": "#ef4444", "ativo": True},
        ]
        
        for stage_data in stages_data:
            existing = db.query(Stage).filter(Stage.nome == stage_data["nome"]).first()
            if not existing:
                stage = Stage(**stage_data)
                db.add(stage)
                print(f"✓ Stage criado: {stage_data['nome']}")
            else:
                print(f"⚠ Stage já existe: {stage_data['nome']}")
        
        db.commit()
        print(f"\n✓ Total de stages: {db.query(Stage).count()}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar stages: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def mapear_status_para_stage(status_etapa, situacao):
    """Mapeia o status da etapa para o stage correspondente"""
    if not status_etapa and not situacao:
        return "Prospecção"
    
    status_lower = str(status_etapa).lower() if status_etapa else ""
    situacao_lower = str(situacao).lower() if situacao else ""
    
    if "conclu" in status_lower or "finaliz" in status_lower or "encerr" in status_lower:
        return "Concluído"
    elif "cancel" in status_lower or "cancel" in situacao_lower or "não convert" in situacao_lower:
        return "Cancelado"
    elif "andamento" in status_lower or "execu" in status_lower or "em anda" in situacao_lower:
        return "Em Andamento"
    elif "contrato" in status_lower or "assinado" in status_lower:
        return "Contrato Assinado"
    elif "negoci" in status_lower or "aguard" in status_lower:
        return "Negociação"
    elif "proposta" in status_lower or "enviado" in status_lower:
        return "Proposta Enviada"
    else:
        return "Prospecção"

def importar_linha_tecnologia():
    """Importa dados da linha tecnologia para o pipeline"""
    db = next(get_db())
    
    try:
        df = pd.read_excel('attached_assets/linha tecnologia_1761007108365.xlsx')
        
        print(f"\n📊 Importando {len(df)} registros da Linha Tecnologia...")
        
        stages_map = {s.nome: s.id for s in db.query(Stage).all()}
        
        importados = 0
        erros = 0
        
        for idx, row in df.iterrows():
            try:
                cnpj = str(row.get('CNPJ', '')).strip() if pd.notna(row.get('CNPJ')) else None
                empresa = str(row.get('EMPRESA', '')).strip() if pd.notna(row.get('EMPRESA')) else None
                
                if not cnpj or not empresa or cnpj in ['nan', '', 'None']:
                    continue
                
                existing = db.query(CompanyPipeline).filter(
                    CompanyPipeline.cnpj == cnpj,
                    CompanyPipeline.linha == "TECNOLOGIA"
                ).first()
                
                if existing:
                    continue
                
                status_etapa = row.get('STATUS DA ETAPA')
                situacao = row.get('SITUAÇÃO')
                stage_nome = mapear_status_para_stage(status_etapa, situacao)
                stage_id = stages_map.get(stage_nome, stages_map["Prospecção"])
                
                valor_str = row.get('VALOR DA PROPOSTA')
                valor = None
                if pd.notna(valor_str):
                    try:
                        valor = float(str(valor_str).replace(',', '.'))
                    except:
                        pass
                
                company = CompanyPipeline(
                    cnpj=cnpj,
                    nome_empresa=empresa,
                    linha="TECNOLOGIA",
                    tipo_programa=str(row.get('TIPO DE PROGRAMA', '')).strip() if pd.notna(row.get('TIPO DE PROGRAMA')) else None,
                    porte=str(row.get('PORTE', '')).strip() if pd.notna(row.get('PORTE')) else None,
                    er_regiao=str(row.get('ER', '')).strip() if pd.notna(row.get('ER')) else None,
                    consultor_responsavel=str(row.get('CONSULTOR', '')).strip() if pd.notna(row.get('CONSULTOR')) else None,
                    stage_id=stage_id,
                    numero_proposta=str(row.get('Nº PROPOSTA', '')).strip() if pd.notna(row.get('Nº PROPOSTA')) else None,
                    valor_proposta=valor,
                    observacoes=None,
                    data_cadastro=datetime.utcnow(),
                    ultima_atualizacao=datetime.utcnow()
                )
                
                db.add(company)
                db.flush()
                
                history = CompanyStageHistory(
                    company_pipeline_id=company.id,
                    stage_id=stage_id,
                    data_entrada=datetime.utcnow(),
                    usuario_id=None,
                    observacao="Importação automática"
                )
                db.add(history)
                
                importados += 1
                
                if importados % 100 == 0:
                    print(f"  Importados: {importados} registros...")
                    db.commit()
                    
            except Exception as e:
                erros += 1
                print(f"  ⚠ Erro na linha {idx}: {e}")
                continue
        
        db.commit()
        print(f"\n✓ Linha Tecnologia: {importados} empresas importadas, {erros} erros")
        return importados
        
    except Exception as e:
        print(f"❌ Erro ao importar linha tecnologia: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def importar_linha_educacional():
    """Importa dados da linha educacional para o pipeline"""
    db = next(get_db())
    
    try:
        df = pd.read_excel('attached_assets/linha educacional_1761007108365.xlsx')
        
        print(f"\n📊 Importando {len(df)} registros da Linha Educacional...")
        
        stages_map = {s.nome: s.id for s in db.query(Stage).all()}
        
        importados = 0
        erros = 0
        
        for idx, row in df.iterrows():
            try:
                cnpj = str(row.get('CNPJ', '')).strip() if pd.notna(row.get('CNPJ')) else None
                empresa = str(row.get('CLIENTE', '')).strip() if pd.notna(row.get('CLIENTE')) else None
                
                if not cnpj or not empresa or cnpj in ['nan', '', 'None']:
                    continue
                
                existing = db.query(CompanyPipeline).filter(
                    CompanyPipeline.cnpj == cnpj,
                    CompanyPipeline.linha == "EDUCACIONAL"
                ).first()
                
                if existing:
                    continue
                
                situacao = row.get('SITUAÇÃO')
                status_proposta = row.get('STATUS DA PROPOSTA')
                stage_nome = mapear_status_para_stage(status_proposta, situacao)
                stage_id = stages_map.get(stage_nome, stages_map["Prospecção"])
                
                valor_str = row.get('VALOR')
                valor = None
                if pd.notna(valor_str):
                    try:
                        valor = float(str(valor_str).replace(',', '.'))
                    except:
                        pass
                
                company = CompanyPipeline(
                    cnpj=cnpj,
                    nome_empresa=empresa,
                    linha="EDUCACIONAL",
                    tipo_programa=str(row.get('PROGRAMA', '')).strip() if pd.notna(row.get('PROGRAMA')) else None,
                    porte=None,
                    er_regiao=None,
                    consultor_responsavel=None,
                    stage_id=stage_id,
                    numero_proposta=str(row.get('Nº PROPOSTA', '')).strip() if pd.notna(row.get('Nº PROPOSTA')) else None,
                    valor_proposta=valor,
                    observacoes=None,
                    data_cadastro=datetime.utcnow(),
                    ultima_atualizacao=datetime.utcnow()
                )
                
                db.add(company)
                db.flush()
                
                history = CompanyStageHistory(
                    company_pipeline_id=company.id,
                    stage_id=stage_id,
                    data_entrada=datetime.utcnow(),
                    usuario_id=None,
                    observacao="Importação automática"
                )
                db.add(history)
                
                importados += 1
                
                if importados % 50 == 0:
                    print(f"  Importados: {importados} registros...")
                    db.commit()
                    
            except Exception as e:
                erros += 1
                print(f"  ⚠ Erro na linha {idx}: {e}")
                continue
        
        db.commit()
        print(f"\n✓ Linha Educacional: {importados} empresas importadas, {erros} erros")
        return importados
        
    except Exception as e:
        print(f"❌ Erro ao importar linha educacional: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

if __name__ == "__main__":
    print("="*70)
    print("POPULANDO PIPELINE KANBAN")
    print("="*70)
    
    print("\n1️⃣ Criando stages do pipeline...")
    if criar_stages():
        print("\n2️⃣ Importando dados da Linha Tecnologia...")
        tech_count = importar_linha_tecnologia()
        
        print("\n3️⃣ Importando dados da Linha Educacional...")
        edu_count = importar_linha_educacional()
        
        print("\n" + "="*70)
        print("✓ IMPORTAÇÃO CONCLUÍDA!")
        print(f"  Total importado: {tech_count + edu_count} empresas")
        print("="*70)
    else:
        print("\n❌ Falha ao criar stages. Abortando importação.")
        sys.exit(1)
