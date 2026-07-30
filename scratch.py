import pandas as pd
import json

df = pd.read_excel("Relação das OS's Pendentes.xlsx")
df.columns = df.columns.str.strip()
print("Total rows:", len(df))
if 'Tipo Solicitação' in df.columns:
    print(df['Tipo Solicitação'].value_counts())
if 'Responsável' in df.columns:
    print(df['Responsável'].value_counts())
