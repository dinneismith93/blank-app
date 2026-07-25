import streamlit as st
import pdfplumber
import pandas as pd
import re

# ==========================================
# FUNÇÃO PARA LER E EXTRAIR O PDF DO ESTOQUE
# ==========================================
def extrair_produtos_do_pdf(pdf_file):
    produtos = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            for line in lines:
                # Procura linhas com padrão NCM + Descrição + Qtd + Preço
                match = re.search(r'^(\d{8})\s+(.+?)\s+([A-Z]{2})\s+(\d+)\s+([\d\.,]+)\s+([\d\.,]+)$', line.strip())
                if match:
                    ncm, descricao, unidade, qtd, valor_unit, valor_total = match.groups()
                    try:
                        qtd = int(qtd)
                        valor_unit = float(valor_unit.replace('.', '').replace(',', '.'))
                    except ValueError:
                        continue

                    produtos.append({
                        "Nome do Produto": descricao,
                        "Laboratório": "Não Informado",
                        "Categoria": "Medicamentos",
                        "Preço de Venda (R$)": valor_unit,
                        "Estoque Inicial": qtd,
                        "NCM": ncm,
                        "Unidade": unidade
                    })
    return pd.DataFrame(produtos)

def salvar_no_estoque(df_novos_produtos):
    if "banco_produtos" not in st.session_state:
        st.session_state["banco_produtos"] = pd.DataFrame()
    
    st.session_state["banco_produtos"] = pd.concat(
        [st.session_state["banco_produtos"], df_novos_produtos], 
        ignore_index=True
    )

# ==========================================
# INTERFACE E NAVEGAÇÃO
# ==========================================
st.set_page_config(page_title="Vendas & Controle", layout="wide")

aba = st.radio(
    "Menu", 
    ["Emitir Pedido", "Novo Produto", "Importar PDF", "Estoque & Preços"], 
    horizontal=True
)

# --- ABA 1: CADASTRO MANUAL ---
if aba == "Novo Produto":
    st.header("➕ Cadastrar Novo Medicamento")
    
    with st.form("form_novo_produto"):
        nome = st.text_input("Nome do Produto / Apresentação:", placeholder="Ex: Amoxicilina 500mg - Comprimido")
        laboratorio = st.text_input("Laboratório:", placeholder="Ex: EMS / Medley")
        categoria = st.selectbox("Categoria:", ["Medicamentos", "Perfumaria", "Higiene", "Outros"])
        preco = st.number_input("Preço de Venda (R$):", min_value=0.0, value=10.0, step=0.50)
        estoque = st.number_input("Estoque Inicial (Unidades):", min_value=0, value=50, step=1)
        
        btn_salvar = st.form_submit_button("💾 Cadastrar Medicamento")
        
        if btn_salvar:
            novo_item = pd.DataFrame([{
                "Nome do Produto": nome,
                "Laboratório": laboratorio,
                "Categoria": categoria,
                "Preço de Venda (R$)": preco,
                "Estoque Inicial": estoque
            }])
            salvar_no_estoque(novo_item)
            st.success(f"Produto '{nome}' cadastrado com sucesso!")

# --- ABA 2: UPLOAD E LEITURA DE PDF AUTOMÁTICA ---
elif aba == "Importar PDF":
    st.header("📄 Importar Estoque via PDF")
    st.write("Faça o upload do seu relatório em PDF para cadastrar e atualizar o estoque automaticamente.")
    
    arquivo_pdf = st.file_uploader("Selecione o arquivo PDF do seu inventário", type=["pdf"])
    
    if arquivo_pdf is not None:
        with st.spinner("Lendo e extraindo os produtos do PDF..."):
            df_extraido = extrair_produtos_do_pdf(arquivo_pdf)
            
        if not df_extraido.empty:
            st.success(f"🎉 **{len(df_extraido)} produtos** identificados!")
            
            st.subheader("Prévia dos dados:")
            st.dataframe(df_extraido[["Nome do Produto", "Preço de Venda (R$)", "Estoque Inicial", "NCM"]], use_container_width=True)
            
            if st.button("🚀 Confirmar e Atualizar Estoque", type="primary"):
                salvar_no_estoque(df_extraido)
                st.balloons()
                st.success("Todos os produtos do PDF foram adicionados ao estoque!")
        else:
            st.error("Nenhum produto foi identificado no PDF. Verifique se o formato do arquivo é o correto.")

# --- ABA 3: VISUALIZAR ESTOQUE ---
elif aba == "Estoque & Preços":
    st.header("📦 Estoque & Preços")
    
    if "banco_produtos" in st.session_state and not st.session_state["banco_produtos"].empty:
        st.dataframe(st.session_state["banco_produtos"], use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado até o momento.")
