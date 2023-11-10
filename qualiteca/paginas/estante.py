from models import Livro, Usuario, session
import streamlit as st


class Estante:
    nome = 'Estante de Livros'

    def __init__(self) -> None:
        super().__init__()

        self.estrutura()
        self.titulo()
        self.adicionar_livro()
        self.ver_livros()
        self.excluir_livro()
        self.editar_livro()

    def estrutura(self):
        if 'livro_funcao' not in st.session_state:
            st.session_state['livro_funcao'] = None

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
                    st.session_state.livro_funcao = 'livro_visualizar'
                    st.rerun()
            with colunas[1]:
                if st.button(':heavy_plus_sign: Receber nova doação'):
                    st.session_state.livro_funcao = 'livro_adicionar'
                    st.rerun()
            st.divider()

    def adicionar_livro(self):
        if st.session_state.livro_funcao == 'livro_adicionar':
            with self.placeholder_adicionar.container():
                with st.form('adicionar_livro', clear_on_submit=True):
                    st.markdown('#### Sobre o livro')
                    colunas = st.columns([0.6, 0.4])
                    with colunas[0]:
                        titulo = st.text_input(
                            'Titulo *', placeholder='Viagem ao centro da terra')
                        autor = st.text_input(
                            'Autor *', placeholder='Júlio Verne')
                        genero = st.text_input(
                            'Genêro *', placeholder='Aventura, Ficção')

                    with colunas[1]:
                        foto_livro = st.camera_input(
                            'Adicione uma foto da capa livro *')
                    observacao = st.text_area(
                        'Observações ou qualquer coisa que queira dizer sobre o livro',
                        placeholder="""Edição com ilustrações, capa dura, folhas em papel especial e etc.\nHistória de uma viagem, literalmente, ao centro da terra"""
                    )

                    st.markdown('#### Sobre o doador')
                    pessoas_doadores = Usuario.retornar(session=session)
                    if pessoas_doadores:
                        doador = st.selectbox(
                            'Doador',
                            options=pessoas_doadores,
                            placeholder="Comece a digitar o nome para encontrar mais rapido...",
                            index=None
                        )
                        st.info(
                            'Doador não listado? Cadastre-o antes em "Pessoas"')
                    else:
                        st.warning(
                            'Antes de continuar, cadastre uma pessoa doadora em "Pessoas"')

                    if st.form_submit_button('Adicionar'):
                        if not all([titulo, autor, genero, foto_livro, doador]):
                            st.error(
                                'Ficou faltando algumas informações, observe o "*"')
                        else:
                            novo = Livro.adicionar(
                                session=session,
                                titulo=titulo,
                                autor=autor,
                                genero=genero,
                                doador_id=doador.id,
                                foto_livro=foto_livro.getvalue(),
                                observacao=observacao,
                                extensao_foto=str(
                                    foto_livro.name.split('.')[-1])
                            )
                            if novo:
                                st.success(
                                    f'{titulo} adicionado a nossa estante')
                                st.session_state.livro_funcao = 'livro_visualizar'
                                st.balloons()
                            else:
                                st.error(
                                    f'Parece que algo não funcionou como deveria. Não foi possivel adicionar o livro')
                                st.session_state.livro_funcao = 'livro_visualizar'

    def ver_livros(self):
        if st.session_state.livro_funcao == 'livro_visualizar':
            with self.placeholder_visualizar.container():
                livros = Livro.retornar(session=session)
                for livro in livros:
                    with st.expander(f'##### {livro.titulo}'):
                        colunas = st.columns(2)
                        with colunas[0]:
                            st.caption(f'ID: {livro.id}')
                            st.caption(f'Autor: {livro.autor}')
                            st.caption(f'Genero: {livro.genero}')
                            st.caption(f'Observacao: {livro.observacao}')
                        with colunas[1]:
                            st.image(
                                image=livro.foto_livro,
                                output_format=livro.extensao_foto
                            )
                        st.caption(f'Doado por: {livro.doador}')
                        botoes = st.columns(2)
                        with botoes[0]:
                            if st.button('Editar', use_container_width=True, key=f'editar_{livro.id}'):
                                st.session_state.livro_funcao = 'livro_editar'
                                st.session_state.livro_funcao_editar = livro
                                st.rerun()

                        with botoes[1]:
                            if st.button('Excluir', use_container_width=True, key=f'excluir_{livro.id}'):
                                st.session_state.livro_funcao = 'livro_excluir'
                                st.session_state.livro_funcao_excluir = livro
                                st.rerun()

    def excluir_livro(self):
        if st.session_state.livro_funcao == 'livro_excluir':
            with self.placeholder_excluir.container():
                if st.session_state.livro_funcao_excluir is None:
                    st.session_state.livro_funcao = 'livro_visualizar'
                else:
                    livro = st.session_state.livro_funcao_excluir

                    with st.expander(f'##### Excluir #{str(livro.id)} {livro.titulo}', expanded=True):
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
                                excluido = Livro.excluir(
                                    session=session,
                                    valor=livro.id
                                )
                                if excluido:
                                    st.info('Excluido com sucesso')
                                    st.session_state.livro_funcao_excluir = None
                                else:
                                    st.error(
                                        'Houve problemas ao excluir o livro')
                                    st.session_state.livro_funcao_excluir = None
                            else:
                                st.error(
                                    'Digite "excluir", para termos certeza que deseja tomar esta ação definitiva.')

    def editar_livro(self):
        if st.session_state.livro_funcao == 'livro_editar':
            with self.placeholder_editar.container():
                if st.session_state.livro_funcao_editar is None:
                    st.session_state.livro_funcao = 'livro_visualizar'
                else:
                    livro = st.session_state.livro_funcao_editar
                    with st.expander(f'##### Editar #{str(livro.id)} {livro.titulo}', expanded=True):
                        st.markdown('#### Sobre o livro')
                        colunas = st.columns([0.6, 0.4])
                        with colunas[0]:
                            titulo = st.text_input(
                                'Titulo *', placeholder='Viagem ao centro da terra', value=livro.titulo)
                            autor = st.text_input(
                                'Autor *', placeholder='Júlio Verne', value=livro.autor)
                            genero = st.text_input(
                                'Genêro *', placeholder='Aventura, Ficção', value=livro.genero)

                        with colunas[1]:
                            st.image(
                                image=livro.foto_livro,
                                output_format=livro.extensao_foto
                            )
                            st.caption(
                                'Caso deseje atualizar a imagem capture uma nova imagem')
                            foto_livro = st.camera_input(
                                'Adicione uma foto da capa livro *')

                        observacao = st.text_area(
                            'Observações ou qualquer coisa que queira dizer sobre o livro',
                            placeholder="""Edição com ilustrações, capa dura, folhas em papel especial e etc.\nHistória de uma viagem, literalmente, ao centro da terra""",
                            value=livro.observacao
                        )

                        st.markdown('### Sobre o doador')
                        pessoas_doadores = Usuario.retornar(session=session)

                        if pessoas_doadores:
                            pessoas_doadores_id = [
                                doador.id for doador in pessoas_doadores]
                            index_lista = pessoas_doadores_id.index(
                                livro.doador_id)

                            doador = st.selectbox(
                                'Doador',
                                options=pessoas_doadores,
                                placeholder="Comece a digitar o nome para encontrar mais rapido...",
                                index=index_lista,
                            )
                            st.info(
                                'Doador não listado? Cadastre-o antes em "Pessoas"')
                        else:
                            st.warning(
                                'Antes de continuar, cadastre uma pessoa doadora em "Pessoas"')

                        if st.button('Salvar alterações'):
                            if not all([titulo, autor, genero, doador]):
                                st.error(
                                    'Ficou faltando algumas informações, observe o "*"')
                            else:
                                resultado_edicao = Livro.editar(
                                    session=session,
                                    valor=livro.id,
                                    edicao={
                                        'titulo': titulo,
                                        'autor': autor,
                                        'genero': genero,
                                        'doador_id': doador.id,
                                        'foto_livro': foto_livro.getvalue() if foto_livro else livro.foto_livro,
                                        'observacao': observacao,
                                        'extensao_foto': str(foto_livro.name.split('.')[-1]) if foto_livro else livro.extensao_foto
                                    }
                                )

                                if resultado_edicao:
                                    st.success('Editado com sucesso')
                                    st.session_state.livro_funcao_editar = None
                                else:
                                    st.error(
                                        'Houve problemas ao editar o livro')
                                    st.session_state.livro_funcao_editar = None
