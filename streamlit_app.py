def extrair_clientes_de_arquivo(uploaded_file):
    novos = []
    filename = uploaded_file.name.lower()
    
    if filename.endswith('.pdf'):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                tabelas = page.extract_tables()
                for tabela in tabelas:
                    for linha in tabela:
                        if len(linha) >= 2 and linha[0] and "Nome" not in str(linha[0]):
                            nome = str(linha[0]).strip()
                            whats = str(linha[1]).strip()
                            end = str(linha[2]).strip() if len(linha) > 2 and linha[2] else ""
                            if nome:
                                novos.append({'Nome': nome, 'WhatsApp': whats, 'Endereço': end})
        return pd.DataFrame(novos)
        
    elif filename.endswith('.xlsx') or filename.endswith('.xls') or filename.endswith('.csv'):
        if filename.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        # Mapeamento dinâmico das colunas do Excel
        col_nome = None
        col_whats = None
        col_end = None
        
        for col in df.columns:
            c_lower = str(col).lower().strip()
            if any(k in c_lower for k in ['nome', 'cliente', 'razão', 'pessoa']):
                col_nome = col
            elif any(k in c_lower for k in ['whats', 'tel', 'celular', 'fone', 'contato', 'numero', 'número']):
                col_whats = col
            elif any(k in c_lower for k in ['end', 'rua', 'bairro', 'local', 'endereço', 'endereco']):
                col_end = col
        
        # Se não achou pelos nomes, usa as 3 primeiras colunas por ordem
        if not col_nome and len(df.columns) >= 1: col_nome = df.columns[0]
        if not col_whats and len(df.columns) >= 2: col_whats = df.columns[1]
        if not col_end and len(df.columns) >= 3: col_end = df.columns[2]
        
        df_formatado = pd.DataFrame()
        df_formatado['Nome'] = df[col_nome].astype(str).str.strip() if col_nome else ""
        df_formatado['WhatsApp'] = df[col_whats].astype(str).str.strip() if col_whats else ""
        df_formatado['Endereço'] = df[col_end].astype(str).str.strip() if col_end else ""
        
        return df_formatado
        
    return pd.DataFrame(novos)
