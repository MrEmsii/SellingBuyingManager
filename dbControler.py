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
    Column('artykul_id', Integer, ForeignKey('artykul_lista.id')),
    Column("cena_jednostkowa", Integer, server_default="0"),
    Column("ilosc_artykulu", Integer, server_default="1")
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

    art_lista = relationship('Artykul_Lista', back_populates='kategoria')
    
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
    
    artykuly = relationship('Artykul_Lista', secondary=artykuly_relacja, backref='zamowienia', cascade="all, delete")
    kupujacy = relationship('Kupujacy', back_populates='zamowienia')
    sklep = relationship('Sklep', back_populates='zamowienia')

    def oblicz_cene(self, session):
        result = session.execute(
            select(
                artykuly_relacja.c.cena_jednostkowa,
                artykuly_relacja.c.ilosc_artykulu
            ).where(artykuly_relacja.c.zamowienie_id == self.id)
        ).fetchall()
        rabat_proc = 1 - self.rabat_procent/100 if self.rabat_procent else 1
        return sum(cena* ilosc for cena, ilosc in result)* rabat_proc  - self.rabat_j

    def get_ilosc_artykul(self, artykul, session):
        # Pobiera ilość danego elementu w projekcie
        wynik = self._get_zamowienie_artykul_miejsce(artykul, session)
        return wynik[3] if wynik else 1

    def _get_zamowienie_artykul_miejsce(self, artykul, session):
        stmt = select(artykuly_relacja).where(artykuly_relacja.c.zamowienie_id == self.id, artykuly_relacja.c.artykul_id == artykul.id) # Tworzenie zapytania select
        wynik = session.execute(stmt).fetchone()
        return wynik

class Artykul_Lista(Base):
    __tablename__ = 'artykul_lista'
    id = Column(Integer, primary_key=True)
    kategoria_id = Column(Integer, ForeignKey('kategoria.id'))
    firma_id = Column(Integer, ForeignKey('firma.id'), default=None)
    artykul = Column(String)
    kolor = Column(String, default=None)
    szczegoly = Column(String, default=None)

    kategoria = relationship('Kategoria', back_populates='art_lista')
    firma = relationship('Firma', back_populates='art_lista')

def SQLconnect(dsc):
    db_path = os.path.join(dsc, '3DSBM.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()

def Test(session):
    kupujacy_1 = Kupujacy(nazwa="F3irma")
    sklep1 = Sklep(nazwa="Te2mu")
    firma_1 = Firma(nazwa="Prusa4")
    kategoria_1 = Kategoria(nazwa="maszyny")
    art_1 = Artykul_Lista(artykul="Azbest", kategoria=kategoria_1)
    zamow_1 = Zamowienie(data=datetime.date(2022,6,18), kupujacy= kupujacy_1, sklep=sklep1)
    
    session.add_all([kupujacy_1, firma_1, sklep1, kategoria_1, art_1, zamow_1])
    session.commit() # Ważne!

    session.execute(artykuly_relacja.insert().values(
        zamowienie_id=zamow_1.id,
        artykul_id=art_1.id,
        cena_jednostkowa=21
    ))
    session.commit() # Ważne!

    print(f"Dodano artykuł {art_1.artykul} do zamówienia {zamow_1.id}")

if __name__ == "__main__":
    # Połączenie z bazą danych (przekaż odpowiednią ścieżkę)
    dsc = os.path.dirname(__file__) # lub inna ścieżka
    session = SQLconnect(dsc)

    Test(session) # Testowanie