import fitz  # PyMuPDF
import re
import pandas as pd
from utils import converter_coluna_valor_monetario, converter_coluna_data

def extrair_sicoob(pdf):
    # Abrir o arquivo PDF
    documento = fitz.open(stream=pdf.read(), filetype="pdf")
    linhas_certas = []
    documento_lista = []
    linhas_historico = []
    k = 0
    aux = False
    datas = False
    historico = False
    count = 0
    comeco = False
    historico_line = ""
    # Iterar sobre as páginas
    for numero_pagina in range(documento.page_count):
        pagina = documento[numero_pagina]

        # Extrair o texto da página
        texto = pagina.get_text("text")

        # Dividir o texto em linhas
        linhas = texto.split("\n")

        # definir indice inicial da extração
        if k == 0:
            index_inicial = 20
        else:
            index_inicial = 0
        k += 1
        current_line = ""
        l = 0
        j = 0
        comeco = False
        # loop que vai percorrer as linhas com os dados
        for i in range(index_inicial, len(linhas)):
            line = linhas[i]
            if line == "RESUMO":
                aux = True
                break
            if (
                i <= 5
                and not (comeco)
                and not (re.search(r"\b\d{2}/\d{2}/\d{4}\S*\b", line))
            ):
                historico_line += line
                historico_line += " "
                j += 1
                continue
            else:
                comeco = True
            if comeco and j > 0:
                linhas_historico.append(historico_line)
                historico_line = ""
                j = 0
            if (
                i == 0
                and re.search(r"\b\d{2}/\d{2}/\d{4}\S*\b", line)
                and numero_pagina > 0
            ):
                count += 1
                linhas_historico.append(historico_line)
                historico_line = ""
            if historico and not (re.search(r"\b\d{2}/\d{2}/\d{4}\S*\b", line)):
                historico_line += line
                historico_line += " "
            if datas:
                documento_lista.append(line)
                datas = False
                historico = True
            if re.search(r"\b\d{2}/\d{2}/\d{4}\S*\b", line):
                l += 1
                datas = True
                historico = False
                if current_line:
                    linhas_certas.append(current_line)
                    current_line = ""
                    linhas_historico.append(historico_line)
                    historico_line = ""
            current_line += line
            current_line += " "
        if current_line:
            linhas_certas.append(current_line)
        if aux:
            break
    # Fechar o arquivo PDF
    linhas_historico.append(historico_line)
    documento.close()
    data_lista = []
    valor_lista = []
    descricao_lista = []
    tipo_lista = []
    for linha in linhas_historico:
        pattern = r"\d{1,3}(?:\.\d{3})*(,\d{2}[CD*])"
        linha_sem = re.sub(pattern, "", linha)
        texto_sem = linha_sem
        texto_sem = texto_sem.replace("SALDO DO DIA ===== >", "")
        descricao_lista.append(texto_sem)

    for linha in linhas_certas:
        pattern = r"\d{1,3}(?:\.\d{3})*(,\d{2}[CD*])"
        match = re.search(pattern, linha)
        if match:
            palavra = match.group(0)
            valor_lista.append(palavra)
            data_lista.append(linha[:10])

    for string in valor_lista:
        if string[-1] == "C":
            tipo_lista.append("C")
        if string[-1] == "D":
            tipo_lista.append("D")
        if string[-1] == "*":
            tipo_lista.append("D")

    report_df = pd.DataFrame(
        {
            "Data": data_lista,
            "Documento": documento_lista,
            "Descricao": descricao_lista,
            "Valor": valor_lista,
            "Tipo": tipo_lista,
        }
    )

    report_df = converter_coluna_data(report_df, 'Data')
    report_df = converter_coluna_valor_monetario(report_df, 'Valor')
    report_df.to_csv("extrato.csv", index=False)
    return report_df
