import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from components import (
    metric_card, filter_section, data_table_with_download,
    chart_container, status_badge, info_box, success_box,
    create_statistics_grid, empty_state, section_divider
)

# ==================== CONFIGURAÇÃO ====================
st.set_page_config(
    page_title="Monitoramento PCI - Políticas Públicas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 28px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 15px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard de Monitoramento")
st.markdown("Programa Cidade Integrada | Acompanhamento de políticas públicas e iniciativas sociais")

# ==================== CARREGAMENTO DO ARQUIVO ====================
@st.cache_data
def load_data(file_path="dashboard-social-geral.csv"):
    try:
        if Path(file_path).exists():
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip()
            return df, True, f"Arquivo `{file_path}` carregado com sucesso!"
        else:
            return None, False, f"Arquivo `{file_path}` não encontrado."
    except Exception as e:
        return None, False, f"Erro ao carregar o arquivo: {e}"

# Upload de arquivo
st.markdown("### 📤 Upload de Arquivo")
uploaded_file = st.file_uploader("Envie um arquivo CSV atualizado", type=["csv"], key="csv_upload")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()
        success_box("Sucesso!", "Arquivo carregado via upload com sucesso!")
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {e}")
        st.stop()
else:
    df, success, message = load_data("dashboard-social-geral.csv")
    if not success:
        st.error(f"❌ {message}")
        st.stop()

if df is None:
    st.stop()

# ==================== PRÉ-PROCESSAMENTO ====================
colmap = {
    'Tarefa': 'Iniciativa',
    'Região (PCI)': 'Região',
    'Localidade Específica': 'Localidade',
    'Responsável - Sec. / Órgão': 'Responsável',
    'Última Atualização': 'Atualização',
    'Tipo': 'Tipo_Atividade',
    'Status': 'Status_Execução'
}

cols_principais = ['Tarefa', 'Região (PCI)', 'Localidade Específica', 'Responsável - Sec. / Órgão',
                   'Última Atualização', 'Tipo', 'Status', 'Data Inicial (Prog. / Interv.)', 
                   'Data Final (Prog. / Interv.)']

df_analise = df[[col for col in cols_principais if col in df.columns]].copy()
df_analise.columns = [colmap.get(col, col) for col in df_analise.columns]

cols_coleta = [col for col in df.columns if col not in cols_principais]

# ==================== DEFINIÇÕES GLOBAIS ====================
regions = df_analise['Região'].dropna().unique().tolist()
status_opcoes = df_analise['Status_Execução'].dropna().unique().tolist()
tipo_opcoes = df_analise['Tipo_Atividade'].dropna().unique().tolist()

# ==================== MÉTRICAS PRINCIPAIS ====================
st.markdown("---")
st.subheader("📈 Indicadores Principais")

em_execucao = len(df_analise[df_analise['Status_Execução'] == 'Em execução'])
concluidas = len(df_analise[df_analise['Status_Execução'] == 'Concluída'])
bloqueadas = len(df_analise[df_analise['Status_Execução'] == 'Bloqueada'])

stats = [
    {
        'label': 'Total de Iniciativas',
        'value': f"{len(df_analise)}",
        'icon': '📋',
        'description': 'Registros no sistema'
    },
    {
        'label': 'Em Execução',
        'value': f"{em_execucao}",
        'icon': '▶️',
        'description': f"{(em_execucao/len(df_analise)*100):.1f}% do total"
    },
    {
        'label': 'Concluídas',
        'value': f"{concluidas}",
        'icon': '✅',
        'description': f"{(concluidas/len(df_analise)*100):.1f}% do total"
    },
    {
        'label': 'Bloqueadas',
        'value': f"{bloqueadas}",
        'icon': '🚫',
        'description': f"{(bloqueadas/len(df_analise)*100):.1f}% do total"
    },
    {
        'label': 'Regiões Cobertas',
        'value': f"{len(regions)}",
        'icon': '🗺️',
        'description': 'Áreas geográficas'
    },
]

create_statistics_grid(stats)

# ==================== ABAS DE VISUALIZAÇÃO ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Dados Processados",
    "🎯 Análise Estratégica",
    "📍 Territorialidade",
    "🔧 Exploração",
    "📊 Dados Brutos"
])

# ========== TAB 1: DADOS PROCESSADOS ==========
with tab1:
    section_divider("Iniciativas Registradas")
    
    filters = filter_section(regions, status_opcoes, tipo_opcoes, key_prefix="tab1")
    
    df_filtered = df_analise[
        (df_analise['Região'].isin(filters['regions'])) &
        (df_analise['Status_Execução'].isin(filters['status'])) &
        (df_analise['Tipo_Atividade'].isin(filters['types']))
    ]
    
    if len(df_filtered) > 0:
        data_table_with_download(
            df_filtered,
            f"Iniciativas Encontradas ({len(df_filtered)})",
            "dashboard_social_processado",
            height=500
        )
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv = df_analise.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Baixar Dados Processados (CSV)",
                data=csv,
                file_name="dashboard_social_processado.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_dl2:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Baixar Dados Brutos (CSV)",
                data=csv,
                file_name="dashboard_social_completo.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        empty_state("Nenhuma iniciativa encontrada com os filtros selecionados", "🔍")

# ========== TAB 2: ANÁLISE ESTRATÉGICA ==========
with tab2:
    section_divider("Análise de Execução por Status")
    
    filters = filter_section(regions, status_opcoes, tipo_opcoes, key_prefix="tab2")
    
    df_filtrado = df_analise[
        (df_analise['Região'].isin(filters['regions'])) &
        (df_analise['Status_Execução'].isin(filters['status'])) &
        (df_analise['Tipo_Atividade'].isin(filters['types']))
    ]
    
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        status_count = df_filtrado['Status_Execução'].value_counts().reset_index()
        status_count.columns = ['Status', 'Quantidade']
        fig_status = px.bar(
            status_count,
            x='Status',
            y='Quantidade',
            title="Distribuição por Status",
            color='Status',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_status.update_layout(showlegend=False, hovermode='x unified')
        chart_container(fig_status, "Status de Execução")
    
    with col_graph2:
        status_count = df_filtrado['Status_Execução'].value_counts().reset_index()
        status_count.columns = ['Status', 'Quantidade']
        fig_status_pie = px.pie(
            status_count,
            values='Quantidade',
            names='Status',
            title="Proporção por Status",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        chart_container(fig_status_pie, "Proporção de Iniciativas")
    
    st.divider()
    st.subheader("📅 Distribuição por Tipo de Atividade")
    
    col_graph3, col_graph4 = st.columns(2)
    
    with col_graph3:
        tipo_count = df_filtrado['Tipo_Atividade'].value_counts().reset_index()
        tipo_count.columns = ['Tipo', 'Quantidade']
        fig_tipo = px.bar(
            tipo_count,
            x='Tipo',
            y='Quantidade',
            title="Tipo de Atividade",
            color='Tipo',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_tipo.update_layout(showlegend=False, hovermode='x unified')
        chart_container(fig_tipo, "Classificação por Tipo")
    
    with col_graph4:
        try:
            responsaveis_count = df_filtrado['Responsável'].dropna().value_counts().head(10).reset_index()
            if len(responsaveis_count) > 0:
                responsaveis_count.columns = ['Órgão', 'Quantidade']
                fig_resp = px.bar(
                    responsaveis_count,
                    x='Quantidade',
                    y='Órgão',
                    orientation='h',
                    title="Top 10 Órgãos",
                    color='Quantidade',
                    color_continuous_scale='Blues'
                )
                fig_resp.update_layout(hovermode='y unified')
                chart_container(fig_resp, "Órgãos Responsáveis")
            else:
                empty_state("Sem dados de responsáveis")
        except Exception as e:
            st.error(f"❌ Erro ao gerar gráfico: {str(e)}")
    
    st.divider()
    st.subheader("⚠️ Gaps de Informação")
    
    gaps = []
    for col in cols_coleta:
        aguardando = len(df[df[col] == 'Aguardando Informação'])
        total = len(df)
        if aguardando > 0:
            gaps.append({
                'Campo': col,
                'Aguardando': aguardando,
                '% Incompleto': (aguardando / total * 100)
            })
    
    if gaps:
        df_gaps = pd.DataFrame(gaps).sort_values('% Incompleto', ascending=False)
        fig_gaps = px.bar(
            df_gaps.head(8),
            x='Campo',
            y='% Incompleto',
            title="Campos com Informações Faltando",
            color='% Incompleto',
            color_continuous_scale='Reds'
        )
        chart_container(fig_gaps, "Análise de Gaps")
        data_table_with_download(df_gaps, "Detalhes dos Gaps", "gaps_informacao", height=300)
    else:
        success_box("Completo!", "Nenhum gap de informação detectado.")

# ========== TAB 3: TERRITORIALIDADE ==========
with tab3:
    section_divider("Análise Territorial")
    
    filters = filter_section(regions, status_opcoes, tipo_opcoes, key_prefix="tab3")
    
    df_filtrado = df_analise[
        (df_analise['Região'].isin(filters['regions'])) &
        (df_analise['Status_Execução'].isin(filters['status'])) &
        (df_analise['Tipo_Atividade'].isin(filters['types']))
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
            color='Região',
            color_discrete_sequence=px.colors.qualitative.Light24
        )
        fig_regiao.update_layout(showlegend=False, hovermode='x unified')
        chart_container(fig_regiao, "Distribuição Regional")
    
    with col_geo2:
        try:
            localidade_count = df_filtrado['Localidade'].dropna().value_counts().head(10).reset_index()
            if len(localidade_count) > 0:
                localidade_count.columns = ['Localidade', 'Quantidade']
                fig_local = px.bar(
                    localidade_count,
                    x='Quantidade',
                    y='Localidade',
                    orientation='h',
                    title="Top 10 Localidades",
                    color='Quantidade',
                    color_continuous_scale='Viridis'
                )
                fig_local.update_layout(hovermode='y unified')
                chart_container(fig_local, "Localidades Principais")
            else:
                empty_state("Sem dados de localidades")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
    
    st.divider()
    data_table_with_download(
        df_filtrado,
        f"Iniciativas por Localidade ({len(df_filtrado)})",
        "territorialidade",
        height=400
    )

# ========== TAB 4: EXPLORAÇÃO AVANÇADA ==========
with tab4:
    section_divider("Filtros e Exploração Detalhada")
    
    col_filt_adv1, col_filt_adv2, col_filt_adv3 = st.columns(3)
    
    with col_filt_adv1:
        filtro_regiao = st.selectbox("Filtrar por Região", ["Todas"] + regions, key="exp_region")
    
    with col_filt_adv2:
        filtro_tipo = st.selectbox("Filtrar por Tipo", ["Todos"] + tipo_opcoes, key="exp_type")
    
    with col_filt_adv3:
        filtro_status = st.selectbox("Filtrar por Status", ["Todos"] + status_opcoes, key="exp_status")
    
    df_exp = df_analise.copy()
    
    if filtro_regiao != "Todas":
        df_exp = df_exp[df_exp['Região'] == filtro_regiao]
    
    if filtro_tipo != "Todos":
        df_exp = df_exp[df_exp['Tipo_Atividade'] == filtro_tipo]
    
    if filtro_status != "Todos":
        df_exp = df_exp[df_exp['Status_Execução'] == filtro_status]
    
    if len(df_exp) > 0:
        data_table_with_download(
            df_exp,
            f"Iniciativas Encontradas ({len(df_exp)})",
            "exploracao_avancada",
            height=500
        )
        
        st.divider()
        st.subheader("Análise de Responsabilidades")
        
        try:
            resp_detalhes = df_exp['Responsável'].dropna().value_counts().reset_index()
            if len(resp_detalhes) > 0:
                resp_detalhes.columns = ['Órgão', 'Quantidade']
                fig_resp_det = px.pie(
                    resp_detalhes,
                    values='Quantidade',
                    names='Órgão',
                    title="Distribuição de Responsabilidades",
                    hole=0.3
                )
                chart_container(fig_resp_det, "Responsáveis")
            else:
                empty_state("Sem dados de responsáveis")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
    else:
        empty_state("Nenhuma iniciativa encontrada com os filtros selecionados")

# ========== TAB 5: DADOS BRUTOS ==========
with tab5:
    section_divider("Dados Completos (Sem Processamento)")
    
    info_box(
        "Visualização Completa",
        "Esta seção mostra todas as colunas e linhas do arquivo original sem nenhum processamento."
    )
    
    data_table_with_download(
        df,
        f"Dados Brutos ({len(df)} registros, {len(df.columns)} colunas)",
        "dados_brutos_completos",
        height=600
    )
    
    st.divider()
    st.subheader("📊 Estatísticas do Dataset")
    
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
    about_text = f"""
    - **Total de Iniciativas:** {len(df_analise)}
    - **Regiões Cobertas:** {len(regions)}
    - **Órgãos Responsáveis:** {df_analise['Responsável'].nunique()}
    - **Última Atualização:** {df_analise['Atualização'].max() if 'Atualização' in df_analise.columns else 'N/A'}
    """
    st.info(about_text)
    
    if st.button("🗑️ Limpar Cache", use_container_width=True):
        st.cache_data.clear()
        st.success("Cache limpo com sucesso!")
    
    st.divider()
    
    st.subheader("📌 Guia de Uso")
    st.markdown("""
    1. **📋 Dados Processados** - Visualize iniciativas filtradas
    2. **🎯 Análise Estratégica** - Gráficos de status e gaps
    3. **📍 Territorialidade** - Distribuição geográfica
    4. **🔧 Exploração** - Filtros avançados customizados
    5. **📊 Dados Brutos** - Visualize tudo sem processamento
    """)
    
    st.divider()
    
    with st.expander("💡 Dicas"):
        st.markdown("""
        - Use **filtros** para análises customizadas
        - **Baixe os dados** para análises externas
        - Os gráficos são **interativos** (passe o mouse)
        - Identifique **gaps** na aba de Análise
        """)
    
    st.caption("📊 Dashboard Modernizado v2.0")
    st.caption("Programa Cidade Integrada")
    st.caption("Última atualização: " + datetime.now().strftime("%d/%m/%Y %H:%M"))
