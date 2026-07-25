import streamlit as st
import pandas as pd
import os
import urllib.parse

st.set_page_config(page_title="Farmácia Menor Preço - Gestão & Pedidos", layout="wide", page_icon="💊")

# Estilização do Design
st.markdown("""
    <style>
    /* Estilo do título principal */
    .main-header {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #0E4B82;
        text-align: center;
        padding: 10px 0px 20px 0px;
        font-weight: 800;
        font-size: 2.2rem;
    }
    
    /* Estilo dos cards/seções */
    .css-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #0E4B82;
        margin-bottom: 15px;
    }
    
    /* Botões personalizados */
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

ARQUIVO_ESTOQUE = "estoque_drogaria.csv"

# Carrega o estoque do repositório
@st.cache_data
def carregar_estoque_base():
    if os.path.exists(ARQUIVO_ESTOQUE):
        try:
            df = pd.read_csv(ARQUIVO_ESTOQUE)
            df['Descrição'] = df['Descrição'].astype(str)
            df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce').fillna(0).astype(int)
            df['Preço Unit. (R$)'] = pd.to_numeric(df['Preço Unit. (R$)'], errors='coerce').fillna(0.0)
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=['Descrição', 'Quantidade', 'Preço Unit. (R$)'])

if 'estoque' not in st.session_state:
    st.session_state['estoque'] = carregar_estoque_base()

if 'carrinho' not in st.session_state:
    st.session_state['carrinho'] = []

st.markdown("<h1 class='main-header'>💊 FARMÁCIA MENOR PREÇO</h1>", unsafe_allow_html=True)

# Menu Principal
menu = st.radio(
    "Navegação",
    ["🛒 Emitir Pedido", "📋 Estoque & Preços", "➕ Novo Produto", "📄 Importar PDF"],
    horizontal=True,
    key="menu_principal"
)

st.divider()

# ==================== ABA 1: EMITIR PEDIDO & CARRINHO ====================
if menu == "🛒 Emitir Pedido":
    st.header("🛒 Emitir Pedido do Cliente")
    
    if st.session_state['estoque'].empty:
        st.warning("⚠️ O arquivo de estoque não foi encontrado no repositório GitHub.")
    else:
        col_busca, col_carrinho = st.columns([1, 1])
        
        with col_busca:
            st.subheader("1. Selecionar Medicamentos")
            busca = st.text_input("🔍 Digite o nome do produto para buscar:", "", key="busca_prod")
            
            df_estoque = st.session_state['estoque']
            
            if busca.strip():
                resultados = df_estoque[df_estoque['Descrição'].str.contains(busca, case=False, na=False)]
            else:
                resultados = df_estoque.head(30)
            
            if resultados.empty:
                st.info("Nenhum produto encontrado.")
            else:
                st.write(f"Encontrados **{len(resultados)}** produto(s):")
                opcoes_produtos = resultados['Descrição'].tolist()
                prod_selecionado = st.selectbox("Selecione o produto da lista:", opcoes_produtos, key="select_prod")
                
                item_info = df_estoque[df_estoque['Descrição'] == prod_selecionado].iloc[0]
                preco_base = float(item_info['Preço Unit. (R$)'])
                qtd_disp = int(item_info['Quantidade'])
                
                st.info(f"💡 **Preço Cadastrado:** R$ {preco_base:.2f} | **Estoque:** {qtd_disp} un")
                
                col_p, col_q = st.columns(2)
                with col_p:
                    preco_venda = st.number_input("Preço de Venda (R$):", min_value=0.0, value=preco_base, format="%.2f", key="preco_venda")
                with col_q:
                    qtd_pedir = st.number_input("Qtd Desejada:", min_value=1, max_value=max(1, qtd_disp), value=1, step=1, key="qtd_pedir")
                
                if st.button("➕ Adicionar ao Carrinho", use_container_width=True, type="primary"):
                    st.session_state['carrinho'].append({
                        'Descrição': prod_selecionado,
                        'Qtd': qtd_pedir,
                        'Preço Unit. (R$)': preco_venda,
                        'Subtotal (R$)': round(qtd_pedir * preco_venda, 2)
                    })
                    st.success(f"Adicionado ao carrinho com o valor de R$ {preco_venda:.2f}!")

            st.divider()
            st.subheader("2. Dados da Entrega / Cliente")
            nome_cliente = st.text_input("👤 Nome do Cliente:", key="nome_cliente")
            whatsapp_cliente = st.text_input("📱 WhatsApp do Cliente (com DDD, só números):", placeholder="22999999999", key="whatsapp_cliente")
            endereco_cliente = st.text_area("📍 Endereço Completo de Entrega:", key="endereco_cliente")
            
            # Opções do Motoboy
            cobrar_taxa = st.checkbox("🛵 Incluir taxa de entrega / Motoboy?", key="cobrar_taxa")
            taxa_motoboy = 0.0
            nome_motoboy = ""
            
            if cobrar_taxa:
                taxa_motoboy = st.number_input("Valor da Taxa (R$):", min_value=2.0, max_value=100.0, value=5.0, step=0.5, key="taxa_motoboy")
                nome_motoboy = st.text_input("🛵 Nome do Motoboy / Entregador:", key="nome_motoboy")

        with col_carrinho:
            st.subheader("3. Resumo do Pedido")
            
            if not st.session_state['carrinho']:
                st.info("O carrinho está vazio no momento.")
            else:
                df_carrinho = pd.DataFrame(st.session_state['carrinho'])
                st.dataframe(df_carrinho[['Descrição', 'Qtd', 'Preço Unit. (R$)', 'Subtotal (R$)']], use_container_width=True)
                
                subtotal_produtos = df_carrinho['Subtotal (R$)'].sum()
                total_geral = subtotal_produtos + taxa_motoboy
                
                st.write(f"Subtotal dos Produtos: **R$ {subtotal_produtos:.2f}**")
                if cobrar_taxa:
                    st.write(f"Taxa do Motoboy ({nome_motoboy if nome_motoboy else 'Não informado'}): **R$ {taxa_motoboy:.2f}**")
                
                st.markdown(f"### **Total do Pedido: R$ {total_geral:.2f}**")
                
                # Montagem do texto do comprovante
                texto_comprovante = "========================================\n"
                texto_comprovante += "       FARMACIA MENOR PRECO - PEDIDO    \n"
                texto_comprovante += "========================================\n"
                if nome_cliente:
                    texto_comprovante += f"Cliente: {nome_cliente}\n"
                if endereco_cliente:
                    texto_comprovante += f"Endereco: {endereco_cliente}\n"
                if nome_motoboy:
                    texto_comprovante += f"Entregador: {nome_motoboy}\n"
                texto_comprovante += "----------------------------------------\n"
                texto_comprovante += "ITENS DO PEDIDO:\n"
                
                for idx, row in df_carrinho.iterrows():
                    texto_comprovante += f"{row['Qtd']}x {row['Descrição']}\n"
                    texto_comprovante += f"   R$ {row['Preço Unit. (R$)']:.2f} un -> R$ {row['Subtotal (R$)']:.2f}\n"
                
                texto_comprovante += "----------------------------------------\n"
                texto_comprovante += f"Subtotal: R$ {subtotal_produtos:.2f}\n"
                if cobrar_taxa:
                    texto_comprovante += f"Taxa Entrega: R$ {taxa_motoboy:.2f}\n"
                texto_comprovante += f"TOTAL: R$ {total_geral:.2f}\n"
                texto_comprovante += "========================================\n"
                texto_comprovante += "Obrigado pela preferencia!"

                # Envio direto por WhatsApp
                if whatsapp_cliente:
                    fone_limpo = ''.join(filter(str.isdigit, whatsapp_cliente))
                    msg_encoded = urllib.parse.quote(texto_comprovante)
                    link_wa = f"https://api.whatsapp.com/send?phone=55{fone_limpo}&text={msg_encoded}"
                    st.link_button("📲 Enviar Comprovante via WhatsApp", link_wa, use_container_width=True)

                col_limpar, col_imprimir = st.columns(2)
                with col_limpar:
                    if st.button("🗑️ Limpar Carrinho", use_container_width=True):
                        st.session_state['carrinho'] = []
                        st.rerun()
                        
                with col_imprimir:
                    st.download_button(
                        label="📄 Baixar Comprovante (.txt)",
                        data=texto_comprovante.encode('utf-8'),
                        file_name="comprovante_pedido.txt",
                        mime="text/plain; charset=utf-8",
                        use_container_width=True
                    )

# ==================== ABA 2: ESTOQUE & PREÇOS ====================
elif menu == "📋 Estoque & Preços":
    st.header("📋 Estoque & Preços")
    df_estoque = st.session_state['estoque']
    if not df_estoque.empty:
        st.write(f"Total de itens no estoque: **{len(df_estoque)}**")
        busca_est = st.text_input("🔍 Filtrar lista de estoque por nome:", key="busca_est")
        if busca_est:
            df_exibir = df_estoque[df_estoque['Descrição'].str.contains(busca_est, case=False, na=False)]
        else:
            df_exibir = df_estoque.head(100)
        st.dataframe(df_exibir, use_container_width=True)

# ==================== ABA 3: NOVO PRODUTO ====================
elif menu == "➕ Novo Produto":
    st.header("➕ Cadastrar Novo Produto Manualmente")
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome do Produto", key="nome_prod")
        preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f", key="preco_prod")
    with col2:
        qtd = st.number_input("Quantidade em Estoque", min_value=0, step=1, key="qtd_prod")
        if st.button("Salvar Produto", key="btn_salvar_manual"):
            if nome:
                novo_item = pd.DataFrame([{'Descrição': nome, 'Quantidade': qtd, 'Preço Unit. (R$)': preco}])
                st.session_state['estoque'] = pd.concat([st.session_state['estoque'], novo_item], ignore_index=True)
                st.success(f"Produto '{nome}' adicionado!")

# ==================== ABA 4: IMPORTAR PDF ====================
elif menu == "📄 Importar PDF":
    st.header("📄 Importar Estoque via PDF")
    uploaded_file = st.file_uploader("Selecione o arquivo PDF do inventário", type=["pdf"], key="pdf_uploader")
