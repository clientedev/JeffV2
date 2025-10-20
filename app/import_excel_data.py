"""
Script de importação segura de dados da planilha Excel
NUNCA remove ou sobrescreve dados existentes
Apenas insere novos registros
"""
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime
import re
from email_validator import validate_email, EmailNotValidError
from app.database import SessionLocal
from app.models.models import (
    Prospeccao, FollowUp, CarteiraGRM, PesquisaSatisfacao, Solucao,
    Contato, Empresa
)

def normalize_cnpj(cnpj_str):
    """Normaliza CNPJ removendo caracteres especiais"""
    if pd.isna(cnpj_str) or cnpj_str is None:
        return None
    cnpj = str(cnpj_str).strip()
    cnpj = re.sub(r'[^\d]', '', cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
    return None

def parse_date(value):
    """Parse date safely"""
    if pd.isna(value) or value is None:
        return None
    try:
        return pd.to_datetime(value).date()
    except:
        return None

def safe_str(value, max_length=None):
    """Converte valor para string de forma segura"""
    if pd.isna(value) or value is None:
        return None
    result = str(value).strip()
    if max_length and len(result) > max_length:
        result = result[:max_length]
    return result if result else None

def safe_float(value):
    """Converte valor para float de forma segura"""
    if pd.isna(value) or value is None:
        return None
    try:
        return float(value)
    except:
        return None

def validate_and_normalize_email(email_str):
    """Valida e normaliza e-mail"""
    if pd.isna(email_str) or email_str is None:
        return None
    
    email = str(email_str).strip()
    if not email:
        return None
    
    try:
        valid = validate_email(email, check_deliverability=False)
        return valid.normalized
    except EmailNotValidError:
        print(f"   ⚠️  E-mail inválido ignorado: {email}")
        return None

def import_prospeccao(excel_file: str, db: Session):
    """Importa dados de prospecção do histórico"""
    print("\n📥 Importando dados de Prospecção...")
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Histórico Prosp')
        
        # Pular linhas vazias
        df = df.dropna(how='all')
        
        imported = 0
        skipped = 0
        
        for _, row in df.iterrows():
            cnpj = normalize_cnpj(row.get('CNPJ'))
            empresa = safe_str(row.get('EMPRESA'), 255)
            
            if not empresa:
                continue
            
            # Verificar se já existe (evitar duplicatas)
            query = db.query(Prospeccao).filter(Prospeccao.empresa == empresa)
            if cnpj:
                query = query.filter(Prospeccao.cnpj == cnpj)
            exists = query.first()
            
            if exists:
                skipped += 1
                continue
            
            prospeccao = Prospeccao(
                empresa=empresa,
                cnpj=cnpj,
                porte=safe_str(row.get('PORTE'), 50),
                er=safe_str(row.get('ER'), 100),
                contato=safe_str(row.get('CONTATO'), 255),
                cargo=safe_str(row.get('CARGO'), 100),
                email=validate_and_normalize_email(row.get('E-MAIL')),
                celular=safe_str(row.get('CELULAR'), 20),
                telefone=safe_str(row.get('TELEFONE'), 20),
                tipo_programa=safe_str(row.get('TIPO DE PROGRAMA'), 100),
                status=safe_str(row.get('STATUS PROSPECÇÃO'), 50) or 'Novo',
                responsavel=safe_str(row.get('RESPONSÁVEL'), 255),
                data_ligacao=parse_date(row.get('DATA LIGAÇÃO')),
                oportunidade=safe_str(row.get('OPORTUNIDADE FINAL'), 500),
                observacoes=safe_str(row.get('OBSERVAÇÕES DE PROSPECÇÃO')),
                dados_iniciais=True
            )
            
            db.add(prospeccao)
            imported += 1
            
            if imported % 100 == 0:
                db.commit()
                print(f"   {imported} registros importados...")
        
        db.commit()
        print(f"✅ Prospecção: {imported} novos registros, {skipped} já existentes")
        
    except Exception as e:
        print(f"❌ Erro ao importar Prospecção: {e}")
        db.rollback()

def import_carteira_grm(excel_file: str, db: Session):
    """Importa dados da Carteira GRM"""
    print("\n📥 Importando dados da Carteira GRM...")
    
    try:
        df = pd.read_excel(excel_file, sheet_name='CARTEIRA GRM')
        df = df.dropna(how='all')
        
        imported = 0
        skipped = 0
        
        for _, row in df.iterrows():
            cnpj = normalize_cnpj(row.get('CNPJ'))
            empresa = safe_str(row.get('EMPRESA'), 255)
            proposta = safe_str(row.get('PROPOSTA'), 50)
            
            if not empresa:
                continue
            
            # Verificar duplicata
            exists = db.query(CarteiraGRM).filter(
                CarteiraGRM.cnpj == cnpj,
                CarteiraGRM.proposta == proposta
            ).first()
            
            if exists:
                skipped += 1
                continue
            
            carteira = CarteiraGRM(
                cnpj=cnpj,
                empresa=empresa,
                porte=safe_str(row.get('PORTE'), 50),
                proposta=proposta,
                solucao=safe_str(row.get('SOLUÇÃO'), 500),
                consultor=safe_str(row.get('CONSULTOR'), 255),
                data_inicio=parse_date(row.get('DATA INÍCIO')),
                data_termino=parse_date(row.get('DATA TÉRMINO')),
                ch=safe_str(row.get('CH'), 50),
                valor=safe_float(row.get('VALOR')),
                status=safe_str(row.get('STATUS'), 100),
                dados_iniciais=True
            )
            
            db.add(carteira)
            imported += 1
            
            if imported % 100 == 0:
                db.commit()
                print(f"   {imported} registros importados...")
        
        db.commit()
        print(f"✅ Carteira GRM: {imported} novos registros, {skipped} já existentes")
        
    except Exception as e:
        print(f"❌ Erro ao importar Carteira GRM: {e}")
        db.rollback()

def import_solucoes(excel_file: str, db: Session):
    """Importa catálogo de soluções"""
    print("\n📥 Importando catálogo de Soluções...")
    
    try:
        df = pd.read_excel(excel_file, sheet_name='SOLUÇÕES')
        df = df.dropna(how='all')
        
        imported = 0
        skipped = 0
        
        for _, row in df.iterrows():
            titulo = safe_str(row.get('TÍTULO CONSULTORIA'), 500)
            
            if not titulo:
                continue
            
            # Verificar duplicata
            exists = db.query(Solucao).filter(
                Solucao.titulo == titulo
            ).first()
            
            if exists:
                skipped += 1
                continue
            
            horas_me_val = row.get('HORAS - ME')
            horas_epp_val = row.get('HORAS - EPP')
            
            solucao = Solucao(
                categoria=safe_str(row.get('CATEGORIA'), 255),
                subgrupo=safe_str(row.get('SUBGRUPO'), 255),
                titulo=titulo,
                etapa=safe_str(row.get('ETAPA'), 100),
                horas_me=int(horas_me_val) if horas_me_val is not None and not pd.isna(horas_me_val) else None,
                horas_epp=int(horas_epp_val) if horas_epp_val is not None and not pd.isna(horas_epp_val) else None,
                estrategia=safe_str(row.get('ESTRATÉGIA'), 50),
                ativo=True
            )
            
            db.add(solucao)
            imported += 1
        
        db.commit()
        print(f"✅ Soluções: {imported} novos registros, {skipped} já existentes")
        
    except Exception as e:
        print(f"❌ Erro ao importar Soluções: {e}")
        db.rollback()

def import_all_from_excel(excel_file: str):
    """Importa todos os dados da planilha Excel de forma segura"""
    print("\n" + "="*70)
    print("📊 IMPORTAÇÃO DE DADOS DA PLANILHA EXCEL")
    print("="*70)
    print(f"📄 Arquivo: {excel_file}")
    
    db = SessionLocal()
    try:
        import_prospeccao(excel_file, db)
        import_carteira_grm(excel_file, db)
        import_solucoes(excel_file, db)
        
        print("\n" + "="*70)
        print("✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erro geral na importação: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    excel_file = "attached_assets/Controle Geral 3.0_151015_1760982752095.xlsx"
    import_all_from_excel(excel_file)
