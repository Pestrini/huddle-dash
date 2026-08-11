import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from data_processor import process_dataframe
from report_generator import generate_pdf
import history_manager
import plotly.express as px

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"analistas_infra": [], "analistas_sistemas": []}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

st.set_page_config(page_title="Huddle TI HURP", layout="wide", initial_sidebar_state="expanded")

# CSS Premium Styling
st.markdown("""
<style>
    /* Cards and Inputs */
    div.stMetric {
        background-color: var(--secondary-background-color);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s ease-in-out;
    }
    div.stMetric:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background: linear-gradient(135deg, #00995D 0%, #007A4B 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #007A4B 0%, #005C38 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 153, 93, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR CONFIGURAÇÃO
st.sidebar.image("logo_huddle_hurp_transparente.png", use_column_width=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
if 'menu' not in st.session_state:
    st.session_state.menu = "🏠 Huddle Diário"

st.sidebar.markdown("**Navegação**")
if st.sidebar.button("🏠 Huddle Diário", use_container_width=True):
    st.session_state.menu = "🏠 Huddle Diário"
if st.sidebar.button("📈 Evolução e Gráficos", use_container_width=True):
    st.session_state.menu = "📈 Evolução e Gráficos"

menu = st.session_state.menu
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Gerenciamento de Equipes")
st.sidebar.markdown("Gerencie a equipe de TI")
config = load_config()

with st.sidebar.expander("Equipe de Infraestrutura"):
    infra_text = st.text_area("Analistas (1 por linha)", value="\n".join(config['analistas_infra']), height=100)
    if st.button("Salvar Infra"):
        config['analistas_infra'] = [x.strip() for x in infra_text.split('\n') if x.strip()]
        save_config(config)
        st.success("Salvo!")

with st.sidebar.expander("Equipe de Sistemas"):
    sistemas_text = st.text_area("Analistas (1 por linha)", value="\n".join(config['analistas_sistemas']), height=100)
    if st.button("Salvar Sistemas"):
        config['analistas_sistemas'] = [x.strip() for x in sistemas_text.split('\n') if x.strip()]
        save_config(config)
        st.success("Salvo!")

if menu == "🏠 Huddle Diário":
    st.title("Huddle Diário TI")

    # BLOCO 1: UPLOAD
    st.header("1. Importação de Dados")
    uploaded_file = st.file_uploader("Arraste e solte o Excel exportado do sistema", type=['xlsx'])

    if uploaded_file is not None:
        # Processa o Excel
        try:
            df = pd.read_excel(uploaded_file)
            metrics = process_dataframe(df, config)
            st.session_state['huddle_metrics'] = metrics
            st.session_state['huddle_filename'] = uploaded_file.name
        except Exception as e:
            st.error(f"Erro ao ler o Excel. Certifique-se que o formato está correto. Erro: {e}")
            metrics = process_dataframe(pd.DataFrame(), config)
    elif 'huddle_metrics' in st.session_state:
        st.success(f"Arquivo **{st.session_state['huddle_filename']}** salvo na memória! (Para alterar, faça o upload de outro arquivo acima)")
        metrics = st.session_state['huddle_metrics']
    else:
        st.info("Por favor, importe o arquivo Excel (.xlsx) das OS's para carregar os indicadores.")
        metrics = process_dataframe(pd.DataFrame(), config)

    # BLOCO 2: METRICAS
    st.header("2. Indicadores Huddle Diário")

    # QUADRO 1
    st.subheader("Visão Geral de Chamados")
    c1, c2, c3 = st.columns(3)
    c1.metric("Abertos (Geral)", metrics.get('q1_geral', {}).get('total', 0))
    c2.metric("Infraestrutura (Geral)", metrics.get('q1_geral', {}).get('infra', 0))
    c3.metric("Sistemas (Geral)", metrics.get('q1_geral', {}).get('sist', 0))
    
    st.markdown("##### Fila Ativa (Desconsiderando Conserto Ext. e Aguard. Material)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Fila Ativa (Total)", metrics.get('q1_ativa', {}).get('total', 0))
    c2.metric("Infraestrutura (Fila Ativa)", metrics.get('q1_ativa', {}).get('infra', 0))
    c3.metric("Sistemas (Fila Ativa)", metrics.get('q1_ativa', {}).get('sist', 0))
    c1, c2, c3 = st.columns(3)
    c1.metric("Em Atendimento (Total)", metrics.get('q1_em_atend', {}).get('total', 0))
    c2.metric("Infraestrutura (Em Atend.)", metrics.get('q1_em_atend', {}).get('infra', 0))
    c3.metric("Sistemas (Em Atend.)", metrics.get('q1_em_atend', {}).get('sist', 0))
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Aguard. Atend. (Total)", metrics.get('q1_ag_atend', {}).get('total', 0))
    c2.metric("Infraestrutura (Ag. Atend.)", metrics.get('q1_ag_atend', {}).get('infra', 0))
    c3.metric("Sistemas (Ag. Atend.)", metrics.get('q1_ag_atend', {}).get('sist', 0))

    c1, c2, c3 = st.columns(3)
    c1.metric("Aguard. Liberação Setor (Total)", metrics.get('q1_ag_lib', {}).get('total', 0))
    c2.metric("Infraestrutura (Ag. Lib.)", metrics.get('q1_ag_lib', {}).get('infra', 0))
    c3.metric("Sistemas (Ag. Lib.)", metrics.get('q1_ag_lib', {}).get('sist', 0))
    
    st.markdown("---")
    # QUADRO 2
    st.subheader("Chamados com SLA Vencido (Fila Ativa)")
    c1, c2, c3 = st.columns(3)
    c1.metric("SLA Vencido (Total Geral)", metrics.get('q2_sla_ativo', {}).get('total', 0))
    c2.metric("Infraestrutura (SLA Vencido)", metrics.get('q2_sla_ativo', {}).get('infra', 0))
    c3.metric("Sistemas (SLA Vencido)", metrics.get('q2_sla_ativo', {}).get('sist', 0))
    c1, c2, c3 = st.columns(3)
    c1.metric("Em Atendimento (Total)", metrics.get('q2_sla_em_atend', {}).get('total', 0))
    c2.metric("Infraestrutura (SLA)", metrics.get('q2_sla_em_atend', {}).get('infra', 0))
    c3.metric("Sistemas (SLA)", metrics.get('q2_sla_em_atend', {}).get('sist', 0))
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Aguard. Atendimento (Total)", metrics.get('q2_sla_ag_atend', {}).get('total', 0))
    c2.metric("Infraestrutura (SLA)", metrics.get('q2_sla_ag_atend', {}).get('infra', 0))
    c3.metric("Sistemas (SLA)", metrics.get('q2_sla_ag_atend', {}).get('sist', 0))

    c1, c2, c3 = st.columns(3)
    c1.metric("Aguard. Liberação Setor (Total)", metrics.get('q2_sla_ag_lib', {}).get('total', 0))
    c2.metric("Infraestrutura (SLA)", metrics.get('q2_sla_ag_lib', {}).get('infra', 0))
    c3.metric("Sistemas (SLA)", metrics.get('q2_sla_ag_lib', {}).get('sist', 0))
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("SLA > 3 Dias (Total)", metrics.get('q2_sla_3_dias', {}).get('total', 0))
    c2.metric("Infraestrutura (SLA > 3d)", metrics.get('q2_sla_3_dias', {}).get('infra', 0))
    c3.metric("Sistemas (SLA > 3d)", metrics.get('q2_sla_3_dias', {}).get('sist', 0))
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Ontem p/ Hoje (Ag. Atend.)", metrics.get('chamados_ontem_hoje', 0))
    with c2:
        apoio_dev_manual = st.number_input("Apoio Desenvolvimento", value=0, min_value=0, step=1)
        metrics['apoio_dev_manual'] = apoio_dev_manual
        
    st.markdown("---")
    # QUADRO 3
    st.subheader("Retidos (Conserto Externo e Material)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Retidos (Geral)", metrics.get('q3_retidos', {}).get('total', 0))
    c2.metric("Infraestrutura (Retidos)", metrics.get('q3_retidos', {}).get('infra', 0))
    c3.metric("Sistemas (Retidos)", metrics.get('q3_retidos', {}).get('sist', 0))
    c1, c2, c3 = st.columns(3)
    c1.metric("Conserto Externo (Total)", metrics.get('q3_ce', {}).get('total', 0))
    c2.metric("Infraestrutura (CE)", metrics.get('q3_ce', {}).get('infra', 0))
    c3.metric("Sistemas (CE)", metrics.get('q3_ce', {}).get('sist', 0))
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Aguard. Material (Total)", metrics.get('q3_am', {}).get('total', 0))
    c2.metric("Infraestrutura (AM)", metrics.get('q3_am', {}).get('infra', 0))
    c3.metric("Sistemas (AM)", metrics.get('q3_am', {}).get('sist', 0))

    # BLOCO 3: FORMULÁRIO DE CONDUÇÃO
    st.header("3. Anotações do Huddle")

    # Inicializa variáveis no session_state para não perder texto ao trocar de tela
    for key in ['f_assuntos', 'f_atividades', 'f_adicionais', 'f_problemas', 'f_acionamentos']:
        if key not in st.session_state:
            st.session_state[key] = ""

    c1, c2 = st.columns(2)
    with c1:
        assuntos = st.text_area("Assuntos Discutidos no Dia (Ações/Ferramentas)", value=st.session_state['f_assuntos'])
        atividades = st.text_area("Atividades Planejadas", value=st.session_state['f_atividades'])
        adicionais = st.text_area("Informações Adicionais (Ex: Acompanhar chamados, responsável...)", value=st.session_state['f_adicionais'])
        
        st.session_state['f_assuntos'] = assuntos
        st.session_state['f_atividades'] = atividades
        st.session_state['f_adicionais'] = adicionais
        
    with c2:
        problemas_infra_sist = st.text_area("Temos problemas críticos (Infra ou Sistemas)? (Ex: Lentidão, Impressora pendente)", value=st.session_state['f_problemas'])
        acionamentos = st.text_area("Temos Acionamentos Críticos no Plantão?", value=st.session_state['f_acionamentos'])
        
        st.session_state['f_problemas'] = problemas_infra_sist
        st.session_state['f_acionamentos'] = acionamentos

    # BLOCO 4: ATIVIDADES EM ANDAMENTO
    st.header("4. Atividades em Andamento (Por Analista)")
    analistas_data = {}

    todos_analistas = sorted(config['analistas_infra'] + config['analistas_sistemas'])
    if not todos_analistas:
        st.warning("Nenhum analista configurado. Configure no menu lateral.")
        
    grid_cols = st.columns(2)
    for i, analista in enumerate(todos_analistas):
        col = grid_cols[i % 2]
        with col:
            os_aberta_solic = metrics.get('os_aberta_solic', {}).get(analista, '')
            os_conserto = metrics.get('os_conserto', {}).get(analista, '')
            os_material = metrics.get('os_material', {}).get(analista, '')
            os_liberacao = metrics.get('os_liberacao', {}).get(analista, '')
            
            default_text = ""
            has_content = os_aberta_solic or os_conserto or os_material or os_liberacao
            if has_content:
                default_text = "Ações Pós Huddle:\n"
                if os_aberta_solic:
                    default_text += f"Sequência de Atendimento: {os_aberta_solic}\n"
                if os_conserto:
                    default_text += f"Chamados em Conserto Externo: {os_conserto}\n"
                if os_material:
                    default_text += f"Chamados Aguardando Material: {os_material}\n"
                if os_liberacao:
                    default_text += f"Chamados Aguardando Liberação do Setor: {os_liberacao}\n"
                
            texto = st.text_area(
                f"Analista {analista}", 
                value=default_text.strip(),
                placeholder="Ações Pós Huddle:\nSequência de Atendimento:", 
                height=180
            )
            analistas_data[analista] = texto

    st.markdown("<br>", unsafe_allow_html=True)
    if 'f_reinc' not in st.session_state:
        st.session_state['f_reinc'] = ""
    reincidentes = st.text_area("Chamados Reincidentes", value=st.session_state['f_reinc'], placeholder="Ex: Impressora Farmacia OS 12345, OS 67890", height=100)
    st.session_state['f_reinc'] = reincidentes


    # BLOCO 5: EXPORTAÇÃO E HISTÓRICO
    st.markdown("---")
    
    # Lógica do Histórico (Checkbox de Sobrescrita)
    historico_existe = history_manager.history_exists_for_today()
    sobrescrever = False
    
    if historico_existe and ('huddle_metrics' in st.session_state or uploaded_file is not None):
        st.warning("⚠️ Os indicadores de hoje já foram salvos no histórico. Deseja sobrescrevê-lo com os números atuais?")
        sobrescrever = st.checkbox("Sim, atualizar histórico de hoje", value=False)
        
    if st.button("Gerar Relatório Huddle", use_container_width=True):
        if 'huddle_metrics' not in st.session_state and uploaded_file is None:
            st.error("Por favor, importe o arquivo de chamados primeiro!")
        else:
            form_data = {
                'assuntos_discutidos': assuntos,
                'atividades_planejadas': atividades,
                'problemas_infra_sistemas': problemas_infra_sist,
                'acionamentos_plantao': acionamentos,
                'informacoes_adicionais': adicionais,
                'reincidentes': reincidentes
            }
            
            # Adiciona a média do mês corrente baseada no histórico
            metrics['media_mes'] = history_manager.get_current_month_averages()
            
            data_atual = datetime.now().strftime("%d_%m_%Y")
            pdf_filename = f"Huddle_Diario_TI_{data_atual}.pdf"
            
            try:
                generate_pdf(metrics, form_data, analistas_data, pdf_filename)
                
                # Tratamento do Histórico
                if not historico_existe or sobrescrever:
                    history_manager.save_daily_metrics(metrics)
                    st.success("Relatório gerado com sucesso e Histórico atualizado! 📈")
                else:
                    st.success("Relatório gerado com sucesso! (Histórico NÃO foi modificado) ✅")
                
                with open(pdf_filename, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                    
                st.download_button(
                    label="📥 Baixar PDF",
                    data=pdf_bytes,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")

elif menu == "📈 Evolução e Gráficos":
    st.title("Evolução dos Chamados Helpdesk")
    st.markdown("Acompanhe o comportamento histórico das filas de atendimento ao longo do tempo.")
    
    df_hist = history_manager.load_history()
    
    if df_hist.empty:
        st.info("Nenhum dado histórico encontrado. Gere o seu primeiro relatório Huddle na página principal para começar a formar os gráficos!")
    else:
        min_date = df_hist['Data'].min().date()
        max_date = df_hist['Data'].max().date()
        
        st.subheader("Filtros de Período")
        start_date, end_date = st.date_input(
            "Selecione o Período para analisar (Mensal/Diário):",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY"
        )
        
        # Filtra o dataframe com base na seleção
        if start_date and end_date:
            mask = (df_hist['Data'].dt.date >= start_date) & (df_hist['Data'].dt.date <= end_date)
            df_filtered = df_hist.loc[mask]
        else:
            df_filtered = df_hist
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Média Diária do Período Selecionado")
        c1, c2, c3 = st.columns(3)
        if not df_filtered.empty:
            media_total = int(df_filtered['Abertos Geral'].mean())
            media_infra = int(df_filtered['Infraestrutura'].mean())
            media_sist = int(df_filtered['Sistemas'].mean())
        else:
            media_total = media_infra = media_sist = 0
            
        c1.metric("Média Diária (Total)", media_total)
        c2.metric("Média Diária (Infra)", media_infra)
        c3.metric("Média Diária (Sistemas)", media_sist)
        
        st.markdown("---")
        
        # Set Date as index for plotting using the filtered dataframe
        df_plot = df_filtered.set_index('Data')
        
        if len(df_plot) <= 1:
            st.info("ℹ️ Você possui 1 ou zero dias no período selecionado. Os gráficos de linha precisam de pelo menos 2 dias para desenharem a curva (linha conectando os pontos).")
        
        st.subheader("1. Evolução do Backlog de Chamados")
        cols_backlog = ['Abertos Geral', 'Sistemas', 'Infraestrutura']
        selecao_backlog = st.multiselect("Filtrar linhas:", cols_backlog, default=cols_backlog, key='ms_backlog')
        if selecao_backlog:
            fig1 = px.line(df_plot, y=selecao_backlog, markers=True, labels={'value': 'Quantidade', 'variable': 'Métrica'})
            fig1.update_layout(
                hovermode="x unified", xaxis_title="", yaxis_title="Quantidade", 
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, title=""),
                margin=dict(t=10, b=10)
            )
            fig1.update_xaxes(dtick="D1", tickformat="%d/%m/%Y")
            st.plotly_chart(fig1, use_container_width=True)
        
        st.markdown("---")
        st.subheader("2. Saúde da Fila (SLA Vencido)")
        cols_sla = ['SLA Vencido Total', 'SLA Vencido Sistemas', 'SLA Vencido Infra']
        selecao_sla = st.multiselect("Filtrar linhas:", cols_sla, default=cols_sla, key='ms_sla')
        if selecao_sla:
            fig2 = px.line(df_plot, y=selecao_sla, markers=True, labels={'value': 'Quantidade', 'variable': 'Métrica'})
            fig2.update_layout(
                hovermode="x unified", xaxis_title="", yaxis_title="Quantidade", 
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, title=""),
                margin=dict(t=10, b=10)
            )
            fig2.update_xaxes(dtick="D1", tickformat="%d/%m/%Y")
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        st.subheader("3. Ofensores Externos")
        cols_externos = ['Aguardando Material', 'Conserto Externo', 'Aguardando Liberação Setor']
        selecao_externos = st.multiselect("Filtrar linhas:", cols_externos, default=cols_externos, key='ms_ext')
        if selecao_externos:
            fig3 = px.line(df_plot, y=selecao_externos, markers=True, labels={'value': 'Quantidade', 'variable': 'Métrica'})
            fig3.update_layout(
                hovermode="x unified", xaxis_title="", yaxis_title="Quantidade", 
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, title=""),
                margin=dict(t=10, b=10)
            )
            fig3.update_xaxes(dtick="D1", tickformat="%d/%m/%Y")
            st.plotly_chart(fig3, use_container_width=True)
        
        # Opcional: mostrar a tabela bruta
        with st.expander("Ver Base de Dados Bruta (CSV)"):
            st.dataframe(df_plot)
