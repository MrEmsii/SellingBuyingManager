from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy import Table, Date, select
import datetime
import os

Base = declarative_base()

artykuly_relacja = Table(
    'lista_dodanie', Base.metadata,
    Column('zamowienie_id', Integer, ForeignKey('zamowienie.id')),
    Column('element_id', Integer, ForeignKey('element.id')),
    Column('ilosc_elem', Integer, default=1)
)

class Kupujacy(Base):
    __tablename__ = 'kupujacy'
    id = Column(Integer, primary_key=True)
    nazwa = Column(String)

    zamowienia = relationship('Zamowienie', back_populates='kupujacy')

class Kategoria(Base):
    __tablename__ = 'kategoria'
    id = Column(Integer, primary_key=True)
    nazwa = Column(String)

    typ = relationship('Typ', back_populates='kategoria')

class Typ(Base):
    __tablename__ = 'typ'
    id = Column(Integer, primary_key=True)
    nazwa = Column(String)
    id_kategoria = Column(Integer, ForeignKey('kategoria.id'))

    kategoria = relationship('Kategoria', back_populates='typ')
    art_lista = relationship('Artykul_Lista', back_populates='typ')
    
class Sklep(Base):
    __tablename__ = 'sklep'
    id = Column(Integer, primary_key=True)
    nazwa = Column(String)

    zamowienia = relationship('Zamowienie', back_populates='sklep')

class Firma(Base):
    __tablename__ = 'firma'
    id = Column(Integer, primary_key=True)
    nazwa = Column(String)

    art_lista = relationship('Artykul_Lista', back_populates='firma')

class Zamowienie(Base):
    __tablename__ = 'zamowienie'
    id = Column(Integer, primary_key=True)
    data = Column(Date, default=datetime.date.today)
    rabat_j = Column(Integer, default=0)
    rabat_procent= Column(Integer, default=0)
    kupujacy_id = Column(Integer, ForeignKey('kupujacy.id'))  # Klucz obcy do tabeli Firma
    sklep_id = Column(Integer, ForeignKey('sklep.id'))  # Klucz obcy do tabeli Firma
    
    kupujacy = relationship('Kupujacy', back_populates='zamowienia')
    sklep = relationship('Sklep', back_populates='zamowienia')

    artykul_dodawanie = relationship('Artykul_Dodawanie', back_populates='zamowienia')

class Artykul_Dodawanie(Base):
    __tablename__ = 'artykul_dodawanie'
    id = Column(Integer, primary_key=True)
    zamowienie_id = Column(Integer, ForeignKey('zamowienie.id'))
    artykul_id = Column(Integer, ForeignKey('artykul_lista.id'))
    cena_jednostkowa = Column(Integer, default=0)
    ilosc = Column(Integer, default=1)

    zamowienia = relationship('Zamowienie', back_populates='artykul_dodawanie')
    art_lista = relationship('Artykul_Lista', secondary=artykuly_relacja, backref='artykul_dodawanie', cascade="all, delete")

class Artykul_Lista(Base):
    __tablename__ = 'artykul_lista'
    id = Column(Integer, primary_key=True)
    typ_id = Column(Integer, ForeignKey('typ.id'))
    firma_id = Column(Integer, ForeignKey('firma.id'))
    artykul = Column(String)
    kolor = Column(String, default=None)
    szczegoly = Column(String, default=None)

    typ = relationship('Typ', back_populates='art_lista')
    firma = relationship('Firma', back_populates='art_lista')

    artykul_dodawanie = relationship('Artykul_Dodawanie', back_populates='art_lista')

def SQLconnect(dsc):
    db_path = os.path.join(dsc, '3DPP.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()

def Test(session):
    kupujacy_1 = Kupujacy(nazwa="Patryk")
    firma_1 = Firma(nazwa="Polgam")

    sklep1 = Sklep(nazwa="Allegro")

    kategoria_1 = Kategoria(nazwa = 'narzędzia')
    typ_1 = Typ(nazwa = 'pendzel', kategoria = kategoria_1)
    art_1 = Artykul_Lista(typ=typ_1, firma=firma_1, artykul="Klej")

    zamow_1 = Zamowienie(kupujacy=kupujacy_1, sklep=sklep1)
    art_ilosc_1 = Artykul_Dodawanie(zamowienia=zamow_1, art_lista=art_1, cena_jednostkowa=1234)

    session.add_all([art_ilosc_1])
    session.commit()

if __name__ == "__main__":
    # Połączenie z bazą danych (przekaż odpowiednią ścieżkę)
    dsc = os.path.dirname(__file__) # lub inna ścieżka
    session = SQLconnect(dsc)