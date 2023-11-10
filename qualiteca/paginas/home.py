import streamlit as st


class Home:
    nome = 'Home'

    def __init__(self) -> None:
        super().__init__()
        st.header('Qualiteca', anchor=False, divider='orange')
        st.markdown(
            'Biblioteca formada com doações de livros do call center para incentivar a leitura de todos. ' +
            'Livros teremos o empréstimo de acordo como tamanho do livro, gibis e revistas ' +
            'ficarão dentro da descompressão para leitura rápida quando estiverem lá.'
        )
