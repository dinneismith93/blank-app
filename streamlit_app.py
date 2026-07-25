import streamlit as st
import pandas as pd
import pdfplumber
import os

st.set_page_config(page_title="Gestão de Estoque", layout="wide")

ARQUIVO_ESTOQUE = "estoque_drogaria.csv"

# Função para carregar o estoque do arquivo no repositório
def carregar_estoque():
    if os.path.exists(ARQUIVO_ESTOQUE):
        try:
            return pd.read_csv(ARQUIVO_ESTOQUE)
        except Exception:
            return pd.DataFrame(columns=['Descrição', 'Quantidade', 'Preço Unit. (R$)'])
    return pd.DataFrame(columns=['Descrição', 'Quantidade', 'Preço Unit. (R$)'])

# Inicializa o estoque com o arquivo permanente
if 'estoque' not in st.session_state:
    st.session_state['estoque'] = carregar_estoque()

st.title("📦 Sistema de Gestão de Estoque")

# Menu principal
menu = st.radio(
    "Menu",
    ["Emitir Pedido", "Novo Produto", "Importar PDF", "Estoque & Preços"],
    horizontal=True,
    key="menu_principal"
)

st.divider()

# --- ABA 1: EMITIR PEDIDO ---
if menu == "Emitir Pedido":
    st.header("🛒 Emitir Pedido")
    if st.session_state['estoque'].empty:
        st.info("O estoque está vazio. Certifique-se de que o arquivo 'estoque_drogaria.csv' está no GitHub.")
    else:
        st.write("Pesquise os produtos para montar seu pedido:")
        
        df_estoque = st.session_state['estoque'].copy()
        
        busca = st.text_input("🔍 Buscar produto pelo nome...", key="busca_pedido")
        if busca:
            df_estoque = df_estoque[df_estoque['Descrição'].str.contains(busca, case=False, na=False)]
        
        st.write(f"Exibindo **{len(df_estoque)}** produtos encontrados:")
        st.dataframe(df_estoque.head(100), use_container_width=True)

# --- ABA 2: NOVO PRODUTO ---
elif menu == "Novo Produto":
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
                st.success(f"Produto '{nome}' adicionado à sessão atual!")
            else:
                st.warning("Preencha o nome do produto.")

# --- ABA 3: IMPORTAR PDF ---
elif menu == "Importar PDF":
    st.header("📄 Importar Estoque via PDF")
    st.write("Upload do relatório para atualizar temporariamente a lista.")
    
    uploaded_file = st.file_uploader("Selecione o arquivo PDF do inventário", type=["pdf"], key="pdf_uploader")
    
    if uploaded_file is not None:
        if st.button("Processar PDF", key="btn_processar_pdf"):
            with st.spinner("Lendo produtos do PDF..."):
                lista_produtos = []
                try:
                    with pdfplumber.open(uploaded_file) as pdf:
                        for page in pdf.pages:
                            texto = page.extract_text()
                            if texto:
                                linhas = texto.split('\n')
                                for linha in linhas:
                                    partes = linha.split(':')
                                    if len(partes) >= 6:
                                        try:
                                            desc = partes[1].strip()
                                            if '-' in desc:
                                                desc = desc.split('-', 1)[1].strip()
                                            
                                            qtd = int(partes[3].strip())
                                            val_unit = float(partes[4].strip().replace(',', '.'))
                                            
                                            lista_produtos.append({
                                                'Descrição': desc,
                                                'Quantidade': qtd,
                                                'Preço Unit. (R$)': val_unit
                                            })
                                        except ValueError:
                                            continue
                    
                    if lista_produtos:
                        st.session_state['estoque'] = pd.DataFrame(lista_produtos)
                        st.success(f"Sucesso! {len(lista_produtos)} produtos carregados.")
                    else:
                        st.warning("Nenhum produto encontrado.")
                        
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")

# --- ABA 4: ESTOQUE & PREÇOS ---
elif menu == "Estoque & Preços":
    st.header("📋 Estoque & Preços")
    if st.session_state['estoque'].empty:
        st.info("Nenhum produto cadastrado no momento.")
    else:
        st.write(f"Total de itens no estoque: **{len(st.session_state['estoque'])}**")
        
        csv_data = st.session_state['estoque'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Backup em CSV",
            data=csv_data,
            file_name="estoque_drogaria.csv",
            mime="text/csv",
            key="btn_download"
        )
        
        st.dataframe(st.session_state['estoque'].head(200), use_container_width=True)
