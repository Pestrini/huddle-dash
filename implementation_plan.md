# Plano de Implementação - Nova Estrutura de Status (Aguardando Atendimento)

Este plano descreve as mudanças necessárias para adaptar o sistema ao novo arquivo de pendências, que introduz o status "Aguardando Atendimento" no lugar de "Solicitação", e muda a semântica do status "Aberta".

## ⚠️ User Review Required

### Dúvidas Críticas para a Regra de Negócio:

1. **Indicador "Chamados Ontem p/ Hoje":** Atualmente ele usa a regra de (Aberta ou Solicitação). Ele deve continuar somando os dois (Aberta + Aguardando Atendimento) ou deve contar apenas um deles?
"Deve continuar somando os dois"
2. **Total SLA Vencido (Restrito):** No painel oculto lá embaixo, temos o "Total SLA Vencido (Abertas)". Ele deverá somar apenas as "Abertas" ou deverá somar "Abertas + Aguardando Atendimento"?
"Deve somar apenas abertas e adicionar um indicador novo com as aguardando atendimento"
3. **Migração do CSV Histórico:** Ao adicionar o indicador "Aguardando Atendimento" no histórico, os dias anteriores (que não possuíam essa métrica) ficarão com o valor `0`. Isso está de acordo para você?
"Sim de acordo"
4. **Espaço no PDF:** Se adicionarmos os 2 novos indicadores de SLA Vencido (Aguardando Atendimento) no PDF, a tabela vai crescer. Não tem problema empurrar um pouco o texto para baixo?
"Não tem problema"

## 📝 Proposed Changes

### `data_processor.py`
- [MODIFY] Atualizar a leitura dos status. Remover `SOLICITAÇÃO` e incluir `AGUARDANDO ATENDIMENTO`.
- [MODIFY] Criar uma nova variável `apenas_aberta = status_upper == 'ABERTA'`
- [MODIFY] Criar uma nova variável `apenas_aguardando = status_upper == 'AGUARDANDO ATENDIMENTO'`
- [NEW] Criar indicadores `infra_sla_vencido_aguardando` e `sistemas_sla_vencido_aguardando`.
- [MODIFY] Ajustar os indicadores antigos (`infra_sla_vencido`, `sistemas_sla_vencido`) para considerarem apenas `apenas_aberta` (conforme sua explicação de que agora "Aberta" significa em atendimento).
- [NEW] Adicionar os novos indicadores no dicionário de retorno `metrics`.

### `main.py`
- [MODIFY] Adicionar uma nova linha no "BLOCO 2: METRICAS" para exibir os 2 novos cards (`Infra SLA Vencido (Aguardando Atendimento)` e `Sistemas SLA Vencido (Aguardando Atendimento)`). "Essas novas métricas devem aparecer ao lado dos outros indicadores de SLA vencido abertas para facil visualização. De preferencia antes do de sla vencido 3 dias."
- [MODIFY] Renomear os labels dos cards antigos para deixar claro que são referentes a "Em Atendimento" ou "Abertas".

### `report_generator.py`
- [MODIFY] Adicionar as duas novas linhas na tabela PDF:
  - `CHAMADOS INFRA SLA VENCIDO (AGUARDANDO ATENDIMENTO)`
  - `CHAMADOS SISTEMAS SLA VENCIDO (AGUARDANDO ATENDIMENTO)`

### `history_manager.py` & `historico_huddle.csv`
- [MODIFY] Atualizar a lista `COLUMNS` no gerenciador para incluir as novas colunas de histórico de Aguardando Atendimento.
- [MODIFY] Injetar as novas colunas no cabeçalho do arquivo CSV existente (e preencher com `0` nas linhas dos dias anteriores para não quebrar a leitura dos gráficos).

## 🧪 Verification Plan

- Realizarei as alterações e em seguida pedirei para você fazer o upload do **novo arquivo Excel** na tela.
- Iremos gerar o PDF para garantir que os novos indicadores apareçam na tabela.
- Iremos abrir a tela de Evolução e Gráficos para garantir que os novos campos apareçam para filtro no Plotly sem quebrar os dados do passado.
