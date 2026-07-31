import os
from fpdf import FPDF
from datetime import datetime

class HuddlePDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configura as margens: esquerda, superior (topo da página para os textos), direita
        self.set_margins(left=10, top=45, right=10)
        # Margem inferior para o auto-page-break
        self.set_auto_page_break(auto=True, margin=35)
        
    def header(self):
        # Header image (width 210mm covers entire A4 width)
        header_path = os.path.join(os.path.dirname(__file__), 'cabecalho 2026.png')
        if os.path.exists(header_path):
            self.image(header_path, x=0, y=0, w=210)
        
    def footer(self):
        # Footer image (width 210mm covers entire A4 width)
        footer_path = os.path.join(os.path.dirname(__file__), 'rodape 2026.png')
        # Posição calculada
        self.set_y(-35)
        if os.path.exists(footer_path):
            # Forçando a imagem a ultrapassar levemente a borda inferior para eliminar a linha branca no PDF viewer
            self.image(footer_path, x=0, y=265, w=210, h=33)

def generate_pdf(metrics, form_data, analistas_data, output_path):
    pdf = HuddlePDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    
    # Title
    pdf.cell(0, 10, 'RELATÓRIO HUDDLE DIÁRIO', ln=True, align='C')
    pdf.ln(5)
    
    # Tabela 1: Área, Unidade, Data
    pdf.set_font("Arial", 'B', 10)
    
    # Header da tabela (ajustado para caber textos longos)
    col_width = [60, 95, 35]
    row_height = 8
    
    pdf.cell(col_width[0], row_height, 'ÁREA', border=1, align='C')
    pdf.cell(col_width[1], row_height, 'UNIDADE', border=1, align='C')
    pdf.cell(col_width[2], row_height, 'DATA', border=1, align='C')
    pdf.ln(row_height)
    
    pdf.set_font("Arial", '', 9)
    pdf.cell(col_width[0], row_height, 'TECNOLOGIA DA INFORMAÇÃO', border=1, align='C')
    pdf.cell(col_width[1], row_height, 'HURP - HOSPITAL UNIMED RIBEIRÃO PRETO', border=1, align='C')
    
    data_str = datetime.today().strftime('%d/%m/%Y')
    pdf.cell(col_width[2], row_height, data_str, border=1, align='C')
    pdf.ln(row_height * 2)
    
    # Objetivo
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(20, 5, 'OBJETIVO: ')
    pdf.set_font("Arial", '', 10)
    objetivo = "Promover discussão rápida e objetiva com o envolvimento dos colaboradores da Equipe de TI buscando soluções através do aprimoramento da comunicação entre os processos, e solucionar todos os problemas operacionais com impacto nos serviços de tecnologia da instituição."
    pdf.multi_cell(0, 5, objetivo)
    pdf.ln(5)
    
    # Helper to print sections
    def print_section(title, content):
        title = title.replace('\u2013', '-').replace('\u2014', '-')
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Arial", '', 10)
        if content and content.strip():
            content = content.replace('\u2013', '-').replace('\u2014', '-')
            # Para evitar mais crashes com FPDF e UTF-8 não suportado no latin-1:
            content = content.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, content)
        else:
            pdf.cell(0, 5, 'Nenhum registro.', ln=True)
        pdf.ln(5)
        
    print_section('ASSUNTOS DISCUTIDOS NO DIA:', form_data.get('assuntos_discutidos', ''))
    print_section('ATIVIDADES PLANEJADAS:', form_data.get('atividades_planejadas', ''))
    print_section('PONTOS DE ATENÇÃO - PROBLEMAS CRÍTICOS:', form_data.get('problemas_criticos', ''))
    print_section('INFORMAÇÕES ADICIONAIS:', form_data.get('informacoes_adicionais', ''))
    
    pdf.add_page()
    
    # Posicionamento Huddle Table
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, 'POSICIONAMENTO HUDDLE', ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 8)
    # Aumentando a largura da primeira coluna para caber o texto gigante sem transbordar
    col1_w, col2_w = 150, 40
    
    def print_metric_row(label, value):
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(col1_w, 8, label, border=1)
        pdf.set_font("Arial", '', 9)
        pdf.cell(col2_w, 8, str(value), border=1, align='C')
        pdf.ln(8)
        
    print_metric_row('CHAMADOS ABERTOS GERAL', metrics.get('chamados_abertos_geral', 0))
    print_metric_row('CHAMADOS DE SISTEMAS', metrics.get('chamados_sistemas', 0))
    print_metric_row('CHAMADOS DE INFRAESTRUTURA', metrics.get('chamados_infra', 0))
    print_metric_row('CHAMADOS QUE PRECISAM APOIO DESENVOLVIMENTO', metrics.get('apoio_dev_manual', 0))
    print_metric_row('TOTAL CHAMADOS SLA VENCIDO DESCONSIDERANDO CONSERTO EXTERNO', metrics.get('sla_vencido_sem_ce', 0))
    print_metric_row('CHAMADOS INFRA SLA VENCIDO', metrics.get('infra_sla_vencido', 0))
    print_metric_row('CHAMADOS SISTEMAS SLA VENCIDO', metrics.get('sistemas_sla_vencido', 0))
    print_metric_row('CHAMADOS SLA VENCIDO A MAIS DE 03 DIAS', metrics.get('sla_vencido_3_dias', 0))
    print_metric_row('CHAMADOS DO FINAL DO DIA PARA OUTRO - ONTEM PARA HOJE', metrics.get('chamados_ontem_hoje', 0))
    
    # Extra Questions inside table
    pdf.set_font("Arial", 'B', 9)
    x1, y1 = pdf.get_x(), pdf.get_y()
    pdf.cell(col1_w, 16, 'TEMOS PROBLEMAS CRÍTICOS (INFRA OU SISTEMAS)?', border=1)
    
    # Desenhando a celula vazia inteira para garantir a borda total do mesmo tamanho
    x2, y2 = pdf.get_x(), pdf.get_y()
    pdf.cell(col2_w, 16, '', border=1)
    
    # Posicionando o texto sem borda no meio do retangulo
    pdf.set_xy(x2, y2 + 4)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(col2_w, 8, form_data.get('problemas_infra_sistemas', '') or 'Sem ocorrências', border=0, align='C')
    pdf.set_xy(10, y1 + 16)
    
    pdf.set_font("Arial", 'B', 9)
    x1, y1 = pdf.get_x(), pdf.get_y()
    pdf.cell(col1_w, 16, 'TEMOS ACIONAMENTOS CRÍTICOS NO PLANTÃO?', border=1)
    
    x2, y2 = pdf.get_x(), pdf.get_y()
    pdf.cell(col2_w, 16, '', border=1)
    
    pdf.set_xy(x2, y2 + 4)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(col2_w, 8, form_data.get('acionamentos_plantao', '') or 'Sem ocorrências', border=0, align='C')
    pdf.set_xy(10, y1 + 16)
    
    pdf.ln(10)
    
    # Atividades em Andamento
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'ATIVIDADES EM ANDAMENTO:', ln=True)
    pdf.ln(2)
    
    for analista, texto in analistas_data.items():
        if texto and texto.strip():
            texto = texto.replace('\u2013', '-').replace('\u2014', '-')
            texto = texto.encode('latin-1', 'replace').decode('latin-1')
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 6, f'ANALISTA {analista.upper()}', ln=True)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 5, texto)
            pdf.ln(5)
            
    pdf.output(output_path)
    return output_path
