import pandas as pd
import streamlit as st
import os
import base64

def adicionar_contas():
    # Verifica se o arquivo "contas.csv" existe
    if os.path.isfile("contas.csv"):
        contas_csv = pd.read_csv("contas.csv")
    else:
        # Se o arquivo não existir, cria um DataFrame vazio
        contas_csv = pd.DataFrame(columns=["Descrição", "Contas"])

    if not os.path.isfile("extrato.csv"):
        return

    extrato_csv = pd.read_csv("extrato.csv")

    # armazena as novas descrições extraidas
    novas_descricoes = []

    # cria um set pra conferir os dados
    contas_set = set(contas_csv["Descricao"].tolist())

    for descricao in extrato_csv["Descricao"]:
        if descricao not in contas_set:
            novas_descricoes.append(descricao)

    st.markdown("<hr style='border: 2px gray;'>", unsafe_allow_html=True)

    novo_df = pd.DataFrame({"Descricao": novas_descricoes, "Contas": 0})

    if novas_descricoes:
        st.session_state.iniciar_lancamento = False
        with st.form("data_editor_form"):
            st.caption("Novas operações encontradas, adicionar número da conta")
            edited = st.data_editor(novo_df, use_container_width=True)
            submit_button = st.form_submit_button("Confirmar")

        # if submit_button:
        #     dados_juntos = pd.concat([contas_csv, edited], ignore_index=True)
        #     dados_juntos.to_csv("contas.csv", index=False)
        #     st.rerun()
        if submit_button:
            dados_juntos = pd.concat([contas_csv, edited], ignore_index=True)
            dados_juntos.to_csv("contas.csv", index=False)
            st.session_state.iniciar_lancamento = True
            st.rerun()

# Função para criar um link de download
def get_csv_download_link(dataframe, filename="contas.csv"):
    csv = dataframe.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f"<a href='data:file/csv;base64,{b64}' download='{filename}'>Clique aqui para baixar o arquivo CSV</a>"
    return href

def editar_contas():
    contas_csv = pd.read_csv("contas.csv")

    with st.form("editor_form"):
        st.caption("Editar planilha de contas")
        edited = st.data_editor(contas_csv, use_container_width=True)
        submit_button = st.form_submit_button("Confirmar")

    if submit_button:
        edited.to_csv("contas.csv", index=False)
        st.rerun()
