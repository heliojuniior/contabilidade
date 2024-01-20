import pandas as pd
import streamlit as st

def match_contas(extrato_csv_path, rows_to_replace, boleto_rows_to_ignore, boleto_csv_path):

    # Lê os arquivos
    extrato_df = pd.read_csv(extrato_csv_path)
    boleto_df = pd.read_csv(boleto_csv_path)

    # filtra linhas pelas linha necessárias para filtrar
    linhas_filtradas = extrato_df[extrato_df['Descricao'].str.strip().isin(rows_to_replace)]
    
    # pega a data dos dias a serem substituídos
    datas = linhas_filtradas['Data']

    # Filtra linhas do boleto correspondendte às datas a serem buscadas
    selected_boleto_columns = boleto_df[boleto_df['Data'].isin(datas.to_list())]
    
    # Deleta linhas do boleto que precisam ser ignoradas
    if len(boleto_rows_to_ignore) > 0:

        selected_boleto_columns = selected_boleto_columns[~selected_boleto_columns['Categoria'].str.contains('|'.join(boleto_rows_to_ignore))]
    
    errors = []
    
    for data in datas:
        # Pega os lançamentos de cada data a ser verificada
        extrato_row = linhas_filtradas[linhas_filtradas['Data'] == data]
        boleto_rows = selected_boleto_columns[selected_boleto_columns['Data'] == data]
        extrato_value = linhas_filtradas[linhas_filtradas['Data'] == data]['Valor'].iloc[0]
        boleto_value = selected_boleto_columns[selected_boleto_columns['Data'] == data]['Valor'].sum()

        # Se dá erro, ignora
        if extrato_value != round(boleto_value, 2):
            lancamento_errado = (extrato_value, boleto_value, extrato_row, boleto_rows)
            errors.append(lancamento_errado)
            continue

        # Deleta as linhas que vão ser substituídas
        extrato_df = extrato_df.drop(extrato_row.index)

        # Seleciona as colunas importantes do boleto
        boleto_columns_to_add = ['Data', 'Documento', 'Descricao', 'Valor', 'Tipo']
        boleto_rows = boleto_rows[boleto_columns_to_add]

        # Adiciona as linhas do boleto
        result_df = pd.concat([extrato_df, boleto_rows])

    # Ordena as linhas por data
    result_df = result_df.sort_values(by='Data').reset_index(drop=True)
        
    # adiciona no csv
    result_df.to_csv(extrato_csv_path)
    
    # gera aviso informando a linha substituída
    for error in errors:
        extrato_value, boleto_value, extrato_row, boleto_rows = error
        st.error(f"""
                Aviso: o lançamento do dia {extrato_row['Data'].values[0]}, {extrato_row['Descricao'].values[0]} \n
                localizado na linha {extrato_row.index.values[0] - 1}, \n 
                não conseguiu encontrar lançamentos no boleto inserido. \n
                Valor esperado: {extrato_value}; \n
                Valor encontrado: {boleto_value}; \n
                Lançamentos encontrados: \n
                {boleto_rows if len(boleto_rows) > 0 else []}
                """)
    