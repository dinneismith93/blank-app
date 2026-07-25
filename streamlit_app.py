import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# Configuração Inicial da Página
st.set_page_config(
    page_title="Drogarias Max - Vendas e Estoque",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS Nativa (Forçando Preto Puro e Alto Contraste em Todos os Elementos)
st.markdown("""
    <style>
    /* Fundo Claro e Texto Preto em Todo o App */
    .stApp {
        background-color: #f8fafc !important;
        color: #000000 !important;
    }
    
    /* Textos, Títulos e Rótulos */
    label, p, span, h1, h2, h3, h4, div {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Forçar Textos Visíveis nos Menus Suspensos e Inputs */
    div[data-baseweb="select"] * {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 16px !important;
    }

    /* Correção do Pop-up Dropdown (Itens do Selectbox) */
    ul[role="listbox"] li, div[role="listbox"] * {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 800 !important;
    }
    
    /* Borda e Fundo dos Campos de Entrada */
    div[data-baseweb="input"] input {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 16px !important;
    }
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border: 2px solid #0d47a1 !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
    }

    /* Header da Drogaria Max */
    .main-header {
        text-align: center;
        padding: 10px 0;
        margin-bottom: 5px;
    }
    .brand-max {
        color: #0d47a1 !important;
        font-size: 30px;
        font-weight: 900;
    }
    .brand-tag {
        color: #e53935 !important;
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
    }

    /* Card do Produto Selecionado */
    .product-box {
        background-color: #ffffff;
        border: 3px solid #e53935;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    .product-name {
        color: #0d47a1 !important;
        font-size: 22px !important;
        font-weight: 900 !important;
    }
    .product-price {
        color: #e53935 !important;
        font-size: 26px !important;
        font-weight: 900 !important;
        margin-top: 5px;
    }

    /* Botão Vermelho Estilizado */
    .stButton>button { 
        width: 100%; 
        background-color: #e53935 !important;
        color: #ffffff !important; 
        border-radius: 10px; 
        height: 52px; 
        font-weight: 900 !important;
        font-size: 17px !important;
        border: none !important;
    }
    .stButton>button * {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Lista Inicial de Medicamentos
dados_iniciais = [
    {"ID": 1001, "Produto": "Atenol 50mg", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 9.50, "Estoque": 99},
    {"ID": 1002, "Produto": "Azitromicina 40mg/mL - Pó p/ Suspensão", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 18.90, "Estoque": 99},
    {"ID": 1003, "Produto": "Azitromicina 500mg - Comprimido", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 14.00, "Estoque": 99},
    {"ID": 1004, "Produto": "Besilato de Anlodipino 5mg", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 6.50, "Estoque": 99},
    {"ID": 1005, "Produto": "Biperideno 2mg - Comprimido", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 12.00, "Estoque": 99},
    {"ID": 1006, "Produto": "Cefalexina 500mg - Comprimido", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 22.50, "Estoque": 99},
    {"ID": 1007, "Produto": "Cetoconazol 20mg/g - Creme Dermatológico", "Categoria": "Dermatologia", "Laboratório": "Genérico", "Preço": 11.00, "Estoque": 99},
    {"ID": 1008, "Produto": "Dipirona Gotas 500mg/mL", "Categoria": "Analgésicos", "Laboratório": "Medley", "Preço": 5.00, "Estoque": 150},
    {"ID": 1009, "Produto": "Losartana Potássica 50mg", "Categoria": "Hipertensão", "Laboratório": "Biosintética", "Preço": 9.90, "Estoque": 120},
    {"ID": 1010, "Produto": "Paracetamol 750mg - Comprimido", "Categoria": "Analgésicos", "Laboratório": "Genérico", "Preço": 6.00, "Estoque": 99}
]

# Estado da Sessão
if "produtos" not in st.session_state:
    st.session_state.produtos = pd.DataFrame(dados_iniciais)

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

if "pedidos" not in st.session_state:
    st.session_state.pedidos = []

if "ultimo_pedido" not in st.session_state:
    st.session_state.ultimo_pedido = None

# Topo
st.markdown("""
    <div class="main-header">
        <div class="brand-max">🔴 DROGARIAS MAX</div>
        <div class="brand-tag">Sempre ao seu lado • Vendas & Controle</div>
    </div>
""", unsafe_allow_html=True)

# Abas de Navegação
tab_venda, tab_cadastro, tab_estoque, tab_historico = st.tabs([
    "🛍️ Emitir Pedido", 
    "➕ Novo Produto", 
    "📦 Estoque & Preços", 
    "📊 Histórico"
])

# --- ABA 1: EMITIR PEDIDO COM DESCONTO INDIVIDUAL ---
with tab_venda:
    st.markdown("### 📋 Dados do Cliente")
    cliente_nome = st.text_input("Cliente / Farmácia:", placeholder="Nome do cliente")
    cliente_tel = st.text_input("WhatsApp para Contato:", placeholder="22999999999")
    endereco_envio = st.text_input("Endereço de Entrega:", placeholder="Rua, Bairro, Cidade")
    pagamento_forma = st.selectbox("Forma de Pagamento:", ["Pix (Aprovação Imediata)", "Cartão de Crédito", "Boleto a Prazo"])

    st.markdown("---")
    st.markdown("### 💊 Seleção do Medicamento")
    
    prod_lista = st.session_state.produtos["Produto"].tolist()
    if prod_lista:
        prod_escolhido = st.selectbox("Escolha o Medicamento:", prod_lista)
        dados_p = st.session_state.produtos[st.session_state.produtos["Produto"] == prod_escolhido].iloc[0]
        
        preco_unitario = float(dados_p['Preço'])
        
        # Display do produto
        st.markdown(f"""
            <div class="product-box">
                <div class="product-name">{dados_p['Produto']}</div>
                <div style="color: #334155; font-size: 14px;">Lab: <b>{dados_p['Laboratório']}</b> | Categoria: <b>{dados_p['Categoria']}</b></div>
                <div class="product-price">Preço Tabela: R$ {preco_unitario:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        col_q, col_d = st.columns(2)
        qtd_compra = col_q.number_input("Quantidade:", min_value=1, max_value=max(1, int(dados_p['Estoque'])), value=1)
        desc_pct = col_d.number_input("Desconto (%):", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
        
        # Cálculo com desconto individual
        preco_com_desconto = preco_unitario * (1 - (desc_pct / 100))
        subtotal_item = preco_com_desconto * qtd_compra
        
        if desc_pct > 0:
            st.info(f"💡 Preço Unitário com {desc_pct}% desc: **R$ {preco_com_desconto:.2f}** | Subtotal: **R$ {subtotal_item:.2f}**")
            
        if st.button("🛒 Adicionar ao Carrinho"):
            st.session_state.carrinho.append({
                "ID": dados_p["ID"],
                "Produto": prod_escolhido,
                "Qtd": qtd_compra,
                "Preço Orig.": preco_unitario,
                "Desc %": desc_pct,
                "Preço Final": preco_com_desconto,
                "Subtotal": subtotal_item
            })
            st.success(f"✅ {qtd_compra}x {prod_escolhido} adicionado ao carrinho!")

    # Exibição do Carrinho
    if st.session_state.carrinho:
        st.markdown("---")
        st.markdown("### 🛒 Itens no Pedido")
        df_cart = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_cart[["Produto", "Qtd", "Desc %", "Preço Final", "Subtotal"]], hide_index=True, use_container_width=True)
        
        val_total = df_cart["Subtotal"].sum()
        st.markdown(f"<h2 style='color:#0d47a1; text-align:right;'>Total: R$ {val_total:.2f}</h2>", unsafe_allow_html=True)
        
        if st.button("🚀 FINALIZAR PEDIDO DROGARIAS MAX"):
            if not cliente_nome.strip():
                st.error("⚠️ Preencha o nome do cliente!")
            else:
                num_pedido = len(st.session_state.pedidos) + 1001
                data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                
                novo_p = {
                    "Pedido": f"#{num_pedido}",
                    "Data": data_atual,
                    "Cliente": cliente_nome,
                    "Telefone": cliente_tel,
                    "Endereço": endereco_envio,
                    "Pagamento": pagamento_forma,
                    "Itens": list(st.session_state.carrinho),
                    "Total": val_total
                }
                
                st.session_state.pedidos.append(novo_p)
                st.session_state.ultimo_pedido = novo_p
                
                # Atualiza Estoque
                for itm in st.session_state.carrinho:
                    idx = st.session_state.produtos[st.session_state.produtos["ID"] == itm["ID"]].index[0]
                    st.session_state.produtos.at[idx, "Estoque"] -= itm["Qtd"]
                
                st.session_state.carrinho = []
                st.balloons()
                st.success(f"🎉 Pedido #{num_pedido} registrado com sucesso!")

    # Comprovante para envio
    if st.session_state.ultimo_pedido:
        ped = st.session_state.ultimo_pedido
        st.markdown("---")
        st.subheader(f"🧾 Comprovante #{ped['Pedido']}")
        
        texto_nota = f"*DROGARIAS MAX - COMPROVANTE DE PEDIDO*\n"
        texto_nota += f"Pedido: {ped['Pedido']} | Data: {ped['Data']}\n"
        texto_nota += f"Cliente: {ped['Cliente']}\n"
        texto_nota += f"Pagamento: {ped['Pagamento']}\n"
        texto_nota += "-------------------------------------\n"
        
        for itm in ped['Itens']:
            desc_str = f" ({itm['Desc %']}% desc)" if itm['Desc %'] > 0 else ""
            texto_nota += f"• {itm['Qtd']}x {itm['Produto']}{desc_str} - R$ {itm['Subtotal']:.2f}\n"
            
        texto_nota += "-------------------------------------\n"
        texto_nota += f"*TOTAL FINAL: R$ {ped['Total']:.2f}*"
        
        st.code(texto_nota, language="text")
        
        if ped['Telefone']:
            tel_limpo = ''.join(filter(str.isdigit, ped['Telefone']))
            msg_url = urllib.parse.quote(texto_nota)
            link_wa = f"https://wa.me/{tel_limpo}?text={msg_url}"
            st.markdown(f"[📲 Enviar Comprovante no WhatsApp]({link_wa})")

# --- ABA 2: CADASTRO DE NOVOS PRODUTOS ---
with tab_cadastro:
    st.markdown("### ➕ Cadastrar Novo Medicamento")
    
    novo_nome = st.text_input("Nome do Produto / Apresentação:", placeholder="Ex: Amoxicilina 500mg - Comprimido")
    col_c1, col_c2 = st.columns(2)
    novo_lab = col_c1.text_input("Laboratório:", placeholder="Ex: EMS / Medley")
    nova_cat = col_c2.selectbox("Categoria:", ["Medicamentos", "Antibióticos", "Analgésicos", "Hipertensão", "Controlados", "Dermatologia", "Vitaminas", "Outros"])
    
    col_p1, col_p2 = st.columns(2)
    novo_preco = col_p1.number_input("Preço de Venda (R$):", min_value=0.10, value=10.00, step=0.50)
    novo_estoque = col_p2.number_input("Estoque Inicial (Unidades):", min_value=1, value=50, step=1)
    
    if st.button("💾 Cadastrar Medicamento"):
        if not novo_nome.strip():
            st.error("⚠️ Insira o nome do produto.")
        else:
            novo_id = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 1001
            novo_item = pd.DataFrame([{
                "ID": novo_id,
                "Produto": novo_nome,
                "Categoria": nova_cat,
                "Laboratório": novo_lab if novo_lab else "Genérico",
                "Preço": float(novo_preco),
                "Estoque": int(novo_estoque)
            }])
            
            st.session_state.produtos = pd.concat([st.session_state.produtos, novo_item], ignore_index=True)
            st.success(f"🎉 {novo_nome} cadastrado com sucesso (Código: {novo_id})!")

# --- ABA 3: ALTERAÇÃO DE PREÇOS E ESTOQUE ---
with tab_estoque:
    st.markdown("### 🛠️ Gerenciar Preços e Estoque")
    
    prods_atuais = st.session_state.produtos["Produto"].tolist()
    if prods_atuais:
        prod_alt = st.selectbox("Selecione o Produto para Alterar:", prods_atuais, key="edit_prod")
        idx_alt = st.session_state.produtos[st.session_state.produtos["Produto"] == prod_alt].index[0]
        
        row_atual = st.session_state.produtos.loc[idx_alt]
        
        col_a1, col_a2 = st.columns(2)
        preco_novo = col_a1.number_input("Novo Preço (R$):", min_value=0.10, value=float(row_atual["Preço"]), step=0.50)
        estoque_add = col_a2.number_input("Adicionar ao Estoque (Qtd):", min_value=0, value=0, step=1)
        
        if st.button("🔄 Atualizar Produto"):
            st.session_state.produtos.at[idx_alt, "Preço"] = preco_novo
            st.session_state.produtos.at[idx_alt, "Estoque"] += estoque_add
            st.success(f"✅ {prod_alt} atualizado com sucesso!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📦 Tabela de Produtos no Sistema")
    st.dataframe(st.session_state.produtos[["ID", "Produto", "Categoria", "Laboratório", "Preço", "Estoque"]], hide_index=True, use_container_width=True)

# --- ABA 4: HISTÓRICO ---
with tab_historico:
    st.subheader("📊 Histórico de Vendas")
    if not st.session_state.pedidos:
        st.info("Nenhuma venda registrada ainda.")
    else:
        df_h = pd.DataFrame(st.session_state.pedidos)
        st.metric("Total Faturado", f"R$ {df_h['Total'].sum():.2f}")
        st.dataframe(df_h[["Pedido", "Data", "Cliente", "Pagamento", "Total"]], hide_index=True, use_container_width=True)
