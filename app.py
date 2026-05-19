import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==================== CONFIGURAÇÃO ====================
st.set_page_config(
    page_title="Análise de Dados - data.csv",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Template Streamlit - data.csv")
st.markdown("Template completo para explorar seu arquivo **data.csv**")

# ==================== CARREGAMENTO DO ARQUIVO ====================
@st.cache_data
def load_data(file_path="data.csv"):
    try:
        if Path(file_path).exists():
            df = pd.read_csv(file_path)
            st.success(f"✅ Arquivo `{file_path}` carregado com sucesso!")
            return df
        else:
            st.error(f"❌ Arquivo `{file_path}` não encontrado.")
            return None
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

# Opção de upload (útil para deploy no Streamlit Cloud)
uploaded_file = st.file_uploader("Ou faça upload do seu data.csv", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Arquivo carregado via upload!")
else:
    df = load_data("data.csv")

if df is None:
    st.stop()

# ==================== INFORMAÇÕES BÁSICAS ====================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Linhas", f"{len(df):,}")
with col2:
    st.metric("Colunas", len(df.columns))
with col3:
    st.metric("Duplicatas", df.duplicated().sum())
with col4:
    st.metric("Valores Nulos", df.isnull().sum().sum())

# ==================== VISUALIZAÇÃO DOS DADOS ====================
tab1, tab2, tab3, tab4 = st.tabs(["📋 Dados", "🔍 Análise", "📈 Gráficos", "🔧 Ferramentas"])

with tab1:
    st.subheader("Visualização dos Dados")
    st.dataframe(df, use_container_width=True, height=600)
    
    st.download_button(
        label="⬇️ Baixar CSV completo",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="data_processado.csv",
        mime="text/csv"
    )

with tab2:
    st.subheader("Estatísticas Descritivas")
    st.dataframe(df.describe(include='all'), use_container_width=True)
    
    st.subheader("Tipos de Dados e Nulos")
    info = pd.DataFrame({
        'Tipo': df.dtypes,
        'Nulos': df.isnull().sum(),
        '% Nulos': (df.isnull().sum() / len(df) * 100).round(2)
    })
    st.dataframe(info, use_container_width=True)

with tab3:
    st.subheader("Visualizações Interativas")
    
    col_plot1, col_plot2 = st.columns(2)
    
    with col_plot1:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            col_x = st.selectbox("Eixo X", numeric_cols, key="x1")
            fig_hist = px.histogram(df, x=col_x, title=f"Distribuição de {col_x}")
            st.plotly_chart(fig_hist, use_container_width=True)
    
    with col_plot2:
        if len(numeric_cols) >= 2:
            x_col = st.selectbox("Eixo X (Scatter)", numeric_cols, key="x2")
            y_col = st.selectbox("Eixo Y (Scatter)", numeric_cols, index=1 if len(numeric_cols)>1 else 0, key="y2")
            fig_scatter = px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
            st.plotly_chart(fig_scatter, use_container_width=True)

    # Gráfico de barras (se houver colunas categóricas)
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    if cat_cols:
        st.subheader("Gráficos de Barras")
        cat_col = st.selectbox("Coluna Categórica", cat_cols)
        fig_bar = px.histogram(df, x=cat_col, title=f"Contagem por {cat_col}")
        st.plotly_chart(fig_bar, use_container_width=True)

with tab4:
    st.subheader("Filtros e Exploração")
    
    # Filtro por colunas
    if cat_cols:
        filtro_col = st.selectbox("Filtrar por coluna", cat_cols)
        valores_unicos = df[filtro_col].dropna().unique()
        valores_selecionados = st.multiselect("Valores", valores_unicos, default=valores_unicos[:3])
        
        if valores_selecionados:
            df_filtrado = df[df[filtro_col].isin(valores_selecionados)]
            st.write(f"**Dados filtrados:** {len(df_filtrado)} linhas")
            st.dataframe(df_filtrado)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("⚙️ Configurações")
    
    st.subheader("Colunas Numéricas")
    st.write(numeric_cols)
    
    if st.button("Limpar Cache"):
        st.cache_data.clear()
        st.success("Cache limpo!")
    
    st.markdown("---")
    st.caption("Template criado para o arquivo **data.csv**")

st.caption("💡 Dica: Coloque seu `data.csv` na mesma pasta do arquivo app.py")
