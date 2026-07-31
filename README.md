# Huddle Diário TI - Dashboard (v0.5)

![Streamlit](https://img.shields.io/badge/Streamlit-1.37.0-FF4B4B.svg?style=flat&logo=Streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.2.2-150458.svg?style=flat&logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-5.23.0-3F4F75.svg?style=flat&logo=plotly)
![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python)

Este é um sistema Web interno desenvolvido em **Python (Streamlit + Pandas + Plotly)** projetado para automatizar a extração de métricas de relatórios de chamados (Service Desk) e gerar, instantaneamente, o documento em PDF de posicionamento diário da TI, conhecido como **Huddle**.

O Huddle é uma prática ágil para reuniões rápidas e diárias de alinhamento. Este sistema reduz o tempo de confecção do relatório de 40 minutos para menos de 3 minutos, eliminando tarefas manuais repetitivas e garantindo um layout padronizado.

## ✨ Funcionalidades
- **Importação Dinâmica:** Drag and Drop de arquivo `.xlsx` (Excel) bruto do seu sistema de chamados.
- **Processamento Rápido:** Backend que analisa os chamados em tempo real (Geral, Sistemas, Infraestrutura, SLA Vencido, etc).
- **Gerenciador de Equipes:** Configuração visual integrada para definir quais analistas são de Infraestrutura e Sistemas.
- **Módulo de Business Intelligence:** Tela dedicada com histórico em `.csv` e gráficos interativos (Plotly) acompanhando a evolução dos indicadores da TI.
- **Relatório PDF Oficial:** Geração do documento em `.pdf` espelhando layouts corporativos exatos, incluindo cabeçalhos, rodapés, tabelas e anotações.

## 📦 Notas de Lançamento (Release v0.5)
- **Regra de Negócio:** "SLA Vencido > 3 Dias" agora passa a abranger a fila global (todos os status) para maior precisão de backlog antigo.
- **Layout:** Reestruturação do painel principal, elevando o "Total SLA Vencido" (incluindo Aguardando Material) para a linha de frente, e movendo a visão restrita para o rodapé.
- **Correção:** Resolvido o bug de `KeyError` ao iniciar a interface pela primeira vez sem dados.

## 📦 Notas de Lançamento (Release v0.4)
- **Novo:** Tela de "Evolução e Gráficos" para acompanhamento da saúde da fila de TI ao longo dos meses.
- **Novo:** Trava de segurança anti-duplicação na geração de relatórios diários.
- **Novo:** Botões unificados usando a paleta de cores institucional.
- **Melhoria:** Migração dos gráficos nativos do Streamlit para o Plotly Express (ferramentas de zoom, tooltip inteligente, etc).
- **Correção:** Ajustes estruturais nas colunas do relatório (Conserto Externo, Aguardando Material, Aguardando Liberação Setor).

## 🚀 Como instalar e rodar localmente

### Pré-requisitos
- Sistema Operacional Windows.
- Opcional: Python 3.10+ instalado no PATH (Caso não possua, o script `.bat` cuidará de baixar e instalar automaticamente de forma silenciosa).

### Passos
1. Clone este repositório.
2. Na pasta raiz, dê um duplo clique no arquivo `run_dashboard.bat`.
3. O script irá instalar o Python (caso não exista), criar um ambiente isolado, baixar as dependências (`streamlit`, `pandas`, `fpdf2`) e abrir uma janela no seu navegador.
4. Para as próximas execuções, basta abrir o mesmo `.bat`.

## 🛠️ Como adaptar para sua Empresa

Você pode usar o esqueleto deste projeto para o Service Desk da sua empresa com facilidade!

1. **Cabeçalho e Rodapé:** 
   Substitua os arquivos `cabecalho 2026.png` e `rodape 2026.png` na raiz do projeto pelas imagens da sua instituição (Recomendado imagens com ~1000px de largura).
2. **Lógica de Colunas (CSV):**
   O projeto atual lê um `.csv` com colunas específicas (`Prioridade`, `SLA Vencido`, `Status`, `Tipo Solicitação`, `Responsável`, etc.). Para adaptar aos relatórios exportados do seu sistema (Zendesk, GLPI, ServiceNow, etc.), basta editar a classe de processamento no arquivo `data_processor.py`.
3. **Métricas Huddle:**
   Se as perguntas do seu Huddle forem diferentes, altere a parte de "Anotações do Huddle" diretamente em `main.py` (Bloco 3) e o layout de impressão em `report_generator.py`.

## 📞 Suporte e Contato

Dúvidas sobre o funcionamento, implantação corporativa ou sugestões de melhorias? Entre em contato:

**Gabriel Pestrini**
- ✉️ Email: [gabriel.pestrini@unimedribeirao.com.br](mailto:gabriel.pestrini@unimedribeirao.com.br)
- 📸 Instagram: [@gpestrini](https://instagram.com/gpestrini)
