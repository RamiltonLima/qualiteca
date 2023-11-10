
from models import Usuario, session
import streamlit as st
from re import fullmatch


class Pessoas:
    nome = 'Pessoas'

    def __init__(self) -> None:
        super().__init__()

        self.estrutura()
        self.titulo()
        self.visualizar_pessoa()
        self.excluir_pessoa()
        self.editar_pessoa()
        self.adicionar_pessoa()

    def estrutura(self):
        if 'pessoa_funcao' not in st.session_state:
            st.session_state['pessoa_funcao'] = None

        self.placeholder_titulo = st.empty()
        self.placeholder_adicionar = st.empty()
        self.placeholder_editar = st.empty()
        self.placeholder_excluir = st.empty()
        self.placeholder_visualizar = st.empty()

    def titulo(self):
        with self.placeholder_titulo.container():

            st.header(self.nome, divider='orange')
            colunas = st.columns([0.20, 0.3, 0.3])

            with colunas[0]:
                if st.button(':eye: Ver todos'):
                    st.session_state.pessoa_funcao = 'pessoa_visualizar'
                    st.rerun()
            with colunas[1]:
                if st.button(':heavy_plus_sign: Adicionar novos'):
                    st.session_state.pessoa_funcao = 'pessoa_adicionar'
                    st.rerun()
            st.divider()

    def visualizar_pessoa(self):
        if st.session_state.pessoa_funcao == 'pessoa_visualizar':
            with self.placeholder_visualizar.container():
                usuarios = Usuario.retornar(session=session)
                for usuario in usuarios:
                    with st.expander(f'##### {usuario.nome}'):
                        st.caption(f'ID: {usuario.id}')
                        st.caption(usuario.email)
                        st.write(
                            f"Genêros preferidos:\n {usuario.genero_preferidos.upper()}")
                        st.caption(
                            f'Cadastro criado em: {usuario.registrado_em}')
                        st.caption(
                            f'Ultima edição no cadastro em: {usuario.ultima_edicao_em}') if usuario.ultima_edicao_em is not None else None

                        botoes = st.columns(2)
                        with botoes[0]:
                            if st.button('Editar', use_container_width=True, key=f'editar_{usuario.id}'):
                                st.session_state.pessoa_funcao = 'pessoa_editar'
                                st.session_state.pessoa_funcao_editar = usuario
                                st.rerun()

                        with botoes[1]:
                            if st.button('Excluir', use_container_width=True, key=f'excluir_{usuario.id}'):
                                st.session_state.pessoa_funcao = 'pessoa_excluir'
                                st.session_state.pessoa_funcao_excluir = usuario
                                st.rerun()

    def excluir_pessoa(self):
        if st.session_state.pessoa_funcao == 'pessoa_excluir':
            with self.placeholder_excluir.container():
                if st.session_state.pessoa_funcao_excluir is None:
                    st.session_state.pessoa_funcao = 'pessoa_visualizar'
                else:
                    usuario = st.session_state.pessoa_funcao_excluir

                    with st.expander(f'##### Excluir #{str(usuario.id)} {usuario.nome}', expanded=True):
                        st.warning('A exclusão é definitiva')
                        st.markdown(f'#### Deseja realmente excluir?')

                        colunas = st.columns([0.7, 0.3])
                        with colunas[0]:
                            texto_confirmacao = st.text_input(
                                label='confirmacao exclusao',
                                placeholder='Digite "excluir" para excluir este cadastro e pressione "enter"',
                                label_visibility='collapsed'
                            )
                        with colunas[1]:
                            botao_excluir = st.button(
                                'Excluir', type='secondary', use_container_width=True)

                        if botao_excluir:
                            if texto_confirmacao == 'excluir':
                                excluido = Usuario.excluir(
                                    session=session,
                                    valor=usuario.id
                                )
                                if excluido:
                                    st.info('Excluido com sucesso')
                                    st.session_state.pessoa_funcao_excluir = None
                                else:
                                    st.error(
                                        'Houve problemas ao excluir o usuário')
                                    st.session_state.pessoa_funcao_excluir = None
                            else:
                                st.error(
                                    'Digite "excluir", para termos certeza que deseja tomar esta ação definitiva.')

    def editar_pessoa(self):
        if st.session_state.pessoa_funcao == 'pessoa_editar':
            with self.placeholder_editar.container():
                if st.session_state.pessoa_funcao_editar is None:
                    st.session_state.pessoa_funcao = 'pessoa_visualizar'
                else:
                    usuario = st.session_state.pessoa_funcao_editar
                    with st.expander(f'##### Editar #{str(usuario.id)} {usuario.nome}', expanded=True):
                        nome = st.text_input('Nome*', value=usuario.nome)
                        email = st.text_input('E-mail*', value=usuario.email)
                        genero_preferidos = st.text_input(
                            'Genêros literários preferidos', value=usuario.genero_preferidos)
                        editado = st.button(
                            "Salvar alterações", key=f'editando_{usuario.id}')
                        if editado:
                            if (not nome) or (not email):
                                st.error(
                                    'Ficou faltando algumas informações, observe o "*"')
                            elif not fullmatch(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email):
                                st.error(
                                    'Confirme se o e-mail digitado é valido')
                            else:
                                resultado_edicao = Usuario.editar(
                                    session=session,
                                    valor=usuario.id,
                                    edicao={
                                        'nome': nome,
                                        'email': email,
                                        'genero_preferidos': genero_preferidos
                                    }
                                )

                                if resultado_edicao:
                                    st.success('Editado com sucesso')
                                    st.session_state.pessoa_funcao_editar = None
                                else:
                                    st.error(
                                        'Houve problemas ao editar o usuário')
                                    st.session_state.pessoa_funcao_editar = None

    def adicionar_pessoa(self):
        if st.session_state.pessoa_funcao == 'pessoa_adicionar':
            with self.placeholder_adicionar.container():
                with st.form('adicionar_pessoa', clear_on_submit=True):
                    st.markdown('### Cadastre uma nova pessoa')
                    nome = st.text_input(
                        'Nome *', placeholder='João Maria José da Silva')
                    email = st.text_input(
                        'E-mail *', placeholder='jose.maria.silva@provedor.com')
                    genero_preferidos = st.text_input(
                        'Genêros literários preferidos', placeholder='Aventura, não-ficção')
                    adicionado = st.form_submit_button("Adicionar")
                    if adicionado:
                        if (not nome) or (not email):
                            st.error(
                                'Ficou faltando algumas informações, observe o "*"')
                        elif not fullmatch(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email):
                            st.error('Confirme se o e-mail digitado é valido')
                        else:
                            novo = Usuario.adicionar(
                                session=session, nome=nome, email=email, genero_preferidos=genero_preferidos)

                            if novo:
                                st.success(
                                    f'Adicionado com sucesso. ID:{novo.id}')
                                st.balloons()
                                st.session_state.pessoa_funcao = 'pessoa_visualizar'
                            else:
                                st.error(
                                    'Houve problemas ao adicionar o usuário')
