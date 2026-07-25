import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# Configuração da página para focar na tela do celular
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

# Inicialização dos Dados
if "produtos" not in st.session_state:
    st.session_state.produtos = pd.DataFrame([
        {"ID": 1001, "Produto": "Atenol 50mg", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 9.50, "Estoque": 99},
        {"ID": 1002, "Produto": "Azitromicina 500mg - Comprimido", "Categoria": "Antibióticos", "Laboratório": "Genérico", "Preço": 14.00, "Estoque": 99},
        {"ID": 1003, "Produto": "Besilato de Anlodipino 5mg", "Categoria": "Medicamentos", "Laboratório": "Genérico", "Preço": 6.50, "Estoque": 99},
        {"ID": 1004, "Produto": "Dipirona Gotas 500mg/mL (20ml)", "Categoria": "Analgésico", "Laboratório": "Medley", "Preço": 5.00, "Estoque": 150}
    ])

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
                
                # Baixa automática no Estoque
                for itm in st.session_state.carrinho:
                    idx = st.session_state.produtos[st.session_state.produtos["ID"] == itm["ID"]].index[0]
                    st.session_state.produtos.at[idx, "Estoque"] -= itm["Qtd"]
                
                st.session_state.carrinho = []
                st.balloons()
                st.success(f"Pedido #{num_pedido} emitido com sucesso!")

    # Exibição do Comprovante/Nota do Último Pedido Emitido
    if st.session_state.ultimo_pedido:
        ped = st.session_state.ultimo_pedido
        st.markdown("---")
        st.subheader(f"🧾 Comprovante de Venda {ped['Pedido']}")
        
        texto_nota = f"*COMPROVANTE DE COMPRA - FARMARCA PRO*\n"
        texto_nota += f"Pedido: {ped['Pedido']} | Data: {ped['Data']}\n"
        texto_nota += f"Cliente: {ped['Cliente']}\n"
        texto_nota += f"Endereço: {ped['Endereço']}\n"
        texto_nota += f"Pagamento: {ped['Pagamento']}\n"
        texto_nota += "-------------------------------------\n"
        
        for itm in ped['Itens']:
            texto_nota += f"• {itm['Qtd']}x {itm['Produto']} - R$ {itm['Subtotal']:.2f}\n"
            
        texto_nota += "-------------------------------------\n"
        texto_nota += f"*TOTAL: R$ {ped['Total']:.2f}*"
        
        st.code(texto_nota, language="text")
        
        # Botão para enviar nota via WhatsApp
        if ped['Telefone']:
            tel_limpo = ''.join(filter(str.isdigit, ped['Telefone']))
            msg_url = urllib.parse.quote(texto_nota)
            link_wa = f"https://wa.me/{tel_limpo}?text={msg_url}"
            st.markdown(f"[📲 Enviar Comprovante no WhatsApp do Cliente]({link_wa})")

# --- ABA 2: ESTOQUE E IMPORTAÇÃO ---
with tab_estoque:
    st.subheader("Catálogo de Produtos e Estoque")
    
    with st.expander("📥 Importar Lista de Medicamentos (Excel ou CSV)"):
        arquivo_enviado = st.file_uploader("Envie sua planilha aqui:", type=["csv", "xlsx"])
        if arquivo_enviado is not None:
            try:
                if arquivo_enviado.name.endswith('.csv'):
                    df_novo = pd.read_csv(arquivo_enviado)
                else:
                    df_novo = pd.read_excel(arquivo_enviado)
                
                st.session_state.produtos = df_novo
                st.success(f"Sucesso! {len(df_novo)} produtos importados para o catálogo.")
            except Exception as e:
                st.error(f"Erro ao ler a planilha: {e}")

    st.markdown("---")
    filtro = st.text_input("🔍 Buscar por produto, categoria ou laboratório:")
    
    df_exib = st.session_state.produtos
    if filtro and not df_exib.empty:
        df_exib = df_exib[
            df_exib["Produto"].astype(str).str.contains(filtro, case=False) | 
            df_exib["Categoria"].astype(str).str.contains(filtro, case=False) |
            df_exib["Laboratório"].astype(str).str.contains(filtro, case=False)
        ]
    
    st.dataframe(df_exib, hide_index=True, use_container_width=True)

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
        st.dataframe(df_hist[["Pedido", "Data", "Cliente", "Pagamento", "Total"]], hide_index=True, use_container_width=True)
