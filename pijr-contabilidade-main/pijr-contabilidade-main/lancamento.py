import pandas as pd
import os
import streamlit as st

def gerar_lancamento():

    if not os.path.isfile("extrato.csv"):
        st.error("Nenhum extrato lido. Por favor, insira um extrato.")
        return

    # Leitura do arquivo CSV de extrato
    df_extrato = pd.read_csv("extrato.csv")

    df_extrato["Data"] = pd.to_datetime(df_extrato["Data"], format="%d/%m/%Y")
    df_extrato["Data"] = df_extrato["Data"].dt.strftime("%Y%m%d")

    # Leitura do arquivo CSV de contas
    df_contas = pd.read_csv("contas.csv")

    # Caminho para o arquivo de lançamento
    caminho_arquivo_lancamento = "lancamento.txt"

    # Lista para armazenar as linhas do arquivo de lançamento
    linhas_lancamento = []

    # Itera sobre as linhas do DataFrame de extrato
    for idx, row in df_extrato.iterrows():
        # Encontra a conta correspondente à descrição
        conta_correspondente = df_contas[df_contas["Descricao"] == row["Descricao"]][
            "Contas"
        ].values[0]

        if row["Tipo"] == "D":
            # Gera a linha do lançamento
            linha = f"{idx+1:05d},{row['Data']},{conta_correspondente},0,{row['Valor']},,{row['Descricao']},{row['Documento']},,,,"
        else:
            linha = f"{idx+1:05d},{row['Data']},0,{conta_correspondente},{row['Valor']},,{row['Descricao']},{row['Documento']},,,,"

        # Adiciona a linha à lista
        linhas_lancamento.append(linha)

    # Escreve as linhas no arquivo de lançamento
    with open(caminho_arquivo_lancamento, "w") as arquivo_lancamento:
        for linha in linhas_lancamento:
            arquivo_lancamento.write(f"{linha}\n")
