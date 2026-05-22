import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime

# ==================== CONFIGURAÇÃO DO STREAMLIT ====================
st.set_page_config(
    page_title="Monitoramento PCI - Urbanismo Social",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar o estado do tema se não estiver definido
if 'theme' not in st.session_state:
    st.session_state.theme = "☀️ Claro"

# Obter tema selecionado ou definir variáveis de cores correspondentes
if st.session_state.theme == "☀️ Claro":
    bg_color = "#F8FAFC"
    card_bg = "#FFFFFF"
    card_border = "rgba(15, 23, 42, 0.08)"
    text_color = "#0F172A"
    subtext_color = "#64748B"
    plotly_template = "plotly_white"
    mapbox_style = "carto-positron"
    metric_title_color = "#64748B"
    metric_value_color = "#1E3A8A"
else:
    bg_color = "#0F172A"
    card_bg = "#1E293B"
    card_border = "rgba(255, 255, 255, 0.08)"
    text_color = "#F8FAFC"
    subtext_color = "#94A3B8"
    plotly_template = "plotly_dark"
    mapbox_style = "carto-darkmatter"
    metric_title_color = "#94A3B8"
    metric_value_color = "#00D4B2"

# Custom CSS for Premium Look based on theme selection
st.markdown(f"""
<style>
    /* Global styles */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Card layout */
    .metric-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, border-color 0.2s;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        border-color: rgba(0, 212, 178, 0.4);
    }}
    
    /* Header styles */
    h1, h2, h3, h4, h5, h6 {{
        color: {text_color} !important;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Styled dividers */
    .custom-hr {{
        margin: 20px 0;
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(0, 212, 178, 0), rgba(0, 212, 178, 0.75), rgba(0, 212, 178, 0));
    }}
</style>
""", unsafe_allow_html=True)


# ==================== COORDENADAS GEOGRÁFICAS ====================
# Carrega de arquivo externo para que adicionar novas localidades não exija
# editar código-fonte. Edite coordenadas.json para incluir novos pontos.
import json as _json

def _load_coords(path="coordenadas.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = _json.load(f)
        # remove chaves de comentário e retorna como dict de tuplas
        return {k: tuple(v) for k, v in raw.items() if not k.startswith("_")}
    except FileNotFoundError:
        st.warning(f"⚠️ Arquivo `{path}` não encontrado. Mapa funcionará apenas com localidades já registradas no fallback.")
        return {}
    except Exception as e:
        st.error(f"Erro ao carregar `{path}`: {e}")
        return {}

COORDS = _load_coords()

# Aliases para normalizar localidades sujas na base de origem.
# Ex.: "Muzema CIEP Professor Lauro De Oliveira Lima Itanhangá" é claramente
# uma concatenação acidental que precisa apontar para a localidade canônica
# (Muzema). Idealmente, isso seria corrigido na fonte do dado.
LOCALITY_ALIASES = {
    "Muzema ": "Muzema",  # trailing space
    "Muzema CIEP Professor Lauro De Oliveira Lima Itanhangá": "Muzema",
    "Itanhangá Tijuquinha": "Tijuquinha",
    "Campo do Abóbora - JacarézinhoManguinhos": "Campo do Abóbora - Jacarézinho",
}

def normalize_locality(s):
    """Normaliza um valor de Localidade Específica vindo do CSV."""
    if pd.isna(s):
        return s
    s = str(s).strip()
    return LOCALITY_ALIASES.get(s, s)


# ==================== CARREGAMENTO E LEITURA INTELIGENTE DE ARQUIVOS ====================
@st.cache_data
def parse_excel_sheets(file_bytes, file_name):
    import io
    try:
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        return excel_file.sheet_names
    except Exception as e:
        st.error(f"Erro ao ler as abas do Excel: {e}")
        return []

@st.cache_data
def read_excel_sheet(file_bytes, file_name, sheet_name):
    import io
    return pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name)

@st.cache_data
def read_csv_file(file_bytes, file_name):
    import io
    return pd.read_csv(io.BytesIO(file_bytes))

def load_default_file(file_path):
    try:
        p = Path(file_path)
        if p.exists():
            if p.suffix == '.csv':
                df = pd.read_csv(p)
            elif p.suffix in ['.xlsx', '.xls']:
                df = pd.read_excel(p)
            else:
                return None
            df.columns = df.columns.str.strip()
            return df
        return None
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo padrão `{file_path}`: {e}")
        return None

@st.cache_data
def load_social_data(file_path="dashboardsocialgeral.csv"):
    return load_default_file(file_path)

@st.cache_data
def load_urbanism_data(file_path="dashboardurbanismogeral.csv"):
    return load_default_file(file_path)

def load_uploaded_file(uploaded_file, key_prefix):
    if uploaded_file is None:
        return None
    
    file_name = uploaded_file.name
    file_bytes = uploaded_file.getvalue()
    
    try:
        if file_name.endswith('.csv'):
            st.info(f"📁 CSV detectado: `{file_name}`")
            df = read_csv_file(file_bytes, file_name)
            df.columns = df.columns.str.strip()
            
            st.write("🔍 Pré-visualização:")
            st.dataframe(df.head(3), use_container_width=True)
            return df
            
        elif file_name.endswith(('.xlsx', '.xls')):
            st.info(f"📁 Excel detectado: `{file_name}`")
            sheets = parse_excel_sheets(file_bytes, file_name)
            
            selected_sheet = sheets[0]
            if len(sheets) > 1:
                selected_sheet = st.selectbox(
                    f"Aba ({key_prefix}):",
                    options=sheets,
                    key=f"{key_prefix}_sheet_select"
                )
            
            df = read_excel_sheet(file_bytes, file_name, selected_sheet)
            df.columns = df.columns.str.strip()
            
            st.write(f"🔍 Pré-visualização (Aba: {selected_sheet}):")
            st.dataframe(df.head(3), use_container_width=True)
            return df
    except Exception as e:
        st.error(f"Erro ao processar o arquivo `{file_name}`: {e}")
        return None

def validate_social_columns(df):
    required_cols = ['Tarefa', 'Região (PCI)', 'Localidade Específica', 'Status', 'Tipo']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"⚠️ Colunas obrigatórias ausentes no arquivo Social: {', '.join(missing)}")
        return False
    return True

def validate_urbanism_columns(df):
    required_cols = ['Tarefa', 'Região (PCI)', 'Localidade Específica', 'Status', 'Tipo', 'Investimento Previsto (R$)', 'Investimento Realizado (R$)']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"⚠️ Colunas obrigatórias ausentes no arquivo de Urbanismo: {', '.join(missing)}")
        return False
    return True


# ==================== CLASSIFICAÇÃO DOS EIXOS SOCIAIS ====================
def classify_social_eixo(row):
    task = str(row['Tarefa']).lower()
    org = str(row['Responsável - Sec. / Órgão']).lower()
    
    # Esporte e Lazer
    if any(k in task for k in ['boxe', 'jiu jitsu', 'futsal', 'basquete', 'judô', 'ginástica', 'capoeira', 'alongamento', 'funcional', 'kickboxing', 'esporte', 'atletas']):
        return 'Esporte e Lazer'
    # Cultura e Arte
    if any(k in task for k in ['ballet', 'sapateado', 'dança', 'música', 'orquestra', 'teatro', 'cine', 'pipoca', 'tela', 'cultural', 'passaporte', 'museu', 'muf', 'sons', 'funarj']):
        return 'Cultura e Arte'
    # Saúde e Bem-estar
    if any(k in task for k in ['saúde', 'mental', 'yoga', 'clínica', 'médico', 'ambulatório', 'reabilita', 'fisioterapia', 'samu', 'acolhe', 'corpoterapia']):
        return 'Saúde e Bem-estar'
    # Qualificação e Empreendedorismo
    if any(k in task for k in ['inglês', 'francês', 'espanhol', 'faetec', 'informática', 'drone', 'edição', 'barbeiro', 'barbearia', 'sobrancelhas', 'unhas', 'cílios', 'maquiagem', 'trancista', 'perucaria', 'costura', 'cozinha', 'empreendedora', 'mulher', 'desenvolve', 'senac', 'sesc', 'qualificação']):
        return 'Qualificação e Renda'
    # Serviços Públicos e Assistência
    if any(k in task for k in ['detran', 'leão xiii', 'alimenta', 'para todos', 'segov', 'agerio', 'assistência', 'acolher', 'reunião ccci']):
        return 'Serviços e Assistência'
        
    # Fallbacks baseados no Org
    if any(k in org for k in ['cultura', 'funarj', 'secec']):
        return 'Cultura e Arte'
    if any(k in org for k in ['esporte', 'seel', 'nobre artes', 'capoeira', 'cantagalo']):
        return 'Esporte e Lazer'
    if any(k in org for k in ['saúde', 'ses', 'samu', 'clínica']):
        return 'Saúde e Bem-estar'
    if any(k in org for k in ['mulher', 'sedsodh', 'faetec', 'senac', 'sesc', 'firjan', 'agerio']):
        return 'Qualificação e Renda'
    if any(k in org for k in ['detran', 'leão xiii', 'segov', 'seijes']):
        return 'Serviços e Assistência'
        
    return 'Geral / Outros'


# ==================== RENDERIZADOR DE MÉTRICAS (HTML) ====================
def render_metric_card(title, value, delta=None, color=None):
    if color is None:
        color = metric_value_color
    delta_html = f"<div style='color: {subtext_color}; font-size: 0.85rem; margin-top: 6px; font-weight: 500;'>{delta}</div>" if delta else ""
    card_html = f"""
    <div class="metric-card">
        <div style="color: {metric_title_color}; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">{title}</div>
        <div style="color: {color}; font-size: 1.9rem; font-weight: 700; margin-top: 8px;">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


# ==================== SIDEBAR (FILTROS GLOBAIS) ====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1205/1205904.png", width=60)
    st.title("Cidade Integrada")
    st.caption("Painel de Controle e Monitoramento de Impacto")
    
    st.markdown("---")
    
    # ☀️ / 🌙 Seletor de Tema
    theme_choice = st.radio(
        "Aparência do Painel",
        options=["☀️ Claro", "🌙 Escuro"],
        horizontal=True,
        key="theme_toggle",
        index=0 if st.session_state.theme == "☀️ Claro" else 1
    )
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()
        
    st.markdown("---")
    
    # 1. EXPANDER DE UPLOAD DE DADOS (RENDERIZADO NO TOPO DO SIDEBAR)
    with st.expander("📤 Upload de Dados Customizados", expanded=False):
        st.caption("Substitua os arquivos de análise carregando novos CSVs ou Excel.")
        uploaded_social = st.file_uploader("Arquivo Eixo Social", type=["csv", "xlsx", "xls"], key="soc_uploader")
        df_soc_uploaded = load_uploaded_file(uploaded_social, "Social")
        
        uploaded_urb = st.file_uploader("Arquivo Eixo Urbanismo", type=["csv", "xlsx", "xls"], key="urb_uploader")
        df_urb_uploaded = load_uploaded_file(uploaded_urb, "Urbanismo")
        
    # 2. CARREGAR DADOS PADRÕES OU UPLOADED COM VALIDAÇÃO
    df_social_raw = load_social_data()
    df_urb_raw = load_urbanism_data()
    
    if df_soc_uploaded is not None:
        if validate_social_columns(df_soc_uploaded):
            df_social_raw = df_soc_uploaded
            st.toast("👥 Eixo Social atualizado com sucesso!")
            
    if df_urb_uploaded is not None:
        if validate_urbanism_columns(df_urb_uploaded):
            df_urb_raw = df_urb_uploaded
            st.toast("🏗️ Eixo Urbanismo atualizado com sucesso!")
            
    if df_social_raw is None or df_urb_raw is None:
        st.error("Erro ao carregar arquivos de dados básicos do repositório.")
        st.stop()
        
    st.subheader("⚙️ Filtros Globais")
    
    # Combinação de Regiões para filtro único
    regions_social = set(df_social_raw['Região (PCI)'].dropna().unique())
    regions_urb = set(df_urb_raw['Região (PCI)'].dropna().unique())
    all_regions = sorted(list(regions_social.union(regions_urb)))
    
    # Filtro 1: Região
    selected_regions = st.multiselect(
        "Região (PCI)",
        options=all_regions,
        default=all_regions,
        help="Selecione as regiões do programa para filtrar todo o painel."
    )
    
    # Filtrar dados temporariamente por região para obter localidades dependentes
    df_soc_temp = df_social_raw[df_social_raw['Região (PCI)'].isin(selected_regions)]
    df_urb_temp = df_urb_raw[df_urb_raw['Região (PCI)'].isin(selected_regions)]
    
    localities_social = set(df_soc_temp['Localidade Específica'].dropna().unique())
    localities_urb = set(df_urb_temp['Localidade Específica'].dropna().unique())
    all_localities = sorted(list(localities_social.union(localities_urb)))
    
    # Filtro 2: Localidade
    selected_localities = st.multiselect(
        "Localidade Específica",
        options=all_localities,
        default=all_localities,
        help="Filtre por bairros/favelas específicos dependendo das regiões selecionadas."
    )
    
    # Filtro 3: Status
    status_social = set(df_soc_temp['Status'].dropna().unique())
    status_urb = set(df_urb_temp['Status'].dropna().unique())
    all_statuses = sorted(list(status_social.union(status_urb)))
    
    selected_statuses = st.multiselect(
        "Status de Execução",
        options=all_statuses,
        default=all_statuses
    )
            
    st.markdown("---")
    if st.button("🗑️ Limpar Cache de Dados"):
        st.cache_data.clear()
        st.success("Cache limpo com sucesso!")
        
    st.markdown("---")
    st.markdown("""
    **Sobre o Dashboard:**
    Este painel consolida as políticas de **Urbanismo Social** do Estado do RJ nas favelas atendidas.
    
    *Última Atualização Geral:*  
    `12/05/2026`
    """)

# ==================== PRÉ-PROCESSAMENTO E APLICAÇÃO DOS FILTROS ====================
# Limpeza Social
df_social = df_social_raw.copy()
df_social['Localidade Específica'] = df_social['Localidade Específica'].apply(normalize_locality)
df_social['Eixo_Social'] = df_social.apply(classify_social_eixo, axis=1)

# Limpeza Urbanismo
df_urb = df_urb_raw.copy()
df_urb['Localidade Específica'] = df_urb['Localidade Específica'].apply(normalize_locality)

# Conversão e limpeza de números no Urbanismo
df_urb['Investimento Previsto (R$)'] = pd.to_numeric(df_urb['Investimento Previsto (R$)'], errors='coerce').fillna(0)
df_urb['Investimento Realizado (R$)'] = pd.to_numeric(df_urb['Investimento Realizado (R$)'], errors='coerce').fillna(0)
df_urb['Qtd. Total'] = pd.to_numeric(df_urb['Qtd. Total'], errors='coerce').fillna(0)

# Conversão e limpeza de números no Social
df_social['Qtd. Total'] = pd.to_numeric(df_social['Qtd. Total'], errors='coerce').fillna(0)
df_social['Média Atendidos (Mensal)'] = pd.to_numeric(df_social['Média Atendidos (Mensal)'], errors='coerce').fillna(0)

# Conversão de datas (formato BR DD/MM/YYYY). Campos vazios viram NaT.
for _df in (df_social, df_urb):
    _df['Data Inicial'] = pd.to_datetime(
        _df['Data Inicial (Prog. / Interv.)'],
        format='%d/%m/%Y', errors='coerce'
    )
    _df['Data Final'] = pd.to_datetime(
        _df['Data Final (Prog. / Interv.)'],
        format='%d/%m/%Y', errors='coerce'
    )

# Indicador de atraso: tem data final no passado E não está concluída
HOJE = pd.Timestamp('today').normalize()
df_social['Em Atraso'] = (
    df_social['Data Final'].notna() &
    (df_social['Data Final'] < HOJE) &
    (df_social['Status'] != 'Concluída')
)
df_urb['Em Atraso'] = (
    df_urb['Data Final'].notna() &
    (df_urb['Data Final'] < HOJE) &
    (df_urb['Status'] != 'Concluída')
)

# Aplicação dos Filtros Globais
df_social_filtered = df_social[
    (df_social['Região (PCI)'].isin(selected_regions)) &
    (df_social['Localidade Específica'].isin(selected_localities)) &
    (df_social['Status'].isin(selected_statuses))
]

df_urb_filtered = df_urb[
    (df_urb['Região (PCI)'].isin(selected_regions)) &
    (df_urb['Localidade Específica'].isin(selected_localities)) &
    (df_urb['Status'].isin(selected_statuses))
]


# ==================== HEADER DA PÁGINA PRINCIPAL ====================
st.title("📊 Painel de Monitoramento Integrado")
st.markdown("Acompanhamento estratégico do **Programa Cidade Integrada** (Governo do Estado do Rio de Janeiro) — Eixos de **Desenvolvimento Social** e **Urbanismo Social**.")
st.markdown('<div class="custom-hr"></div>', unsafe_allow_html=True)


# ==================== CONFIGURAÇÃO DAS ABAS ====================
tab_geral, tab_social, tab_urbanismo, tab_explorar = st.tabs([
    "🏠 Painel Geral Integrado", 
    "👥 Eixo Social", 
    "🏗️ Eixo Urbanismo (Obras)", 
    "🔍 Exploração Avançada"
])


# ==================== TAB 1: PAINEL GERAL INTEGRADO ====================
with tab_geral:
    # 1. Cards de Métricas Integradas
    col1, col2, col3, col4 = st.columns(4)
    
    # Métricas de Obras
    tot_previsto = df_urb_filtered['Investimento Previsto (R$)'].sum()
    tot_realizado = df_urb_filtered['Investimento Realizado (R$)'].sum()
    pct_exec = (tot_realizado / tot_previsto * 100) if tot_previsto > 0 else 0
    
    # Métricas Sociais
    total_soc_iniciativas = len(df_social_filtered)
    atendidos_soc = df_social_filtered['Qtd. Total'].sum()
    
    # Total Beneficiários Estimados (União dos eixos)
    total_beneficiarios_estimados = atendidos_soc + df_urb_filtered['Qtd. Total'].sum()
    
    with col1:
        render_metric_card(
            title="Investimento Total (Urbanismo)",
            value=f"R$ {tot_previsto/1e6:.1f}M",
            delta=f"R$ {tot_realizado/1e6:.1f}M executados ({pct_exec:.1f}%)",
            color="#10B981"
        )
    with col2:
        render_metric_card(
            title="Iniciativas Sociais",
            value=f"{total_soc_iniciativas}",
            delta=f"{len(df_social_filtered[df_social_filtered['Status'] == 'Em execução'])} ativas no momento",
            color="#1E3A8A"
        )
    with col3:
        render_metric_card(
            title="População Beneficiada",
            value=f"{total_beneficiarios_estimados:,.0f}",
            delta=f"{atendidos_soc:,.0f} via Social + {df_urb_filtered['Qtd. Total'].sum():,.0f} via Obras",
            color="#6366F1"
        )
    with col4:
        # Status de Projetos no Prazo (% de projetos concluídos ou em execução que não estão paralisados/bloqueados)
        total_projetos = len(df_social_filtered) + len(df_urb_filtered)
        bloqueados_parados = len(df_social_filtered[df_social_filtered['Status'] == 'Bloqueada']) + len(df_urb_filtered[df_urb_filtered['Status'] == 'Bloqueada'])
        pct_no_prazo = ((total_projetos - bloqueados_parados) / total_projetos * 100) if total_projetos > 0 else 0
        render_metric_card(
            title="Índice de Execução no Prazo",
            value=f"{pct_no_prazo:.1f}%",
            delta=f"{bloqueados_parados} iniciativa(s) bloqueada(s)",
            color="#00D4B2"
        )
        
    st.markdown('<div class="custom-hr"></div>', unsafe_allow_html=True)
    
    # 2. Mapa e Gráfico de Comparação
    col_left, col_right = st.columns([2, 3])
    
    with col_left:
        st.subheader("📍 Integração Territorial")
        st.markdown("Compare a distribuição das ações sociais com os investimentos de infraestrutura por região do PCI.")
        
        # Gráfico 1: Ações Sociais vs Investimento de Obras por Região
        agg_soc = df_social_filtered.groupby('Região (PCI)').size().reset_index(name='Iniciativas Sociais')
        agg_urb = df_urb_filtered.groupby('Região (PCI)')['Investimento Previsto (R$)'].sum().reset_index(name='Investimento Obras (R$)')
        comparison_df = pd.merge(agg_soc, agg_urb, on='Região (PCI)', how='outer').fillna(0)
        
        fig_comp = make_subplots(specs=[[{"secondary_y": True}]])
        fig_comp.add_trace(go.Bar(
            x=comparison_df['Região (PCI)'],
            y=comparison_df['Iniciativas Sociais'],
            name='Iniciativas Sociais (Qtd)',
            marker_color='#6366F1'
        ), secondary_y=False)
        
        fig_comp.add_trace(go.Scatter(
            x=comparison_df['Região (PCI)'],
            y=comparison_df['Investimento Obras (R$)'],
            name='Investimento Urbanismo (R$)',
            marker=dict(color='#10B981', size=10),
            line=dict(color='#10B981', width=3)
        ), secondary_y=True)
        
        try:
            fig_comp.update_layout(
                title="Relação: Iniciativas Sociais × Investimento Urbanismo",
                template=plotly_template,
                yaxis=dict(
                    title="Iniciativas Sociais (Qtd)",
                    titlefont=dict(color="#6366F1"),
                    tickfont=dict(color="#6366F1"),
                    gridcolor="rgba(128, 128, 128, 0.1)"
                ),
                yaxis2=dict(
                    title="Investimento Urbanismo (R$)",
                    titlefont=dict(color="#10B981"),
                    tickfont=dict(color="#10B981"),
                    gridcolor="rgba(0, 0, 0, 0)"
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(x=0.01, y=0.99, bgcolor="rgba(15,23,42,0.8)", bordercolor="rgba(255,255,255,0.05)"),
                font=dict(color=text_color)
            )
        except Exception as e:
            st.warning(f"Erro ao formatar gráfico: {str(e)[:100]}")
            fig_comp.update_layout(title="Gráfico", template="plotly_dark")
            
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Filtro de tamanho de bolha do mapa
        map_size_mode = st.radio(
            "Tamanho das Bolhas no Mapa representa:",
            ["Quantidade de Iniciativas", "Pessoas Atendidas / Beneficiários", "Investimento de Obras (R$)"],
            horizontal=True
        )

    with col_right:
        st.subheader("🗺️ Mapeamento de Localidades Atendidas")
        
        # Construção da base consolidada do mapa
        map_points = []
        
        # Processar Social
        if len(df_social_filtered) > 0:
            grouped = df_social_filtered.groupby(['Localidade Específica', 'Região (PCI)']).agg(
                iniciativas=('Tarefa', 'count'),
                beneficiarios=('Qtd. Total', 'sum')
            ).reset_index()
            
            for _, r in grouped.iterrows():
                loc = r['Localidade Específica']
                if loc in COORDS:
                    lat, lon = COORDS[loc]
                    map_points.append({
                        'Localidade': loc,
                        'Região': r['Região (PCI)'],
                        'Eixo': 'Eixo Social',
                        'Latitude': lat,
                        'Longitude': lon,
                        'Iniciativas': r['iniciativas'],
                        'Investimento (R$)': 0.0,
                        'Beneficiários': r['beneficiarios'] if r['beneficiarios'] > 0 else 100,
                        'Tamanho_Iniciativas': r['iniciativas'],
                        'Tamanho_Beneficiarios': r['beneficiarios'] if r['beneficiarios'] > 0 else 100,
                        'Tamanho_Investimento': 10 # nominal
                    })
                    
        # Processar Urbanismo
        if len(df_urb_filtered) > 0:
            grouped_u = df_urb_filtered.groupby(['Localidade Específica', 'Região (PCI)']).agg(
                iniciativas=('Tarefa', 'count'),
                investimento=('Investimento Previsto (R$)', 'sum'),
                beneficiarios=('Qtd. Total', 'sum')
            ).reset_index()
            
            for _, r in grouped_u.iterrows():
                loc = r['Localidade Específica']
                if loc in COORDS:
                    lat, lon = COORDS[loc]
                    # Adicionar jitter nas coordenadas do Urbanismo para não sobrepor perfeitamente as do Social
                    map_points.append({
                        'Localidade': loc,
                        'Região': r['Região (PCI)'],
                        'Eixo': 'Eixo Urbanismo',
                        'Latitude': lat + 0.0012,
                        'Longitude': lon + 0.0012,
                        'Iniciativas': r['iniciativas'],
                        'Investimento (R$)': r['investimento'],
                        'Beneficiários': r['beneficiarios'] if r['beneficiarios'] > 0 else 500,
                        'Tamanho_Iniciativas': r['iniciativas'],
                        'Tamanho_Beneficiarios': r['beneficiarios'] if r['beneficiarios'] > 0 else 500,
                        'Tamanho_Investimento': r['investimento']
                    })
                    
        if map_points:
            df_map = pd.DataFrame(map_points)
            
            # Mapear tamanho das bolhas
            if map_size_mode == "Quantidade de Iniciativas":
                df_map['Size_Metric'] = df_map['Tamanho_Iniciativas']
            elif map_size_mode == "Pessoas Atendidas / Beneficiários":
                df_map['Size_Metric'] = df_map['Tamanho_Beneficiarios']
            else:
                df_map['Size_Metric'] = df_map['Tamanho_Investimento']
                # Ajustar bolhas sociais para ter tamanho mínimo legível mesmo se investimento for 0
                df_map.loc[df_map['Eixo'] == 'Eixo Social', 'Size_Metric'] = df_map['Tamanho_Iniciativas'] * 1e5
                
            fig_map = px.scatter_mapbox(
                df_map,
                lat="Latitude",
                lon="Longitude",
                color="Eixo",
                size="Size_Metric",
                hover_name="Localidade",
                hover_data={
                    "Região": True,
                    "Iniciativas": True,
                    "Investimento (R$)": ":,.2f",
                    "Beneficiários": ":,.0f",
                    "Latitude": False,
                    "Longitude": False,
                    "Size_Metric": False
                },
                color_discrete_map={"Eixo Social": "#6366F1", "Eixo Urbanismo": "#10B981"},
                zoom=11,
                size_max=25,
                mapbox_style=mapbox_style
            )
            
            fig_map.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01,
                    bgcolor=card_bg,
                    bordercolor=card_border,
                    borderwidth=1,
                    font=dict(color=text_color)
                ),
                height=450
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("Sem dados geográficos com coordenadas disponíveis para os filtros atuais.")


# ==================== TAB 2: EIXO SOCIAL ====================
with tab_social:
    st.subheader("👥 Indicadores de Políticas e Iniciativas Sociais")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    
    media_atendidos_mensal = df_social_filtered['Média Atendidos (Mensal)'].sum()
    
    # Maturidade de coleta de dados
    cols_coleta_social = [
        'Possui Dados de Gênero', 'Possui Dados de Cor/Raça', 'Possui Dados Etários',
        'Possui Dados de Renda', 'Possui Dados de Escolaridade', 'Possui Dados de Programas Sociais',
        'Possui Dados de Estado Civil', 'Possui Dados de Pessoas Com Deficiência (PCD)',
        'Possui Dados Quantitativos de Filhos'
    ]
    total_cells = len(df_social_filtered) * len(cols_coleta_social)
    if total_cells > 0:
        filled_cells = 0
        for c in cols_coleta_social:
            filled_cells += len(df_social_filtered[(df_social_filtered[c] == 'Sim') | (df_social_filtered[c] == 'Não') | (df_social_filtered[c] == 'Retorno Facultativo')])
        pct_cobertura = (filled_cells / total_cells * 100)
    else:
        pct_cobertura = 0
    
    concluidos_soc = len(df_social_filtered[df_social_filtered['Status'] == 'Concluída'])
    em_atraso_soc = int(df_social_filtered['Em Atraso'].sum())
    
    with col_s1:
        render_metric_card(
            title="Total de Projetos",
            value=f"{len(df_social_filtered)}",
            delta=f"{em_atraso_soc} em atraso" if em_atraso_soc > 0 else "Todos no prazo",
            color="#1E3A8A"
        )
    with col_s2:
        render_metric_card(
            title="Atendimentos / Mês",
            value=f"{media_atendidos_mensal:,.0f}",
            delta="Soma da média mensal das iniciativas",
            color="#6366F1"
        )
    with col_s3:
        render_metric_card(
            title="Maturidade de Coleta",
            value=f"{pct_cobertura:.1f}%",
            delta="Campos socioeconômicos preenchidos",
            color="#00D4B2" if pct_cobertura >= 60 else "#EF4444"
        )
    with col_s4:
        pct_concl = (concluidos_soc / len(df_social_filtered) * 100) if len(df_social_filtered) > 0 else 0
        render_metric_card(
            title="Projetos Concluídos",
            value=f"{concluidos_soc}",
            delta=f"{pct_concl:.1f}% do total",
            color="#10B981"
        )
        
    st.markdown('<div class="custom-hr"></div>', unsafe_allow_html=True)
    
    col_graph_s1, col_graph_s2 = st.columns(2)
    
    with col_graph_s1:
        st.subheader("📚 Iniciativas por Categoria")
        cat_counts = df_social_filtered['Eixo_Social'].value_counts().reset_index()
        cat_counts.columns = ['Categoria', 'Quantidade']
        
        fig_cat = px.bar(
            cat_counts,
            x='Quantidade',
            y='Categoria',
            orientation='h',
            color='Categoria',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="Distribuição das Ações Sociais por Tipo"
        )
        fig_cat.update_layout(
            template=plotly_template,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            showlegend=False,
            xaxis=dict(gridcolor="rgba(128, 128, 128, 0.1)")
        )
        st.plotly_chart(fig_cat, use_container_width=True)
        
        st.subheader("🏢 Top 10 Órgãos Responsáveis")
        top_orgs = df_social_filtered['Responsável - Sec. / Órgão'].value_counts().head(10).reset_index()
        top_orgs.columns = ['Órgão / Secretaria', 'Projetos']
        
        fig_orgs = px.bar(
            top_orgs,
            x='Projetos',
            y='Órgão / Secretaria',
            orientation='h',
            color_discrete_sequence=['#1E3A8A']
        )
        fig_orgs.update_layout(
            template=plotly_template,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            xaxis=dict(gridcolor="rgba(128, 128, 128, 0.1)")
        )
        st.plotly_chart(fig_orgs, use_container_width=True)
        
    with col_graph_s2:
        st.subheader("🎯 Matriz de Gaps de Coleta de Dados")
        st.markdown("Visualização da qualidade de transparência e demografia nos projetos do Eixo Social.")
        
        # Calcular os percentuais de preenchimento para as colunas de dados
        gap_metrics = []
        for col in cols_coleta_social:
            counts = df_social_filtered[col].value_counts().to_dict()
            total = len(df_social_filtered)
            if total > 0:
                gap_metrics.append({
                    'Dados Socioeconômicos': col.replace('Possui Dados de ', '').replace('Possui Dados ', ''),
                    'Coleta Realizada (Sim)': counts.get('Sim', 0) / total * 100,
                    'Sem Coleta (Não)': counts.get('Não', 0) / total * 100,
                    'Aguardando Cadastro': counts.get('Aguardando Informação', 0) / total * 100,
                    'Retorno Facultativo': counts.get('Retorno Facultativo', 0) / total * 100
                })
        
        if gap_metrics:
            df_gaps_s = pd.DataFrame(gap_metrics)
            df_gaps_melt = df_gaps_s.melt(
                id_vars='Dados Socioeconômicos',
                var_name='Status da Coleta',
                value_name='Percentual'
            )
            
            fig_gap_bar = px.bar(
                df_gaps_melt,
                x='Percentual',
                y='Dados Socioeconômicos',
                color='Status da Coleta',
                orientation='h',
                color_discrete_map={
                    'Coleta Realizada (Sim)': '#10B981',
                    'Sem Coleta (Não)': '#EF4444',
                    'Aguardando Cadastro': '#6B7280',
                    'Retorno Facultativo': '#6366F1'
                },
                title="Status de Coleta Cadastral (% de Iniciativas)"
            )
            fig_gap_bar.update_layout(
                template=plotly_template,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color),
                legend=dict(orientation="h", y=-0.15, x=0),
                xaxis=dict(gridcolor="rgba(128, 128, 128, 0.1)")
            )
            st.plotly_chart(fig_gap_bar, use_container_width=True)
            
            # Adicionar matriz térmica de dados por iniciativa
            st.write("**Mapeamento por Iniciativa individual (Filtrado):**")
            with st.expander("🔍 Ver Mapa Térmico Completo por Projeto"):
                if len(df_social_filtered) > 0:
                    # Mapear strings para valores numéricos para criar mapa térmico
                    heatmap_val_map = {
                        'Sim': 3,
                        'Retorno Facultativo': 2,
                        'Não': 1,
                        'Aguardando Informação': 0
                    }
                    
                    df_heat = df_social_filtered[['Tarefa'] + cols_coleta_social].copy()
                    for c in cols_coleta_social:
                        df_heat[c] = df_heat[c].map(heatmap_val_map).fillna(0)
                    
                    # Nomes curtos das colunas
                    short_cols = [c.replace('Possui Dados de ', '').replace('Possui Dados ', '') for c in cols_coleta_social]
                    
                    gray_color = '#CBD5E1' if st.session_state.theme == "☀️ Claro" else '#475569'
                    fig_heat = px.imshow(
                        df_heat[cols_coleta_social].values,
                        labels=dict(x="Tipo de Dado", y="Projeto", color="Status de Coleta"),
                        x=short_cols,
                        y=df_heat['Tarefa'],
                        color_continuous_scale=[
                            [0.0, gray_color], # Cinza - Aguardando
                            [0.33, '#EF4444'], # Vermelho - Não
                            [0.66, '#6366F1'], # Roxo - Facultativo
                            [1.0, '#10B981']  # Verde - Sim
                        ],
                        aspect="auto"
                    )
                    fig_heat.update_layout(
                        template=plotly_template,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=text_color),
                        coloraxis_showscale=False,
                        height=max(400, len(df_social_filtered) * 15)
                    )
                    st.plotly_chart(fig_heat, use_container_width=True)
                    st.caption("Legenda de Cores: 🟥 Não | 🟩 Sim | 🟪 Retorno Facultativo | ⬜ Aguardando Cadastro")
                else:
                    st.info("Sem iniciativas para exibir no mapa térmico.")
        else:
            st.info("Nenhuma métrica de coleta encontrada nos arquivos carregados.")


# ==================== TAB 3: EIXO URBANISMO ====================
with tab_urbanismo:
    st.subheader("🏗️ Monitoramento do Eixo de Urbanismo e Obras")
    
    col_u1, col_u2, col_u3, col_u4 = st.columns(4)
    
    obras_em_exec = len(df_urb_filtered[df_urb_filtered['Status'] == 'Em execução'])
    em_atraso_urb = int(df_urb_filtered['Em Atraso'].sum())
    pct_exec_urb = (tot_realizado / tot_previsto * 100) if tot_previsto > 0 else 0
    
    with col_u1:
        render_metric_card(
            title="Obras Cadastradas",
            value=f"{len(df_urb_filtered)}",
            delta=f"{obras_em_exec} em execução",
            color="#1E3A8A"
        )
    with col_u2:
        render_metric_card(
            title="Orçamento Planejado",
            value=f"R$ {tot_previsto/1e6:.1f}M",
            delta=f"R$ {tot_previsto:,.0f}",
            color="#6366F1"
        )
    with col_u3:
        render_metric_card(
            title="Orçamento Executado",
            value=f"R$ {tot_realizado/1e6:.1f}M",
            delta=f"{pct_exec_urb:.1f}% do previsto",
            color="#10B981"
        )
    with col_u4:
        render_metric_card(
            title="Obras em Atraso",
            value=f"{em_atraso_urb}",
            delta="Data final passada e não concluída" if em_atraso_urb > 0 else "Tudo no prazo",
            color="#EF4444" if em_atraso_urb > 0 else "#10B981"
        )
        
    st.markdown('<div class="custom-hr"></div>', unsafe_allow_html=True)
    
    # ============ GANTT / CRONOGRAMA DAS OBRAS ============
    st.subheader("🗓️ Cronograma de Obras (Gantt)")
    st.caption("Obras com data inicial registrada. Quando não há data final, usa-se a data de hoje como projeção.")
    
    gantt_df = df_urb_filtered.dropna(subset=['Data Inicial']).copy()
    if len(gantt_df) > 0:
        gantt_df['Data Final Plot'] = gantt_df['Data Final'].fillna(HOJE)
        # Limitar nome para não estourar o eixo Y
        gantt_df['Obra'] = gantt_df['Tarefa'].str.slice(0, 60) + gantt_df['Tarefa'].apply(lambda s: '…' if len(str(s)) > 60 else '')
        
        fig_gantt = px.timeline(
            gantt_df,
            x_start='Data Inicial',
            x_end='Data Final Plot',
            y='Obra',
            color='Status',
            hover_data={
                'Localidade Específica': True,
                'Sub-Eixo': True,
                'Investimento Previsto (R$)': ':,.0f',
                'Investimento Realizado (R$)': ':,.0f',
                'Data Inicial': '|%d/%m/%Y',
                'Data Final Plot': '|%d/%m/%Y',
                'Obra': False
            },
            color_discrete_map={
                'Em execução': '#F59E0B',
                'Concluída': '#10B981',
                'Bloqueada': '#EF4444',
                'Aguardando Informação': '#6B7280'
            }
        )
        fig_gantt.update_yaxes(autorange="reversed")
        # Linha vertical no "hoje"
        fig_gantt.add_vline(
            x=HOJE, line_width=2, line_dash="dash", line_color="#00D4B2",
            annotation_text="Hoje", annotation_position="top"
        )
        fig_gantt.update_layout(
            template=plotly_template,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            height=max(400, len(gantt_df) * 35),
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(gridcolor="rgba(128, 128, 128, 0.1)"),
            legend=dict(orientation="h", y=-0.08, x=0)
        )
        st.plotly_chart(fig_gantt, use_container_width=True)
    else:
        st.info("Nenhuma obra com data inicial registrada para os filtros atuais.")
    
    st.markdown('<div class="custom-hr"></div>', unsafe_allow_html=True)
    
    col_graph_u1, col_graph_u2 = st.columns(2)
    
    with col_graph_u1:
        st.subheader("💰 Investimento por Sub-Eixo de Infraestrutura")
        sub_eixo_inv = df_urb_filtered.groupby('Sub-Eixo')[['Investimento Previsto (R$)', 'Investimento Realizado (R$)']].sum().reset_index()
        
        fig_sub = go.Figure()
        fig_sub.add_trace(go.Bar(
            x=sub_eixo_inv['Sub-Eixo'],
            y=sub_eixo_inv['Investimento Previsto (R$)'],
            name='Investimento Previsto',
            marker_color='#1E3A8A'
        ))
        fig_sub.add_trace(go.Bar(
            x=sub_eixo_inv['Sub-Eixo'],
            y=sub_eixo_inv['Investimento Realizado (R$)'],
            name='Investimento Realizado',
            marker_color='#10B981'
        ))
        
        fig_sub.update_layout(
            template=plotly_template,
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            yaxis=dict(gridcolor="rgba(128, 128, 128, 0.1)", title="Valores em Reais (R$)"),
            legend=dict(x=0.01, y=0.99, bgcolor="rgba(15,23,42,0.8)", bordercolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_sub, use_container_width=True)
        
        st.subheader("🏢 Investimento por Região do PCI")
        region_inv = df_urb_filtered.groupby('Região (PCI)')[['Investimento Previsto (R$)', 'Investimento Realizado (R$)']].sum().reset_index()
        
        fig_reg_inv = go.Figure()
        fig_reg_inv.add_trace(go.Bar(
            x=region_inv['Região (PCI)'],
            y=region_inv['Investimento Previsto (R$)'],
            name='Previsto',
            marker_color='#1E3A8A'
        ))
        fig_reg_inv.add_trace(go.Bar(
            x=region_inv['Região (PCI)'],
            y=region_inv['Investimento Realizado (R$)'],
            name='Realizado',
            marker_color='#10B981'
        ))
        fig_reg_inv.update_layout(
            template=plotly_template,
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            yaxis=dict(gridcolor="rgba(128, 128, 128, 0.1)", title="Valores em Reais (R$)"),
            legend=dict(x=0.01, y=0.99, bgcolor="rgba(15,23,42,0.8)", bordercolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_reg_inv, use_container_width=True)
        
    with col_graph_u2:
        st.subheader("📋 Acompanhamento de Obras e Intervenções")
        st.markdown("Status de execução física e progresso das obras cadastrados.")
        
        # Tabela simplificada de obras e status de orçamento
        df_urb_table = df_urb_filtered[[
            'Tarefa', 'Localidade Específica', 'Sub-Eixo', 'Status', 
            'Investimento Previsto (R$)', 'Investimento Realizado (R$)'
        ]].copy()
        
        df_urb_table.columns = ['Intervenção', 'Localidade', 'Setor', 'Status', 'Orçamento Previsto', 'Orçamento Realizado']
        
        # Adicionar barra de progresso do orçamento
        df_urb_table['Progresso Financeiro'] = (df_urb_table['Orçamento Realizado'] / df_urb_table['Orçamento Previsto'] * 100).fillna(0).round(1)
        
        # Formatar moedas para exibição
        df_display = df_urb_table.copy()
        df_display['Orçamento Previsto'] = df_display['Orçamento Previsto'].map('R$ {:,.2f}'.format)
        df_display['Orçamento Realizado'] = df_display['Orçamento Realizado'].map('R$ {:,.2f}'.format)
        df_display['Progresso Financeiro'] = df_display['Progresso Financeiro'].map('{:.1f}%'.format)
        
        st.dataframe(df_display, use_container_width=True, height=350)
        
        # Proporção de status de obras
        st.write("**Distribuição Físico-Financeira por Status:**")
        status_urb_counts = df_urb_filtered['Status'].value_counts().reset_index()
        status_urb_counts.columns = ['Status', 'Quantidade']
        
        fig_status_u = px.pie(
            status_urb_counts,
            values='Quantidade',
            names='Status',
            color='Status',
            color_discrete_map={
                'Em execução': '#F59E0B',
                'Concluída': '#10B981',
                'Bloqueada': '#EF4444',
                'Aguardando Informação': '#6B7280',
                'Em Planejamento': '#3B82F6'
            },
            hole=0.4,
            title="Proporção de Obras por Status Físico"
        )
        fig_status_u.update_layout(
            template=plotly_template,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            legend=dict(orientation="h", y=-0.1, x=0)
        )
        st.plotly_chart(fig_status_u, use_container_width=True)


# ==================== TAB 4: EXPLORAÇÃO AVANÇADA E DADOS BRUTOS ====================
with tab_explorar:
    st.subheader("🔍 Filtros Avançados e Inspeção Detalhada")
    
    # 1. Filtros Cruzados Extras na tela
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        eixo_selecao = st.radio("Filtrar Tabela por Eixo:", ["Todos", "Eixo Social", "Eixo Urbanismo"], horizontal=True)
    with col_f2:
        # Procurar por texto
        text_search = st.text_input("🔍 Buscar por termo (ex: esporte, asfalto, FAETEC):")
    with col_f3:
        # Filtro de órgão específico dependendo dos eixos
        available_orgs = sorted(list(set(df_social_filtered['Responsável - Sec. / Órgão'].dropna().unique()).union(set(df_urb_filtered['Responsável - Sec. / Órgão'].dropna().unique()))))
        selected_org = st.selectbox("Órgão Responsável:", ["Todos"] + available_orgs)
        
    # Construção da tabela de exportação
    # Unificar colunas chave para visualização única
    df_soc_export = df_social_filtered[['Tarefa', 'Região (PCI)', 'Localidade Específica', 'Responsável - Sec. / Órgão', 'Status', 'Tipo', 'Qtd. Total']].copy()
    df_soc_export['Eixo'] = 'Social'
    df_soc_export.columns = ['Nome da Iniciativa', 'Região', 'Localidade', 'Órgão Responsável', 'Status', 'Tipo de Projeto', 'Beneficiários Estimados', 'Eixo']
    
    df_urb_export = df_urb_filtered[['Tarefa', 'Região (PCI)', 'Localidade Específica', 'Responsável - Sec. / Órgão', 'Status', 'Tipo', 'Qtd. Total']].copy()
    df_urb_export['Eixo'] = 'Urbanismo'
    df_urb_export.columns = ['Nome da Iniciativa', 'Região', 'Localidade', 'Órgão Responsável', 'Status', 'Tipo de Projeto', 'Beneficiários Estimados', 'Eixo']
    
    df_combined = pd.concat([df_soc_export, df_urb_export], ignore_index=True)
    
    # Aplicar filtros adicionais
    if eixo_selecao == "Eixo Social":
        df_combined = df_combined[df_combined['Eixo'] == 'Social']
    elif eixo_selecao == "Eixo Urbanismo":
        df_combined = df_combined[df_combined['Eixo'] == 'Urbanismo']
        
    if text_search:
        df_combined = df_combined[
            df_combined['Nome da Iniciativa'].str.contains(text_search, case=False, na=False) |
            df_combined['Localidade'].str.contains(text_search, case=False, na=False) |
            df_combined['Órgão Responsável'].str.contains(text_search, case=False, na=False)
        ]
        
    if selected_org != "Todos":
        df_combined = df_combined[df_combined['Órgão Responsável'] == selected_org]
        
    st.markdown(f"**Iniciativas Encontradas:** `{len(df_combined)}` registros correspondentes.")
    
    # Exibir tabela com estilo
    st.dataframe(df_combined, use_container_width=True, height=400)
    
    # Download dos dados filtrados
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv_data = df_combined.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Dados Filtrados (CSV)",
            data=csv_data,
            file_name="cidade_integrada_filtrado.csv",
            mime="text/csv"
        )
    with col_dl2:
        try:
            # Exportação Excel formatada
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_combined.to_excel(writer, index=False, sheet_name='Integrado')
            xlsx_data = output.getvalue()
            st.download_button(
                label="📥 Baixar Excel Completo (XLSX)",
                data=xlsx_data,
                file_name="cidade_integrada_completo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.caption(f"Exportação Excel indisponível temporariamente. Erro: {e}")
            
    st.markdown('<div class="custom-hr"></div>', unsafe_allow_html=True)
    
    # 2. Inspetor Individual de Projetos
    st.subheader("🔍 Inspetor Detalhado de Projetos")
    st.markdown("Selecione um projeto de qualquer eixo para inspecionar cronogramas, dados coletados e responsáveis.")
    
    project_list = sorted(df_combined['Nome da Iniciativa'].tolist())
    if project_list:
        selected_project = st.selectbox("Escolha o projeto para inspecionar:", project_list)
        
        # Encontrar nas bases originais
        proj_soc = df_social[df_social['Tarefa'] == selected_project]
        proj_urb = df_urb[df_urb['Tarefa'] == selected_project]
        
        if not proj_soc.empty:
            proj_data = proj_soc.iloc[0]
            st.info(f"📌 **Eixo:** Social | **Categoria:** {proj_data['Eixo_Social']}")
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown(f"""
                **Informações Básicas:**
                *   **Nome:** {proj_data['Tarefa']}
                *   **Região:** {proj_data['Região (PCI)']}
                *   **Localidade Específica:** {proj_data['Localidade Específica']}
                *   **Órgão Responsável:** {proj_data['Responsável - Sec. / Órgão']}
                *   **Última Atualização:** {proj_data['Última Atualização']}
                *   **Tipo de Atividade:** {proj_data['Tipo']}
                """)
            with col_d2:
                st.markdown(f"""
                **Cronograma e Impacto:**
                *   **Status de Execução:** `{proj_data['Status']}`
                *   **Data de Início:** {proj_data['Data Inicial (Prog. / Interv.)'] if pd.notnull(proj_data['Data Inicial (Prog. / Interv.)']) else 'Não informada'}
                *   **Data Fim:** {proj_data['Data Final (Prog. / Interv.)'] if pd.notnull(proj_data['Data Final (Prog. / Interv.)']) else 'Não informada'}
                *   **Média Mensal de Atendimento:** {proj_data['Média Atendidos (Mensal)'] if proj_data['Média Atendidos (Mensal)'] > 0 else 'Não informada'}
                *   **Total de Beneficiários:** {proj_data['Qtd. Total'] if proj_data['Qtd. Total'] > 0 else 'Não informado'}
                """)
                
            # Exibir checklist de dados do projeto
            st.markdown("**Matriz Cadastral de Dados Coletados pelo Projeto:**")
            col_ck1, col_ck2, col_ck3 = st.columns(3)
            
            # Formatação visual amigável do status de dados
            def format_check_status(val):
                if val == 'Sim':
                    return "🟩 Coleta Ativa"
                elif val == 'Não':
                    return "🟥 Sem Coleta"
                elif val == 'Retorno Facultativo':
                    return "🟪 Facultativo"
                return "⬜ Aguardando Cadastro"
                
            with col_ck1:
                st.write(f"- **Gênero:** {format_check_status(proj_data['Possui Dados de Gênero'])}")
                st.write(f"- **Cor/Raça:** {format_check_status(proj_data['Possui Dados de Cor/Raça'])}")
                st.write(f"- **Etários (Idade):** {format_check_status(proj_data['Possui Dados Etários'])}")
            with col_ck2:
                st.write(f"- **Renda:** {format_check_status(proj_data['Possui Dados de Renda'])}")
                st.write(f"- **Escolaridade:** {format_check_status(proj_data['Possui Dados de Escolaridade'])}")
                st.write(f"- **Prog. Sociais:** {format_check_status(proj_data['Possui Dados de Programas Sociais'])}")
            with col_ck3:
                st.write(f"- **Estado Civil:** {format_check_status(proj_data['Possui Dados de Estado Civil'])}")
                st.write(f"- **PCD (Deficiência):** {format_check_status(proj_data['Possui Dados de Pessoas Com Deficiência (PCD)'])}")
                st.write(f"- **Filhos (Qtd):** {format_check_status(proj_data['Possui Dados Quantitativos de Filhos'])}")
                
        elif not proj_urb.empty:
            proj_data = proj_urb.iloc[0]
            st.success(f"📌 **Eixo:** Urbanismo & Obras | **Sub-Eixo:** {proj_data['Sub-Eixo']}")
            
            col_du1, col_du2 = st.columns(2)
            with col_du1:
                st.markdown(f"""
                **Informações Básicas da Obra:**
                *   **Intervenção:** {proj_data['Tarefa']}
                *   **Região:** {proj_data['Região (PCI)']}
                *   **Localidade Específica:** {proj_data['Localidade Específica']}
                *   **Órgão Executor:** {proj_data['Responsável - Sec. / Órgão']}
                *   **Última Atualização:** {proj_data['Última Atualização']}
                *   **Tipo de Intervenção:** {proj_data['Tipo']}
                """)
            with col_du2:
                previsto = proj_data['Investimento Previsto (R$)']
                realizado = proj_data['Investimento Realizado (R$)']
                prog_fin = (realizado / previsto * 100) if previsto > 0 else 0
                st.markdown(f"""
                **Orçamento e Cronograma:**
                *   **Status da Obra:** `{proj_data['Status']}`
                *   **Investimento Planejado:** R$ {previsto:,.2f}
                *   **Investimento Liquidado:** R$ {realizado:,.2f}
                *   **Execução Financeira:** {prog_fin:.1f}%
                *   **Data de Início das Obras:** {proj_data['Data Inicial (Prog. / Interv.)'] if pd.notnull(proj_data['Data Inicial (Prog. / Interv.)']) else 'Não informada'}
                *   **Data de Conclusão:** {proj_data['Data Final (Prog. / Interv.)'] if pd.notnull(proj_data['Data Final (Prog. / Interv.)']) else 'Não informada'}
                *   **População Beneficiada Estimada:** {proj_data['Qtd. Total']:,.0f} moradores
                """)
    else:
        st.info("Nenhum projeto encontrado para inspeção.")
