import pandas as pd
import os
from datetime import datetime

HISTORY_FILE = 'historico_huddle.csv'

COLUMNS = [
    'Data',
    'Abertos Geral',
    'Sistemas',
    'Infraestrutura',
    'SLA Vencido Total',
    'SLA Vencido Sistemas',
    'SLA Vencido Infra',
    'Aguardando Material',
    'Conserto Externo',
    'Aguardando Liberação Setor',
    'Aguardando Atendimento'
]

def load_history():
    """Carrega o histórico de chamados em um DataFrame."""
    if os.path.exists(HISTORY_FILE):
        try:
            df = pd.read_csv(HISTORY_FILE)
            # Garante que a coluna de data seja lida corretamente
            df['Data'] = pd.to_datetime(df['Data'], format='%Y-%m-%d', errors='coerce')
            return df
        except Exception:
            return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

def history_exists_for_today():
    """Verifica se já existe um registro salvo para a data de hoje."""
    hoje_str = datetime.today().strftime('%Y-%m-%d')
    df = load_history()
    if df.empty:
        return False
    # Converte para string YYYY-MM-DD para comparação precisa
    datas_salvas = df['Data'].dt.strftime('%Y-%m-%d').tolist()
    return hoje_str in datas_salvas

def save_daily_metrics(metrics):
    """Salva as métricas do dia ou atualiza se já existir."""
    df = load_history()
    hoje_str = datetime.today().strftime('%Y-%m-%d')
    
    nova_linha = {
        'Data': hoje_str,
        'Abertos Geral': metrics.get('q1_geral', {}).get('total', 0),
        'Sistemas': metrics.get('q1_geral', {}).get('sist', 0),
        'Infraestrutura': metrics.get('q1_geral', {}).get('infra', 0),
        'SLA Vencido Total': metrics.get('q2_sla_em_atend', {}).get('total', 0),
        'SLA Vencido Sistemas': metrics.get('q2_sla_em_atend', {}).get('sist', 0),
        'SLA Vencido Infra': metrics.get('q2_sla_em_atend', {}).get('infra', 0),
        'Aguardando Material': metrics.get('q3_am', {}).get('total', 0),
        'Conserto Externo': metrics.get('q3_ce', {}).get('total', 0),
        'Aguardando Liberação Setor': metrics.get('q1_ag_lib', {}).get('total', 0),
        'Aguardando Atendimento': metrics.get('q1_ag_atend', {}).get('total', 0)
    }
    
    if history_exists_for_today():
        # Atualiza a linha existente
        df.loc[df['Data'].dt.strftime('%Y-%m-%d') == hoje_str, list(nova_linha.keys())] = list(nova_linha.values())
    else:
        # Adiciona nova linha (usando pd.concat em vez do append que foi depreciado no pandas 2.0)
        nova_linha_df = pd.DataFrame([nova_linha])
        nova_linha_df['Data'] = pd.to_datetime(nova_linha_df['Data'])
        df = pd.concat([df, nova_linha_df], ignore_index=True)
    
    # Salva o arquivo CSV
    # Re-converte data para string YYYY-MM-DD antes de salvar para ficar limpo no CSV
    df['Data'] = df['Data'].dt.strftime('%Y-%m-%d')
    df.to_csv(HISTORY_FILE, index=False)
