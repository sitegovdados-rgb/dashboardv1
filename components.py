"""
Componentes customizados para o Dashboard Modernizado
"""
import streamlit as st
import pandas as pd
from typing import List, Optional, Dict, Any
import plotly.express as px
import plotly.graph_objects as go


def metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    icon: str = "📊",
) -> None:
    """
    Card de métrica modernizado
    
    Args:
        title: Título da métrica
        value: Valor a ser exibido
        delta: Mudança em relação ao período anterior (opcional)
        delta_color: "normal", "off", "inverse"
        icon: Emoji ou ícone para o card
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.metric(
            label=title,
            value=value,
            delta=delta,
            delta_color=delta_color,
        )
    
    with col2:
        st.write(f"<div style='font-size: 32px;'>{icon}</div>", unsafe_allow_html=True)


def filter_section(
    regions: List[str],
    status_opcoes: List[str],
    tipo_opcoes: List[str],
    key_prefix: str = "filter"
) -> Dict[str, Any]:
    """
    Seção de filtros avançados com layout melhorado
    
    Args:
        regions: Lista de regiões disponíveis
        status_opcoes: Lista de status disponíveis
        tipo_opcoes: Lista de tipos de atividade
        key_prefix: Prefixo para as chaves dos widgets
    
    Returns:
        Dicionário com filtros selecionados
    """
    with st.expander("🔍 Filtros Avançados", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_regions = st.multiselect(
                "📍 Regiões",
                regions,
                default=regions,
                key=f"{key_prefix}_regions"
            )
        
        with col2:
            selected_status = st.multiselect(
                "🎯 Status",
                status_opcoes,
                default=status_opcoes,
                key=f"{key_prefix}_status"
            )
        
        with col3:
            selected_types = st.multiselect(
                "📋 Tipo de Atividade",
                tipo_opcoes,
                default=tipo_opcoes,
                key=f"{key_prefix}_types"
            )
    
    return {
        "regions": selected_regions,
        "status": selected_status,
        "types": selected_types
    }


def data_table_with_download(
    df: pd.DataFrame,
    title: str,
    file_name: str,
    height: int = 400,
) -> None:
    """
    Tabela de dados com opção de download
    
    Args:
        df: DataFrame a exibir
        title: Título da tabela
        file_name: Nome do arquivo para download
        height: Altura da tabela em pixels
    """
    st.subheader(title)
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.write(f"**Registros encontrados:** {len(df)}")
    
    with col2:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ CSV",
            data=csv,
            file_name=f"{file_name}.csv",
            mime="text/csv"
        )
    
    with col3:
        if st.button("📋 Copiar", key=f"copy_{file_name}"):
            st.toast("✅ Copiado!", icon="✓")
    
    st.dataframe(df, use_container_width=True, height=height)


def chart_container(
    fig: go.Figure,
    title: str,
    description: Optional[str] = None,
) -> None:
    """
    Container para gráficos com título e descrição
    
    Args:
        fig: Figure do Plotly
        title: Título do gráfico
        description: Descrição adicional (opcional)
    """
    with st.container(border=True):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.subheader(title)
        with col2:
            if st.button("ℹ️", key=f"info_{title}"):
                if description:
                    st.info(description)
        
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{title}")


def status_badge(status: str) -> str:
    """
    Retorna HTML para badge de status com cor apropriada
    
    Args:
        status: Status texto
    
    Returns:
        HTML do badge
    """
    colors = {
        "Concluída": "#27AE60",
        "Em execução": "#3498DB",
        "Bloqueada": "#E74C3C",
        "Planejada": "#F39C12",
    }
    
    color = colors.get(status, "#95A5A6")
    return f"""
    <span style='
        background-color: {color};
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    '>{status}</span>
    """


def info_box(title: str, content: str, icon: str = "ℹ️") -> None:
    """
    Box de informação customizado
    
    Args:
        title: Título do box
        content: Conteúdo
        icon: Emoji/ícone
    """
    st.info(f"{icon} **{title}**\n\n{content}")


def success_box(title: str, content: str) -> None:
    """Box de sucesso customizado"""
    st.success(f"✅ **{title}**\n\n{content}")


def error_box(title: str, content: str) -> None:
    """Box de erro customizado"""
    st.error(f"❌ **{title}**\n\n{content}")


def warning_box(title: str, content: str) -> None:
    """Box de aviso customizado"""
    st.warning(f"⚠️ **{title}**\n\n{content}")


def create_statistics_grid(stats: List[Dict[str, str]]) -> None:
    """
    Grid de estatísticas com layout responsivo
    
    Args:
        stats: Lista de dicionários com 'label', 'value', 'icon'
    """
    cols = st.columns(len(stats))
    
    for col, stat in zip(cols, stats):
        with col:
            with st.container(border=True):
                st.write(f"**{stat.get('icon', '📊')} {stat['label']}**")
                st.write(f"### {stat['value']}")
                if 'description' in stat:
                    st.caption(stat['description'])


def empty_state(message: str = "Nenhum dado disponível", icon: str = "📭") -> None:
    """
    Estado vazio com mensagem amigável
    
    Args:
        message: Mensagem a exibir
        icon: Emoji/ícone
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write(f"<div style='text-align: center; padding: 40px;'><div style='font-size: 48px;'>{icon}</div><p style='font-size: 18px; color: #95A5A6;'>{message}</p></div>", unsafe_allow_html=True)


def section_divider(title: str) -> None:
    """
    Divisor de seção com título
    
    Args:
        title: Título da seção
    """
    st.markdown(f"## {title}")
    st.divider()
