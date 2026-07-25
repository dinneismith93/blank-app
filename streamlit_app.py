import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gestão de Estoque - Drogaria", layout="wide")

ARQUIVO_ESTOQUE = "estoque_drogaria.csv"

# Carrega o estoque fixo do arquivo do repositório
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

# Inicializa estados do app
if 'estoque' not in st.session_state:
    st.session_state['estoque'] = carregar_estoque_base()

if 'carrinho' not in st.session_state:
    st.session_state['carrinho'] = []

st.title("📦 Sistema de Gestão de Estoque & Pedidos")

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
        col_busca, col_carrinho = st.columns([3, 2])
        
        with col_busca:
            st.subheader("1. Selecionar Medicamentos")
            busca = st.text_input("🔍 Digite o nome do produto para buscar:", "", key="busca_prod")
            
            df_estoque = st.session_state['estoque']
            
            if busca.strip():
                # Filtra os produtos com base na busca
                resultados = df_estoque[df_estoque['Descrição'].str.contains(busca, case=False, na=False)]
            else:
                resultados = df_estoque.head(30) # Exibe 30 por padrão para não carregar a tela à toa
            
            if resultados.empty:
                st.info("Nenhum produto encontrado com essa busca.")
            else:
                st.write(f"Encontrados **{len(resultados)}** produto(s):")
                
                # Seleção por Dropdown do produto desejado
                opcoes_produtos = resultados['Descrição'].tolist()
                prod_selecionado = st.selectbox("Selecione o produto da lista:", opcoes_produtos, key="select_prod")
                
                # Dados do produto selecionado
                item_info = df_estoque[df_estoque['Descrição'] == prod_selecionado].iloc[0]
                preco_unit = float(item_info['Preço Unit. (R$)'])
                qtd_disp = int(item_info['Quantidade'])
                
                st.write(f"**Preço:** R$ {preco_unit:.2f} | **Disponível em Estoque:** {qtd_disp} un")
                
                col_q, col_b = st.columns([1, 1])
                with col_q:
                    qtd_pedir = st.number_input("Qtd Desejada:", min_value=1, max_value=max(1, qtd_disp), value=1, step=1, key="qtd_pedir")
                with col_b:
                    st.write("")
                    st.write("")
                    if st.button("➕ Adicionar ao Carrinho", use_container_width=True):
                        st.session_state['carrinho'].append({
                            'Descrição': prod_selecionado,
                            'Qtd': qtd_pedir,
                            'Preço Unit. (R$)': preco_unit,
                            'Subtotal (R$)': round(qtd_pedir * preco_unit, 2)
                        })
                        st.success(f"Adicionado: {prod_selecionado} ({qtd_pedir} un)")

        with col_carrinho:
            st.subheader("2. Carrinho do Cliente")
            
            if not st.session_state['carrinho']:
                st.info("O carrinho está vazio no momento.")
            else:
                df_carrinho = pd.DataFrame(st.session_state['carrinho'])
                st.dataframe(df_carrinho, use_container_width=True)
                
                total_pedido = df_carrinho['Subtotal (R$)'].sum()
                st.markdown(f"### **Total do Pedido: R$ {total_pedido:.2f}**")
                
                col_limpar, col_imprimir = st.columns(2)
                with col_limpar:
                    if st.button("🗑️ Limpar Carrinho", use_container_width=True):
                        st.session_state['carrinho'] = []
                        st.rerun()
                        
                with col_imprimir:
                    # Gera comprovante simplificado
                    comprovante_txt = f"========================================\n"
                    comprovante_txt += f"           DROGARIA MAX - PEDIDO        \n"
                    comprovante_txt += f"========================================\n\n"
                    for idx, row in df_carrinho.iterrows():
                        comprovante_txt += f"{row['Qtd']}x {row['Descrição']}\n"
                        comprovante_txt += f"   R$ {row['Preço Unit. (R$)']:.2f} un -> R$ {row['Subtotal (R$)']:.2f}\n"
                    comprovante_txt += f"----------------------------------------\n"
                    comprovante_txt += f"TOTAL: R$ {total_pedido:.2f}\n"
                    comprovante_txt += f"========================================\n"
                    comprovante_txt += f"Obrigado pela preferência!\n"
                    
                    st.download_button(
                        label="📄 Emitir / Baixar Comprovante",
                        data=comprovante_txt,
                        file_name="comprovante_pedido.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

# ==================== ABA 2: ESTOQUE & PREÇOS ====================
elif menu == "📋 Estoque & Preços":
    st.header("📋 Estoque & Preços")
    df_estoque = st.session_state['estoque']
    
    if df_estoque.empty:
        st.info("Nenhum produto cadastrado.")
    else:
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
            else:
                st.warning("Preencha o nome do produto.")

# ==================== ABA 4: IMPORTAR PDF ====================
elif menu == "📄 Importar PDF":
    st.header("📄 Importar Estoque via PDF")
    uploaded_file = st.file_uploader("Selecione o arquivo PDF do inventário", type=["pdf"], key="pdf_uploader")
    if uploaded_file is not None:
        st.info("Para salvar definitivamente após importação do PDF, utilize a função de download e substitua o arquivo 'estoque_drogaria.csv' no GitHub.")
