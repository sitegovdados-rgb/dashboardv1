import streamlit as st
import pandas as pd

# 1. Configuração do título da página
st.set_page_config(page_title="Meu Dashboard", layout="wide")
st.title("📊 Meu Primeiro Dashboard Gratuito")

# 2. LER O SEU CSV (Substitua 'seu_arquivo.csv' pelo nome exato do seu arquivo)
# Importante: mantenha as aspas!
df = pd.read_csv("seu_arquivo.csv")

# 3. Mostrar os dados em formato de tabela interativa na tela
st.subheader("Visualização dos Dados")
st.dataframe(df)

# 4. Criar um gráfico automático
# O Streamlit tentará criar um gráfico com as colunas numéricas do seu CSV
st.subheader("Gráfico de Linhas dos Dados")
st.line_chart(df)
