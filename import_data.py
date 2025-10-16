import pandas as pd
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models.models import Empresa, Consultor, Proposta, Cronograma, Feriado
from app.auth import get_password_hash

def clean_cnpj(cnpj_str):
    if pd.isna(cnpj_str):
        return None
    return str(cnpj_str).strip().replace('.', '').replace('/', '').replace('-', '')

def parse_date(date_val):
    if pd.isna(date_val):
        return None
    if isinstance(date_val, str):
        try:
            return datetime.strptime(date_val, '%Y-%m-%d').date()
        except:
            return None
    if hasattr(date_val, 'date'):
        return date_val.date()
    return None

def import_cronograma_data(db: Session):
    print("=" * 80)
    print("IMPORTANDO DADOS DO CRONOGRAMA")
    print("=" * 80)
    
    cronograma_file = "attached_assets/CRONOGRAMA 2.0 (4)_1760642348599.xlsx"
    
    df_info = pd.read_excel(cronograma_file, sheet_name="CONSULTA INFO.")
    print(f"\nLidas {len(df_info)} linhas da aba CONSULTA INFO.")
    
    consultores_map = {}
    empresas_map = {}
    
    for idx, row in df_info.iterrows():
        try:
            consultor_nome = str(row.get('CONSULTOR 1', '')).strip()
            if consultor_nome and consultor_nome not in ['nan', 'None', '']:
                if consultor_nome not in consultores_map:
                    consultor = db.query(Consultor).filter(Consultor.nome == consultor_nome).first()
                    if not consultor:
                        import hashlib
                        email_base = consultor_nome.lower().replace(' ', '.')
                        email_hash = hashlib.md5(consultor_nome.encode()).hexdigest()[:6]
                        email = f"{email_base}.{email_hash}@sistema.com"
                        
                        consultor = Consultor(
                            nome=consultor_nome,
                            email=email,
                            cargo="Consultor",
                            ativo=True
                        )
                        db.add(consultor)
                        db.flush()
                        print(f"✓ Consultor criado: {consultor_nome}")
                    consultores_map[consultor_nome] = consultor
            
            cnpj = clean_cnpj(row.get('CNPJ'))
            empresa_nome = str(row.get('EMPRESA', '')).strip()
            
            if cnpj and empresa_nome and empresa_nome not in ['nan', 'None', '']:
                if cnpj not in empresas_map:
                    empresa = db.query(Empresa).filter(Empresa.cnpj == cnpj).first()
                    if not empresa:
                        empresa = Empresa(
                            cnpj=cnpj,
                            nome=empresa_nome,
                            segmento=str(row.get('SOLUÇÃO', '')),
                            regiao=str(row.get('REGIÃO', '')),
                            er=str(row.get('ER', ''))
                        )
                        db.add(empresa)
                        db.flush()
                        print(f"✓ Empresa criada: {empresa_nome}")
                    empresas_map[cnpj] = empresa
                
                proposta_num = str(row.get('PROPOSTA', '')).strip()
                if proposta_num and proposta_num not in ['nan', 'None', '']:
                    proposta_existe = db.query(Proposta).filter(Proposta.numero_proposta == proposta_num).first()
                    
                    if not proposta_existe:
                        proposta = Proposta(
                            numero_proposta=proposta_num,
                            empresa_id=empresas_map[cnpj].id,
                            consultor_id=consultores_map.get(consultor_nome).id if consultor_nome in consultores_map else None,
                            solucao=str(row.get('SOLUÇÃO', '')),
                            data_contato=parse_date(row.get('INÍCIO')),
                            data_proposta=parse_date(row.get('INÍCIO')),
                            valor_proposta=None,
                            data_fechamento=parse_date(row.get('TÉRMINO')),
                            status="Fechado",
                            resultado="Ganho",
                            observacoes=f"Importado automaticamente. Horas: {row.get('HORAS', 0)}"
                        )
                        db.add(proposta)
                        db.flush()
                        
                        cronograma = Cronograma(
                            proposta_id=proposta.id,
                            data_inicio=parse_date(row.get('INÍCIO')),
                            data_termino=parse_date(row.get('TÉRMINO')),
                            horas_previstas=float(row.get('HORAS', 0)) if pd.notna(row.get('HORAS')) else 0,
                            horas_executadas=0,
                            percentual_conclusao=0,
                            status="Em andamento",
                            observacoes=f"Solução: {row.get('SOLUÇÃO', '')}"
                        )
                        db.add(cronograma)
                        print(f"✓ Proposta e cronograma criados: {proposta_num}")
        
        except Exception as e:
            print(f"✗ Erro na linha {idx}: {str(e)}")
            continue
    
    db.commit()
    print(f"\n✓ Importação da aba CONSULTA INFO concluída!")

def import_feriados(db: Session):
    print("\n" + "=" * 80)
    print("IMPORTANDO FERIADOS")
    print("=" * 80)
    
    try:
        cronograma_file = "attached_assets/CRONOGRAMA 2.0 (4)_1760642348599.xlsx"
        df_feriados = pd.read_excel(cronograma_file, sheet_name="FERIADOS")
        
        for idx, row in df_feriados.iterrows():
            try:
                data_feriado = parse_date(row.get('DATA'))
                descricao = str(row.get('DESCRIÇÃO', row.get('FERIADO', 'Feriado'))).strip()
                
                if data_feriado:
                    feriado_existe = db.query(Feriado).filter(Feriado.data == data_feriado).first()
                    if not feriado_existe:
                        feriado = Feriado(
                            data=data_feriado,
                            descricao=descricao,
                            tipo="Nacional"
                        )
                        db.add(feriado)
            except Exception as e:
                continue
        
        db.commit()
        print(f"✓ Feriados importados com sucesso!")
    except Exception as e:
        print(f"✗ Erro ao importar feriados: {str(e)}")

def import_controle_geral(db: Session):
    print("\n" + "=" * 80)
    print("IMPORTANDO CONTROLE GERAL - DADOS CADASTRAIS")
    print("=" * 80)
    
    try:
        controle_file = "attached_assets/Controle Geral 3.0_151015_1760642348601.xlsx"
        df_cadastro = pd.read_excel(controle_file, sheet_name="Dados Cadastrais", nrows=100)
        
        for idx, row in df_cadastro.iterrows():
            try:
                cnpj = clean_cnpj(row.get('CNPJ'))
                empresa_nome = str(row.get('EMPRESA', row.get('RAZÃO SOCIAL', ''))).strip()
                
                if cnpj and empresa_nome and empresa_nome not in ['nan', 'None', '']:
                    empresa_existe = db.query(Empresa).filter(Empresa.cnpj == cnpj).first()
                    if not empresa_existe:
                        empresa = Empresa(
                            cnpj=cnpj,
                            nome=empresa_nome,
                            segmento=str(row.get('SEGMENTO', row.get('PORTE', ''))),
                            regiao=str(row.get('REGIÃO', '')),
                            er=str(row.get('ER', ''))
                        )
                        db.add(empresa)
                        print(f"✓ Empresa cadastrada: {empresa_nome}")
            except Exception as e:
                continue
        
        db.commit()
        print(f"✓ Dados cadastrais importados!")
    except Exception as e:
        print(f"✗ Erro ao importar dados cadastrais: {str(e)}")

if __name__ == "__main__":
    print("\n" + "🚀 " * 40)
    print(" " * 20 + "IMPORTAÇÃO AUTOMÁTICA DE DADOS")
    print("🚀 " * 40 + "\n")
    
    init_db()
    db = SessionLocal()
    
    try:
        import_cronograma_data(db)
        import_feriados(db)
        import_controle_geral(db)
        
        total_empresas = db.query(Empresa).count()
        total_consultores = db.query(Consultor).count()
        total_propostas = db.query(Proposta).count()
        total_cronogramas = db.query(Cronograma).count()
        total_feriados = db.query(Feriado).count()
        
        print("\n" + "=" * 80)
        print(" " * 30 + "RESUMO DA IMPORTAÇÃO")
        print("=" * 80)
        print(f"✓ Total de Empresas no banco: {total_empresas}")
        print(f"✓ Total de Consultores no banco: {total_consultores}")
        print(f"✓ Total de Propostas no banco: {total_propostas}")
        print(f"✓ Total de Cronogramas no banco: {total_cronogramas}")
        print(f"✓ Total de Feriados no banco: {total_feriados}")
        print("=" * 80)
        print("\n✓ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!\n")
        
    except Exception as e:
        print(f"\n✗ ERRO GERAL: {str(e)}")
        db.rollback()
    finally:
        db.close()
