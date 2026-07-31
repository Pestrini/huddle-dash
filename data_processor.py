import pandas as pd
from datetime import datetime, timedelta

def find_column(df, keyword):
    for col in df.columns:
        if keyword.upper() in col.upper():
            return col
    return None

def get_equipe(row, config, col_resp, col_tipo):
    # Regra 1: Separação estrita por Tipo de Solicitação
    tipo = str(row.get(col_tipo, '')) if col_tipo else ''
    tipo = tipo.strip().upper()
    
    if 'MANUTENÇÃO' in tipo:
        return 'Infraestrutura'
    elif 'SOLICITAÇÃO' in tipo or 'SOLICITACAO' in tipo:
        return 'Sistemas'
        
    return 'Outros'

def process_dataframe(df, config):
    if df.empty:
        return {
            'chamados_abertos_geral': 0,
            'chamados_sistemas': 0,
            'chamados_infra': 0,
            'sugestao_apoio_dev': 0,
            'total_sla_vencido': 0,
            'sla_vencido_sem_ce': 0,
            'infra_sla_vencido': 0,
            'sistemas_sla_vencido': 0,
            'sla_vencido_3_dias': 0,
            'chamados_ontem_hoje': 0,
            'ce_total': 0, 'ce_infra': 0, 'ce_sist': 0,
            'am_total': 0, 'am_infra': 0, 'am_sist': 0,
            'al_total': 0, 'al_infra': 0, 'al_sist': 0,
            'total_outros': 0,
            'os_por_analista': {}
        }

    # Limpa colunas e dados gerais
    df.columns = df.columns.str.strip()

    col_resp = find_column(df, 'Respons')
    col_tipo = find_column(df, 'Tipo Solicita')
    col_status = find_column(df, 'Status')
    col_sla = find_column(df, 'SLA Vencido')
    col_data = find_column(df, 'Data Solicita')
    col_os = find_column(df, 'Os')

    df['Equipe'] = df.apply(lambda r: get_equipe(r, config, col_resp, col_tipo), axis=1)
    
    # Tratamento de datas
    today = datetime.today().date()
    if today.weekday() == 0:
        ontem = today - timedelta(days=3)
    elif today.weekday() == 6:
        ontem = today - timedelta(days=2)
    else:
        ontem = today - timedelta(days=1)

    def parse_date(val):
        if pd.isna(val): return None
        if hasattr(val, 'date'): return val.date()
        s = str(val).strip().split()[0]
        try:
            return datetime.strptime(s, '%d/%m/%Y').date()
        except:
            try:
                return datetime.strptime(s, '%Y-%m-%d').date()
            except:
                return None

    def is_older_than_3_days(val):
        d = parse_date(val)
        if d:
            return (today - d).days > 3
        return False

    def is_yesterday(val):
        d = parse_date(val)
        if d:
            return d == ontem
        return False

    # Lógicas e Condições Base
    abertos_geral = len(df)
    sistemas = len(df[df['Equipe'] == 'Sistemas'])
    infra = len(df[df['Equipe'] == 'Infraestrutura'])
    
    apoio_dev = 0
    if col_status:
        apoio_dev = len(df[(df['Equipe'] == 'Sistemas') & (df[col_status].astype(str).str.strip().str.upper().str.contains('AGENDAR', na=False))])
        
    status_upper = df[col_status].astype(str).str.strip().str.upper() if col_status else pd.Series(['']*len(df))
    
    sla_vencido_cond = pd.Series([False]*len(df))
    if col_sla:
        sla_vencido_cond = df[col_sla].astype(str).str.strip().str.upper() == 'SIM'
        
    # Regra 2: Desconsiderar Conserto Externo e Aguardando Material
    nao_conserto_aguardando = ~status_upper.isin(['CONSERTO EXTERNO', 'AGUARDANDO MATERIAL'])
    
    # Regra 3: Apenas Aberta ou Solicitação para Infra e Sistemas
    aberta_ou_solicitacao = status_upper.isin(['ABERTA', 'SOLICITAÇÃO', 'SOLICITACAO'])
    
    # Aplicando as regras aos indicadores
    
    # Novo indicador que desconsidera APENAS Conserto Externo
    nao_conserto = ~status_upper.isin(['CONSERTO EXTERNO'])
    sla_vencido_sem_ce = len(df[sla_vencido_cond & nao_conserto])
    
    # Total SLA Vencido (Regra 2) -> Como o usuário pediu para "bater com o total" dos analistas (Regra 3), usarei a mesma lógica estrita de Aberta/Solicitação para garantir consistência perfeita.
    total_sla_vencido = len(df[sla_vencido_cond & aberta_ou_solicitacao])
    
    # Infra e Sistemas SLA Vencido (Regra 3)
    infra_sla_vencido = len(df[(df['Equipe'] == 'Infraestrutura') & sla_vencido_cond & aberta_ou_solicitacao])
    sistemas_sla_vencido = len(df[(df['Equipe'] == 'Sistemas') & sla_vencido_cond & aberta_ou_solicitacao])
    
    # SLA Vencido > 3 Dias (Regra 4)
    older_3_days_cond = df[col_data].apply(is_older_than_3_days) if col_data else pd.Series([False]*len(df))
    sla_vencido_3_dias = len(df[sla_vencido_cond & older_3_days_cond])
    
    # Chamados Ontem p/ Hoje (Regra 5)
    ontem_hoje_cond = df[col_data].apply(is_yesterday) if col_data else pd.Series([False]*len(df))
    chamados_ontem_hoje = len(df[ontem_hoje_cond & aberta_ou_solicitacao])

    # Novos Indicadores Discretos (Conserto, Material, Liberação)
    conserto_ext = status_upper == 'CONSERTO EXTERNO'
    ce_total = len(df[conserto_ext])
    ce_infra = len(df[(df['Equipe'] == 'Infraestrutura') & conserto_ext])
    ce_sist = len(df[(df['Equipe'] == 'Sistemas') & conserto_ext])
    
    ag_mat = status_upper == 'AGUARDANDO MATERIAL'
    am_total = len(df[ag_mat])
    am_infra = len(df[(df['Equipe'] == 'Infraestrutura') & ag_mat])
    am_sist = len(df[(df['Equipe'] == 'Sistemas') & ag_mat])
    
    ag_lib = status_upper.str.contains('AGUARDANDO LIBERA', na=False)
    al_total = len(df[ag_lib])
    al_infra = len(df[(df['Equipe'] == 'Infraestrutura') & ag_lib])
    al_sist = len(df[(df['Equipe'] == 'Sistemas') & ag_lib])
    
    total_outros = ce_total + am_total + al_total

    # Ordenar Dataframe para extração de OS
    col_prio = find_column(df, 'Prioridade')
    prio_map = { 'MUITO ALTA': 5, 'ALTA': 4, 'MÉDIA': 3, 'MEDIA': 3, 'BAIXA': 2, 'MUITO BAIXA': 1 }
    if col_prio:
        df['Prio_Peso'] = df[col_prio].astype(str).str.strip().str.upper().map(prio_map).fillna(0)
    else:
        df['Prio_Peso'] = 0
        
    if col_data:
        df['Data_Ord'] = pd.to_datetime(df[col_data].apply(parse_date), errors='coerce')
    else:
        df['Data_Ord'] = pd.Timestamp.min
        
    df = df.sort_values(by=['Prio_Peso', 'Data_Ord'], ascending=[False, True])

    # Agrupar OS por Analista (4 categorias)
    os_aberta_solic = {}
    os_conserto = {}
    os_material = {}
    os_liberacao = {}
    
    todos_analistas = config.get('analistas_infra', []) + config.get('analistas_sistemas', [])
    
    if col_resp and col_os:
        for analista in todos_analistas:
            analista_nome = analista.strip().upper()
            if not analista_nome: continue
            
            df_analista = df[df[col_resp].astype(str).str.strip().str.upper().str.contains(analista_nome, na=False)]
            
            if not df_analista.empty:
                # Helper to format list
                def get_os_string(condition):
                    filtered = df_analista[condition]
                    if filtered.empty: return ""
                    return ", ".join(filtered[col_os].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().tolist())
                
                # Aberta / Solicitação
                cond_aberta = df_analista[col_status].astype(str).str.strip().str.upper().isin(['ABERTA', 'SOLICITAÇÃO', 'SOLICITACAO']) if col_status else pd.Series([True]*len(df_analista), index=df_analista.index)
                os_aberta_solic[analista] = get_os_string(cond_aberta)
                
                # Conserto Externo
                cond_conserto = df_analista[col_status].astype(str).str.strip().str.upper() == 'CONSERTO EXTERNO' if col_status else pd.Series([False]*len(df_analista), index=df_analista.index)
                os_conserto[analista] = get_os_string(cond_conserto)
                
                # Aguardando Material
                cond_mat = df_analista[col_status].astype(str).str.strip().str.upper() == 'AGUARDANDO MATERIAL' if col_status else pd.Series([False]*len(df_analista), index=df_analista.index)
                os_material[analista] = get_os_string(cond_mat)
                
                # Aguardando Liberação Setor
                cond_lib = df_analista[col_status].astype(str).str.strip().str.upper().str.contains('AGUARDANDO LIBERA', na=False) if col_status else pd.Series([False]*len(df_analista), index=df_analista.index)
                os_liberacao[analista] = get_os_string(cond_lib)
            else:
                os_aberta_solic[analista] = ""
                os_conserto[analista] = ""
                os_material[analista] = ""
                os_liberacao[analista] = ""

    return {
        'chamados_abertos_geral': abertos_geral,
        'chamados_sistemas': sistemas,
        'chamados_infra': infra,
        'sla_vencido_sem_ce': sla_vencido_sem_ce,
        'sugestao_apoio_dev': apoio_dev,
        'total_sla_vencido': total_sla_vencido,
        'infra_sla_vencido': infra_sla_vencido,
        'sistemas_sla_vencido': sistemas_sla_vencido,
        'sla_vencido_3_dias': sla_vencido_3_dias,
        'chamados_ontem_hoje': chamados_ontem_hoje,
        'ce_total': ce_total, 'ce_infra': ce_infra, 'ce_sist': ce_sist,
        'am_total': am_total, 'am_infra': am_infra, 'am_sist': am_sist,
        'al_total': al_total, 'al_infra': al_infra, 'al_sist': al_sist,
        'total_outros': total_outros,
        'os_aberta_solic': os_aberta_solic,
        'os_conserto': os_conserto,
        'os_material': os_material,
        'os_liberacao': os_liberacao
    }
