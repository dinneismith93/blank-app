import streamlit as st
import pandas as pd
import pdfplumber

st.set_page_config(page_title="Gestão de Estoque", layout="wide")

st.title("📦 Sistema de Gestão de Estoque")

# Criação do menu principal
menu = st.radio(
    "Menu",
    ["Emitir Pedido", "Novo Produto", "Importar PDF", "Estoque & Preços"],
    horizontal=True
)

st.divider()

if menu == "Emitir Pedido":
    st.header("🛒 Emitir Pedido")
    st.info("Selecione os itens do estoque para gerar o pedido.")

elif menu == "Novo Produto":
    st.header("➕ Cadastrar Novo Produto")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Nome do Produto")
        st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
    with col2:
        st.number_input("Quantidade em Estoque", min_value=0, step=1)
        st.button("Salvar Produto")

elif menu == "Importar PDF":
    st.header("📄 Importar Estoque via PDF")
    st.write("Faça o upload do seu relatório em PDF para cadastrar e atualizar o estoque automaticamente.")
    
    uploaded_file = st.file_uploader("Selecione o arquivo PDF do seu inventário", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("Lendo e extraindo os produtos do PDF..."):
            try:
                produtos_extraidos = []
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        texto = page.extract_text()
                        if texto:
                            produtos_extraidos.append(texto)
                
                st.success("PDF processado com sucesso!")
                st.write(f"Total de páginas lidas: {len(produtos_extraidos)}")
                
                if produtos_extraidos:
                    st.subheader("Exemplo do conteúdo da Página 1:")
                    st.text(produtos_extraidos[0][:1000])

            except Exception as e:
                st.error(f"Erro ao ler o PDF: {e}")

elif menu == "Estoque & Preços":
    st.header("📋 Estoque & Preços")
    st.write("Visualização dos produtos cadastrados.")
