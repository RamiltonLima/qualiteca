
import dropbox
from datetime import datetime
import pandas as pd
from typing import Literal
import streamlit as st
from io import BytesIO
from models import  Livro, Usuario, Emprestimo

class Backup:
    def __init__(self, streamlit_secrets) -> None:
        self.app_key = streamlit_secrets['DROPBOX_APP_KEY']
        self.app_secret = streamlit_secrets['DROPBOX_APP_SECRET']
        self.refresh_token = streamlit_secrets['DROPBOX_REFRESH_TOKEN']
        self.nome_banco_dados = streamlit_secrets['NOME_BANCO_DADOS']
        self.pasta_backup = streamlit_secrets['DROPBOX_PASTA_BACKUP']
        self.meses_versoes = streamlit_secrets['BACKUP_MESES']
        self.dias_versoes = streamlit_secrets['BACKUP_DIAS']
        self.ultimas_versoes = streamlit_secrets['BACKUP_ULTIMAS']

        self.template_headers = ['nome', 'hash_conteudo', 'modificado_em']
        self.dtypes = {'nome':'string','hash_conteudo':'string', 'modificado_em':'datetime64[ns]'}
        self.template = pd.DataFrame(columns=self.template_headers)
        self.template = self.template.astype(self.dtypes)
        self.fluxo_autenticacao = None

    @property
    def dropbox_autenticado(self):
        try:
            return dropbox.Dropbox(oauth2_refresh_token=self.refresh_token, app_key=self.app_key)
        except Exception as e:
            raise f"Problemas com autenticação dos backups. Segue texto do erro:\n\n{e}"
        

    def dropbox_autorizacao(self, momento:Literal['inicio','fim'], codigo_autorizacao:str = None):
        if momento == 'inicio':
            self.fluxo_autenticacao = dropbox.DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret, use_pkce=True, token_access_type='offline')
            return self.fluxo_autenticacao.start()
        
        elif momento == 'fim':
            resultado_autenticacao = self.fluxo_autenticacao.finish(codigo_autorizacao)
            return resultado_autenticacao.refresh_token
        
        else:
            return False
    
    def automatico(self):
        disponiveis = self.listar()
        ultimo_registro = disponiveis['modificado_em'].max().tz_localize(tz='UTC').astimezone(tz='America/Sao_Paulo').date()
        if datetime.now().date() > ultimo_registro:
            st.info('Backup: Criando vesão de hoje')
            self.criar()
        
        irrelevantes = self.listar_irrelevantes()
        if not irrelevantes.empty:
            irrelevantes_nome = irrelevantes['nome'].to_list()


            for irrelevante in irrelevantes_nome:
                st.info(f"Excluindo backup {irrelevante}, tornou-se irrelevante.")
                self.excluir(irrelevante)
                


    def criar(self):
        try:
            with self.dropbox_autenticado as dbx:
                with open(self.nome_banco_dados, 'rb') as f:
                    dbx.files_upload(f.read(), f'/backup_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.db')
                    return True
        except Exception as e:
            print(e)
            return False

    def restaurar(self, arquivo):
        try:
            with self.dropbox_autenticado as dbx:
                metadata, response = dbx.files_download(f'/{arquivo}')
                with open(self.nome_banco_dados, 'wb') as f:
                    f.write(response.content)
                    return True
        except Exception as e:
            return False
    
    def listar(self):
        with self.dropbox_autenticado as dbx:
            arquivos = []
            for arquivo in dbx.files_list_folder('').entries:
                arquivos.append({
                    'nome' : arquivo.name,
                    'hash_conteudo' : arquivo.content_hash,
                    'modificado_em' :  arquivo.server_modified
                })

        if arquivos:
            return pd.DataFrame(arquivos).sort_values('modificado_em', ascending=False).reset_index(drop=True)
        else:
            return self.template.copy()
    
    def listar_relevantes(self):
        dados = self.listar()
        dados['mes'] = dados['modificado_em'].dt.to_period('M')
        dados['dia'] = dados['modificado_em'].dt.to_period('D')
        ultimas = dados.nlargest(self.ultimas_versoes, 'modificado_em')
        mensais = dados[ dados['mes'] >= dados['mes'].max() - self.meses_versoes ].drop_duplicates('mes')
        diarias = dados[ dados['dia'] >= dados['dia'].max() - self.dias_versoes ].drop_duplicates('dia')
        relevantes = pd.concat([ultimas, mensais, diarias]).drop_duplicates('nome')
        return relevantes[self.template_headers]

    def listar_irrelevantes(self):
        arquivos = self.listar()
        relevantes = self.listar_relevantes()
        return arquivos[~(arquivos['nome'].isin(relevantes['nome']))]

    def excluir(self, arquivo):
        with self.dropbox_autenticado as dbx:
            dbx.files_delete_v2(f'/{arquivo}')
            return True

class Dados:
    nome = 'Backup'
    nomes_abas = ['Criar','Restaurar','Gerenciar', 'Exportar']
    def __init__(self) -> None:
        super().__init__()
        st.header(self.nome, divider='orange')
        abas = st.tabs(self.nomes_abas)

        with abas[0]:
            self.criar()
        
        with abas[1]:
            self.restaurar()

        with abas[2]:
            self.gerenciar()

        with abas[3]:
            self.exportar()

    def criar(self):
        st.markdown('### Crie novos backups')
        st.caption('O arquivo de banco de dados é guardado em uma conta do dropbox, vinculado ao e-mail qualiteca.livros@gmail.com')
        if st.button('Criar backup'):
            backup = Backup(st.secrets)
            if backup.criar():
                st.success('Backup criado com sucesso!')
            else: 
                st.error('Não foi possivel criar o backup')


    def restaurar(self):
        
        st.markdown('### Restaure os backups')
        st.caption('Abaixo são listados os backups gerados automaticamente e manualmente.')
        st.caption(f'São apenas mantidos até 1 backup dos ultimos {st.secrets.BACKUP_MESES} meses,'+
                   f' um de cada mês, 1 backup dos ultimos {st.secrets.BACKUP_DIAS} dias,'+
                   f' um de cada dia e os ultimos {st.secrets.BACKUP_ULTIMAS} gerados')
        if st.button('Carregar backups disponiveis'):
            backup = Backup(st.secrets)
            lista_backups = backup.listar_relevantes()
            if not lista_backups.empty:
                backup_selecionado = st.selectbox(
                    'Backups',
                    index=0,
                    options=lista_backups,
                    placeholder="Escolha uma versão")
                if st.button('Restaurar'):
                    restaurado = backup.restaurar(backup_selecionado)
                    if restaurado:
                        st.success('Backup restaurado com sucesso')
                    else:
                        st.error('Problemas ao restaurar backup')


    def gerenciar(self):
        if st.button('Iniciar gerenciamento'):
            if 'BACKUP' not in st.session_state:
                st.session_state['BACKUP'] = Backup(st.secrets)

            st.markdown('### Gerencie as configurações do backup')
            st.markdown('#### Autenticação DropBox')
            st.caption('Após gerar o "link de autenticação" cole-o na caixa abaixo, depois guarde-o nos segredos do aplicação')
            
            gerar_link, receber_codigo = st.columns(2)
            with gerar_link:
                st.markdown('##### 1. Gerar link')
                if st.button('Gerar link de autenticação'):
                    link_autenticacao = st.session_state.BACKUP.dropbox_autorizacao('inicio')
                    st.markdown(f"Vá até a [Pagina de autenticação]({link_autenticacao})")
            with receber_codigo:
                st.markdown('##### 2. Receber o codigo')
                codigo_gerado = st.text_input('Qual o código gerado?')
                botao_gerar_refresh_code = st.button('Gerar "refresh code"')

            if botao_gerar_refresh_code:
                if codigo_gerado.strip() is not None and codigo_gerado.strip() != '':
                    refresh_token = st.session_state.BACKUP.dropbox_autorizacao('fim', codigo_gerado)
                    if refresh_token:
                        st.code(f"DROPBOX_REFRESH_TOKEN = '{refresh_token}'", language='toml')
                    else:
                        st.error('Ocorreu algum problema ao gerar o refresh token')
                else:
                    st.error('Ocorreu algum problema ao gerar o refresh token')
        
    def exportar(self):
        st.markdown('### Exporte os arquivos em um formato offline')

        formato = st.radio(
            'Formato Exportação',
            options=['Excel','Sqlite'],
            index=None,
            horizontal=True,
            captions=['Cada tabela será uma planilha.', 'Arquivo de banco de dados unico.']
        )
        
        if formato == 'Excel':
            tabelas = [Emprestimo, Livro, Usuario]
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter', mode='w') as writer:
                for tabela in tabelas:
                    tabela.em_dataframe().to_excel(writer, sheet_name=tabela.__tablename__, index=False)
                

            st.info('Caso não haja dados o arquivo será gerado vazio')
            st.download_button(
                'Baixar Excel',
                data=excel_buffer,
                file_name=f'backup_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.xlsx',
            )




        if formato == 'Sqlite':
            with open(st.secrets.NOME_BANCO_DADOS, 'rb') as f:
                conteudo_arquivo = f.read()

            st.download_button(
                'Baixar Sqlite',
                data=conteudo_arquivo,
                file_name=f'backup_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.db',
            )
