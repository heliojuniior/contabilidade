import pandas as pd
import re

def extrair_valor_monetario(texto):
    # Encontrar todos os dígitos e ponto decimal na string
    matches = re.findall(r'-?[\d,]+[.\d]*', texto)

    # Juntar os dígitos encontrados em uma string
    valor_str = ''.join(matches)

    # Substituir vírgulas por pontos (para tratar valores em formato brasileiro, por exemplo)
    valor_str = valor_str.replace('.', '')
    valor_str = valor_str.replace(',', '.')

    return valor_str

def converter_coluna_valor_monetario(df : pd.DataFrame, nome_coluna):
    # Verifica se a coluna existe no DataFrame
    if nome_coluna not in df.columns:
        raise ValueError(f"A coluna {nome_coluna} não existe no DataFrame.")

    # Aplica a função à coluna específica
    df[nome_coluna] = df[nome_coluna].astype(str).apply(extrair_valor_monetario)

    return df

def converter_coluna_data(df, nome_coluna):
    # Verifica se a coluna existe no DataFrame
    if nome_coluna not in df.columns:
        raise ValueError(f"A coluna {nome_coluna} não existe no DataFrame.")

    # Converte a coluna de string para o tipo datetime do pandas
    df[nome_coluna] = pd.to_datetime(df[nome_coluna], format="%d/%m/%Y")

    # Cria uma nova coluna com a data no formato "aaaa-mm-dd"
    df[nome_coluna] = df[nome_coluna].dt.strftime("%Y%m%d")

    return df

