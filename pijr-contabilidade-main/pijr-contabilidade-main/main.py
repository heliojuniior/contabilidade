import streamlit as st
import pandas as pd
from extrato_sicoob import *
from extrato_sicredi import *
from extrato_credisis import *
from extrato_bradesco import *
from boleto_sicoob import *
from boleto_sicredi import *
from gerenciar_contas import *
from match_contas import match_contas
from lancamento import *
from streamlit_option_menu import option_menu

TITULO_LANCAMENTOS_BOLETO_SICOOB = ["CRÉD.LIQUIDAÇÃO COBRANÇA"]
TITULO_LANCAMENTOS_BOLETO_SICREDI = ["LIQ.COBRANCA SIMPLES"]

LANCAMENTOS_A_IGNORAR_SICOOB = ["PEDIDO CEDENTE"]


class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            "title": title,
            "function": func
        })

    def main():
        if "boleto_ativo" not in st.session_state:
            st.session_state.boleto_ativo = False

        if "lancamento_ativo" not in st.session_state:
            st.session_state.lancamento_ativo = False

        if st.session_state.lancamento_ativo:
            st.session_state.chave_escolha = "LANÇAMENTOS"
            st.session_state.lancamento_ativo = False

        if "lancamento_a_ignorar" not in st.session_state:
            st.session_state.lancamentos_a_ignorar = []
        if "iniciar_lancamento" not in st.session_state:
            st.session_state.iniciar_lancamento = True

        with st.sidebar:
            st.image("hunika.png", width=450)
                # Adiciona CSS para alinhar a imagem à esquerda
            st.markdown(
                """
                <style>
                    img {
                        margin-left: -80px;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            app = option_menu(
                menu_title=None,
                options=['Inicio','Lançamentos','Serfim','Prefeitura','Dashboard'],
                icons=['house-fill','person-circle','trophy-fill','chat-fill','info-circle-fill'],
                menu_icon='chat-text-fill',
                default_index=1,
                styles={
                    "container": {"padding": "5!important","background-color":'black'},
        "icon": {"color": "white", "font-size": "23px"}, 
        "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
        "nav-link-selected": {"background-color": "#02ab21"},}
                
                )

        # interface da opção "Upload"
        if app == "Inicio":
            # selecionar empresa a fazer o lançamento
            bancos = ["Bradesco", "Credisis", "Sicoob", "Sicredi"]

            st.title("Faça o Upload do Extrato em PDF")
            banco = st.selectbox("Selecione o banco", ["Selecione o banco", *bancos])

            if banco in bancos:
                
                # ler extrato bancário
                uploaded_files = st.file_uploader(
                    "Selecione o Arquivo", accept_multiple_files=False, type=["pdf"], key=1
                )
                
                if uploaded_files is not None:
                    st.markdown("<hr style='border: 2px gray;'>", unsafe_allow_html=True)
                    if banco == "Sicoob":
                        extrato_df = extrair_sicoob(uploaded_files)

                    elif banco == "Sicredi":
                        extrato_df = extrair_sicredi(uploaded_files)

                    elif banco == "Bradesco":
                        extrato_df = extrair_bradesco(uploaded_files)

                    elif banco == "Credisis":
                        extrato_df = extrair_credisis(uploaded_files)

                    if banco == "Sicoob" or banco == "Sicredi":
                        # botão para adicionar relatorio de boleto
                        check_state = st.checkbox("Adicionar Relatório de Boleto?")
                        if check_state:
                            uploaded_files_boleto = st.file_uploader(
                                "Selecione o Arquivo",
                                accept_multiple_files=False,
                                type=["pdf"],
                                key=2,
                            )
                            st.session_state.boleto_ativo = True
                            if uploaded_files_boleto is not None:
                                if banco == "Sicoob":
                                    boleto_df = boleto_sicoob(uploaded_files_boleto)
                                    st.session_state.titulo_lancamentos_boleto = TITULO_LANCAMENTOS_BOLETO_SICOOB
                                    st.session_state.lancamentos_a_ignorar = LANCAMENTOS_A_IGNORAR_SICOOB

                                elif banco == "Sicredi":
                                    boleto_df = boleto_sicredi(uploaded_files_boleto)
                                    st.session_state.titulo_lancamentos_boleto = TITULO_LANCAMENTOS_BOLETO_SICREDI
                        else:
                            st.session_state.boleto_ativo = False

                    # criar posição para o botão de lançamento
                    col1, col2 = st.columns(2)

                    # botão para gerar lançamento
                    if col2.button("Gerar Lançamento"):
                        st.session_state.lancamento_ativo = True
                        st.rerun()
                        match_contas("extrato.csv", st.session_state.titulo_lancamentos_boleto, st.session_state.lancamentos_a_ignorar, "boletos.csv")

                    if col1.button("Visualizar Arquivo"):
                        st.title("Visualização do extrato")
                        st.dataframe(extrato_df, height=300, width=1200)
                        if check_state:
                            st.title("Visualização do boleto")
                            st.dataframe(boleto_df, height=300, width=1200)

        if app == "Lançamentos":
            st.title("Lançamentos")

            adicionar_contas()

            st.write(
                "<span style='font-size:1.2em'>**Visualizar extrato coletado**</span>",
                unsafe_allow_html=True,
            )

            # st.write("Visualizar extrato coletado")

            check_state_2 = st.checkbox("Visualizar")
            if check_state_2:
                try:
                    ultimo_extrato = pd.read_csv("extrato.csv")
                    st.write("Último extrato coletado:")
                    st.dataframe(ultimo_extrato, height=300, width=1200)
                except:
                    st.write("Nenhum extrato coletado")

            st.write(
                "<span style='font-size:1.2em'>**Editar planilha de contas**</span>",
                unsafe_allow_html=True,
            )

            # st.write("Editar planilha de contas")

            check_state_3 = st.checkbox("Editar")
            if check_state_3:
                editar_contas()

            if st.session_state.boleto_ativo:
                st.write("teve boleto")

            if st.session_state.iniciar_lancamento:
                st.write(
                    "<span style='font-size:1.5em'>**Baixar lançamento**</span>",
                    unsafe_allow_html=True,
                )

                gerar_lancamento()
                
                if os.path.isfile("lancamento.txt"):
                    with open("lancamento.txt", "r") as file:
                        file_contents = file.read()
                    st.download_button(
                        label="Baixar arquivo",
                        data=file_contents,
                        file_name="lancamento.txt",
                        mime="text/plain",
                )
        if app == 'Your Posts':
            your.app()
        if app == 'about':
            about.app() 


    if __name__ == "__main__":
        main()
