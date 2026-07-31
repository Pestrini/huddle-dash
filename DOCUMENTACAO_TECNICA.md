# Documentação Técnica Oficial - Huddle Dash (TI HURP)

## 1. Visão Geral do Sistema
O **Huddle Dash** é uma aplicação web interna desenvolvida com a finalidade de automatizar a extração, o processamento e a geração de indicadores diários (Huddle) da equipe de TI. O sistema lê dados brutos extraídos do sistema de chamados (em formato `.xlsx`), processa regras de negócio (SLA, equipes, ofensores) e gera dois resultados primários:
1. Um relatório `.pdf` oficial, padronizado, pronto para envio para diretoria/gestores.
2. Um banco de dados em formato `.csv` que alimenta painéis gráficos interativos (Business Intelligence) para acompanhamento da saúde da TI ao longo do tempo.

---

## 2. Requisitos do Sistema

### 2.1 Requisitos Funcionais
- **RF01 - Importação de Dados:** O sistema deve permitir que o usuário faça o *upload* de uma planilha `.xlsx` contendo os chamados em andamento.
- **RF02 - Configuração de Equipes:** O sistema deve permitir atribuir visualmente os analistas às equipes de **Infraestrutura** ou **Sistemas**.
- **RF03 - Cálculo de Métricas:** O sistema deve calcular indicadores em tempo real, como: total de abertos, SLA vencido, chamados em atraso > 3 dias, etc.
- **RF04 - Geração de PDF:** O sistema deve gerar e exportar um relatório em formato `.pdf` com as métricas calculadas e respostas do usuário (Anotações do Huddle).
- **RF05 - Histórico e BI (Business Intelligence):** O sistema deve registrar as métricas diárias em um histórico persistente e renderizar gráficos de evolução filtráveis.
- **RF06 - Proteção de Dados:** O sistema deve alertar o usuário caso tente salvar o histórico mais de uma vez no mesmo dia, prevenindo sobreposição acidental.

### 2.2 Requisitos Não Funcionais
- **RNF01 - Portabilidade:** O sistema deve ser executável em qualquer máquina Windows através de um simples clique (script `.bat`).
- **RNF02 - Autoinstalação:** O script de execução deve ser capaz de verificar, baixar e instalar o Python e suas dependências automaticamente, sem exigir conhecimentos técnicos do usuário.
- **RNF03 - Desempenho:** O processamento da planilha `.xlsx` e a geração do PDF devem ocorrer em questão de segundos.
- **RNF04 - Interface:** A interface web deve ser amigável e seguir uma identidade visual padrão corporativa (Verde Unimed).

---

## 3. Arquitetura e Bibliotecas (requirements.txt)

O sistema foi construído sobre a linguagem **Python**. Abaixo, as bibliotecas (pacotes) centrais que sustentam a aplicação:

- **`streamlit` (Framework Web):** Responsável por criar toda a interface visual (botões, uploads, painéis) sem necessidade de escrever HTML/CSS complexo. O Streamlit re-executa o script do topo ao fim sempre que o usuário interage com um botão.
- **`pandas` (Motor de Dados):** Biblioteca de altíssimo desempenho para leitura e manipulação de tabelas. Usado extensivamente para filtrar colunas do Excel, contar chamados por status, equipe e prazos.
- **`openpyxl` (Leitor Excel):** Dependência secundária do Pandas que fornece a capacidade técnica de ler arquivos com extensão `.xlsx`.
- **`fpdf2` (Gerador de PDF):** Biblioteca que permite programar a escrita de um documento PDF, desenhando tabelas, textos e posicionando imagens em coordenadas exatas (X e Y) no papel (A4).
- **`plotly` (Motor Gráfico Interativo):** Biblioteca avançada (`plotly.express`) utilizada na aba de Business Intelligence para desenhar gráficos de linha interativos que suportam marcadores, filtros e *tooltips* ao passar o mouse.

---

## 4. Estrutura de Arquivos e Componentes

### 4.1. `main.py`
É o **coração** (arquivo principal) da aplicação visual. É ele quem o Streamlit executa.
- **Sessão 1 (Estilo e Navegação):** Injeta um bloco de CSS (linguagem de estilo) para alterar a cor dos botões para Verde e criar efeitos visuais de sombra. Em seguida, desenha o menu lateral de navegação (Huddle Diário vs Evolução e Gráficos).
- **Sessão 2 (Gerenciador de Equipes):** Fica no menu lateral. Lê o arquivo `config.json` e permite que o usuário adicione ou remova nomes das caixas de "Sistemas" e "Infraestrutura".
- **Sessão 3 (Página Inicial - Huddle Diário):**
  - Solicita o *upload* da planilha `.xlsx`.
  - Passa o arquivo recebido para o `data_processor.py`.
  - Renderiza painéis (cards de métricas) exibindo as variáveis numéricas devolvidas (ex: `Total SLA Vencido`).
  - Cria caixas de texto (inputs) para as anotações diárias (Problemas Críticos, Ações em Andamento).
  - Executa o botão de Salvar Histórico (acionando o `history_manager.py`) e o botão de Gerar PDF (acionando o `report_generator.py`).
- **Sessão 4 (Página Evolução e Gráficos):** Carrega o CSV de histórico e usa o `plotly` para plotar 3 gráficos principais, habilitando caixas de seleção (filtros multi-seleção) para cada um deles.

### 4.2. `data_processor.py`
É o **cérebro matemático** do sistema. Ele não tem interface gráfica; recebe uma tabela crua do Pandas e devolve um dicionário de números mastigados.
- **Variáveis Chaves e Dicionário de Retorno:** Caso a tabela venha vazia, ele devolve imediatamente um dicionário com todos os valores zerados (ex: `{'total_sla_vencido': 0}`).
- **Função `get_equipe`:** Analisa cada linha do Excel. Observa a coluna "Responsável" (Analista) e compara com o dicionário do `config.json` para carimbar o chamado como sendo de "Infraestrutura" ou "Sistemas".
- **Tratamento de Datas:** Descobre quando foi "Ontem" (Regra 5), ignorando fins de semana (se hoje for Segunda, ontem foi Sexta-feira). Converte as strings de texto em objetos de Data reais do Python.
- **Regras de Negócio (Exclusões):**
  - `nao_conserto`: Ignora linhas onde o status é 'CONSERTO EXTERNO'.
  - `aberta_ou_solicitacao`: Isola estritamente os chamados aguardando atendimento em primeiro nível de suporte.
  - `older_3_days_cond`: Conta o relógio para trás e identifica tickets parados há mais de 72h.

### 4.3. `history_manager.py`
É o **guardião do Banco de Dados**. Ele escreve e lê dados.
- Utiliza um arquivo chamado `historico_huddle.csv`. O formato `.csv` foi escolhido por ser levíssimo, à prova de corrupções complexas e lido como texto simples (texto puro separado por vírgulas).
- **`save_history(metrics)`:** Extrai os totais diários (Geral, SLA, CE) e grava em uma nova linha no final do CSV, acompanhados da data de hoje.
- **`history_exists_for_today()`:** Função de segurança para conferir se o arquivo já possui uma linha escrita na data corrente (evitando gerar relatórios duplicados em dias de teste).

### 4.4. `report_generator.py`
É a **máquina de impressão**. Usa a biblioteca `fpdf2` (que utiliza conceitos de classe PDF orientada a objetos).
- **Header e Footer (Cabeçalho e Rodapé):** O arquivo sobrescreve métodos nativos do FPDF para que toda página criada injete as imagens `cabecalho 2026.png` e `rodape 2026.png` no topo e no fundo da folha.
- **`print_metric_row`:** Função auxiliar criada para evitar repetição de código. Ela desenha uma borda (retângulo), pinta uma cor de fundo, escreve o título do indicador à esquerda e preenche o número exato à direita.
- No final, ele lê os textos preenchidos pelo usuário e gera laços de repetição (`for analista, texto in analistas_data.items()`) para imprimir as atividades listadas por analista. O resultado final é "cuspido" (exportado) como bytes do arquivo gerado para o navegador baixar.

### 4.5. `run_dashboard.bat` (O Operário Silencioso)
Este arquivo em **Batch** (linguagem de script do Windows) é a cola que une todo o projeto de infraestrutura de TI do usuário comum.
1. `cd /d "%~dp0"`: Garante que, mesmo que o arquivo seja aberto a partir de atalhos em rede (Drive G:), ele direcione a execução do terminal para o diretório raiz correto onde os arquivos estão fisicamente salvos.
2. Faz o teste do `python --version`. Se falhar, usa a ferramenta `curl` para baixar o instalador oficial e instala silenciosamente no Windows da máquina (ideal para novos estagiários/funcionários).
3. Executa `pip install -r requirements.txt`, que vasculha a biblioteca local da máquina e instala apenas o que estiver faltando (processo inteligente e rápido).
4. Sobe o servidor web via comando `python -m streamlit run main.py`.

---

## 5. Como Manter e Evoluir
- **Adicionar Novos Gráficos:** Para criar um gráfico sobre um novo assunto, vá no `history_manager.py` e inclua o indicador na lista `COLUMNS`. Em seguida, mande gravar o valor na função `save_history`. Por último, modifique o `main.py` na Sessão 4 para plotar a nova coluna usando o `plotly.express`.
- **Mudar Regras Contábeis:** Qualquer alteração no modo como o SLA ou Backlog é filtrado ou descartado deve ser feito exclusivamente no `data_processor.py`. As outras pontas do sistema se atualizarão automaticamente ao receber os valores corrigidos deste arquivo.
