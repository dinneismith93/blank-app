import streamlit as st
import pandas as pd
import datetime

# Configuração da página para focar na tela do celular
st.set_page_config(
    page_title="FarmaRCA Pro - Sistema de Vendas",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS para visual moderno no celular
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        background-color: #0066cc; 
        color: white; 
        border-radius: 10px; 
        height: 48px; 
        font-weight: bold;
        font-size: 16px;
        border: none;
        box-shadow: 0px 4px 10px rgba(0, 102, 204, 0.2);
    }
    .stButton>button:hover {
        background-color: #004999;
        color: white;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #e9ecef;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização do Estoque e Dados
if "produtos" not in st.session_state:
    st.session_state.produtos = pd.DataFrame([
        {"ID": 1001, "Produto": "Losartana Potássica 50mg (30 cp)", "Categoria": "Hipertensão", "Laboratório": "Biosintética", "Preço": 9.90, "Estoque": 120},
        {"ID": 1002, "Produto": "Metformina 850mg (30 cp)", "Categoria": "Diabetes", "Laboratório": "Prati", "Preço": 11.20, "Estoque": 85},
        {"ID": 1003, "Produto": "Hidroclorotiazida 25mg (30 cp)", "Categoria": "Hipertensão", "Laboratório": "Prati", "Preço": 4.50, "Estoque": 200},
        {"ID": 1004, "Produto": "Azitromicina 500mg (3 cp)", "Categoria": "Antibiótico", "Laboratório": "Eurofarma", "Preço": 14.00, "Estoque": 45},
        {"ID": 1005, "Produto": "Dipirona Gotas 500mg/mL (20ml)", "Categoria": "Analgésico", "Laboratório": "Medley", "Preço": 5.00, "Estoque": 150},
        {"ID": 1006, "Produto": "Sinvastatina 20mg (30 cp)", "Categoria": "Farmácia Popular", "Laboratório": "Neo Química", "Preço": 8.00, "Estoque": 90}
    ])

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

if "pedidos" not in st.session_state:
    st.session_state.pedidos = []

# Cabeçalho do App
st.title("💊 FarmaRCA Pro")
st.caption("Força de Vendas e Pedidos Diretos - Uso Mobile")

# Navegação por Abas
tab_venda, tab_estoque, tab_historico = st.tabs(["🛍️ Novo Pedido", "📦 Catálogo / Estoque", "📈 Histórico Vendas"])

# --- ABA 1: EMISSÃO DE PEDIDOS ---
with tab_venda:
    st.subheader("Emitir Pedido de Venda")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cliente_nome = st.text_input("Cliente / Farmácia:", placeholder="Nome do Comprador")
    with col_c2:
        cliente_tel = st.text_input("WhatsApp para Contato:", placeholder="(00) 00000-0000")
        
    endereco_envio = st.text_input("Endereço Completo de Entrega:", placeholder="Rua, Número, Bairro, Cidade")
    pagamento_forma = st.selectbox("Forma de Pagamento:", ["Pix (Aprovação Imediata)", "Cartão de Crédito em Loja", "Boleto a Prazo (30 dias)"])

    st.markdown("---")
    st.markdown("#### **Adicionar Itens ao Carrinho**")
    
    prod_lista = st.session_state.produtos["Produto"].tolist()
    prod_escolhido = st.selectbox("Selecione o Produto:", prod_lista)
    
    dados_p = st.session_state.produtos[st.session_state.produtos["Produto"] == prod_escolhido].iloc[0]
    
    col_p1, col_p2, col_p3 = st.columns(3)
    col_p1.metric("Preço Un.", f"R$ {dados_p['Preço']:.2f}")
    col_p2.metric("Estoque", f"{dados_p['Estoque']} un")
    
    qtd_compra = col_p3.number_input("Qtd:", min_value=1, max_value=int(dados_p['Estoque']), value=1)
    
    if st.button("➕ Adicionar ao Pedido"):
        subtot = qtd_compra * dados_p['Preço']
        st.session_state.carrinho.append({
            "ID": dados_p["ID"],
            "Produto": prod_escolhido,
            "Qtd": qtd_compra,
            "Preço": dados_p['Preço'],
            "Subtotal": subtot
        })
        st.success(f"{qtd_compra}x {prod_escolhido} inserido com sucesso!")

    # Carrinho Ativo
    if st.session_state.carrinho:
        st.markdown("---")
        st.markdown("### 🛒 Resumo do Carrinho")
        df_cart = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_cart[["Produto", "Qtd", "Subtotal"]], hide_index=True, use_container_width=True)
        
        val_total = df_cart["Subtotal"].sum()
        st.markdown(f"### **Total do Pedido: R$ {val_total:.2f}**")
        
        if st.button("🚀 FINALIZAR E GRAVAR PEDIDO"):
            if not cliente_nome.strip():
                st.error("Por favor, preencha o nome do cliente antes de finalizar.")
            else:
                num_pedido = len(st.session_state.pedidos) + 1001
                novo_p = {
                    "Pedido": f"#{num_pedido}",
                    "Data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Cliente": cliente_nome,
                    "Telefone": cliente_tel,
                    "Endereço": endereco_envio,
                    "Pagamento": pagamento_forma,
                    "Itens": len(st.session_state.carrinho),
                    "Total": val_total,
                    "Status": "Aprovado"
                }
                st.session_state.pedidos.append(novo_p)
                
                # Baixa automática no Estoque
                for itm in st.session_state.carrinho:
                    idx = st.session_state.produtos[st.session_state.produtos["ID"] == itm["ID"]].index[0]
                    st.session_state.produtos.at[idx, "Estoque"] -= itm["Qtd"]
                
                st.session_state.carrinho = []
                st.balloons()
                st.success(f"Pedido #{num_pedido} registrado e salvo com sucesso!")

# --- ABA 2: ESTOQUE E PREÇOS ---
with tab_estoque:
    st.subheader("Catálogo de Produtos e Estoque")
    filtro = st.text_input("🔍 Buscar por produto, categoria ou laboratório:")
    
    df_exib = st.session_state.produtos
    if filtro:
        df_exib = df_exib[
            df_exib["Produto"].str.contains(filtro, case=False) | 
            df_exib["Categoria"].str.contains(filtro, case=False) |
            df_exib["Laboratório"].str.contains(filtro, case=False)
        ]
    
    st.dataframe(
        df_exib[["ID", "Produto", "Laboratório", "Categoria", "Preço", "Estoque"]], 
        hide_index=True, 
        use_container_width=True
    )

# --- ABA 3: HISTÓRICO DE VENDAS ---
with tab_historico:
    st.subheader("Painel de Vendas Realizadas")
    if not st.session_state.pedidos:
        st.info("Nenhum pedido foi registrado ainda.")
    else:
        df_hist = pd.DataFrame(st.session_state.pedidos)
        tot_faturado = df_hist["Total"].sum()
        
        st.metric("Total Faturado em Vendas", f"R$ {tot_faturado:.2f}")
        st.markdown("---")
        st.dataframe(df_hist, hide_index=True, use_container_width=True)
                    
