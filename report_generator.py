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

    # ---------------- QUADROS DE MÉTRICAS ----------------
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, 'POSICIONAMENTO HUDDLE', ln=True, align='C')
    pdf.ln(2)
    
    col_status_w = 95
    col_num_w = 30
    
    def print_quadro_header(title):
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(col_status_w + (col_num_w * 3), 8, title, border=1, ln=True, align='C', fill=True)
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(col_status_w, 6, 'STATUS', border=1, align='C', fill=True)
        pdf.cell(col_num_w, 6, 'TOTAL', border=1, align='C', fill=True)
        pdf.cell(col_num_w, 6, 'INFRA', border=1, align='C', fill=True)
        pdf.cell(col_num_w, 6, 'SISTEMAS', border=1, align='C', fill=True)
        pdf.ln(6)
        
    def print_quadro_row(status, total, infra, sist, is_bold=False):
        pdf.set_font("Arial", 'B' if is_bold else '', 8)
        pdf.cell(col_status_w, 6, str(status), border=1)
        pdf.set_font("Arial", '', 9)
        pdf.cell(col_num_w, 6, str(total), border=1, align='C')
        pdf.cell(col_num_w, 6, str(infra), border=1, align='C')
        pdf.cell(col_num_w, 6, str(sist), border=1, align='C')
        pdf.ln(6)
        
    def g(q, key):
        return metrics.get(q, {}).get(key, 0)
        
    # QUADRO 1
    print_quadro_header('QUADRO 1: VISÃO GERAL DE CHAMADOS')
    print_quadro_row('Total Chamados (todos os status)', g('q1_geral', 'total'), g('q1_geral', 'infra'), g('q1_geral', 'sist'), True)
    
    media_mes = metrics.get('media_mes', {'total': 0, 'infra': 0, 'sist': 0})
    print_quadro_row('Média Diária (Mês Atual)', media_mes.get('total', 0), media_mes.get('infra', 0), media_mes.get('sist', 0), True)
    
    print_quadro_row('TOTAL FILA ATIVA (Sem Conserto Externo e Aguardando Material)', g('q1_ativa', 'total'), g('q1_ativa', 'infra'), g('q1_ativa', 'sist'), True)
    print_quadro_row('   -> Em Atendimento', g('q1_em_atend', 'total'), g('q1_em_atend', 'infra'), g('q1_em_atend', 'sist'))
    print_quadro_row('   -> Aguardando Atendimento', g('q1_ag_atend', 'total'), g('q1_ag_atend', 'infra'), g('q1_ag_atend', 'sist'))
    print_quadro_row('   -> Aguardando Liberação Setor', g('q1_ag_lib', 'total'), g('q1_ag_lib', 'infra'), g('q1_ag_lib', 'sist'))
    pdf.ln(3)
    
    # QUADRO 2
    print_quadro_header('QUADRO 2: CHAMADOS COM SLA VENCIDO')
    print_quadro_row('TOTAL SLA VENCIDO (FILA ATIVA)', g('q2_sla_ativo', 'total'), g('q2_sla_ativo', 'infra'), g('q2_sla_ativo', 'sist'), True)
    print_quadro_row('   -> Em Atendimento', g('q2_sla_em_atend', 'total'), g('q2_sla_em_atend', 'infra'), g('q2_sla_em_atend', 'sist'))
    print_quadro_row('   -> Aguardando Atendimento', g('q2_sla_ag_atend', 'total'), g('q2_sla_ag_atend', 'infra'), g('q2_sla_ag_atend', 'sist'))
    print_quadro_row('   -> Aguardando Liberação Setor', g('q2_sla_ag_lib', 'total'), g('q2_sla_ag_lib', 'infra'), g('q2_sla_ag_lib', 'sist'))
    print_quadro_row('Chamados de ontem para Hoje (Aguard. Atendimento)', metrics.get('chamados_ontem_hoje', 0), '-', '-')
    print_quadro_row('SLA Vencido > 3 dias', g('q2_sla_3_dias', 'total'), g('q2_sla_3_dias', 'infra'), g('q2_sla_3_dias', 'sist'))
    pdf.ln(3)

    # QUADRO 3
    print_quadro_header('QUADRO 3: RETIDOS (CONSERTO E MATERIAL)')
    print_quadro_row('TOTAL RETIDOS', g('q3_retidos', 'total'), g('q3_retidos', 'infra'), g('q3_retidos', 'sist'), True)
    print_quadro_row('   -> Conserto Externo', g('q3_ce', 'total'), g('q3_ce', 'infra'), g('q3_ce', 'sist'))
    print_quadro_row('   -> Aguardando Material', g('q3_am', 'total'), g('q3_am', 'infra'), g('q3_am', 'sist'))
    pdf.ln(5)
    
    # ---------------- TEXTOS LIVRES ----------------
    pdf.add_page()
    print_section('ASSUNTOS DISCUTIDOS NO DIA:', form_data.get('assuntos_discutidos', ''))
    print_section('TEMOS PROBLEMAS CRÍTICOS (INFRA OU SISTEMAS)?', form_data.get('problemas_infra_sistemas', 'Sem ocorrências'))
    print_section('TEMOS ACIONAMENTOS CRÍTICOS NO PLANTÃO?', form_data.get('acionamentos_plantao', 'Sem ocorrências'))
    print_section('ATIVIDADES PLANEJADAS:', form_data.get('atividades_planejadas', ''))
    print_section('INFORMAÇÕES ADICIONAIS:', form_data.get('informacoes_adicionais', ''))
    
    # Se precisar de Apoio Dev, colocar nas info adicionais pra não perder
    apoio_dev = metrics.get('sugestao_apoio_dev', 0)
    if apoio_dev > 0:
        print_section('APOIO DESENVOLVIMENTO:', f"Sugerido avaliar {apoio_dev} chamados da equipe de Sistemas.")

    pdf.add_page()
    
    pdf.ln(10)
    
    # Atividades em Andamento
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'ATIVIDADES EM ANDAMENTO:', ln=True)
    pdf.ln(2)
    
    for analista, texto in analistas_data.items():
        if texto and texto.strip():
            texto = texto.replace('\u2013', '-').replace('\u2014', '-')
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 6, f'ANALISTA {analista.upper()}', ln=True)
            pdf.set_font("Arial", '', 10)
            
            if '🔴' in texto:
                import re
                # Prepara o HTML e faz o parse da bolinha vermelha para a tag HTML da fonte
                html_texto = texto.replace('\n', '<br>')
                # Remove o icone 🔴 e coloca o que vier depois (a OS) em vermelho
                # Match números e possíveis letras da OS
                html_texto = re.sub(r'🔴\s*([A-Za-z0-9_-]+)', r'<font color="#ff0000">\1</font>', html_texto)
                
                # Falha segura: remove qualquer bolinha residual que a regex não tenha pego, 
                # pois emojis quebram o parser do FPDF (helvetica/latin-1)
                html_texto = html_texto.replace('🔴', '')
                
                # FPDF write_html pode quebrar com encodes não suportados
                html_texto = html_texto.encode('latin-1', 'replace').decode('latin-1')
                
                pdf.write_html(html_texto)
                pdf.ln(5)
            else:
                texto = texto.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 5, texto)
                pdf.ln(5)
            
    # Chamados Reincidentes
    reincidentes = form_data.get('reincidentes', '')
    if reincidentes and reincidentes.strip():
        reincidentes = reincidentes.replace('\u2013', '-').replace('\u2014', '-')
        reincidentes = reincidentes.encode('latin-1', 'replace').decode('latin-1')
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(200, 0, 0) # Red color for the title to stand out
        pdf.cell(0, 6, 'CHAMADOS REINCIDENTES', ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 5, reincidentes)
        pdf.ln(5)
    pdf.output(output_path)
    return output_path
