import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

from app.database import engine, SessionLocal
from app.models.models import Empresa

def importar_empresas_excel(arquivo_excel):
    df = pd.read_excel(arquivo_excel)
    
    db = SessionLocal()
    importados = 0
    erros = []
    
    try:
        for index, row in df.iterrows():
            try:
                cnpj = str(row['CNPJ']).strip() if pd.notna(row['CNPJ']) else None
                
                if not cnpj:
                    erros.append(f"Linha {index + 2}: CNPJ não fornecido")
                    continue
                
                empresa_existente = db.query(Empresa).filter(Empresa.cnpj == cnpj).first()
                if empresa_existente:
                    print(f"Empresa com CNPJ {cnpj} já existe. Pulando...")
                    continue
                
                cadastro_atualizacao = None
                if pd.notna(row['CADASTRO / ATUALIZAÇÃO']):
                    try:
                        cadastro_atualizacao = pd.to_datetime(row['CADASTRO / ATUALIZAÇÃO'])
                    except:
                        pass
                
                num_func = None
                if pd.notna(row['Nº FUNC.']):
                    try:
                        num_func = int(float(row['Nº FUNC.']))
                    except:
                        pass
                
                empresa = Empresa(
                    cnpj=cnpj,
                    nome=str(row['EMPRESA']).strip() if pd.notna(row['EMPRESA']) else "Sem Nome",
                    sigla=str(row['SIGLA']).strip() if pd.notna(row['SIGLA']) else None,
                    porte=str(row['PORTE']).strip() if pd.notna(row['PORTE']) else None,
                    er=str(row['ER']).strip() if pd.notna(row['ER']) else None,
                    carteira=str(row['CARTEIRA22']).strip() if pd.notna(row['CARTEIRA22']) else None,
                    endereco=str(row['ENDEREÇO']).strip() if pd.notna(row['ENDEREÇO']) else None,
                    bairro=str(row['BAIRRO']).strip() if pd.notna(row['BAIRRO']) else None,
                    zona=str(row['ZONA']).strip() if pd.notna(row['ZONA']) else None,
                    municipio=str(row['MUNICÍPIO']).strip() if pd.notna(row['MUNICÍPIO']) else None,
                    estado=str(row['ESTADO']).strip() if pd.notna(row['ESTADO']) else None,
                    pais=str(row['PAÍS']).strip() if pd.notna(row['PAÍS']) else None,
                    area=str(row['ÁREA']).strip() if pd.notna(row['ÁREA']) else None,
                    cnae_principal=str(row['CNAE PRINCIPAL']).strip() if pd.notna(row['CNAE PRINCIPAL']) else None,
                    descricao_cnae=str(row['DESCRIÇÃO CNAE']).strip() if pd.notna(row['DESCRIÇÃO CNAE']) else None,
                    tipo_empresa=str(row['TIPO DE EMPRESA']).strip() if pd.notna(row['TIPO DE EMPRESA']) else None,
                    cadastro_atualizacao=cadastro_atualizacao,
                    num_funcionarios=num_func,
                    observacao=str(row['Observação']).strip() if pd.notna(row['Observação']) else None,
                    segmento=str(row['ÁREA']).strip() if pd.notna(row['ÁREA']) else None
                )
                
                db.add(empresa)
                db.flush()
                importados += 1
                
                if importados % 50 == 0:
                    db.commit()
                    print(f"{importados} empresas importadas...")
                    
            except Exception as e:
                erros.append(f"Linha {index + 2}: {str(e)}")
                continue
        
        db.commit()
        print(f"\n✓ Importação concluída!")
        print(f"Total importado: {importados}")
        print(f"Total de erros: {len(erros)}")
        
        if erros and len(erros) <= 10:
            print("\nErros encontrados:")
            for erro in erros:
                print(f"  - {erro}")
                
    except Exception as e:
        print(f"Erro geral na importação: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando importação de empresas...")
    importar_empresas_excel("attached_assets/empresas_1760721836326.xlsx")
