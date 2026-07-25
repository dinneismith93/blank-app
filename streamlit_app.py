import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# Configuração da página para celular e layout limpo
st.set_page_config(
    page_title="Drogarias Max - Sistema de Vendas",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS Forçada para Contraste Máximo e Leitura Perfeita
st.markdown("""
    <style>
    /* Fundo Geral da Aplicação Claro */
    .stApp {
        background-color: #f4f6f9 !important;
        color: #000000 !important;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    /* Título da Drogaria Max em Destaque */
    .main-header {
        text-align: center;
        padding: 10px 0;
        margin-bottom: 5px;
    }
    .brand-max {
        color: #0d47a1;
        font-size: 32px;
        font-weight: 900;
        letter-spacing: -1px;
    }
    .brand-tag {
        color: #e53935;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        margin-top: -5px;
    }

    /* Rótulos e Textos Globais em Preto Forte */
    label, p, span, h1, h2, h3, h4, .stMarkdown {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* Forçar TODOS os Inputs, Caixas de Texto e Menus para Fundo Branco e Texto Preto */
    input, select, textarea, div[data-baseweb="input"] input, div[data-baseweb="select"] div {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Borda das Caixas de Texto */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border: 2px solid #0d47a1 !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
    }
    
    /* Menu Pop-up / Dropdown de Medicamentos (Fundo Branco, Letras Pretas) */
    ul[data-baseweb="menu"], div[role="listbox"], li[role="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    li[role="option"]:hover {
        background-color: #e3f2fd !important;
        color: #0d47a1 !important;
    }

    /* Card do Medicamento Selecionado (Destaque e Fonte Grande) */
    .product-box {
        background-color: #ffffff;
        border: 3px solid #e53935;
        border-radius: 12px;
        padding: 18px;
        margin: 15px 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .product-name {
        color: #0d47a1 !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        line-height: 1.2;
    }
    .product-price {
        color: #e53935 !important;
        font-size: 28px !important;
        font-weight: 900 !important;
        margin-top: 8px;
    }

    /* Botão Vermelho Oficial Drogaria Max */
    .stButton>button { 
        width: 100%; 
        background-color: #e53935 !important;
        color: #ffffff !important; 
        border-radius: 10px; 
        height: 54px; 
        font-weight: 800 !important;
        font-size: 18px !important;
        border: none !important;
        box-shadow: 0 4px 8px rgba(229, 57, 53, 0.4);
    }
    .stButton>button * {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Banco de dados dos medicamentos
dados_iniciais = [
    {"ID": 1001, "Produto": "Atenol 50mg", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 9.50, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1002, "Produto": "Azitromicina 40mg/mL - Pó p/ Suspensão", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 18.90, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/garrafa-de-xarope-de-remedio-com-colher_1308-109012.jpg"},
    {"ID": 1003, "Produto": "Azitromicina 500mg - Comprimido", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 14.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1004, "Produto": "Besilato de Anlodipino 5mg", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 6.50, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1005, "Produto": "Biperideno 2mg - Comprimido", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 12.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1006, "Produto": "Cefalexina 500mg - Comprimido", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 22.50, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1007, "Produto": "Cetoconazol 20mg/g - Creme Dermatológico", "Categoria": "Dermatologia", "Laboratório": "Genérico", "Preço": 11.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1008, "Produto": "Cinarizina 75mg - Comprimido", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 8.50, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1009, "Produto": "Ciprofloxacino 500mg - Comprimido", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 19.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1010, "Produto": "Clonazepam 2mg - Comprimido", "Categoria": "Controlados", "Laboratório": "Genérico", "Preço": 7.80, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1018, "Produto": "Dipirona Gotas 500mg/mL", "Categoria": "Analgésicos", "Laboratório": "Medley", "Preço": 5.00, "Estoque": 150, "Imagem": "https://img.freepik.com/vetores-gratis/garrafa-de-xarope-de-remedio-com-colher_1308-109012.jpg"},
    {"ID": 1026, "Produto": "Losartana Potássica 50mg", "Categoria": "Hipertensão", "Laboratório": "Biosintética", "Preço": 9.90, "Estoque": 120, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1029, "Produto": "Paracetamol 750mg - Comprimido", "Categoria": "Analgésicos", "Laboratório": "Genérico", "Preço": 6.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"}
]

# Inicialização de Variáveis na Sessão
if "produtos" not in st.session_state:
    st.session_state.produtos = pd.DataFrame(dados_iniciais)

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

if "pedidos" not in st.session_state:
    st.session_state.pedidos = []

if "ultimo_pedido" not in st.session_state:
    st.session_state.ultimo_pedido = None

# Header da Marca Drogaria Max (Garantido sem Erro de Imagem)
st.markdown("""
    <div class="main-header">
        <div class="brand-max">🔴 DROGARIAS MAX</div>
        <div class="brand-tag">Sempre ao seu lado • Vendas Mobile</div>
    </div>
""", unsafe_allow_html=True)

tab_venda, tab_estoque, tab_historico = st.tabs(["🛍️ Emitir Pedido", "📦 Catálogo", "📊 Vendas Realizadas"])

# --- ABA 1: EMITIR PEDIDO ---
with tab_venda:
    st.markdown("### 📋 Dados do Cliente")
    
    cliente_nome = st.text_input("Cliente / Farmácia:", placeholder="Nome do Cliente")
    cliente_tel = st.text_input("WhatsApp para Contato:", placeholder="22999999999")
    endereco_envio = st.text_input("Endereço Completo de Entrega:", placeholder="Rua, Número, Bairro, Cidade")
    pagamento_forma = st.selectbox("Forma de Pagamento:", ["Pix (Aprovação Imediata)", "Cartão de Crédito em Loja", "Boleto a Prazo (30 dias)"])

    st.markdown("---")
    st.markdown("### 💊 Seleção do Medicamento")
    
    prod_lista = st.session_state.produtos["Produto"].tolist()
    if prod_lista:
        prod_escolhido = st.selectbox("Escolha o Produto na Lista:", prod_lista)
        dados_p = st.session_state.produtos[st.session_state.produtos["Produto"] == prod_escolhido].iloc[0]
        
        # CARD DO PRODUTO (FONTE GRANDE, CONTRASTE ALTO, LEITURA FÁCIL)
        st.markdown(f"""
            <div class="product-box">
                <div class="product-name">{dados_p['Produto']}</div>
                <div style="color: #475569; font-size: 14px; margin-top: 4px;">
                    Laboratório: <b>{dados_p['Laboratório']}</b> | Categoria: <b>{dados_p['Categoria']}</b>
                </div>
                <div class="product-price">R$ {float(dados_p['Preço']):.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Estoque Disponível", f"{int(dados_p['Estoque'])} un")
        qtd_compra = col_m2.number_input("Quantidade Desejada:", min_value=1, max_value=max(1, int(dados_p['Estoque'])), value=1)
        
        if st.button("🛒 Adicionar ao Carrinho"):
            subtot = qtd_compra * float(dados_p['Preço'])
            st.session_state.carrinho.append({
                "ID": dados_p["ID"],
                "Produto": prod_escolhido,
                "Qtd": qtd_compra,
                "Preço": float(dados_p['Preço']),
                "Subtotal": subtot
            })
            st.success(f"✅ {qtd_compra}x {prod_escolhido} adicionado com sucesso!")

    # Carrinho de Compras
    if st.session_state.carrinho:
        st.markdown("---")
        st.markdown("### 🛒 Itens no Pedido")
        df_cart = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_cart[["Produto", "Qtd", "Subtotal"]], hide_index=True, use_container_width=True)
        
        val_total = df_cart["Subtotal"].sum()
        st.markdown(f"<h2 style='color:#0d47a1; text-align:right;'>Total: R$ {val_total:.2f}</h2>", unsafe_allow_html=True)
        
        if st.button("🚀 FINALIZAR PEDIDO DROGARIAS MAX"):
            if not cliente_nome.strip():
                st.error("⚠️ Preencha o nome do cliente para prosseguir.")
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
                    "Total": val_total,
                    "Status": "Aprovado"
                }
                
                st.session_state.pedidos.append(novo_p)
                st.session_state.ultimo_pedido = novo_p
                
                # Atualização do Estoque
                for itm in st.session_state.carrinho:
                    idx = st.session_state.produtos[st.session_state.produtos["ID"] == itm["ID"]].index[0]
                    st.session_state.produtos.at[idx, "Estoque"] -= itm["Qtd"]
                
                st.session_state.carrinho = []
                st.balloons()
                st.success(f"🎉 Pedido #{num_pedido} registrado com sucesso!")

    # Comprovante
    if st.session_state.ultimo_pedido:
        ped = st.session_state.ultimo_pedido
        st.markdown("---")
        st.subheader(f"🧾 Comprovante do Pedido {ped['Pedido']}")
        
        texto_nota = f"*DROGARIAS MAX - COMPROVANTE DE PEDIDO*\n"
        texto_nota += f"Pedido: {ped['Pedido']} | Data: {ped['Data']}\n"
        texto_nota += f"Cliente: {ped['Cliente']}\n"
        texto_nota += f"Endereço: {ped['Endereço']}\n"
        texto_nota += f"Pagamento: {ped['Pagamento']}\n"
        texto_nota += "-------------------------------------\n"
        
        for itm in ped['Itens']:
            texto_nota += f"• {itm['Qtd']}x {itm['Produto']} - R$ {itm['Subtotal']:.2f}\n"
            
        texto_nota += "-------------------------------------\n"
        texto_nota += f"*TOTAL FINAL: R$ {ped['Total']:.2f}*"
        
        st.code(texto_nota, language="text")
        
        if ped['Telefone']:
            tel_limpo = ''.join(filter(str.isdigit, ped['Telefone']))
            msg_url = urllib.parse.quote(texto_nota)
            link_wa = f"https://wa.me/{tel_limpo}?text={msg_url}"
            st.markdown(f"[📲 Enviar Comprovante via WhatsApp]({link_wa})")

# --- ABA 2: CATÁLOGO ---
with tab_estoque:
    st.subheader("📦 Catálogo Geral de Produtos")
    st.dataframe(
        st.session_state.produtos[["ID", "Produto", "Categoria", "Laboratório", "Preço", "Estoque"]], 
        hide_index=True, 
        use_container_width=True
    )

# --- ABA 3: HISTÓRICO ---
with tab_historico:
    st.subheader("📊 Painel Geral de Vendas")
    if not st.session_state.pedidos:
        st.info("Nenhuma venda registrada até o momento.")
    else:
        df_hist = pd.DataFrame(st.session_state.pedidos)
        st.metric("Total Faturado", f"R$ {df_hist['Total'].sum():.2f}")
        st.dataframe(df_hist[["Pedido", "Data", "Cliente", "Pagamento", "Total"]], hide_index=True, use_container_width=True)
