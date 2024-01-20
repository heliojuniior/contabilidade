import PyPDF2
import pandas as pd
import re
from utils import converter_coluna_valor_monetario, converter_coluna_data

def extrair_credisis(pdf):
    # Crie um objeto PdfReader
    pdf_reader = PyPDF2.PdfReader(pdf)

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
        file_text += " " + page_text

    # seguido de um valor monetário com vírgula para casas decimais
    pattern = r"(\d{2}/\d{2}/\d{4})[\s\n]+([A-Za-z0-9]+)[\s\n]+(.+?)(?:[\s\n]+(.+?))?\s*[\s\n]+R\$ ([+-]?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2}))\s+R\$ ([+-]?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2}))"

    # encontra todas as ocorrências de lançamentos padrão na data
    matches = re.finditer(pattern, file_text)

    for match in matches:
        # pega as informações do lançamento
        operation_info = match.groups()

        # insere a tupla das informações concatenadas com o conjunto da data
        report_data.append(operation_info)

    # Converter os dados do relatório em um DataFrame do pandas
    report_df = pd.DataFrame(
        report_data,
        columns=["Data", "Documento", "Descricao", "nome", "Valor", "saldo"],
    )

    report_df["Descricao"] = report_df["Descricao"] + " " + report_df["nome"]

    report_df.drop("nome", axis=1, inplace=True)

    report_df["Valor"] = report_df["Valor"].str.replace(".", "")  # Remove os pontos
    report_df["Valor"] = report_df["Valor"].str.replace(
        ",", "."
    )  # Substitui a vírgula por ponto
    report_df["Valor"] = report_df["Valor"].astype(float)  # Converte para float
    report_df["Tipo"] = report_df["Valor"].apply(lambda x: "D" if x >= 0 else "C")
    # Transforme todos os valores em positivos
    report_df["Valor"] = report_df["Valor"].abs()

    report_df.to_csv("extrato.csv")
    return report_df
