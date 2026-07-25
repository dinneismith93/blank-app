import streamlit as st
import pandas as pd
import datetime
import urllib.parse
from fpdf import FPDF

# Configuração da página
st.set_page_config(
    page_title="FarmaRCA Pro - Sistema de Vendas",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS
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
    }
    </style>
""", unsafe_allow_html=True)

# Função para gerar o PDF da Nota / Comprovante
def gerar_pdf_nota(pedido_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Cabeçalho
    pdf.cell(0, 10, "FARMARCA PRO - COMPROVANTE DE PEDIDO", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, f"Pedido: {pedido_data['Pedido']} | Data: {pedido_data['Data']}", ln=True)
    pdf.cell(0, 6, f"Cliente: {pedido_data['Cliente']}", ln=True)
    pdf.cell(0, 6, f"Telefone: {pedido_data['Telefone']}", ln=True)
    pdf.cell(0, 6, f"Endereço: {pedido_data['Endereço']}", ln=True)
    pdf.cell(0, 6, f"Forma de Pagamento: {pedido_data['Pagamento']}", ln=True)
    
    pdf.ln(5)
    pdf.cell(0, 0, "", "T", ln=True) # Linha divisória
    pdf.ln(5)
    
    # Tabela de Itens
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(100, 8, "Item / Produto", 1)
    pdf.cell(25, 8, "Qtd", 1, align='C')
    pdf.cell(30, 8, "Unitario", 1, align='R')
    pdf.cell(35, 8, "Subtotal", 1, align='R')
    pdf.ln()
    
    pdf.set_font("Arial", size=10)
    for itm in pedido_data['Itens']:
        pdf.cell(100, 7, str(itm['Produto'])[:40], 1)
        pdf.cell(25, 7, str(itm['Qtd']), 1, align='C')
        pdf.cell(30, 7, f"R$ {itm['Preço']:.2f}", 1, align='R')
        pdf.cell(35, 7, f"R$ {itm['Subtotal']:.2f}", 1, align='R')
        pdf.ln()
        
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"TOTAL DO PEDIDO: R$ {pedido_data['Total']:.2f}", ln=True, align='R')
    
    # Retorna o arquivo em bytes
    return bytes(pdf.output(dest='S'))

# Lista completa dos medicamentos
dados_iniciais = [
    {"ID": 1001, "Produto": "Atenol 50mg", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 9.50, "Estoque": 99},
    {"ID": 1002, "Produto": "Azitromicina 40mg/mL - Pó para Suspensão Oral", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 18.90, "Estoque": 99},
    {"ID": 1003, "Produto": "Azitromicina 500mg - Comprimido", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 14.00, "Estoque": 99},
    {"ID": 1004, "Produto": "Besilato de Anlodipino 5mg - Comprimido", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 6.50, "Estoque": 99},
    {"ID": 1005, "Produto": "Biperideno 2mg - Comprimido", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 12.00, "Estoque": 99},
    {"ID": 1006, "Produto": "Cefalexina 500mg - Comprimido", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 22.50, "Estoque": 99},
    {"ID": 1007, "Produto": "Cetoconazol 20mg/g - Creme Dermatológico", "Categoria": "Dermatologia", "Laboratório": "Genérico", "Preço": 11.00, "Estoque": 99},
    {"ID": 1008, "Produto": "Cinarizina 75mg - Comprimido", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 8.50, "Estoque": 99},
    {"ID": 1009, "Produto": "Ciprofloxacino 500mg - Comprimido", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 19.00, "Estoque": 99},
    {"ID": 1010, "Produto": "Clonazepam 2mg - Comprimido", "Categoria": "Controlados", "Laboratório": "Genérico", "Preço": 7.80, "Estoque": 99},
    {"ID": 1011, "Produto": "Clordiazepóxido + Cloreto de Clidínio", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 15.30, "Estoque": 99},
    {"ID": 1012, "Produto": "Cloridrato de Amitriptilina 25mg", "Categoria": "Controlados", "Laboratório": "Genérico", "Preço": 9.00, "Estoque": 99},
    {"ID": 1013, "Produto": "Cloridrato de Metformina 850mg", "Categoria": "Diabetes", "Laboratório": "Genérico", "Preço": 11.20, "Estoque": 99},
    {"ID": 1014, "Produto": "Cloridrato de Propranolol 40mg", "Categoria": "Hipertensão", "Laboratório": "Genérico", "Preço": 5.50, "Estoque": 99},
    {"ID": 1015, "Produto": "Dexametasona 4mg - Comprimido", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 8.00, "Estoque": 99},
    {"ID": 1016, "Produto": "Diazepam 10mg - Comprimido", "Categoria": "Controlados", "Laboratório": "Genérico", "Preço": 6.00, "Estoque": 99},
    {"ID": 1017, "Produto": "Diclofenaco Sódico 50mg", "Categoria": "Analgésicos", "Laboratório": "Genérico", "Preço": 7.50, "Estoque": 99},
    {"ID": 1018, "Produto": "Dipirona Gotas 500mg/mL", "Categoria": "Analgésicos", "Laboratório": "Medley", "Preço": 5.00, "Estoque": 150},
    {"ID": 1019, "Produto": "Enalapril 20mg - Comprimido", "Categoria": "Hipertensão", "Laboratório": "Genérico", "Preço": 8.90, "Estoque": 99},
    {"ID": 1020, "Produto": "Fluconazol 150mg - Cápsula", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 6.80, "Estoque": 99},
    {"ID": 1021, "Produto": "Furosemida 40mg - Comprimido", "Categoria": "Diuréticos", "Laboratório": "Genérico", "Preço": 4.90, "Estoque": 99},
    {"ID": 1022, "Produto": "Glibenclamida 5mg - Comprimido", "Categoria": "Diabetes", "Laboratório": "Genérico", "Preço": 5.20, "Estoque": 99},
    {"ID": 1023, "Produto": "Hidroclorotiazida 25mg - Comprimido", "Categoria": "Hipertensão", "Laboratório": "Prati", "Preço": 4.50, "Estoque": 200},
    {"ID": 1024, "Produto": "Ibuprofeno 600mg - Comprimido", "Categoria": "Analgésicos", "Laboratório": "Genérico", "Preço": 12.50, "Estoque": 99},
    {"ID": 1025, "Produto": "Loratadina 10mg - Comprimido", "Categoria": "Antialérgicos", "Laboratório": "Genérico", "Preço": 9.90, "Estoque": 99},
    {"ID": 1026, "Produto": "Losartana Potássica 50mg - Comprimido", "Categoria": "Hipertensão", "Laboratório": "Biosintética", "Preço": 9.90, "Estoque": 120},
    {"ID": 1027, "Produto": "Nimesulida 100mg - Comprimido", "Categoria": "Analgésicos", "Laboratório": "Genérico", "Preço": 10.50, "Estoque": 99},
    {"ID": 1028, "Produto": "Omeprazol 20mg - Cápsula", "Categoria": "Gastro", "Laboratório": "Genérico", "Preço": 11.50, "Estoque": 99},
    {"ID": 1029, "Produto": "Paracetamol 750mg - Comprimido", "Categoria": "Analgésicos", "Laboratório": "Genérico", "Preço": 6.00, "Estoque": 99},
    {"ID": 1030, "Produto": "Prednisona 20mg - Comprimido", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 13.80, "Estoque": 99},
    {"ID": 1031, "Produto": "Sinvastatina 20mg - Comprimido", "Categoria": "Farmácia Popular", "Laboratório": "Neo Química", "Preço": 8.00, "Estoque": 90},
    {"ID": 1032, "Produto": "Sulfato Ferroso 40mg", "Categoria": "Vitaminas", "Laboratório": "Genérico", "Preço": 4.00, "Estoque": 99},
    {"ID": 1033, "Produto": "Sulfametoxazol + Trimetoprima", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 16.50, "Estoque": 99},
    {"ID": 1034, "Produto": "Varfarina Sódica 5mg", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 14.20, "Estoque": 99},
    {"ID": 1035, "Produto": "Verapamil 80mg - Comprimido", "Categoria": "Hipertensão", "Laboratório": "Genérico", "Preço": 10.80, "Estoque": 99},
    {"ID": 1036, "Produto": "Amoxicilina 500mg - Cápsula", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 18.00, "Estoque": 99},
    {"ID": 1037, "Produto": "Carbamazepina 200mg - Comprimido", "Categoria": "Controlados", "Laboratório": "Genérico", "Preço": 16.00, "Estoque": 99},
    {"ID": 1038, "Produto": "Haloperidol 5mg - Comprimido", "Categoria": "Controlados", "Laboratório": "Genérico", "Preço": 7.00, "Estoque": 99},
    {"ID": 1039, "Produto": "Levotiroxina Sódica 50mcg", "Categoria": "Hormônios", "Laboratório": "Genérico", "Preço": 12.90, "Estoque": 99},
    {"ID": 1040, "Produto": "Risperidona 2mg - Comprimido", "Categoria": "Controlados", "Laboratório": "Genérico", "Preço": 21.00, "Estoque": 99}
]

# Inicialização de Estado
if "produtos" not in st.session_state:
    st.session_state.produtos = pd.DataFrame(dados_iniciais)

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

if "pedidos" not in st.session_state:
    st.session_state.pedidos = []

if "ultimo_pedido" not in st.session_state:
    st.session_state.ultimo_pedido = None

st.title("💊 FarmaRCA Pro")
st.caption("Força de Vendas e Pedidos Diretos - Uso Mobile")

tab_venda, tab_estoque, tab_historico = st.tabs(["🛍️ Novo Pedido", "📦 Catálogo / Estoque", "📈 Histórico Vendas"])

# --- ABA 1: EMISSÃO DE PEDIDOS ---
with tab_venda:
    st.subheader("Emitir Pedido de Venda")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cliente_nome = st.text_input("Cliente / Farmácia:", placeholder="Nome do Comprador")
    with col_c2:
        cliente_tel = st.text_input("WhatsApp para Contato:", placeholder="22999999999")
        
    endereco_envio = st.text_input("Endereço Completo de Entrega:", placeholder="Rua, Número, Bairro, Cidade")
    pagamento_forma = st.selectbox("Forma de Pagamento:", ["Pix (Aprovação Imediata)", "Cartão de Crédito em Loja", "Boleto a Prazo (30 dias)"])

    st.markdown("---")
    st.markdown("#### **Adicionar Itens ao Carrinho**")
    
    prod_lista = st.session_state.produtos["Produto"].tolist()
    if prod_lista:
        prod_escolhido = st.selectbox("Selecione o Produto:", prod_lista)
        dados_p = st.session_state.produtos[st.session_state.produtos["Produto"] == prod_escolhido].iloc[0]
        
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Preço Un.", f"R$ {float(dados_p['Preço']):.2f}")
        col_p2.metric("Estoque", f"{int(dados_p['Estoque'])} un")
        
        qtd_compra = col_p3.number_input("Qtd:", min_value=1, max_value=max(1, int(dados_p['Estoque'])), value=1)
        
        if st.button("➕ Adicionar ao Pedido"):
            subtot = qtd_compra * float(dados_p['Preço'])
            st.session_state.carrinho.append({
                "ID": dados_p["ID"],
                "Produto": prod_escolhido,
                "Qtd": qtd_compra,
                "Preço": float(dados_p['Preço']),
                "Subtotal": subtot
            })
            st.success(f"{qtd_compra}x {prod_escolhido} inserido!")

    # Carrinho Ativo
    if st.session_state.carrinho:
        st.markdown("---")
        st.markdown("### 🛒 Resumo do Carrinho")
        df_cart = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_cart[["Produto", "Qtd", "Subtotal"]], hide_index=True, use_container_width=True)
        
        val_total = df_cart["Subtotal"].sum()
        st.markdown(f"### **Total do Pedido: R$ {val_total:.2f}**")
        
        if st.button("🚀 FINALIZAR E EMITIR NOTA DO PEDIDO"):
            if not cliente_nome.strip():
                st.error("Por favor, preencha o nome do cliente antes de finalizar.")
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
                
                # Baixa no Estoque
                for itm in st.session_state.carrinho:
                    idx = st.session_state.produtos[st.session_state.produtos["ID"] == itm["ID"]].index[0]
                    st.session_state.produtos.at[idx, "Estoque"] -= itm["Qtd"]
                
                st.session_state.carrinho = []
                st.balloons()
                st.success(f"Pedido #{num_pedido} emitido com sucesso!")

    # Exibição do Comprovante e Botão do PDF
    if st.session_state.ultimo_pedido:
        ped = st.session_state.ultimo_pedido
        st.markdown("---")
        st.subheader(f"🧾 Comprovante do Pedido {ped['Pedido']}")
        
        # Gerar o PDF em memória
        pdf_bytes = gerar_pdf_nota(ped)
        
        st.download_button(
            label="📄 Baixar Comprovante em PDF",
            data=pdf_bytes,
            file_name=f"Nota_Pedido_{ped['Pedido']}.pdf",
            mime="application/pdf"
        )
        
        texto_nota = f"*COMPROVANTE DE COMPRA - FARMARCA PRO*\n"
        texto_nota += f"Pedido: {ped['Pedido']} | Data: {ped['Data']}\n"
        texto_nota += f"Cliente: {ped['Cliente']}\n"
        texto_nota += f"Pagamento: {ped['Pagamento']}\n"
        texto_nota += f"Total: R$ {ped['Total']:.2f}\n\n"
        texto_nota += "Segue acima a confirmação do seu pedido!"
        
        if ped['Telefone']:
            tel_limpo = ''.join(filter(str.isdigit, ped['Telefone']))
            msg_url = urllib.parse.quote(texto_nota)
            link_wa = f"https://wa.me/{tel_limpo}?text={msg_url}"
            st.markdown(f"[📲 Enviar Notificação no WhatsApp do Cliente]({link_wa})")

# --- ABA 2: ESTOQUE ---
with tab_estoque:
    st.subheader("Catálogo de Produtos e Estoque")
    st.dataframe(st.session_state.produtos, hide_index=True, use_container_width=True)

# --- ABA 3: HISTÓRICO DE VENDAS ---
with tab_historico:
    st.subheader("Painel de Vendas Realizadas")
    if not st.session_state.pedidos:
        st.info("Nenhum pedido foi registrado ainda.")
    else:
        df_hist = pd.DataFrame(st.session_state.pedidos)
        st.metric("Total Faturado em Vendas", f"R$ {df_hist['Total'].sum():.2f}")
        st.dataframe(df_hist[["Pedido", "Data", "Cliente", "Pagamento", "Total"]], hide_index=True, use_container_width=True)
