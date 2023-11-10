from models import Livro, Usuario, Emprestimo, session
import streamlit as st
from datetime import datetime, timedelta
import locale

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
except:
    pass

class Emprestimos:
    nome = 'Empréstimos'

    def __init__(self) -> None:
        super().__init__()

        self.estrutura()
        self.titulo()
        self.adicionar_emprestimo()
        self.ver_emprestimos()

    def estrutura(self):
        if 'emprestimo_funcao' not in st.session_state:
            st.session_state['emprestimo_funcao'] = None

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
                    st.session_state.emprestimo_funcao = 'emprestimo_visualizar'
                    st.rerun()
            with colunas[1]:
                if st.button(':heavy_plus_sign: Emprestar'):
                    st.session_state.emprestimo_funcao = 'emprestimo_adicionar'
                    st.rerun()

            st.divider()

    def adicionar_emprestimo(self):
        if st.session_state.emprestimo_funcao == 'emprestimo_adicionar':
            with self.placeholder_adicionar.container():
                st.markdown('#### Sobre o livro')
                livros_disponiveis = Livro.retornar_livro_disponiveis(
                    session=session
                )
                if livros_disponiveis:
                    livro_escolhido = st.selectbox(
                        'Livro desejado *',
                        options=livros_disponiveis,
                        placeholder="Comece a digitar o nome para encontrar mais rapido...",
                        index=None
                    )
                    if livro_escolhido:
                        with st.expander(f'##### {livro_escolhido.titulo}'):
                            colunas = st.columns(2)
                            with colunas[0]:
                                st.caption(f'ID: {livro_escolhido.id}')
                                st.caption(f'Autor: {livro_escolhido.autor}')
                                st.caption(f'Genero: {livro_escolhido.genero}')
                                st.caption(
                                    f'Observacao: {livro_escolhido.observacao}')
                            with colunas[1]:
                                st.image(
                                    image=livro_escolhido.foto_livro,
                                    output_format=livro_escolhido.extensao_foto
                                )
                    else:

                        st.info(
                            'Caso tenha o livro e ele não esteja listado, cheque se não está como "Emprestado"')

                else:
                    livro_escolhido = None
                    st.warning('Parece que não há livros dispoiveis')

                st.markdown('#### Sobre o leitor')
                leitores = Usuario.retornar(session=session)
                if leitores:
                    leitor = st.selectbox(
                        'Leitor *',
                        options=leitores,
                        placeholder="Comece a digitar o nome para encontrar mais rapido...",
                        index=None
                    )
                    if leitor:
                        with st.expander(f'##### {leitor.nome}'):
                            st.caption(f'ID: {leitor.id}')
                            st.caption(leitor.email)
                            st.write(
                                f"Genêros preferidos:\n {leitor.genero_preferidos.upper()}")
                            st.caption(
                                f'Cadastro criado em: {leitor.registrado_em}')
                            st.caption(
                                f'Ultima edição no cadastro em: {leitor.ultima_edicao_em}') if leitor.ultima_edicao_em is not None else None
                            if leitor.volume_emprestimos_ativos():
                                st.warning(
                                    f'Este leitor está com {leitor.volume_emprestimos_ativos()} emprestimos atualmente')
                            else:
                                st.caption(
                                    f'Este leitor está com {leitor.volume_emprestimos_ativos()} emprestimos atualmente')

                else:
                    st.warning(
                        'Antes de continuar, cadastre uma pessoa leitora em "Pessoas"')

                quantidade_dias = st.number_input(
                    f'Hoje é {datetime.now().date().strftime("%A, %d de %B de %Y")}. Quantos dias durárá o empréstimo?',
                    min_value=1, value=1, step=1
                )
                dia_devolucao = datetime.now().date() + timedelta(days=quantidade_dias)
                st.caption(
                    f'Então a devolução será em: {dia_devolucao.strftime("%A, %d de %B de %Y")}')

                if st.button('Emprestar'):
                    if not livro_escolhido:
                        st.error('Então, não há livros.')
                    elif not all([leitor, livro_escolhido, quantidade_dias]):
                        st.error(
                            'Ficou faltando algumas informações, observe o "*"')
                    else:
                        novo = Emprestimo.adicionar(
                            session=session,
                            leitor_id=leitor.id,
                            livro_id=livro_escolhido.id,
                            data_inicio=datetime.now().date(),
                            data_fim=dia_devolucao,
                            terminado=False
                        )
                        if novo:
                            st.success(
                                f'{livro_escolhido.titulo} Emprestado a {leitor.nome}, até {dia_devolucao.strftime("%A, %d de %B de %Y")}')
                            st.session_state.emprestimo_funcao = 'emprestimo_visualizar'
                            st.balloons()
                        else:
                            st.error(
                                f'Parece que algo não funcionou como deveria. Não foi possivel emprestar o livro')

    def ver_emprestimos(self):
        if st.session_state.emprestimo_funcao == 'emprestimo_visualizar':
            with self.placeholder_visualizar.container():

                emprestimos_abertos = Emprestimo.retornar_abertos_ordenados(
                    session=session)
                if emprestimos_abertos:
                    st.markdown('#### Empréstimos pendentes')
                    for emprestimo in emprestimos_abertos:
                        with st.expander(f'##### {emprestimo}'):
                            st.caption(f'ID: {emprestimo.id}')
                            st.markdown(
                                f'Este empréstimo acaba em {emprestimo.data_fim.strftime("%A, %d de %B de %Y")}. ' +
                                f'Daqui a {emprestimo.dias_para_termino} dia(s)'
                            )
                            st.divider()
                            st.markdown('##### Livro')
                            colunas = st.columns(2)
                            with colunas[0]:
                                st.caption(f'ID: {emprestimo.livro.id}')
                                st.caption(f'Autor: {emprestimo.livro.autor}')
                                st.caption(
                                    f'Genero: {emprestimo.livro.genero}')
                                st.caption(
                                    f'Observacao: {emprestimo.livro.observacao}')
                            with colunas[1]:
                                st.image(
                                    image=emprestimo.livro.foto_livro,
                                    output_format=emprestimo.livro.extensao_foto
                                )

                            st.divider()
                            st.markdown('##### Leitor')
                            st.caption(f'ID: {emprestimo.leitor.id}')
                            st.caption(emprestimo.leitor.email)
                            st.write(
                                f"Genêros preferidos:\n {emprestimo.leitor.genero_preferidos.upper()}")
                            st.caption(
                                f'Cadastro criado em: {emprestimo.leitor.registrado_em}')
                            st.caption(
                                f'Ultima edição no cadastro em: {emprestimo.leitor.ultima_edicao_em}') if emprestimo.leitor.ultima_edicao_em is not None else None
                            if emprestimo.leitor.volume_emprestimos_ativos():
                                st.warning(
                                    f'Este leitor está com {emprestimo.leitor.volume_emprestimos_ativos()} emprestimos atualmente')
                            else:
                                st.caption(
                                    f'Este leitor está com {emprestimo.leitor.volume_emprestimos_ativos()} emprestimos atualmente')

                            st.divider()
                            colunas = st.columns(2)
                            with colunas[0]:
                                devolver = st.button(
                                    'Devolver', use_container_width=True, key=f'devolver_{emprestimo.id}')
                            with colunas[1]:
                                mais_prazo = st.button(
                                    '+ 1 dia de prazo', use_container_width=True, key=f'mais_prazo_{emprestimo.id}')

                            if devolver:
                                emprestimo_modificado = emprestimo.devolver(
                                    session)
                                st.success('Livro devolvido')

                            if mais_prazo:
                                emprestimo_modificado = emprestimo.mais_prazo(
                                    session)
                                st.info(
                                    f'OK. Novo prazo em: {emprestimo_modificado.data_fim}')

                    st.divider()

                emprestimos_fechados = Emprestimo.retornar(
                    session=session,
                    campo='terminado',
                    valor=True
                )
                if emprestimos_fechados:
                    st.markdown('#### Empréstimos fechados')
                    for emprestimo in emprestimos_fechados:
                        with st.expander(f'##### {emprestimo}'):
                            st.write(emprestimo)
