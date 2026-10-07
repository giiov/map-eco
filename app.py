import streamlit as st
import yaml
import pandas as pd
from streamlit_echarts import st_echarts

# A) Configuração da página e Título
st.set_page_config(page_title="Caso DataPulse", layout="wide")
st.title("Caso DataPulse: Ética e Privacidade em IA")
st.subheader("Fase 1 · Comitê Técnico de Crise e Conduta (Grupo 1) · Monitoramento em home office e triagem de currículos")

# Carregar dados
@st.cache_data
def carregar_dados():
    with open("dados.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)

dados = carregar_dados()

# Faixa curta de contexto (2 colunas)
contexto = dados.get("contexto", {})
if contexto:
    col_ctx1, col_ctx2 = st.columns(2)
    with col_ctx1:
        st.info(f"**O que aconteceu:** {contexto.get('casos', '')}")
    with col_ctx2:
        st.warning(f"**Pergunta central:** {contexto.get('perguntas', '')}")

st.markdown("**Como ler:** Clique nos nós para abrir ou fechar ramos. Escolha um tópico no mapa para ler o detalhe.")

# B) Cores e Legenda
raiz = dados["arvore"]
filhos_raiz = raiz.get("filhos", [])

def get_cor_padrao(indice):
    # Paleta de 7 cores distintas para tema escuro
    paleta = ["#E06666", "#4F9DFF", "#FF9F43", "#90C870", "#B48EAD", "#E5C07B", "#56B6C2"]
    return paleta[indice % len(paleta)]

# Aplicar cores aos ramos principais (caso não estejam no YAML)
for i, f in enumerate(filhos_raiz):
    if "cor" not in f:
        f["cor"] = get_cor_padrao(i)

# Renderizar legenda
legenda_html = "<div style='margin-bottom: 15px;'>"
for f in filhos_raiz:
    cor = f["cor"]
    legenda_html += f"<span style='display:inline-block; margin-right: 20px; font-size: 14px;'><span style='display:inline-block; width:12px; height:12px; background-color:{cor}; border-radius:50%; margin-right:6px; vertical-align: middle;'></span><span style='vertical-align: middle;'>{f['nome']}</span></span>"
legenda_html += "</div>"
st.markdown(legenda_html, unsafe_allow_html=True)

# Processar a árvore para o ECharts e D) Tooltip
detalhes = {} # Armazena informações completas de cada nó

def processar_no(no, cor_herdada, caminho_pai):
    nome = no["nome"]
    cor = no.get("cor", cor_herdada)
    pilar = no.get("pilar")
    detalhe = no.get("detalhe", "")
    
    # Gerar resumo para o tooltip
    resumo_padrao = detalhe.split("\n")[0][:140] if detalhe else ""
    resumo = no.get("resumo", resumo_padrao)
    
    # Escapar aspas e tags HTML para o formatter do tooltip
    resumo_escaped = str(resumo).replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    tooltip_html = f"<b>{nome}</b><br/>{resumo_escaped}"
    
    caminho = caminho_pai + [nome] if caminho_pai else [nome]
    filhos = no.get("filhos", [])
    filhos_nomes = [f["nome"] for f in filhos]
    
    detalhes[nome] = {
        "detalhe": detalhe,
        "cor": cor,
        "pilar": pilar,
        "filhos_nomes": filhos_nomes,
        "caminho": caminho
    }
    
    # Construir objeto para o ECharts
    item = {
        "name": nome,
        "tooltip": {
            "formatter": tooltip_html,
            "extraCssText": "white-space: normal; max-width: 320px;"
        }
    }
    
    # Aplicar cores (itemStyle e lineStyle)
    if cor:
        item["itemStyle"] = {"color": cor, "borderColor": cor}
        item["lineStyle"] = {"color": cor}
    else:
        # Nó raiz fica neutro
        item["itemStyle"] = {"color": "#CCCCCC", "borderColor": "#CCCCCC"}
        
    if filhos:
        item["children"] = [processar_no(f, cor, caminho) for f in filhos]
        
    return item

tree_data = processar_no(raiz, None, [])

# Controle de expansão da árvore
if "tree_depth" not in st.session_state:
    st.session_state["tree_depth"] = 1
if "chart_key" not in st.session_state:
    st.session_state["chart_key"] = 0

col_b1, col_b2, _ = st.columns([2, 2, 6])
with col_b1:
    if st.button("🔽 Expandir tudo", use_container_width=True):
        st.session_state["tree_depth"] = 3
        st.session_state["chart_key"] += 1
        st.rerun()
with col_b2:
    if st.button("▶️ Fechar tudo", use_container_width=True):
        st.session_state["tree_depth"] = 1
        st.session_state["chart_key"] += 1
        st.rerun()

# E) Ajustes visuais no mapa
opcoes_echarts = {
    "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
    "series": [{
        "type": "tree", "data": [tree_data],
        "layout": "orthogonal", "orient": "LR", "edgeShape": "curve",
        "initialTreeDepth": st.session_state["tree_depth"], # Dinâmico pelos botões
        "expandAndCollapse": True, "roam": True,
        "top": "3%", "bottom": "3%", "left": "8%", "right": "35%", # Margem direita aumentada
        "symbolSize": 12, "lineStyle": {"width": 2, "curveness": 0.5},
        "label": {
            "position": "left", "verticalAlign": "middle", "align": "right", 
            "fontSize": 14, "width": 180, "overflow": "break" # Evitar rótulos cortados
        },
        "leaves": {
            "label": {
                "position": "right", "verticalAlign": "middle", "align": "left", 
                "width": 220, "overflow": "break"
            }
        },
    }]
}

# Layout do Mapa e Painel de Detalhe
col_mapa, col_texto = st.columns([6, 4])

with col_mapa:
    # C) Evento de clique para o painel de detalhe
    map_event = st_echarts(
        opcoes_echarts, 
        height="900px", 
        events={"click": "function(params) { return params.name }"},
        key=f"echarts_tree_{st.session_state['chart_key']}"
    )

with col_texto:
    # Gerenciar estado do clique
    if "no_selecionado" not in st.session_state:
        st.session_state["no_selecionado"] = raiz["nome"]
    if "last_map_event" not in st.session_state:
        st.session_state["last_map_event"] = None

    if map_event:
        # Lidar com possíveis retornos não-string (dict, ComponentResult, etc)
        nome_clicado = map_event
        if isinstance(map_event, dict):
            nome_clicado = map_event.get("name")
        elif not isinstance(map_event, str):
            try:
                nome_clicado = str(map_event)
            except:
                pass

        if nome_clicado and isinstance(nome_clicado, str):
            # Limpar a string caso ela venha com sujeira
            nome_clicado = nome_clicado.strip()
            if nome_clicado != st.session_state["last_map_event"]:
                if nome_clicado in detalhes:
                    st.session_state["no_selecionado"] = nome_clicado
                st.session_state["last_map_event"] = nome_clicado

    escolhido = st.session_state["no_selecionado"]
    
    # Opção de navegação em duas etapas (Fallback solicitado)
    with st.expander("Navegação manual (Fallback)", expanded=False):
        ramos = [f["nome"] for f in raiz.get("filhos", [])]
        
        # Tentar adivinhar o ramo do nó atual
        ramo_atual = ramos[0] if ramos else ""
        if escolhido in detalhes and len(detalhes[escolhido]["caminho"]) > 1:
            if detalhes[escolhido]["caminho"][1] in ramos:
                ramo_atual = detalhes[escolhido]["caminho"][1]
                
        ramo_selecionado = st.selectbox("1. Ramo principal", ramos, index=ramos.index(ramo_atual) if ramo_atual in ramos else 0)
        
        def obter_descendentes(no_nome):
            desc = []
            for f in detalhes[no_nome]["filhos_nomes"]:
                desc.append(f)
                desc.extend(obter_descendentes(f))
            return desc
            
        subtopicos = [ramo_selecionado] + obter_descendentes(ramo_selecionado)
        
        # Subtópico atual
        sub_atual = escolhido if escolhido in subtopicos else ramo_selecionado
        sub_selecionado = st.selectbox("2. Tópico", subtopicos, index=subtopicos.index(sub_atual))
        
        if st.button("Abrir Tópico Selecionado"):
            st.session_state["no_selecionado"] = sub_selecionado
            st.rerun()

    # C) Renderizar Painel de Detalhe
    info = detalhes[escolhido]
    cor_painel = info["cor"] if info["cor"] else "#CCCCCC"
    
    # Cabeçalho com a cor do ramo
    st.markdown(f"<h3 style='color:{cor_painel}; margin-bottom:0;'>{escolhido}</h3>", unsafe_allow_html=True)
    
    # Breadcrumb
    breadcrumb = " › ".join(info["caminho"])
    st.caption(f"**Caminho:** {breadcrumb}")
    
    # Badge do Pilar
    if info.get("pilar"):
        st.markdown(
            f"<span style='background-color:{cor_painel}; color:#111; padding: 3px 10px; "
            f"border-radius: 12px; font-size: 12px; font-weight: bold;'>"
            f"{info['pilar']}</span>", 
            unsafe_allow_html=True
        )
        
    st.write("")
    
    # Conteúdo do detalhe
    st.markdown(info["detalhe"])
    
    if escolhido == "Matriz de mapeamento":
        st.markdown("<br>", unsafe_allow_html=True)
        df = pd.DataFrame(dados["matriz"]).rename(columns={
            "situacao": "Situação", "problema": "Problema identificado",
            "conflito_etico_comportamental": "Conflito ético / comportamental",
            "conflito_tecnico_legal": "Conflito técnico / legal"})
        st.dataframe(df, hide_index=True, use_container_width=True)

    # Subtópicos do ramo
    if info["filhos_nomes"]:
        st.markdown("---")
        st.markdown(f"**Neste ramo:**")
        for f in info["filhos_nomes"]:
            st.markdown(f"- {f}")

st.divider()

# Glossário
with st.expander("Glossário de conceitos"):
    for g in dados["glossario"]:
        st.markdown(f"**{g['termo']}:** {g['definicao']}")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 👥 Equipe - 3º AMS")

cols = st.columns(4)

integrantes = [
    {"nome": "Antonella Prucoli"},
    {"nome": "Bruno Holanda"},
    {"nome": "Emilly Vitória"},
    {"nome": "Giovana Cipulo"},
    {"nome": "Heloisa Fernandes"},
    {"nome": "Heloisa Torres"},
    {"nome": "Maria Eduarda Chella"},
    {"nome": "Matheus Amorim"}
]

cores = ["#E06666", "#4F9DFF", "#FF9F43", "#90C870", "#B48EAD", "#E5C07B", "#56B6C2", "#E06666"]

for i, integrante in enumerate(integrantes):
    cor = cores[i % len(cores)]
    with cols[i % 4]:
        st.markdown(f"""
        <div style="
            border: 1px solid rgba(255,255,255,0.1);
            border-top: 4px solid {cor};
            padding: 1.5rem 1rem;
            border-radius: 0.5rem;
            text-align: center;
            background-color: rgba(255,255,255,0.02);
            margin-bottom: 1rem;
        ">
            <h4 style="margin: 0; font-size: 1.1rem;">{integrante['nome']}</h4>
        </div>
        """, unsafe_allow_html=True)