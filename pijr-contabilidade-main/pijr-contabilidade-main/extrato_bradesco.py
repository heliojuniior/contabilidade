import fitz  # PyMuPDF
import re
import pandas as pd
from utils import converter_coluna_data, converter_coluna_valor_monetario

def extrair_bradesco(pdf):
    # Abrir o arquivo PDF
    documento = fitz.open(stream=pdf.read(), filetype="pdf")
    dados_extraidos = []

    descricao_tt = ""
    documento_tt = ""
    valor_tt = ""
    saldo_tt = ""
    data_aux = ""

    # Iterar sobre as páginas
    for numero_pagina in range(documento.page_count):
        pagina = documento[numero_pagina]

        # Extrair o texto da página
        page_text = pagina.get_text("text")

        texto_final = page_text

        # alterar índice inicial e final
        index_inicio = page_text.find("Os dados acima")
        if index_inicio != -1 and numero_pagina != (documento.page_count - 1):
            linhas_apos_substring = page_text[index_inicio:].split("\n")[3:]
            texto_final = "\n".join(linhas_apos_substring)
            index_inicio = 9
        else:
            index_inicio = 0

        lines = texto_final.split("\n")

        for line in range(index_inicio, len(lines) - 1):
            elemento = lines[line]
            padrao_data = r"(\d{2}/\d{2}/\d{4})"
            padrao_numero = r"-?\b\d+(?:[.,]\d{3})*(?:[.,]\d+)?\b"
            padrao_fimPagina = r"Folha \d+/\d+"

            if re.match(padrao_fimPagina, elemento):
                break

            achou_data = re.search(padrao_data, elemento)
            if achou_data:
                data_aux = achou_data.group()

            elif re.match(padrao_numero, elemento):
                if documento_tt == "":
                    documento_tt = elemento
                elif valor_tt == "":
                    valor_tt = elemento
                else:
                    saldo_tt = elemento

            else:
                descricao_tt = descricao_tt + elemento
                if descricao_tt == "Total" and numero_pagina == (
                    documento.page_count - 1
                ):
                    break

            if saldo_tt != "":
                dados_extraidos.append((data_aux, descricao_tt, documento_tt, valor_tt))
                descricao_tt = ""
                documento_tt = ""
                valor_tt = ""
                saldo_tt = ""

    df = pd.DataFrame(
        dados_extraidos, columns=["Data", "Descricao", "Documento", "Valor"]
    )
    # df = converter_coluna_data(df, 'Data')
    # df = converter_coluna_valor_monetario(df, 'Valor')

    df["Valor"] = df["Valor"].str.replace(".", "")  # Remove os pontos
    df["Valor"] = df["Valor"].str.replace(",", ".")  # Substitui a vírgula por ponto
    df["Valor"] = df["Valor"].astype(float)  # Converte para float
    df["Tipo"] = df["Valor"].apply(lambda x: "D" if x >= 0 else "C")
    # Transforme todos os valores em positivos
    df["Valor"] = df["Valor"].abs()

    df.to_csv("extrato.csv")
    return df
