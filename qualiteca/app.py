import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

from paginas.dados import Dados, Backup
from paginas.emprestimos import Emprestimos
from paginas.estante import Estante
from paginas.home import Home
from paginas.pessoas import Pessoas


class Biblioteca:

    paginas_navegaveis = {
        Home.nome: Home,
        Estante.nome: Estante,
        Pessoas.nome: Pessoas,
        Emprestimos.nome: Emprestimos,
        Dados.nome: Dados
    }

    def __init__(self) -> None:
        st.set_page_config(
            page_title="Qualiteca",
            page_icon="📚",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get help': 'mailto:ramilton.silva.lima@live.com',
                'Report a bug': "mailto:ramilton.silva.lima@live.com",
                'About': "Para compartilhar livros"
            }
        )

        self.pin()
        if 'backup_coletado' not in st.session_state:
            with st.spinner('Preparando backup...'):
                backup = Backup(st.secrets)
                backup.automatico()
                st.session_state.backup_coletado = True

    def pin(self):
        if ('logado' not in st.session_state):
            st.markdown('# Qualiteca')

            pin = st.text_input(
                'PIN',
                label_visibility='collapsed',
                type='password',
                max_chars=4,
                placeholder="Digite o pin de 4 digitos para desbloquear"
            )

            if str(pin) == str(st.secrets.SENHA):

                st.session_state['logado'] = True
                self.menu()
                st.rerun()
            elif str(pin) != str(st.secrets.SENHA) and str(pin) != '' and str(pin) is not None:
                st.error('PIN incorreto')
        else:

            self.menu()

    def menu(self):
        with st.sidebar:
            destino = option_menu(
                menu_title="Vamos lá!",
                menu_icon="cast",
                default_index=0,
                orientation="vertical",
                on_change=self.visualizacoes_inciais,
                options=list(self.paginas_navegaveis.keys()),
                key='menus_opcoes',
                styles={
                    "container": {"background-color": "transparent"}
                }
            )
            st.session_state
        self.paginas_navegaveis[destino]()

    def visualizacoes_inciais(self, _):
        st.session_state.livro_funcao = 'livro_visualizar'
        st.session_state.pessoa_funcao = 'pessoa_visualizar'
        st.session_state.emprestimo_funcao = 'emprestimo_visualizar'


Biblioteca()
