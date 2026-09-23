import streamlit as st
import pandas as pd
import boto3
import plotly.graph_objects as go
from io import StringIO
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Dashboard de Vendas", page_icon="📊", layout="wide")

def obter_credencial(chave):
    if chave in os.environ:
        return os.environ[chave]
    return st.secrets.get(chave)

@st.cache_data
def carregar_dados():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=obter_credencial("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=obter_credencial("AWS_SECRET_ACCESS_KEY"),
        region_name=obter_credencial("AWS_REGION")
    )

# ---------- Carregar dados ----------
@st.cache_data
def carregar_dados():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )
    response = s3.get_object(Bucket="ecommerce-portfolio-pedro", Key="dados/dados_ecommerce.csv")
    conteudo_csv = response["Body"].read().decode("utf-8")
    return pd.read_csv(StringIO(conteudo_csv))

df_original = carregar_dados()
df_original["data_pedido"] = pd.to_datetime(df_original["data_pedido"])
df_original["cliente"] = df_original["nome"] + " " + df_original["sobrenome"]

# ---------- Filtros (sidebar) ----------
st.sidebar.header(" Filtros")

data_min = df_original["data_pedido"].min().date()
data_max = df_original["data_pedido"].max().date()

periodo = st.sidebar.date_input(
    "Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

produtos_disponiveis = sorted(df_original["nome_produto"].unique())
produtos_selecionados = st.sidebar.multiselect(
    "Produto",
    options=produtos_disponiveis,
    default=[]
)

clientes_disponiveis = sorted(df_original["cliente"].unique())
cliente_selecionado = st.sidebar.selectbox(
    "Cliente",
    options=["Todos"] + clientes_disponiveis
)

# Aplicando os filtros em sequência
df = df_original.copy()

if len(periodo) == 2:
    data_inicio, data_fim = periodo
    df = df[(df["data_pedido"].dt.date >= data_inicio) & (df["data_pedido"].dt.date <= data_fim)]

if produtos_selecionados:
    df = df[df["nome_produto"].isin(produtos_selecionados)]

if cliente_selecionado != "Todos":
    df = df[df["cliente"] == cliente_selecionado]

st.sidebar.markdown(f"**{len(df)}** itens de pedido no filtro atual")

# ---------- Cálculos ----------
receita_total = df["valor_total_item"].sum()
num_pedidos = df["pedido_id"].nunique()
ticket_medio = receita_total / num_pedidos if num_pedidos > 0 else 0
clientes_ativos = df["cliente_id"].nunique()

def formatar_moeda_br(valor, com_centavos=True):
    texto = f"R$ {valor:,.2f}" if com_centavos else f"R$ {valor:,.0f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")

# ---------- CSS customizado ----------
st.markdown("""
<style>
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
.main-title {
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    animation: fadeInUp 0.6s ease-out;
}
.kpi-card {
    background: linear-gradient(145deg, #1e2530, #171c26);
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    border: 1px solid #2d3648;
    animation: fadeInUp 0.6s ease-out;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
.kpi-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 24px rgba(96, 165, 250, 0.15);
    border-color: #60a5fa;
}
.kpi-label {
    font-size: 13px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 30px;
    font-weight: 800;
    color: #ffffff;
}
.section-block {
    animation: fadeInUp 0.7s ease-out;
    background: #171c26;
    border: 1px solid #2d3648;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
}
.ranking-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 4px;
    border-bottom: 1px solid #2d3648;
    transition: background-color 0.2s ease;
}
.ranking-row:hover {
    background-color: #1e2530;
}
.ranking-badge {
    display: inline-block;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    color: white;
    font-weight: 700;
    font-size: 12px;
    text-align: center;
    line-height: 26px;
    margin-right: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title"> Dashboard de Vendas — E-commerce</h1>', unsafe_allow_html=True)
st.caption("Pipeline de dados")

# ---------- Cartões KPI ----------
def cartao_kpi(coluna, label, valor):
    coluna.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{valor}</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
cartao_kpi(col1, "Receita Total", formatar_moeda_br(receita_total, com_centavos=False))
cartao_kpi(col2, "Pedidos", num_pedidos)
cartao_kpi(col3, "Ticket Médio", formatar_moeda_br(ticket_medio, com_centavos=False))
cartao_kpi(col4, "Clientes Ativos", clientes_ativos)

st.write("")

# ---------- Receita mensal acumulada ----------
if len(df) > 0:
    df["mes"] = df["data_pedido"].dt.to_period("M")
    receita_mensal = df.groupby("mes")["valor_total_item"].sum().reset_index()
    receita_mensal["mes"] = receita_mensal["mes"].astype(str)
    receita_mensal["receita_acumulada"] = receita_mensal["valor_total_item"].cumsum()

    st.markdown('<div class="section-block">', unsafe_allow_html=True)
    st.subheader("📈 Receita Mensal Acumulada")

    fig_receita = go.Figure()
    fig_receita.add_trace(go.Scatter(
        x=receita_mensal["mes"],
        y=receita_mensal["receita_acumulada"],
        mode="lines+markers",
        line=dict(color="#60a5fa", width=3, shape="spline"),
        marker=dict(size=6, color="#a78bfa"),
        fill="tozeroy",
        fillcolor="rgba(96, 165, 250, 0.15)",
        hovertemplate="%{x}<br>R$ %{y:,.2f}<extra></extra>"
    ))
    fig_receita.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=350,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#2d3648"),
    )
    st.plotly_chart(fig_receita, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Top 5 produtos ----------
    top_produtos = (
        df.groupby("nome_produto")["quantidade"]
        .sum()
        .reset_index()
        .sort_values("quantidade", ascending=True)
        .tail(5)
    )

    st.markdown('<div class="section-block">', unsafe_allow_html=True)
    st.subheader("🏆 Top 5 Produtos Mais Vendidos")

    fig_produtos = go.Figure(go.Bar(
        x=top_produtos["quantidade"],
        y=top_produtos["nome_produto"],
        orientation="h",
        marker=dict(
            color=top_produtos["quantidade"],
            colorscale=[[0, "#60a5fa"], [1, "#a78bfa"]],
        ),
        hovertemplate="%{y}: %{x} unidades<extra></extra>"
    ))
    fig_produtos.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
        xaxis=dict(showgrid=True, gridcolor="#2d3648"),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_produtos, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Top 10 clientes ----------
    top_clientes = (
        df.groupby(["cliente_id", "cliente"])["valor_total_item"]
        .sum()
        .reset_index()
        .sort_values("valor_total_item", ascending=False)
        .head(10)
    )

    st.markdown('<div class="section-block">', unsafe_allow_html=True)
    st.subheader(" Top 10 Clientes Mais Valiosos")

    linhas_html = ""
    for i, row in enumerate(top_clientes.itertuples(), start=1):
        valor_formatado = formatar_moeda_br(row.valor_total_item, com_centavos=False)
        linhas_html += f"""
        <div class="ranking-row">
            <span><span class="ranking-badge">{i}</span>{row.cliente}</span>
            <span style="font-weight:700;">{valor_formatado}</span>
        </div>
        """

    st.markdown(linhas_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")