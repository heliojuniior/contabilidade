import PyPDF2
import pandas as pd
import streamlit as st
import re
import difflib


def merge(l, r):
    m = difflib.SequenceMatcher(None, l, r)
    for o, i1, i2, j1, j2 in m.get_opcodes():
        if o == "equal":
            yield l[i1:i2]
        elif o == "delete":
            yield l[i1:i2]
        elif o == "insert":
            yield r[j1:j2]
        elif o == "replace":
            yield l[i1:i2]
            yield r[j1:j2]


def boleto_sicredi(pdf_file):
    # Crie um objeto PdfReader
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    # Obtenha o número de páginas do PDF
    num_pages = len(pdf_reader.pages)

    # Inicialize uma lista vazia para armazenar as linhas do relatório
    report_data = []

    # Inicialize uma string vazia para armazenar todas as páginas do relatório
    file_text = ""

    # Itere pelas páginas do PDF
    for page_num in range(num_pages):
        # Obtenha a página
        page = pdf_reader.pages[page_num]

        # Extraia o texto da página
        page_text = page.extract_text()

        # concatena
        file_text += page_text

    # Substitui as quebras de linha da página por espaços
    # para remover desfragmentação de informações
    file_text = file_text.replace("\n", " ")
    file_text = re.sub(r"\s+", " ", file_text)

    # padrão de lançamentos
    # regex para reconhecer o padrão numérico
    # regex para reconhecer o padrão numérico
    # seguido de um sequência não numérica
    # seguido de uma strin - %
    # seguido de um valor monetário com vírgula para casas decimais
    pattern = r"(?<!\d)(\d{2}[0-9]\d{5}\d)([^0-9]+)(\d{2}\/\d{2}\/\d{4})\s+(\d+)\s*-\s*%\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2}))"

    # casos onde ocorre quebra de página
    duplicated_pattern = r"(\d{2}[0-9]\d{5}\d)\s+([^0-9]+)(\d{2}\/\d{2}\/\d{4})\s+(\d+)\s*-\s*%\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2}))"

    # Encontre todas as correspondências de pattern duplicado
    duplicated_pattern_matches = re.finditer(duplicated_pattern, file_text)

    # Itere sobre as correspondências de pattern duplicado
    for duplicated_pattern_match in duplicated_pattern_matches:
        duplicated_pattern_start = duplicated_pattern_match.start()
        previous_text = file_text[:duplicated_pattern_start]

        # Use findall para obter todas os patterns que antecedem a correspondência do pattern duplicado
        pattern_matches = re.findall(pattern, previous_text)

        # Se houver correspondências do pattern, use a última correspondência
        if pattern_matches:
            last_pattern_match = pattern_matches[-1]

            # merge splitted name
            merged = merge(
                last_pattern_match[1].split(), duplicated_pattern_match.group(2).split()
            )
            merged_name = " ".join(" ".join(x) for x in merged)

            splitted_pattern_match = (
                last_pattern_match[0]
                + " ".join(last_pattern_match[1:4])
                + " - % "
                + last_pattern_match[-1]
            )

            merged_pattern_match = (
                duplicated_pattern_match.group(1)
                + merged_name
                + " "
                + " ".join(last_pattern_match[2:4])
                + " - % "
                + last_pattern_match[-1]
            )

            # Substitua a string inteira no texto original
            file_text = re.sub(
                re.sub(r"\s+", " ", splitted_pattern_match),
                merged_pattern_match,
                file_text,
                1,
            )

    file_text = re.sub(r"\s+", " ", file_text)

    # Divide o texto da página em seções por data de lançamentos
    lines = file_text.split("Movimentos de ")

    for line in lines:
        # regex pare achar data
        date_pattern = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")

        # acha a primeira data
        date_match = date_pattern.search(line)

        if date_match:
            day, month, year = map(int, date_match.groups())

            # armazena a data do lançamento
            date = f"{day:02d}/{month:02d}/{year:04d}"

            # encontra todas as ocorrências de lançamentos padrão na data
            matches = re.finditer(pattern, line)

            for match in matches:
                # pega as informações do lançamento
                operation_info = match.groups()

                # insere a tupla das informações concatenadas com o conjunto da data
                report_data.append(operation_info + (date,))

    # Converter os dados do relatório em um DataFrame do pandas
    report_df = pd.DataFrame(
        report_data,
        columns=[
            "Processo", 
            "Nome", 
            "Vencimento", 
            "Documento", 
            "Valor", 
            "Data"
        ],
    )

    report_df.to_csv("boletos.csv")
    return report_df


boleto_sicredi("boletos/boleto_sicredi.pdf")
