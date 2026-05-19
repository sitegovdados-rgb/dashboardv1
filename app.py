import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# ==================== CONFIGURAÇÃO ====================
st.set_page_config(
    page_title="Monitoramento PCI - Políticas Públicas",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Monitoramento - Programa Cidade Integrada")
st.markdown("Acompanhamento de **políticas públicas e iniciativas sociais** por região")

# ==================== CARREGAMENTO DO ARQUIVO ====================
@st.cache_data
def load_data(file_path="dashboard-social-geral.csv"):
    try:
        if Path(file_path).exists():
            df = pd.read_csv(file_path)
            # Renomear colunas para melhor visualização
            df.columns = df.columns.str.strip()
            st.success(f"✅ Arquivo `{file_path}` carregado com sucesso!")
            return df
        else:
            st.error(f"❌ Arquivo `{file_path}` não encontrado.")
            return None
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

# Opção de upload (útil para deploy no Streamlit Cloud)
uploaded_file = st.file_uploader("Ou faça upload do seu arquivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Arquivo carregado via upload!")
else:
    df = load_data("dashboard-social-geral.csv")

if df is None:
    st.stop()

# ==================== PRÉ-PROCESSAMENTO ====================
# Mapear nomes das colunas para variáveis mais legíveis
colmap = {
    'Tarefa': 'Iniciativa',
    'Região (PCI)': 'Região',
    'Localidade Específica': 'Localidade',
    'Responsável - Sec. / Órgão': 'Responsável',
    'Última Atualização': 'Atualização',
    'Tipo': 'Tipo_Atividade',
    'Status': 'Status_Execução'
}

# Selecionar apenas colunas relevantes para análise
cols_principais = ['Tarefa', 'Região (PCI)', 'Localidade Específica', 'Responsável - Sec. / Órgão',
                   'Última Atualização', 'Tipo', 'Status', 'Data Inicial (Prog. / Interv.)', 
                   'Data Final (Prog. / Interv.)']

df_analise = df[[col for col in cols_principais if col in df.columns]].copy()
df_analise.columns = [colmap.get(col, col) for col in df_analise.columns]

# Identificar colunas de coleta de dados (sim/não/aguardando)
cols_coleta = [col for col in df.columns if col not in cols_principais]

# ==================== DEFINIÇÕES GLOBAIS ====================
regions = df_analise['Região'].dropna().unique().tolist()
status_opcoes = df_analise['Status_Execução'].dropna().unique().tolist()
tipo_opcoes = df_analise['Tipo_Atividade'].dropna().unique().tolist()

# ==================== MÉTRICAS PRINCIPAIS ====================
st.subheader("📈 Indicadores Principais")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total de Iniciativas", len(df_analise))

with col2:
    em_execucao = len(df_analise[df_analise['Status_Execução'] == 'Em execução'])
    st.metric("Em Execução", em_execucao, f"{(em_execucao/len(df_analise)*100):.1f}%")

with col3:
    concluidas = len(df_analise[df_analise['Status_Execução'] == 'Concluída'])
    st.metric("Concluídas", concluidas, f"{(concluidas/len(df_analise)*100):.1f}%")

with col4:
    bloqueadas = len(df_analise[df_analise['Status_Execução'] == 'Bloqueada'])
    st.metric("Bloqueadas", bloqueadas, f"{(bloqueadas/len(df_analise)*100):.1f}%")

with col5:
    regioes_ativas = len(regions)
    st.metric("Regiões Cobertas", regioes_ativas)

# ==================== ABAS DE VISUALIZAÇÃO ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Dados", "🎯 Análise Estratégica", "📍 Territorialidade", "🔧 Exploração", "📊 Dados Brutos"])

# ========== TAB 1: VISUALIZAÇÃO DOS DADOS ==========
with tab1:
    st.subheader("Iniciativas Registradas")
    st.dataframe(df_analise, use_container_width=True, height=600)
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="⬇️ Baixar dados processados (CSV)",
            data=df_analise.to_csv(index=False).encode('utf-8'),
            file_name="dashboard_social_processado.csv",
            mime="text/csv"
        )
    with col_dl2:
        st.download_button(
            label="⬇️ Baixar dados brutos (CSV)",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="dashboard_social_completo.csv",
            mime="text/csv"
        )

# ========== TAB 2: ANÁLISE ESTRATÉGICA ==========
with tab2:
    st.subheader("🎯 Análise de Execução por Status")
    
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        status_count = df_analise['Status_Execução'].value_counts().reset_index()
        status_count.columns = ['Status', 'Quantidade']
        fig_status = px.bar(
            status_count,
            x='Status',
            y='Quantidade',
            title="Distribuição por Status de Execução",
            color='Status'
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col_graph2:
        status_count = df_analise['Status_Execução'].value_counts().reset_index()
        status_count.columns = ['Status', 'Quantidade']
        fig_status_pie = px.pie(
            status_count,
            values='Quantidade',
            names='Status',
            title="Proporção de Iniciativas por Status",
            hole=0.3
        )
        st.plotly_chart(fig_status_pie, use_container_width=True)
    
    st.subheader("📅 Distribuição por Tipo de Atividade")
    col_graph3, col_graph4 = st.columns(2)
    
    with col_graph3:
        tipo_count = df_analise['Tipo_Atividade'].value_counts().reset_index()
        tipo_count.columns = ['Tipo', 'Quantidade']
        fig_tipo = px.bar(
            tipo_count,
            x='Tipo',
            y='Quantidade',
            title="Tipo de Atividade (Contínua, Temporária, Esporádica)",
            color='Tipo'
        )
        st.plotly_chart(fig_tipo, use_container_width=True)
    
    with col_graph4:
        try:
            responsaveis_count = df_analise['Responsável'].dropna().value_counts().head(10).reset_index()
            if len(responsaveis_count) > 0:
                responsaveis_count.columns = ['Órgão', 'Quantidade']
                responsaveis_count = responsaveis_count.astype({'Quantidade': 'int64'})
                fig_resp = px.bar(
                    responsaveis_count,
                    x='Quantidade',
                    y='Órgão',
                    orientation='h',
                    title="Top 10 Órgãos Responsáveis"
                )
                st.plotly_chart(fig_resp, use_container_width=True)
            else:
                st.warning("Sem dados de responsáveis para exibir.")
        except Exception as e:
            st.error(f"Erro ao gerar gráfico de responsáveis: {str(e)}")
    
    st.subheader("⚠️ Gaps de Informação")
    gaps = []
    for col in cols_coleta:
        aguardando = len(df[df[col] == 'Aguardando Informação'])
        total = len(df)
        if aguardando > 0:
            gaps.append({
                'Campo': col,
                'Aguardando Informação': aguardando,
                '% Incompleto': (aguardando / total * 100)
            })
    
    if gaps:
        df_gaps = pd.DataFrame(gaps).sort_values('% Incompleto', ascending=False)
        fig_gaps = px.bar(
            df_gaps.head(8),
            x='Campo',
            y='% Incompleto',
            title="Campos com Informações Faltando",
            color='% Incompleto'
        )
        st.plotly_chart(fig_gaps, use_container_width=True)
        st.dataframe(df_gaps, use_container_width=True)

# ========== TAB 3: TERRITORIALIDADE ==========
with tab3:
    st.subheader("📍 Análise Territorial")
    
    col_filt1, col_filt2 = st.columns(2)
    
    with col_filt1:
        regioes_selecionadas = st.multiselect(
            "Selecionar Regiões",
            regions,
            default=regions
        )
    
    with col_filt2:
        status_selecionados = st.multiselect(
            "Selecionar Status",
            status_opcoes,
            default=status_opcoes
        )
    
    df_filtrado = df_analise[
        (df_analise['Região'].isin(regioes_selecionadas)) &
        (df_analise['Status_Execução'].isin(status_selecionados))
    ]
    
    col_geo1, col_geo2 = st.columns(2)
    
    with col_geo1:
        regiao_count = df_filtrado['Região'].value_counts().reset_index()
        regiao_count.columns = ['Região', 'Quantidade']
        fig_regiao = px.bar(
            regiao_count,
            x='Região',
            y='Quantidade',
            title="Iniciativas por Região",
            color='Região'
        )
        st.plotly_chart(fig_regiao, use_container_width=True)
    
    with col_geo2:
        try:
            localidade_count = df_filtrado['Localidade'].dropna().value_counts().head(10).reset_index()
            if len(localidade_count) > 0:
                localidade_count.columns = ['Localidade', 'Quantidade']
                localidade_count = localidade_count.astype({'Quantidade': 'int64'})
                fig_local = px.bar(
                    localidade_count,
                    x='Quantidade',
                    y='Localidade',
                    orientation='h',
                    title="Top 10 Localidades"
                )
                st.plotly_chart(fig_local, use_container_width=True)
            else:
                st.warning("Sem dados de localidades para exibir.")
        except Exception as e:
            st.error(f"Erro ao gerar gráfico de localidades: {str(e)}")
    
    st.subheader(f"Iniciativas Filtradas: {len(df_filtrado)}")
    st.dataframe(df_filtrado, use_container_width=True, height=400)

# ========== TAB 4: EXPLORAÇÃO AVANÇADA ==========
with tab4:
    st.subheader("🔧 Filtros e Exploração Detalhada")
    
    col_filt_adv1, col_filt_adv2, col_filt_adv3 = st.columns(3)
    
    with col_filt_adv1:
        filtro_regiao = st.selectbox("Filtrar por Região", ["Todas"] + regions)
    
    with col_filt_adv2:
        filtro_tipo = st.selectbox("Filtrar por Tipo", ["Todos"] + tipo_opcoes)
    
    with col_filt_adv3:
        filtro_status = st.selectbox("Filtrar por Status", ["Todos"] + status_opcoes)
    
    # Aplicar filtros
    df_exp = df_analise.copy()
    
    if filtro_regiao != "Todas":
        df_exp = df_exp[df_exp['Região'] == filtro_regiao]
    
    if filtro_tipo != "Todos":
        df_exp = df_exp[df_exp['Tipo_Atividade'] == filtro_tipo]
    
    if filtro_status != "Todos":
        df_exp = df_exp[df_exp['Status_Execução'] == filtro_status]
    
    st.write(f"**Iniciativas encontradas:** {len(df_exp)}")
    st.dataframe(df_exp, use_container_width=True, height=500)
    
    if len(df_exp) > 0:
        st.subheader("Detalhes dos Responsáveis")
        try:
            resp_detalhes = df_exp['Responsável'].dropna().value_counts().reset_index()
            if len(resp_detalhes) > 0:
                resp_detalhes.columns = ['Órgão', 'Quantidade']
                resp_detalhes = resp_detalhes.astype({'Quantidade': 'int64'})
                fig_resp_det = px.pie(
                    resp_detalhes,
                    values='Quantidade',
                    names='Órgão',
                    title="Distribuição de Responsabilidades",
                    hole=0.3
                )
                st.plotly_chart(fig_resp_det, use_container_width=True)
            else:
                st.warning("Sem dados de responsáveis para exibir.")
        except Exception as e:
            st.error(f"Erro ao gerar gráfico de responsáveis: {str(e)}")

# ========== TAB 5: DADOS BRUTOS ==========
with tab5:
    st.subheader("📊 Dados Completos")
    st.info("Visualização de todas as colunas e linhas do arquivo original")
    st.dataframe(df, use_container_width=True, height=600)
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("Total de Linhas", len(df))
    with col_info2:
        st.metric("Total de Colunas", len(df.columns))
    with col_info3:
        st.metric("Valores Nulos", df.isnull().sum().sum())

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("⚙️ Configurações")
    
    st.subheader("ℹ️ Sobre os Dados")
    st.write(f"""
    - **Total de Iniciativas:** {len(df_analise)}
    - **Regiões Cobertas:** {len(regions)}
    - **Órgãos Responsáveis:** {df_analise['Responsável'].nunique()}
    - **Última Atualização:** {df_analise['Atualização'].max()}
    """)
    
    if st.button("🗑️ Limpar Cache"):
        st.cache_data.clear()
        st.success("Cache limpo com sucesso!")
    
    st.markdown("---")
    
    st.subheader("📌 Dicas de Uso")
    st.markdown("""
    1. Use as **abas** para diferentes perspectivas de análise
    2. Aplique **filtros** na aba de Exploração para análises customizadas
    3. Baixe os dados processados para análises avançadas
    4. Identifique **gaps de informação** na aba de Análise Estratégica
    """)
    
    st.caption("📊 Dashboard para Programa Cidade Integrada v1.0")
    st.caption("Dados de políticas públicas e iniciativas sociais")
