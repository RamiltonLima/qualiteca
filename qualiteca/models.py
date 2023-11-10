from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, DateTime, LargeBinary, Boolean, or_, and_, func
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
import pandas as pd
from typing import Any

engine = create_engine('sqlite:///biblioteca.db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class ModeloBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    registrado_em = Column(DateTime, nullable=False, default=datetime.now)
    ultima_edicao_em = Column(DateTime, nullable=True)
    modificado = Column(Boolean, nullable=False, default=False)
    excluido_em = Column(DateTime, nullable=True)
    excluido = Column(Boolean, nullable=False, default=False)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.id == other.id
        )

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    def __str__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    @classmethod
    def adicionar(cls, session: Session = session, **kwargs):
        try:
            novo = cls(**kwargs)
            session.add(novo)
            session.commit()
            return novo
        except Exception as e:
            print(e)
            return False

    @classmethod
    def retornar(cls, session: Session = session, campo='id', valor=None):
        if valor is None:
            filtro = True
        else:
            filtro = (getattr(cls, campo) == valor)

        return session.query(cls).where(cls.excluido == False, filtro).all()

    @classmethod
    def editar(cls, session: Session = session, campo='id', valor=None, edicao: dict[str, Any] = None):

        objeto = cls.retornar(
            campo=campo,
            session=session,
            valor=valor
        )

        if not objeto:
            return None

        editados = []
        for item in objeto:
            if edicao is not None:
                for campo_edicao, valor_edicao in edicao.items():
                    setattr(item, campo_edicao, valor_edicao)
            setattr(item, 'ultima_edicao_em', datetime.now())
            setattr(item, 'modificado', True)
            session.commit()
            editados.append(item)

        return editados

    @classmethod
    def excluir(cls, session: Session = session, campo='id', valor=None):
        return cls.editar(
            campo=campo,
            valor=valor,
            edicao={
                'excluido_em': datetime.now(),
                'excluido': True
            },
            session=session
        )

    @classmethod
    def em_dataframe(
        cls,
        session: Session = session,
        campo=None,
        valor=None,
    ):
        objetos = cls.retornar(campo=campo, session=session, valor=valor)

        objetos_dict = [objeto.em_dict() for objeto in objetos]
        df = pd.DataFrame(objetos_dict)
        colunas = df.columns
        colunas = df.columns
        novas_colunas = dict()
        for coluna in colunas:
            if not coluna.startswith('_'):
                novas_colunas[coluna] = coluna.capitalize().replace(
                    '_', ' ').strip()

        return df

    def em_dict(self):
        objeto_dict = {}
        for attr, value in self.__dict__.items():
            objeto_dict[attr] = value
        return objeto_dict


class Usuario(ModeloBase):
    __tablename__ = 'usuarios'

    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    genero_preferidos = Column(String, nullable=True)

    emprestimos = relationship('Emprestimo', back_populates='leitor')
    doacao = relationship('Livro', back_populates='doador')

    @classmethod
    def busca(cls, termos: list[str]):
        resultados = []
        for termo in termos:
            resultado = session.query(cls).filter(
                and_(
                    or_(
                        func.lower(cls.nome).ilike(f'%{termo}%'),
                        func.lower(cls.email).ilike(f'%{termo}%'),
                        func.lower(cls.genero_preferidos).ilike(f'%{termo}%')
                    ),
                    (cls.excluido == False)
                )
            ).all()

            resultados.extend(resultado)
        return set(resultados)

    def volume_emprestimos_ativos(self):

        livros_emprestados = session.query(Emprestimo.id).filter(
            (Emprestimo.terminado == False), (self.id == Emprestimo.leitor_id)
        ).count()

        return livros_emprestados

    def __str__(self):
        return f"(#{self.id}) {self.nome}"


class Livro(ModeloBase):
    __tablename__ = 'livros'
    def tempo_emprestimo_padrao(): return 1

    titulo = Column(String, nullable=False)
    autor = Column(String, nullable=False)
    genero = Column(String, nullable=False)
    doador_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    foto_livro = Column(LargeBinary, nullable=False)
    observacao = Column(String, nullable=True)
    extensao_foto = Column(String, nullable=False)

    doador = relationship('Usuario', back_populates='doacao')
    emprestimos = relationship('Emprestimo', back_populates='livro')

    def __str__(self):
        return f"(#{self.id}) {self.titulo}< {self.autor} >"

    @classmethod
    def retornar_livro_disponiveis(cls, session: Session = session):
        livros_emprestados = session.query(Emprestimo.livro_id).filter(
            Emprestimo.terminado == False).distinct()
        livros_disponiveis = session.query(Livro).filter(
            ~(Livro.id.in_(livros_emprestados)))
        return livros_disponiveis.all()


class Emprestimo(ModeloBase):
    __tablename__ = 'emprestimos'

    leitor_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    livro_id = Column(Integer, ForeignKey('livros.id'), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    data_devolucao = Column(Date, nullable=True)
    terminado = Column(Boolean, nullable=False, default=False)

    leitor = relationship('Usuario', back_populates='emprestimos')
    livro = relationship('Livro', back_populates='emprestimos')

    def __str__(self):
        return f'{self.livro.titulo} para {self.leitor.nome} até {self.data_fim.strftime("%A, %d de %B de %Y")}'

    @classmethod
    def retornar_abertos_ordenados(cls, session: Session = session):

        emprestimos_abertos = cls.retornar(
            session=session,
            campo='terminado',
            valor=False
        )
        if emprestimos_abertos:
            return sorted(emprestimos_abertos, key=lambda x: x.data_fim)
        else:
            return []

    @property
    def dias_para_termino(self):
        return (self.data_fim - datetime.now().date()).days

    def devolver(self, session: Session = session):
        self.terminado = True
        self.data_devolucao = datetime.now().date()
        self.modificado = True
        self.ultima_edicao_em = datetime.now().date()
        session.commit()
        return self

    def mais_prazo(self, session: Session = session, aumento_prazo: int = 1):
        self.data_fim = self.data_fim + timedelta(days=aumento_prazo)
        self.modificado = True
        self.ultima_edicao_em = datetime.now().date()
        session.commit()
        return self


Base.metadata.create_all(engine)
