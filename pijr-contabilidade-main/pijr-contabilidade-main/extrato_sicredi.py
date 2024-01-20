import fitz  # PyMuPDF
import re
import pandas as pd
from utils import converter_coluna_data, converter_coluna_valor_monetario

def extrair_sicredi(pdf):
    # Abrir o arquivo PDF
    documento = fitz.open(stream=pdf.read(), filetype="pdf")
    linhas_certas = []

    # Iterar sobre as páginas
    for numero_pagina in range(documento.page_count):
        pagina = documento[numero_pagina]

        # Extrair o texto da página
        texto = pagina.get_text("text")

        # Dividir o texto em linhas
        linhas = texto.split("\n")

        # definir indice inicial da extração
        if "Saldo Anterior" in linhas:
            index_inicial = linhas.index("Saldo Anterior") + 1
        else:
            index_inicial = 0

        current_line = ""
        # loop que vai percorrer as linhas com os dados
        for i in range(index_inicial, len(linhas)):
            line = linhas[i]
            # fim do arquivo que não precisa extrair mais nada
            if line == "Saldo da Conta":
                break
            if re.search(r"\b\d{2}/\d{2}/\d{4}\S*\b", line):
                if current_line:
                    linhas_certas.append(current_line)
                    current_line = ""

            current_line += line
            current_line += " "
        if current_line:
            linhas_certas.append(current_line)

    # Fechar o arquivo PDF
    documento.close()
    data_lista = []
    valor_lista = []
    saldo_lista = []
    descricao_lista = []
    documento_lista = []

    for linha in linhas_certas:
        primeiro_numero = re.search(r"[-+]?\d{1,3}(\.\d{3})*,\d{2}", linha)
        if primeiro_numero:
            posicao_inicial = primeiro_numero.start()
            descricao = linha[10:posicao_inicial]
            linha = linha.replace("-", " -")
            termos = linha.split()
            data_lista.append(linha[:10])
            documentos = descricao.split()
            documento = documentos[-1]
            if documento != "BLOQUETOS":
                documento_lista.append(documento)
                posicao_ultimo_espaco = descricao.rfind(" ")
                posicao_penultimo_espaco = descricao.rfind(
                    " ", 0, posicao_ultimo_espaco
                )
                descricao = descricao[:posicao_penultimo_espaco]
                descricao_lista.append(descricao)
            else:
                documento_lista.append("")
                descricao_lista.append(descricao)
            valor1_ = termos[-2]
            valor2_ = termos[-1]
            valor_lista.append(valor1_)
            saldo_lista.append(valor2_)

    report_df = pd.DataFrame(
        {
            "Data": data_lista,
            "Descricao": descricao_lista,
            "Documento": documento_lista,
            "Valor": valor_lista,
            "Saldo": saldo_lista,
        }
    )

    report_df["Valor"] = report_df["Valor"].str.replace(".", "")  # Remove os pontos
    report_df["Valor"] = report_df["Valor"].str.replace(
        ",", "."
    )  # Substitui a vírgula por ponto
    report_df["Valor"] = report_df["Valor"].astype(float)  # Converte para float
    report_df["Tipo"] = report_df["Valor"].apply(lambda x: "D" if x >= 0 else "C")
    # Transforme todos os valores em positivos
    report_df["Valor"] = report_df["Valor"].abs()

    report_df.to_csv("extrato.csv", index=False)
    return report_df
