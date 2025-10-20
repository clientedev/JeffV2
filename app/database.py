import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models import models
    Base.metadata.create_all(bind=engine)

def ensure_database_setup():
    """
    Verifica e cria tabelas e colunas faltantes de forma segura.
    NUNCA remove ou recria tabelas/colunas existentes.
    Loga todas as operações para transparência.
    """
    from app.models import models
    from sqlalchemy import inspect, text
    
    print("\n" + "="*70)
    print("🔍 VERIFICAÇÃO DE ESTRUTURA DO BANCO DE DADOS")
    print("="*70)
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"\n📊 Tabelas existentes no banco: {len(existing_tables)}")
    for table in sorted(existing_tables):
        print(f"   ✓ {table}")
    
    expected_tables = [
        'usuarios', 'empresas', 'consultores', 'propostas', 'cronogramas',
        'tarefas', 'contratos', 'feriados', 'alocacoes_cronograma',
        'contatos', 'linha_tecnologia', 'linha_educacional',
        'prospeccao', 'followups', 'carteira_grm', 'pesquisas_satisfacao', 'solucoes',
        'stages', 'company_pipeline', 'company_stage_history', 'notes', 'attachments', 'activities'
    ]
    
    missing_tables = [t for t in expected_tables if t not in existing_tables]
    
    if missing_tables:
        print(f"\n⚠️  Tabelas faltantes detectadas: {len(missing_tables)}")
        for table in missing_tables:
            print(f"   ⚙️  Criando tabela: {table}")
        
        Base.metadata.create_all(bind=engine)
        print(f"\n✅ Tabelas criadas com sucesso!")
    else:
        print(f"\n✅ Todas as tabelas esperadas já existem.")
    
    # Verificar colunas faltantes nas tabelas existentes
    print(f"\n🔍 Verificando colunas em cada tabela...")
    columns_added = False
    
    with engine.connect() as conn:
        for table_name in expected_tables:
            if table_name not in existing_tables:
                continue  # Tabela nova, já criada acima
            
            # Obter colunas existentes
            existing_columns = {col['name'] for col in inspector.get_columns(table_name)}
            
            # Obter colunas esperadas do modelo
            table_obj = Base.metadata.tables.get(table_name)
            if table_obj is None:
                continue
            
            expected_columns = {col.name for col in table_obj.columns}
            missing_columns = expected_columns - existing_columns
            
            if missing_columns:
                print(f"\n⚠️  Tabela '{table_name}' tem colunas faltantes:")
                for col_name in sorted(missing_columns):
                    col_obj = table_obj.columns[col_name]
                    col_type = col_obj.type.compile(engine.dialect)
                    
                    try:
                        # Estratégia segura para adicionar colunas NOT NULL:
                        # 1. Adicionar como nullable com default
                        # 2. Depois fazer ALTER para NOT NULL se necessário
                        
                        if not col_obj.nullable and col_obj.server_default is None:
                            # Processo completo para colunas NOT NULL sem default:
                            # 1. ADD COLUMN com default temporário
                            # 2. UPDATE valores existentes (já preenchidos pelo default)
                            # 3. ALTER SET NOT NULL
                            # 4. DROP DEFAULT temporário
                            
                            # Define defaults temporários baseados no tipo
                            if 'VARCHAR' in str(col_type) or 'TEXT' in str(col_type):
                                temp_default = "''"
                            elif 'INTEGER' in str(col_type):
                                temp_default = "0"
                            elif 'NUMERIC' in str(col_type) or 'DECIMAL' in str(col_type):
                                temp_default = "0"
                            elif 'BOOLEAN' in str(col_type):
                                temp_default = "FALSE"
                            elif 'DATE' in str(col_type):
                                temp_default = "CURRENT_DATE"
                            elif 'TIMESTAMP' in str(col_type):
                                temp_default = "CURRENT_TIMESTAMP"
                            else:
                                # Para outros tipos, adicionar como nullable
                                temp_default = None
                            
                            # Passo 1: Adicionar coluna com default
                            if temp_default:
                                alter_sql = f'ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col_name} {col_type} DEFAULT {temp_default}'
                                conn.execute(text(alter_sql))
                                conn.commit()
                                
                                # Passo 2: Tornar NOT NULL
                                alter_not_null = f'ALTER TABLE {table_name} ALTER COLUMN {col_name} SET NOT NULL'
                                conn.execute(text(alter_not_null))
                                conn.commit()
                                
                                # Passo 3: Remover default temporário
                                drop_default = f'ALTER TABLE {table_name} ALTER COLUMN {col_name} DROP DEFAULT'
                                conn.execute(text(drop_default))
                                conn.commit()
                                
                                print(f"   ✅ Coluna NOT NULL adicionada: {col_name} ({col_type})")
                            else:
                                # Se não há default seguro, adicionar como nullable
                                alter_sql = f'ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col_name} {col_type}'
                                conn.execute(text(alter_sql))
                                conn.commit()
                                print(f"   ✅ Coluna adicionada como nullable: {col_name} ({col_type})")
                        
                        else:
                            # Colunas nullable ou com server_default: adicionar normalmente
                            nullable = "NULL" if col_obj.nullable else "NOT NULL"
                            default = f" DEFAULT {col_obj.server_default.arg}" if col_obj.server_default else ""
                            alter_sql = f'ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col_name} {col_type} {nullable}{default}'
                            conn.execute(text(alter_sql))
                            conn.commit()
                            print(f"   ✅ Coluna adicionada: {col_name} ({col_type})")
                        
                        columns_added = True
                        
                    except Exception as e:
                        print(f"   ❌ Erro ao adicionar coluna {col_name}: {e}")
                        conn.rollback()
    
    if columns_added:
        print(f"\n✅ Colunas faltantes foram adicionadas!")
    else:
        print(f"\n✅ Todas as colunas esperadas já existem.")
    
    print("\n" + "="*70)
    print("✓ VERIFICAÇÃO CONCLUÍDA - NENHUM DADO FOI PERDIDO")
    print("="*70 + "\n")
