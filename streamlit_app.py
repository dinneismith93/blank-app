import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# Configuração da página para celular e layout moderno
st.set_page_config(
    page_title="Drogaria Max - Sistema de Vendas",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização Customizada CSS (Design Moderno & Fontes Maior)
st.markdown("""
    <style>
    /* Estilo Global e Fundo */
    .stApp {
        background-color: #0e1117;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Título e Header */
    .app-title {
        color: #00e676;
        font-size: 28px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2px;
    }
    .app-subtitle {
        color: #a0aab8;
        font-size: 14px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Card de Produto Selecionado com Fonte Maior */
    .product-card {
        background: linear-gradient(135deg, #1e2638 0%, #151b27 100%);
        border: 1px solid #2e3a52;
        border-radius: 12px;
        padding: 18px;
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .product-title {
        color: #ffffff;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .product-category {
        display: inline-block;
        background-color: #0066cc;
        color: white;
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 12px;
        margin-bottom: 10px;
        font-weight: 600;
    }
    
    /* Botões Modernos */
    .stButton>button { 
        width: 100%; 
        background: linear-gradient(90deg, #00c853 0%, #009624 100%);
        color: white; 
        border-radius: 10px; 
        height: 50px; 
        font-weight: 700;
        font-size: 17px;
        border: none;
        box-shadow: 0 4px 10px rgba(0, 200, 83, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0, 200, 83, 0.5);
    }
    
    /* Inputs Formatados */
    div[data-baseweb="input"] {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Lista padrão com os medicamentos e suporte a URL de imagens
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
    {"ID": 1011, "Produto": "Clordiazepóxido + Cloreto de Clidínio", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 15.30, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1012, "Produto": "Cloridrato de Amitriptilina 25mg", "Categoria": "Controlados", "Laboratório": "Genérico", "Preço": 9.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1013, "Produto": "Cloridrato de Metformina 850mg", "Categoria": "Diabetes", "Laboratório": "Genérico", "Preço": 11.20, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1014, "Produto": "Cloridrato de Propranolol 40mg", "Categoria": "Hipertensão", "Laboratório": "Genérico", "Preço": 5.50, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1015, "Produto": "Dexametasona 4mg - Comprimido", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 8.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1016, "Produto": "Diazepam 10mg - Comprimido", "Categoria": "Controlados", "Laboratório": "Genérico", "Preço": 6.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1017, "Produto": "Diclofenaco Sódico 50mg", "Categoria": "Analgésicos", "Laboratório": "Genérico", "Preço": 7.50, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1018, "Produto": "Dipirona Gotas 500mg/mL", "Categoria": "Analgésicos", "Laboratório": "Medley", "Preço": 5.00, "Estoque": 150, "Imagem": "https://img.freepik.com/vetores-gratis/garrafa-de-xarope-de-remedio-com-colher_1308-109012.jpg"},
    {"ID": 1019, "Produto": "Enalapril 20mg - Comprimido", "Categoria": "Hipertensão", "Laboratório": "Genérico", "Preço": 8.90, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1020, "Produto": "Fluconazol 150mg - Cápsula", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 6.80, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1021, "Produto": "Furosemida 40mg - Comprimido", "Categoria": "Diuréticos", "Laboratório": "Genérico", "Preço": 4.90, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1022, "Produto": "Glibenclamida 5mg - Comprimido", "Categoria": "Diabetes", "Laboratório": "Genérico", "Preço": 5.20, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1023, "Produto": "Hidroclorotiazida 25mg - Comprimido", "Categoria": "Hipertensão", "Laboratório": "Prati", "Preço": 4.50, "Estoque": 200, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1024, "Produto": "Ibuprofeno 600mg - Comprimido", "Categoria": "Analgésicos", "Laboratório": "Genérico", "Preço": 12.50, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1025, "Produto": "Loratadina 10mg - Comprimido", "Categoria": "Antialérgicos", "Laboratório": "Genérico", "Preço": 9.90, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1026, "Produto": "Losartana Potássica 50mg", "Categoria": "Hipertensão", "Laboratório": "Biosintética", "Preço": 9.90, "Estoque": 120, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1027, "Produto": "Nimesulida 100mg - Comprimido", "Categoria": "Analgésicos", "Laboratório": "Genérico", "Preço": 10.50, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1028, "Produto": "Omeprazol 20mg - Cápsula", "Categoria": "Gastro", "Laboratório": "Genérico", "Preço": 11.50, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1029, "Produto": "Paracetamol 750mg - Comprimido", "Categoria": "Analgésicos", "Laboratório": "Genérico", "Preço": 6.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1030, "Produto": "Prednisona 20mg - Comprimido", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 13.80, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1031, "Produto": "Sinvastatina 20mg - Comprimido", "Categoria": "Farmácia Popular", "Laboratório": "Neo Química", "Preço": 8.00, "Estoque": 90, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1032, "Produto": "Sulfato Ferroso 40mg", "Categoria": "Vitaminas", "Laboratório": "Genérico", "Preço": 4.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1033, "Produto": "Sulfametoxazol + Trimetoprima", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 16.50, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1034, "Produto": "Varfarina Sódica 5mg", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 14.20, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1035, "Produto": "Verapamil 80mg - Comprimido", "Categoria": "Hipertensão", "Laboratório": "Genérico", "Preço": 10.80, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1036, "Produto": "Amoxicilina 500mg - Cápsula", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 18.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1037, "Produto": "Carbamazepina 200mg - Comprimido", "Categoria": "Controlados", "Laboratório": "Genérico", "Preço": 16.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1038, "Produto": "Haloperidol 5mg - Comprimido", "Categoria": "Controlados", "Laboratório": "Genérico", "Preço": 7.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1039, "Produto": "Levotiroxina Sódica 50mcg", "Categoria": "Hormônios", "Laboratório": "Genérico", "Preço": 12.90, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"},
    {"ID": 1040, "Produto": "Risperidona 2mg - Comprimido", "Categoria": "Controlados", "Laboratório": "Genérico", "Preço": 21.00, "Estoque": 99, "Imagem": "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg"}
]

# Inicialização da Memória
if "produtos" not in st.session_state:
    st.session_state.produtos = pd.DataFrame(dados_iniciais)

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

if "pedidos" not in st.session_state:
    st.session_state.pedidos = []

if "ultimo_pedido" not in st.session_state:
    st.session_state.ultimo_pedido = None

# Cabeçalho Principal Customizado
st.markdown("<h1 class='app-title'>🔴 Drogaria Max</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>Sistema Móvel de Emissão de Pedidos & Vendas</p>", unsafe_allow_html=True)

tab_venda, tab_estoque, tab_historico = st.tabs(["🛍️ Emitir Pedido", "📦 Catálogo & Fotos", "📊 Vendas Realizadas"])

# --- ABA 1: EMITIR PEDIDO ---
with tab_venda:
    st.markdown("### 📋 Dados do Cliente")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cliente_nome = st.text_input("Cliente / Farmácia:", placeholder="Ex: Farmácia Central")
    with col_c2:
        cliente_tel = st.text_input("WhatsApp para Contato:", placeholder="22999999999")
        
    endereco_envio = st.text_input("Endereço Completo de Entrega:", placeholder="Rua, Número, Bairro, Cidade")
    pagamento_forma = st.selectbox("Forma de Pagamento:", ["Pix (Aprovação Imediata)", "Cartão de Crédito em Loja", "Boleto a Prazo (30 dias)"])

    st.markdown("---")
    st.markdown("### 💊 Seleção do Medicamento")
    
    prod_lista = st.session_state.produtos["Produto"].tolist()
    if prod_lista:
        prod_escolhido = st.selectbox("Selecione o Produto no Menu:", prod_lista)
        dados_p = st.session_state.produtos[st.session_state.produtos["Produto"] == prod_escolhido].iloc[0]
        
        # CARD MODERNO DO PRODUTO (FONTE MAIOR + DETALHES + FOTO)
        col_img, col_info = st.columns([1, 2])
        
        with col_img:
            img_url = dados_p.get("Imagem", "https://img.freepik.com/vetores-gratis/ilustracao-em-vetor-de-garrafa-de-pulas-de-medicina-isolada_1380-607.jpg")
            st.image(img_url, use_column_width=True)
            
        with col_info:
            st.markdown(f"""
                <div class="product-card">
                    <span class="product-category">{dados_p['Categoria']}</span>
                    <div class="product-title">{dados_p['Produto']}</div>
                    <div style="color: #a0aab8; font-size: 13px;">Laboratório: <b>{dados_p['Laboratório']}</b></div>
                    <div style="color: #00e676; font-size: 26px; font-weight: 800; margin-top: 5px;">
                        R$ {float(dados_p['Preço']):.2f}
                    </div>
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
        st.markdown(f"<h2 style='color:#00e676; text-align:right;'>Total: R$ {val_total:.2f}</h2>", unsafe_allow_html=True)
        
        if st.button("🚀 FINALIZAR PEDIDO DROGARIA MAX"):
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
                
                # Atualização de Estoque
                for itm in st.session_state.carrinho:
                    idx = st.session_state.produtos[st.session_state.produtos["ID"] == itm["ID"]].index[0]
                    st.session_state.produtos.at[idx, "Estoque"] -= itm["Qtd"]
                
                st.session_state.carrinho = []
                st.balloons()
                st.success(f"🎉 Pedido #{num_pedido} registrado com sucesso!")

    # Exibição do Comprovante Formatado
    if st.session_state.ultimo_pedido:
        ped = st.session_state.ultimo_pedido
        st.markdown("---")
        st.subheader(f"🧾 Comprovante do Pedido {ped['Pedido']}")
        
        texto_nota = f"*DROGARIA MAX - COMPROVANTE DE PEDIDO*\n"
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

# --- ABA 2: CATÁLOGO & ESTOQUE ---
with tab_estoque:
    st.subheader("📦 Catálogo Geral com Imagens")
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
