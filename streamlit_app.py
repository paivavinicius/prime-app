import streamlit as st
import pandas as pd

# Carregar os dados formatados
df_leads = pd.read_csv('leads_formatado.csv')
df_vendas = pd.read_csv('vendas_com_produto.csv')

# Lista de diretores conhecidos
diretores_conhecidos = [
    'Erico_prime', 'Fabiano.caetano_prime', 'Piazitto_primedd', 'Mario_primedd', 'Patricia.marques.prime',
    'Fernando.rocha_primeeee', 'Natane_primee', 'James_prime', 'Fraga_prime', 'William_primedd',
    'Fortuna_prime', 'Leonardo_Prime'
]

# Adicionar a categoria "Outros" para diretores não conhecidos
df_leads['Diretor_Categorizado'] = df_leads['Diretor'].apply(lambda x: x if x in diretores_conhecidos else 'Outros')
df_leads['Lead.CorretorNaoConversao__r.Account.Owner.Name'] = df_leads['Lead.CorretorNaoConversao__r.Account.Owner.Name'].apply(lambda x: x if x in diretores_conhecidos else 'Outros')
df_vendas['Owner.Account.Owner.Name'] = df_vendas['Owner.Account.Owner.Name'].apply(lambda x: x if x in diretores_conhecidos else 'Outros')

# Configuração da interface
st.title('Análise de Leads Mensal')

# Seleção dos filtros com múltipla seleção e opção "Todos"
anos = sorted(df_leads['CreatedDate_Ano'].unique())
diretores_selecionados = st.sidebar.multiselect('Selecione o Diretor', ['Todos'] + diretores_conhecidos, default='Todos')
ano_selecionado = st.sidebar.selectbox('Selecione o Ano', ['Todos'] + anos, index=0)

# Filtrar dados de leads com base na seleção do usuário
df_filtrado_leads = df_leads.copy()
df_filtrado_nao_convertidos = df_leads.copy()

if 'Todos' not in diretores_selecionados:
    df_filtrado_leads = df_filtrado_leads[df_filtrado_leads['Diretor_Categorizado'].isin(diretores_selecionados)]
    df_filtrado_nao_convertidos = df_filtrado_nao_convertidos[df_filtrado_nao_convertidos['Lead.CorretorNaoConversao__r.Account.Owner.Name'].isin(diretores_selecionados)]

if ano_selecionado != 'Todos':
    df_filtrado_leads = df_filtrado_leads[df_filtrado_leads['CreatedDate_Ano'] == ano_selecionado]
    df_filtrado_nao_convertidos = df_filtrado_nao_convertidos[df_filtrado_nao_convertidos['CreatedDate_Ano'] == ano_selecionado]

# Filtrar dados de vendas com base na seleção do usuário
df_filtrado_vendas = df_vendas.copy()

if 'Todos' not in diretores_selecionados:
    df_filtrado_vendas = df_filtrado_vendas[df_filtrado_vendas['Owner.Account.Owner.Name'].isin(diretores_selecionados)]

if ano_selecionado != 'Todos':
    df_filtrado_vendas = df_filtrado_vendas[df_filtrado_vendas['CreatedDate_Ano'] == ano_selecionado]

# Contar a quantidade de leads ativos por mês
contagem_leads_ativos = df_filtrado_leads.groupby(['CreatedDate_Mes']).size().reset_index(name='Qtd_Leads_Ativos')

# Contar a quantidade de leads não convertidos por mês
contagem_nao_convertidos = df_filtrado_nao_convertidos[df_filtrado_nao_convertidos['Lead.Status'] == 'Não Convertido'].groupby(['CreatedDate_Mes']).size().reset_index(name='Qtd_Nao_Convertidos')

# Calcular Leads Totais
contagem_leads_totais = pd.merge(contagem_leads_ativos, contagem_nao_convertidos, on='CreatedDate_Mes', how='outer').fillna(0)
contagem_leads_totais['Qtd_Leads_Totais'] = contagem_leads_totais['Qtd_Leads_Ativos'] + contagem_leads_totais['Qtd_Nao_Convertidos']

# Contar a quantidade de visitas da loja por mês, filtrando por diretor corretamente
df_visitas = df_leads.dropna(subset=['Lead.DataVisitaLoja__c']).copy()
df_visitas['Visitas_Diretor'] = df_visitas.apply(
    lambda row: row['Lead.CorretorNaoConversao__r.Account.Owner.Name'] if row['Lead.Status'] == 'Não Convertido' else row['Diretor_Categorizado'],
    axis=1
)

# Aplicar filtros às visitas
if 'Todos' not in diretores_selecionados:
    df_visitas = df_visitas[df_visitas['Visitas_Diretor'].isin(diretores_selecionados)]

if ano_selecionado != 'Todos':
    df_visitas = df_visitas[df_visitas['Lead.DataVisitaLoja__c_Ano'] == ano_selecionado]

# Contar visitas por mês
contagem_visitas_loja = df_visitas.groupby(['Lead.DataVisitaLoja__c_Mes'])['LeadId'].nunique().reset_index(name='Qtd_Visitas_Loja')
contagem_visitas_loja['CreatedDate_Mes'] = contagem_visitas_loja['Lead.DataVisitaLoja__c_Mes']

# Contar oportunidades por mês
contagem_oportunidades = df_filtrado_vendas.groupby(['CreatedDate_Mes']).size().reset_index(name='Qtd_Oportunidades')

# Contar oportunidades HubGrowth por mês
contagem_oportunidades_hubgrowth = df_filtrado_vendas[df_filtrado_vendas['hubgrowth']].groupby(['CreatedDate_Mes']).size().reset_index(name='Qtd_Oportunidades_HubGrowth')

# Filtrar vendas com StageName 'Contrato Assinado - Oppty Ganha'
df_vendas_contrato_assinado = df_filtrado_vendas[df_filtrado_vendas['StageName'] == 'Contrato Assinado - Oppty Ganha']

# Contar vendas por mês
contagem_vendas = df_vendas_contrato_assinado.groupby(['DataHoraContratoAssinado__c_Mes']).size().reset_index(name='Qtd_Vendas')
contagem_vendas['CreatedDate_Mes'] = contagem_vendas['DataHoraContratoAssinado__c_Mes']

# Contar vendas HubGrowth por mês
contagem_vendas_hubgrowth = df_vendas_contrato_assinado[df_vendas_contrato_assinado['hubgrowth']].groupby(['DataHoraContratoAssinado__c_Mes']).size().reset_index(name='Qtd_Vendas_HubGrowth')
contagem_vendas_hubgrowth['CreatedDate_Mes'] = contagem_vendas_hubgrowth['DataHoraContratoAssinado__c_Mes']

# Unir as contagens em um único DataFrame
contagem_total = pd.merge(contagem_leads_totais, contagem_visitas_loja, on='CreatedDate_Mes', how='outer').fillna(0)
contagem_total = pd.merge(contagem_total, contagem_oportunidades, on='CreatedDate_Mes', how='outer').fillna(0)
contagem_total = pd.merge(contagem_total, contagem_oportunidades_hubgrowth, on='CreatedDate_Mes', how='outer').fillna(0)
contagem_total = pd.merge(contagem_total, contagem_vendas, on='CreatedDate_Mes', how='outer').fillna(0)
contagem_total = pd.merge(contagem_total, contagem_vendas_hubgrowth, on='CreatedDate_Mes', how='outer').fillna(0)

# Calcular os totais de cada coluna
totais = contagem_total.sum(numeric_only=True)

# Exibir os totais como indicadores
st.write('### Totais')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Leads", int(totais['Qtd_Leads_Totais']))
col2.metric("Leads Não Convertidos", int(totais['Qtd_Nao_Convertidos']))
col3.metric("Visitas Loja", int(totais['Qtd_Visitas_Loja']))
col4.metric("Oportunidades", int(totais['Qtd_Oportunidades']))

col5, col6, col7 = st.columns(3)
col5.metric("Oportunidades HubGrowth", int(totais['Qtd_Oportunidades_HubGrowth']))
col6.metric("Vendas", int(totais['Qtd_Vendas']))
col7.metric("Vendas HubGrowth", int(totais['Qtd_Vendas_HubGrowth']))

# Exibir a tabela com colunas de mês e especificar a ordem das linhas
st.write('**Tabela de Leads Mês a Mês**')
order = ['Qtd_Leads_Totais', 'Qtd_Leads_Ativos', 'Qtd_Nao_Convertidos', 'Qtd_Visitas_Loja', 'Qtd_Oportunidades', 'Qtd_Oportunidades_HubGrowth', 'Qtd_Vendas', 'Qtd_Vendas_HubGrowth']
tabela_pivot = contagem_total.pivot_table(index=None, columns='CreatedDate_Mes', values=order).fillna(0).astype(int)
st.dataframe(tabela_pivot)

# Tabela secundária filtrada por Equipe

# Obter as equipes dos diretores selecionados
equipes_selecionadas = set(df_leads[df_leads['Diretor_Categorizado'].isin(diretores_selecionados)]['Equipe'].unique()) | \
                       set(df_leads[df_leads['Lead.CorretorNaoConversao__r.Account.Owner.Name'].isin(diretores_selecionados)]['Lead.CorretorNaoConversao__r.Account.Name'].unique()) | \
                       set(df_vendas[df_vendas['Owner.Account.Owner.Name'].isin(diretores_selecionados)]['Owner.Account.Name'].unique())

equipes_selecionadas = sorted(equipes_selecionadas)

# Seleção das equipes com múltipla seleção e opção "Todos"
equipes_selecionadas = st.sidebar.multiselect('Selecione a Equipe', ['Todos'] + list(equipes_selecionadas), default='Todos')

# Filtrar dados de leads por equipe
df_filtrado_leads_equipe = df_filtrado_leads.copy()
df_filtrado_nao_convertidos_equipe = df_filtrado_nao_convertidos.copy()

if 'Todos' not in equipes_selecionadas:
    df_filtrado_leads_equipe = df_filtrado_leads_equipe[df_filtrado_leads_equipe['Equipe'].isin(equipes_selecionadas)]
    df_filtrado_nao_convertidos_equipe = df_filtrado_nao_convertidos_equipe[df_filtrado_nao_convertidos_equipe['Lead.CorretorNaoConversao__r.Account.Name'].isin(equipes_selecionadas)]

# Filtrar dados de visitas por equipe
df_visitas_equipe = df_visitas.copy()

if 'Todos' not in equipes_selecionadas:
    df_visitas_equipe = df_visitas_equipe[df_visitas_equipe['Lead.CorretorNaoConversao__r.Account.Name'].isin(equipes_selecionadas) | df_visitas_equipe['Equipe'].isin(equipes_selecionadas)]

# Filtrar dados de vendas por equipe
df_filtrado_vendas_equipe = df_filtrado_vendas.copy()

if 'Todos' not in equipes_selecionadas:
    df_filtrado_vendas_equipe = df_filtrado_vendas_equipe[df_filtrado_vendas_equipe['Owner.Account.Name'].isin(equipes_selecionadas)]

# Contagem por Equipe
# Contar a quantidade de leads ativos por mês por equipe
contagem_leads_ativos_equipe = df_filtrado_leads_equipe.groupby(['CreatedDate_Mes']).size().reset_index(name='Qtd_Leads_Ativos')

# Contar a quantidade de leads não convertidos por mês por equipe
contagem_nao_convertidos_equipe = df_filtrado_nao_convertidos_equipe[df_filtrado_nao_convertidos_equipe['Lead.Status'] == 'Não Convertido'].groupby(['CreatedDate_Mes']).size().reset_index(name='Qtd_Nao_Convertidos')

# Calcular Leads Totais por equipe
contagem_leads_totais_equipe = pd.merge(contagem_leads_ativos_equipe, contagem_nao_convertidos_equipe, on='CreatedDate_Mes', how='outer').fillna(0)
contagem_leads_totais_equipe['Qtd_Leads_Totais'] = contagem_leads_totais_equipe['Qtd_Leads_Ativos'] + contagem_leads_totais_equipe['Qtd_Nao_Convertidos']

# Contar a quantidade de visitas da loja por mês por equipe
contagem_visitas_loja_equipe = df_visitas_equipe.groupby(['Lead.DataVisitaLoja__c_Mes'])['LeadId'].nunique().reset_index(name='Qtd_Visitas_Loja')
contagem_visitas_loja_equipe['CreatedDate_Mes'] = contagem_visitas_loja_equipe['Lead.DataVisitaLoja__c_Mes']

# Contar oportunidades por mês por equipe
contagem_oportunidades_equipe = df_filtrado_vendas_equipe.groupby(['CreatedDate_Mes']).size().reset_index(name='Qtd_Oportunidades')

# Contar oportunidades HubGrowth por mês por equipe
contagem_oportunidades_hubgrowth_equipe = df_filtrado_vendas_equipe[df_filtrado_vendas_equipe['hubgrowth']].groupby(['CreatedDate_Mes']).size().reset_index(name='Qtd_Oportunidades_HubGrowth')

# Filtrar vendas com StageName 'Contrato Assinado - Oppty Ganha' por equipe
df_vendas_contrato_assinado_equipe = df_filtrado_vendas_equipe[df_filtrado_vendas_equipe['StageName'] == 'Contrato Assinado - Oppty Ganha']

# Contar vendas por mês por equipe
contagem_vendas_equipe = df_vendas_contrato_assinado_equipe.groupby(['DataHoraContratoAssinado__c_Mes']).size().reset_index(name='Qtd_Vendas')
contagem_vendas_equipe['CreatedDate_Mes'] = contagem_vendas_equipe['DataHoraContratoAssinado__c_Mes']

# Contar vendas HubGrowth por mês por equipe
contagem_vendas_hubgrowth_equipe = df_vendas_contrato_assinado_equipe[df_vendas_contrato_assinado_equipe['hubgrowth']].groupby(['DataHoraContratoAssinado__c_Mes']).size().reset_index(name='Qtd_Vendas_HubGrowth')
contagem_vendas_hubgrowth_equipe['CreatedDate_Mes'] = contagem_vendas_hubgrowth_equipe['DataHoraContratoAssinado__c_Mes']

# Unir as contagens em um único DataFrame
contagem_total_equipe = pd.merge(contagem_leads_totais_equipe, contagem_visitas_loja_equipe, on='CreatedDate_Mes', how='outer').fillna(0)
contagem_total_equipe = pd.merge(contagem_total_equipe, contagem_oportunidades_equipe, on='CreatedDate_Mes', how='outer').fillna(0)
contagem_total_equipe = pd.merge(contagem_total_equipe, contagem_oportunidades_hubgrowth_equipe, on='CreatedDate_Mes', how='outer').fillna(0)
contagem_total_equipe = pd.merge(contagem_total_equipe, contagem_vendas_equipe, on='CreatedDate_Mes', how='outer').fillna(0)
contagem_total_equipe = pd.merge(contagem_total_equipe, contagem_vendas_hubgrowth_equipe, on='CreatedDate_Mes', how='outer').fillna(0)

# Calcular os totais de cada coluna para a segunda tabela
totais_equipe = contagem_total_equipe.sum(numeric_only=True)

# Exibir os totais como indicadores para a segunda tabela
st.write('### Totais por Equipe')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Leads", int(totais_equipe['Qtd_Leads_Totais']))
col2.metric("Leads Não Convertidos", int(totais_equipe['Qtd_Nao_Convertidos']))
col3.metric("Visitas Loja", int(totais_equipe['Qtd_Visitas_Loja']))
col4.metric("Oportunidades", int(totais_equipe['Qtd_Oportunidades']))

col5, col6, col7 = st.columns(3)
col5.metric("Oportunidades HubGrowth", int(totais_equipe['Qtd_Oportunidades_HubGrowth']))
col6.metric("Vendas", int(totais_equipe['Qtd_Vendas']))
col7.metric("Vendas HubGrowth", int(totais_equipe['Qtd_Vendas_HubGrowth']))

# Exibir a tabela com colunas de mês e especificar a ordem das linhas para a segunda tabela
st.write('**Tabela de Leads por Equipe Mês a Mês**')
order_equipe = ['Qtd_Leads_Totais', 'Qtd_Leads_Ativos', 'Qtd_Nao_Convertidos', 'Qtd_Visitas_Loja', 'Qtd_Oportunidades', 'Qtd_Oportunidades_HubGrowth', 'Qtd_Vendas', 'Qtd_Vendas_HubGrowth']
tabela_pivot_equipe = contagem_total_equipe.pivot_table(index=None, columns='CreatedDate_Mes', values=order_equipe).fillna(0).astype(int)
st.dataframe(tabela_pivot_equipe)

# Executar o streamlit no modo de simulação
# Para executar, o usuário deve rodar: `streamlit run nome_do_arquivo.py` em seu ambiente local
