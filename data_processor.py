import pandas as pd
from datetime import datetime, timedelta

def find_column(df, keyword):
    for col in df.columns:
        if keyword.upper() in col.upper():
            return col
    return None

def get_equipe(row, config, col_resp, col_tipo):
    # Tenta usar o Tipo de Solicitação primeiro
    tipo = str(row.get(col_tipo, '')) if col_tipo else ''
    tipo = tipo.strip().upper()
    
    if 'MANUTENÇÃO' in tipo or 'MANUTENCAO' in tipo:
        return 'Infraestrutura'
    elif 'SOLICITAÇÃO' in tipo or 'SOLICITACAO' in tipo or 'AGUARDANDO ATENDIMENTO' in tipo:
        return 'Sistemas'
        
    # Se não encontrou pelo tipo, usa o Analista (Responsável)
    resp = str(row.get(col_resp, '')) if col_resp else ''
    resp = resp.strip().upper()
    
    analistas_infra = [x.strip().upper() for x in config.get('analistas_infra', [])]
    analistas_sistemas = [x.strip().upper() for x in config.get('analistas_sistemas', [])]
    
    for a in analistas_infra:
        if a in resp:
            return 'Infraestrutura'
            
    for a in analistas_sistemas:
        if a in resp:
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
            'total_sla_vencido_aguardando': 0,
            'infra_sla_vencido_aguardando': 0,
            'sistemas_sla_vencido_aguardando': 0,
            'sla_vencido_3_dias': 0,
            'chamados_ontem_hoje': 0,
            'ce_total': 0, 'ce_infra': 0, 'ce_sist': 0,
            'am_total': 0, 'am_infra': 0, 'am_sist': 0,
            'al_total': 0, 'al_infra': 0, 'al_sist': 0,
            'aat_total': 0,
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
    
    # Remover "Não Classificada" / Sem Responsável de TODOS os cálculos
    if col_status:
        status_temp = df[col_status].astype(str).str.strip().str.upper()
        df = df[~status_temp.isin(['NÃO CLASSIFICADA', 'NAO CLASSIFICADA', 'SEM RESPONSÁVEL', 'SEM RESPONSAVEL'])]

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

    # Status upper reconstruído
    status_upper = df[col_status].astype(str).str.strip().str.upper() if col_status else pd.Series(['']*len(df), index=df.index)

    sla_vencido_cond = pd.Series([False]*len(df), index=df.index)
    if col_sla:
        sla_vencido_cond = df[col_sla].astype(str).str.strip().str.upper() == 'SIM'

    # Filtros base
    apenas_aberta = status_upper == 'ABERTA' # Equivale a "Em Atendimento"
    apenas_aguardando = status_upper == 'AGUARDANDO ATENDIMENTO'
    apenas_liberacao = status_upper.str.contains('AGUARDANDO LIBERA', na=False)
    apenas_ce = status_upper == 'CONSERTO EXTERNO'
    apenas_am = status_upper == 'AGUARDANDO MATERIAL'
    
    # Condições Quadros
    is_infra = df['Equipe'] == 'Infraestrutura'
    is_sist = df['Equipe'] == 'Sistemas'
    
    # Função auxiliar de contagem
    def count(cond):
        return {
            'total': len(df[cond]),
            'infra': len(df[cond & is_infra]),
            'sist': len(df[cond & is_sist])
        }

    # QUADRO 1: Visão Geral de Chamados
    q1_geral = count(pd.Series([True]*len(df), index=df.index))
    
    cond_fila_ativa = ~(apenas_ce | apenas_am)
    q1_ativa = count(cond_fila_ativa)
    
    q1_em_atend = count(apenas_aberta)
    q1_ag_atend = count(apenas_aguardando)
    q1_ag_lib = count(apenas_liberacao)
    
    # QUADRO 2: SLA Vencido
    cond_sla_ativo = sla_vencido_cond & cond_fila_ativa
    q2_sla_ativo = count(cond_sla_ativo)
    
    q2_sla_em_atend = count(sla_vencido_cond & apenas_aberta)
    q2_sla_ag_atend = count(sla_vencido_cond & apenas_aguardando)
    q2_sla_ag_lib = count(sla_vencido_cond & apenas_liberacao)
    
    older_3_days_cond = df[col_data].apply(is_older_than_3_days) if col_data else pd.Series([False]*len(df), index=df.index)
    q2_sla_3_dias = count(cond_sla_ativo & older_3_days_cond)
    
    ontem_hoje_cond = df[col_data].apply(is_yesterday) if col_data else pd.Series([False]*len(df), index=df.index)
    # Ontem p/ hoje considera apenas Aguardando Atendimento (conforme alinhamento do usuário)
    chamados_ontem_hoje = len(df[ontem_hoje_cond & apenas_aguardando])
    
    # QUADRO 3: Conserto Externo e Material
    cond_ce_am = apenas_ce | apenas_am
    q3_retidos = count(cond_ce_am)
    q3_ce = count(apenas_ce)
    q3_am = count(apenas_am)
    
    # Legados necessários
    apoio_dev = 0
    if col_status:
        apoio_dev = len(df[is_sist & status_upper.str.contains('AGENDAR', na=False)])

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
                def get_os_string(condition):
                    filtered = df_analista[condition].copy()
                    if filtered.empty: return ""
                    
                    if col_sla:
                        filtered['SLA_VENCIDO_FLAG'] = filtered[col_sla].astype(str).str.strip().str.upper() == 'SIM'
                    else:
                        filtered['SLA_VENCIDO_FLAG'] = False
                        
                    res = []
                    for idx, row in filtered.iterrows():
                        os_val = str(row[col_os]).replace('.0', '').strip()
                        if row['SLA_VENCIDO_FLAG']:
                            res.append(f"🔴 {os_val}")
                        else:
                            res.append(os_val)
                    return ", ".join(res)
                
                # Aberta / Aguardando Atendimento
                cond_aberta = df_analista[col_status].astype(str).str.strip().str.upper().isin(['ABERTA', 'AGUARDANDO ATENDIMENTO']) if col_status else pd.Series([True]*len(df_analista), index=df_analista.index)
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
        'q1_geral': q1_geral,
        'q1_ativa': q1_ativa,
        'q1_em_atend': q1_em_atend,
        'q1_ag_atend': q1_ag_atend,
        'q1_ag_lib': q1_ag_lib,
        
        'q2_sla_ativo': q2_sla_ativo,
        'q2_sla_em_atend': q2_sla_em_atend,
        'q2_sla_ag_atend': q2_sla_ag_atend,
        'q2_sla_ag_lib': q2_sla_ag_lib,
        'q2_sla_3_dias': q2_sla_3_dias,
        'chamados_ontem_hoje': chamados_ontem_hoje,
        
        'q3_retidos': q3_retidos,
        'q3_ce': q3_ce,
        'q3_am': q3_am,
        
        'sugestao_apoio_dev': apoio_dev,
        'os_aberta_solic': os_aberta_solic,
        'os_conserto': os_conserto,
        'os_material': os_material,
        'os_liberacao': os_liberacao
    }
