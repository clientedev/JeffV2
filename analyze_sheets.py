import pandas as pd
import sys

def analyze_excel(file_path, file_name):
    print(f"\n{'='*80}")
    print(f"Analisando: {file_name}")
    print(f"{'='*80}")
    
    try:
        xl_file = pd.ExcelFile(file_path)
        print(f"\nAbas encontradas: {xl_file.sheet_names}\n")
        
        for sheet_name in xl_file.sheet_names:
            print(f"\n--- Aba: {sheet_name} ---")
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=5)
            print(f"Dimensões: {len(pd.read_excel(file_path, sheet_name=sheet_name))} linhas x {len(df.columns)} colunas")
            print(f"\nColunas: {list(df.columns)}")
            print(f"\nPrimeiras linhas:")
            print(df.to_string(index=False))
            
    except Exception as e:
        print(f"Erro ao ler {file_name}: {str(e)}")

if __name__ == "__main__":
    files = [
        ("attached_assets/CRONOGRAMA 2.0 (4)_1760642348599.xlsx", "CRONOGRAMA"),
        ("attached_assets/Controle Geral 3.0_151015_1760642348601.xlsx", "CONTROLE GERAL"),
        ("attached_assets/Controle Geral_Considerações_1760642348602.xlsx", "CONSIDERAÇÕES")
    ]
    
    for file_path, file_name in files:
        analyze_excel(file_path, file_name)
