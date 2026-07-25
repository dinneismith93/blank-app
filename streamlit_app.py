import streamlit as st
import pandas as pd
import os
import urllib.parse

st.set_page_config(page_title="Farmácia Menor Preço - Gestão & Pedidos", layout="wide", page_icon="💊")

# Estilização
st.markdown("""
    <style>
    .main-header {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #0E4B82;
        text-align: center;
        padding: 10px 0px 15px 0px;
        font-weight: 800;
        font-size: 2.2rem;
    }
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
            if 'Preço Custo (R$)' not in df.columns:
                df['Preço Custo (R$)'] = (df['Preço Unit. (R$)'] * 0.60).round(2) # Estimativa inicial de custo (60% do valor de venda)
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=['Descrição', 'Quantidade', 'Preço Unit. (R$)', 'Preço Custo (R$)'])

if 'estoque' not in st.session_state:
    st.session_state['estoque'] = carregar_estoque_base()

if 'carrinho' not in st.session_state:
    st.session_state['carrinho'] = []

if 'vendas_historico' not in st.session_state:
    st.session_state['vendas_historico'] = pd.DataFrame(columns=['Data/Hora', 'Cliente', 'Produto', 'Qtd', 'Custo Total (R$)', 'Venda Total (R$)', 'Lucro (R$)'])

st.markdown("<h1 class='main-header'>💊 FARMÁCIA MENOR PREÇO</h1>", unsafe_allow_html=True)

# Menu Principal Atualizado com a nova aba
menu = st.radio(
    "Navegação",
    ["🛒 Emitir Pedido", "📋 Estoque & Preços", "📈 Lucros & Metas", "➕ Novo Produto", "📄 Importar PDF"],
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
                preco_custo = float(item_info.get('Preço Custo (R$)', preco_base * 0.6))
                qtd_disp = int(item_info['Quantidade'])
                
                st.info(f"💡 **Preço Cadastrado:** R$ {preco_base:.2f} | **Custo Est.:** R$ {preco_custo:.2f} | **Estoque:** {qtd_disp} un")
                
                col_p, col_q = st.columns(2)
                with col_p:
                    preco_venda = st.number_input("Preço de Venda (R$):", min_value=0.0, value=preco_base, format="%.2f", key="preco_venda")
                with col_q:
                    qtd_pedir = st.number_input("Qtd Desejada:", min_value=1, max_value=max(1, qtd_disp), value=1, step=1, key="qtd_pedir")
                
                if st.button("➕ Adicionar ao Carrinho", use_container_width=True, type="primary"):
                    st.session_state['carrinho'].append({
                        'Descrição': prod_selecionado,
                        'Qtd': qtd_pedir,
                        'Custo Unit. (R$)': preco_custo,
                        'Preço Unit. (R$)': preco_venda,
                        'Subtotal (R$)': round(qtd_pedir * preco_venda, 2),
                        'Custo Subtotal (R$)': round(qtd_pedir * preco_custo, 2)
                    })
                    st.success(f"Adicionado ao carrinho!")

            st.divider()
            st.subheader("2. Dados da Entrega / Cliente")
            nome_cliente = st.text_input("👤 Nome do Cliente:", key="nome_cliente")
            whatsapp_cliente = st.text_input("📱 WhatsApp do Cliente (com DDD, só números):", placeholder="22999999999", key="whatsapp_cliente")
            endereco_cliente = st.text_area("📍 Endereço Completo de Entrega:", key="endereco_cliente")
            
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
                
                # Botão para Finalizar Venda e computar nos lucros
                if st.button("✅ Confirmar Venda & Atualizar Estoque/Lucros", use_container_width=True, type="primary"):
                    novas_vendas = []
                    data_hora = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                    
                    for item in st.session_state['carrinho']:
                        # Atualiza estoque
                        desc = item['Descrição']
                        qtd_vendid = item['Qtd']
                        idx = st.session_state['estoque'][st.session_state['estoque']['Descrição'] == desc].index
                        if not idx.empty:
                            st.session_state['estoque'].loc[idx, 'Quantidade'] = max(0, st.session_state['estoque'].loc[idx, 'Quantidade'].values[0] - qtd_vendid)
                        
                        # Registra no histórico de vendas
                        custo_tot = item['Custo Subtotal (R$)']
                        venda_tot = item['Subtotal (R$)']
                        novas_vendas.append({
                            'Data/Hora': data_hora,
                            'Cliente': nome_cliente if nome_cliente else 'Cliente Balcão',
                            'Produto': desc,
                            'Qtd': qtd_vendid,
                            'Custo Total (R$)': custo_tot,
                            'Venda Total (R$)': venda_tot,
                            'Lucro (R$)': round(venda_tot - custo_tot, 2)
                        })
                    
                    st.session_state['vendas_historico'] = pd.concat([st.session_state['vendas_historico'], pd.DataFrame(novas_vendas)], ignore_index=True)
                    st.success("Venda registrada com sucesso! Estoque e relatórios de lucros atualizados.")

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

# ==================== ABA 2: ESTOQUE & PREÇOS (EDITÁVEL) ====================
elif menu == "📋 Estoque & Preços":
    st.header("📋 Gerenciar Estoque e Editar Preços")
    df_estoque = st.session_state['estoque']
    
    if not df_estoque.empty:
        st.write(f"Total de itens no estoque: **{len(df_estoque)}**")
        
        # Painel de Edição Rápida de Produto
        st.subheader("✏️ Editar Produto Selecionado")
        busca_est = st.text_input("🔍 Digite o nome do medicamento para alterar dados:", key="busca_est")
        
        if busca_est:
            filtrados = df_estoque[df_estoque['Descrição'].str.contains(busca_est, case=False, na=False)]
            if not filtrados.empty:
                item_edit = st.selectbox("Selecione o item exato para editar:", filtrados['Descrição'].tolist(), key="select_item_edit")
                idx = df_estoque[df_estoque['Descrição'] == item_edit].index[0]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    nova_qtd = st.number_input("Nova Quantidade:", value=int(df_estoque.loc[idx, 'Quantidade']), min_value=0, step=1, key="edit_qtd")
                with col2:
                    novo_preco_venda = st.number_input("Novo Preço Venda (R$):", value=float(df_estoque.loc[idx, 'Preço Unit. (R$)']), min_value=0.0, format="%.2f", key="edit_pvenda")
                with col3:
                    preco_c_atual = float(df_estoque.loc[idx, 'Preço Custo (R$)']) if 'Preço Custo (R$)' in df_estoque.columns else float(df_estoque.loc[idx, 'Preço Unit. (R$)']) * 0.6
                    novo_preco_custo = st.number_input("Novo Preço Custo (R$):", value=preco_c_atual, min_value=0.0, format="%.2f", key="edit_pcusto")
                
                if st.button("💾 Salvar Alterações no Produto", type="primary"):
                    st.session_state['estoque'].loc[idx, 'Quantidade'] = nova_qtd
                    st.session_state['estoque'].loc[idx, 'Preço Unit. (R$)'] = novo_preco_venda
                    st.session_state['estoque'].loc[idx, 'Preço Custo (R$)'] = novo_preco_custo
                    st.success(f"Dados atualizados com sucesso para '{item_edit}'!")
            else:
                st.info("Nenhum produto encontrado com essa busca.")
        
        st.divider()
        st.subheader("📋 Tabela Geral do Estoque")
        st.dataframe(df_estoque, use_container_width=True)

# ==================== ABA 3: LUCROS & METAS ====================
elif menu == "📈 Lucros & Metas":
    st.header("📈 Relatório de Vendas, Lucros e Metas")
    
    df_vendas = st.session_state['vendas_historico']
    
    # 1. Métricas Principais
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    vendas_totais = df_vendas['Venda Total (R$)'].sum() if not df_vendas.empty else 0.0
    custo_total = df_vendas['Custo Total (R$)'].sum() if not df_vendas.empty else 0.0
    lucro_total = vendas_totais - custo_total
    margem = (lucro_total / vendas_totais * 100) if vendas_totais > 0 else 0.0
    
    col_m1.metric("💰 Faturamento Total", f"R$ {vendas_totais:.2f}")
    col_m2.metric("📦 Custo dos Produtos", f"R$ {custo_total:.2f}")
    col_m3.metric("📊 Lucro Líquido", f"R$ {lucro_total:.2f}", delta=f"{margem:.1f}% Margem")
    
    # Meta do Mês
    meta_mes = st.sidebar.number_input("🎯 Definir Meta Mensal de Vendas (R$):", min_value=1000.0, value=30000.0, step=1000.0)
    progresso_meta = min(1.0, vendas_totais / meta_mes) if meta_mes > 0 else 0.0
    col_m4.metric("🎯 Meta Atingida", f"{progresso_meta*100:.1f}%", f"Meta: R$ {meta_mes:.2f}")
    
    st.write("---")
    st.subheader("🎯 Progresso da Meta do Mês")
    st.progress(progresso_meta)
    
    # 2. Gráficos de Projeção / Vendas
    st.divider()
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("📊 Comparativo: Custo vs Venda vs Lucro")
        df_chart = pd.DataFrame({
            'Categoria': ['Custo Total', 'Venda Total', 'Lucro Bruto'],
            'Valor (R$)': [custo_total, vendas_totais, lucro_total]
        })
        st.bar_chart(df_chart.set_index('Categoria'))
        
    with col_g2:
        st.subheader("📈 Projeção de Vendas vs Meta")
        df_meta_chart = pd.DataFrame({
            'Indicador': ['Vendas Atuais', 'Falta p/ Meta'],
            'Valor (R$)': [vendas_totais, max(0.0, meta_mes - vendas_totais)]
        })
        st.bar_chart(df_meta_chart.set_index('Indicador'))
        
    # 3. Tabela Detalhada de Histórico de Vendas
    st.divider()
    st.subheader("📜 Histórico Detalhado de Vendas")
    if df_vendas.empty:
        st.info("Nenhuma venda finalizada ainda. Realize pedidos na aba 'Emitir Pedido' para visualizar seus lucros detalhados.")
    else:
        st.dataframe(df_vendas, use_container_width=True)

# ==================== ABA 4: NOVO PRODUTO ====================
elif menu == "➕ Novo Produto":
    st.header("➕ Cadastrar Novo Produto Manualmente")
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome do Produto", key="nome_prod")
        preco_venda = st.number_input("Preço de Venda (R$)", min_value=0.0, format="%.2f", key="preco_prod")
    with col2:
        preco_custo = st.number_input("Preço de Custo (R$)", min_value=0.0, format="%.2f", key="preco_custo_prod")
        qtd = st.number_input("Quantidade em Estoque", min_value=0, step=1, key="qtd_prod")
        
    if st.button("Salvar Produto", key="btn_salvar_manual", type="primary"):
        if nome:
            novo_item = pd.DataFrame([{
                'Descrição': nome, 
                'Quantidade': qtd, 
                'Preço Unit. (R$)': preco_venda,
                'Preço Custo (R$)': preco_custo
            }])
            st.session_state['estoque'] = pd.concat([st.session_state['estoque'], novo_item], ignore_index=True)
            st.success(f"Produto '{nome}' adicionado!")

# ==================== ABA 5: IMPORTAR PDF ====================
elif menu == "📄 Importar PDF":
    st.header("📄 Importar Estoque via PDF")
    uploaded_file = st.file_uploader("Selecione o arquivo PDF do inventário", type=["pdf"], key="pdf_uploader")
