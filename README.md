# SellingBuyingManager - System zarządzania zamówieniami

## Opis
SellingBuyingManager to system do zarządzania zamówieniami, kupującymi oraz produktami. Wykorzystuje SQLAlchemy do interakcji z bazą danych SQLite, a relacje między obiektami są zarządzane poprzez modele ORM.

## Funkcje
- Tworzenie kupujących, firm i sklepów
- Kategoryzacja artykułów na podstawie typów
- Powiązanie artykułów z firmami
- Tworzenie zamówień powiązanych ze sklepami i kupującymi
- Przechowywanie listy artykułów w zamówieniu wraz z ilością i ceną jednostkową

## Struktura bazy danych
Projekt wykorzystuje modele ORM:
- **Kupujacy** - Klient składający zamówienia
- **Firma** - Producent artykułów
- **Sklep** - Miejsce zakupu
- **Kategoria** - Klasyfikacja artykułów
- **Typ** - Podkategoria artykułów
- **Artykul_Lista** - Lista artykułów dostępnych do zamówienia
- **Zamowienie** - Zamówienie powiązane z kupującym i sklepem
- **Tabela pomocnicza `lista_dodanie`** - Przechowuje relacje artykułów do zamówień wraz z ceną jednostkową i ilością

## Instalacja i uruchomienie
1. **Klonowanie repozytorium**:
    ```sh
    git clone https://github.com/MrEmsii/SellingBuyingManager.git
    cd SellingBuyingManager
    ```

2. **Instalacja zależności**:
    ```sh
    pip install sqlalchemy
    ```

3. **Uruchomienie skryptu**:
    ```sh
    python main.py
    ```

## Jak dodać artykuł do zamówienia?
Aby dodać artykuł do zamówienia, wykonaj następujące kroki:

```python
def Test(session):
    kupujacy_1 = Kupujacy(nazwa="Patryk")
    firma_1 = Firma(nazwa="Polgam")
    sklep1 = Sklep(nazwa="Allegro")
    kategoria_1 = Kategoria(nazwa='narzędzia')
    typ_1 = Typ(nazwa='pendzel', kategoria=kategoria_1)
    art_1 = Artykul_Lista(typ=typ_1, firma=firma_1, artykul="Klej")
    zamow_1 = Zamowienie(kupujacy=kupujacy_1, sklep=sklep1)
    
    session.add_all([kupujacy_1, firma_1, sklep1, kategoria_1, typ_1, art_1, zamow_1])
    session.commit()

    session.execute(artykuly_relacja.insert().values(
        zamowienie_id=zamow_1.id,
        artykul_id=art_1.id,
        cena_jednostkowa=1234,
        ilosc_elem=2
    ))

    session.commit()
    print(f"Dodano artykuł {art_1.artykul} do zamówienia {zamow_1.id}")
```

## Autor
Projekt stworzony przez **MrEmsii**.

## Licencja
MIT License

