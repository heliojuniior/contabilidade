import PyPDF2
import pandas as pd
import streamlit as st
import re
from utils import converter_coluna_data, converter_coluna_valor_monetario 

def boleto_sicoob(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    # Obtenha o número de páginas do PDF
    num_pages = len(pdf_reader.pages)

    # Inicializa listas a serem utilizadas
    textos_desejados = []
    numeros_desejados = []
    linhas_certas = []
    numeros_documento = []
    categorias = []

    # Itere pelas páginas do PDF
    for page_num in range(num_pages):
        
        page = pdf_reader.pages[page_num]
       
        # Extraia o texto da página
        page_text = page.extract_text()

        # Divida o texto da página em linhas
        lines = page_text.split("\n")

        # Encontre o índice onde começa a seção relevante
        indexes = [i for i, x in enumerate(lines) if x == "Dt. Previsão "]


        for i in range(len(indexes)):
            linhas_certas = []

            index_inicio = indexes[i] + 1

            if i < len(indexes) - 1:
                index_fim = indexes[i + 1]
            else:
                index_fim = len(lines) - 2

            # Seleciona a categoria
            categoria = lines[indexes[i] - 1]
            prefix = "Sacado Nosso Número Seu Número Valor (R$) Dt."
            categoria = categoria[len(prefix):]

            # Itere pelas linhas relevantes
            for line in range(index_inicio, index_fim):
                elemento = lines[line]
                indice = elemento.find("-")
                
                # dados a serem ignorados
                indice_total = elemento.find("Total")
                indice_sacado = elemento.find("Sacado")
                indice_prev = elemento.find("Previsão")
                indice_cred = elemento.find("CréditoVlr")
                indice_acresc = elemento.find("Acresc")

                # junta linhas quebradas se for uma linha desejada
                if indice != -1 and indice_total == -1 and indice_sacado == -1:
                    linhas_certas.append(elemento)
                elif (
                    indice_total == -1
                    and indice_sacado == -1
                    and indice_prev == -1
                    and indice_cred == -1
                    and indice_acresc == -1
                    and len(linhas_certas) > 0
                ):
                    linhas_certas[-1] = linhas_certas[-1] + elemento

            for linha in linhas_certas:
                texto_linha = re.findall(r"[A-Z][A-Z.\s]+", linha)
                numeros_linha = re.search(
                    r"(\d{2}/\d{2}/\d{4}) (\S+) (\S+) (\S+) (\S+) (\d{2}/\d{2}/\d{4})",
                    linha,
                )
                num_doc = re.findall(r"(\d{8})", linha)

                if numeros_linha:
                    # Adicione cada valor diferente como uma coluna
                    numeros_desejados.append(numeros_linha.groups())

                # Adicione o texto à lista
                textos_desejados.append(" ".join(texto_linha).strip())

                categorias.append(categoria)

                numeros_documento += num_doc

    # Converter os textos desejados em um DataFrame do pandas
    textos_df = pd.DataFrame(
        numeros_desejados,
        columns=["Data", "Valor", "Tipo", "Valor3", "Valor4", "Data2"],
    )
    textos_df["Descricao"] = textos_desejados
    textos_df["Documento"] = numeros_documento
    textos_df["Categoria"] = categorias
    textos_df = converter_coluna_data(textos_df, 'Data')
    textos_df = converter_coluna_valor_monetario(textos_df, 'Valor')
    textos_df.to_csv("boletos.csv", index=False)
    return textos_df

