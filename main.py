import os, shutil
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, PhotoImage, Listbox
from tkinterdnd2 import DND_FILES, TkinterDnD
from dbControler import SQLconnect, select, Kupujacy, Kategoria, Sklep, Firma, Zamowienie, Artykul_Lista, artykuly_relacja
from tkcalendar import DateEntry
import datetime as datetime


class FolderApp:
    def __init__(self, master):
        self.master = master
        self.dsc = os.path.dirname(__file__)
        self.style = ttk.Style()
        master.tk.call('source', self.dsc + '/themes/awdark.tcl')

        self.style.theme_use("awdark")  # Use a modern theme
        self.style.configure("Treeview", background="#D8E8E8", foreground="black", rowheight=15, fieldbackground="#E8E8E8", font=('Arial', 8))
        self.style.map("Treeview", background=[('selected', '#347083')], foreground=[('selected', 'white')])

        master.title("Selling/Buying Manager")
        master.iconbitmap(os.path.join(self.dsc, "image", "icon.ico"))

        self.style.configure('TButton', justify="left", anchor='w')
        self.background_image = PhotoImage(file=os.path.join(self.dsc, "image", "background.png"))
        self.background_label = tk.Label(master, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1) 

        # Połączenie z bazą danych
        self.db_session = SQLconnect(self.dsc)

        # Tworzenie okienka dla listy przycisków
        self.button_frame = ttk.Frame(master, padding=5)

        self.main_frame = ttk.Frame(master, padding=5)

        self.button_icon_pack()
        self.start_frame()

        # Grid ustawienia
        self.button_frame.grid(row=0, column=0, rowspan=5, sticky="nsew", padx=5, pady=5)

        master.grid_rowconfigure(0, weight=2)
        master.grid_rowconfigure(1, weight=4)
        master.grid_rowconfigure(2, weight=400)
        master.grid_rowconfigure(3, weight=4)

        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=20)
        master.grid_columnconfigure(2, weight=20)
        master.grid_columnconfigure(3, weight=20)

    def start_frame(self):
        self.secend_frame = ttk.Frame(self.master, padding=5)
        self.third_frame = ttk.Frame(self.master, padding=5)
        self.zamowienia_tree = self.create_zamowienie_tree(self.main_frame, 'Zamówienia') 
        self.inside_frame(frame="main", startup=True)
        self.load_zamowienia()
        
        self.zamowienia_tree.bind("<Double-1>", self.on_double_click)
        self.main_frame.grid(row=0, column=1, columnspan=3, rowspan=5, sticky="nsew", padx=5, pady=5, ipadx=5)

    def inside_frame(self, frame, commend = 'main', startup = False):
        if startup == False:
            for widget in self.main_frame.winfo_children():
                widget.destroy()

            for widget in self.button_frame.winfo_children():
                widget.destroy()
        
        if frame == "main":
            self.button_dodaj_zamowienie(self.button_frame)
            self.button_modyfikuj_zamowienie(self.button_frame)
            self.button_usun_zamowienie(self.button_frame)
            self.button_lista_artykulow(self.button_frame)
            self.button_lista_sklepow(self.button_frame)
            self.button_lista_kupujacych(self.button_frame)
            self.button_refresh_zamowienia(self.button_frame)   

        elif frame == "lista dodanych do zamowienia":
            self.button_dodaj_artykul_zamowienie(self.button_frame)
            self.button_usun_artykul_zamowienie(self.button_frame)

        elif frame == "kupujacy":
            self.button_dodaj_kupujacy(self.button_frame)

        elif frame == "sklepy":
            self.button_dodaj_sklep(self.button_frame) 

        elif frame == "artykuly":
            self.button_create_artykul(self.button_frame) 

        elif frame == "add_zamowienie":
            self.buttons_zatwierdz_zamowienia(self.button_frame) 

        elif frame == 'tworzenie_artykuly':
            self.button_dodaj_kategoria(self.button_frame) 
            self.button_dodaj_firma(self.button_frame)
            commend = 'lista_artykułów' 

        if frame != 'main':
            self.button_back_pack(self.button_frame, commend)
        self.main_frame.grid(row=0, column=1, columnspan=3, rowspan=5, sticky="nsew", padx=5, pady=5, ipadx=5)


    def create_inside_tree(self, parent_frame, label_text):
        label = ttk.Label(parent_frame, text=label_text, font=("Arial", 12))
        label.pack(pady=5)

        tree = ttk.Treeview(parent_frame, columns=("id_artykul", 'Cena', 'Ilosc', "Kategoria", 'Marka', 'Artykul', 'Kolor', 'Szczegoly'), show='headings')

        tree.column('id_artykul', width=50, anchor='e')
        tree.heading('id_artykul', text='ID', anchor='center')

        tree.column('Cena', width=100, anchor='e')
        tree.heading('Cena', text='Cena', anchor='center')

        tree.column('Ilosc', width=100, anchor='e')
        tree.heading('Ilosc', text='Ilosc', anchor='center')

        tree.column('Kategoria', width=100, anchor='e')
        tree.heading('Kategoria', text='Kategoria', anchor='center')

        tree.column('Marka', width=100, anchor='e')
        tree.heading('Marka', text='Marka', anchor='center')

        tree.column('Artykul', width=100, anchor='e')
        tree.heading('Artykul', text='Artykul', anchor='center')     

        tree.column('Kolor', width=100, anchor='e')
        tree.heading('Kolor', text='Kolor', anchor='center')   

        tree.column('Szczegoly', width=300, anchor='e')
        tree.heading('Szczegoly', text='Szczegoly', anchor='center')

        tree.pack(expand=True, fill='both')

        return tree  

    def create_artykuly_tree(self, parent_frame, label_text):
        label = ttk.Label(parent_frame, text=label_text, font=("Arial", 12))
        tree = ttk.Treeview(parent_frame, columns=("id", 'Kategoria', 'Firma', 'artykul','Kolor','szczegoly'), show='headings')
        label.pack(pady=5)

        tree.column('id', width=50, anchor='e')
        tree.heading('id', text='id_artykułu', anchor='e')

        tree.column('Kategoria', width=100, anchor='w')
        tree.heading('Kategoria', text='Kategoria', anchor='w')

        tree.column('Firma', width=100, anchor='w')
        tree.heading('Firma', text='Firma', anchor='w')

        tree.column('artykul', width=100, anchor='w')
        tree.heading('artykul', text='Artykuł', anchor='w')        

        tree.column('Kolor', width=100, anchor='w')
        tree.heading('Kolor', text='Kolor', anchor='w')

        tree.column('szczegoly', width=100, anchor='w')
        tree.heading('szczegoly', text='Szczegoly', anchor='w')
       
        tree.pack(expand=True, fill='both')

        return tree       

    def create_name_tree(self, parent_frame, label_text, status):
        label = ttk.Label(parent_frame, text=label_text, font=("Arial", 12))
        label.pack(pady=5)

        tree = ttk.Treeview(parent_frame, columns=('id', 'name'), show='headings', height=10)
        tree.column('id', width=30, anchor='e')
        tree.heading('id', text='ID', anchor='e')

        tree.column('name', width=200, anchor='w')
        tree.heading('name', text='Nazwa', anchor='w')
        tree.pack(expand=status, fill='both')

        return tree  

    def create_zamowienie_tree(self, parent_frame, label_text):
        label = ttk.Label(parent_frame, text=label_text, font=("Arial", 12))
        tree = ttk.Treeview(parent_frame, columns=("id_zamowiania", 'Data', 'Kupujacy', 'Sklep','Rabat jednostkowy','Rabat procentowy', 'Cena', "Cena_po_rabacie"), show='headings')
        label.pack(pady=5)

        tree.column('id_zamowiania', width=50, anchor='e')
        tree.heading('id_zamowiania', text='id_zamowiania', anchor='e')

        tree.column('Data', width=100, anchor='w')
        tree.heading('Data', text='Data', anchor='w')

        tree.column('Kupujacy', width=100, anchor='w')
        tree.heading('Kupujacy', text='Kupujacy', anchor='w')

        tree.column('Sklep', width=100, anchor='w')
        tree.heading('Sklep', text='Sklep', anchor='w')

        tree.column('Rabat jednostkowy', width=100, anchor='e')
        tree.heading('Rabat jednostkowy', text='Rabat jednostkowy', anchor='e')        

        tree.column('Rabat procentowy', width=100, anchor='e')
        tree.heading('Rabat procentowy', text='Rabat procentowy', anchor='e')

        tree.column('Cena', width=100, anchor='e')
        tree.heading('Cena', text='Cena', anchor='e')

        tree.column('Cena_po_rabacie', width=100, anchor='e')
        tree.heading('Cena_po_rabacie', text='Cena po rabacie', anchor='e')
        
        tree.pack(expand=True, fill='both')

        return tree  

    def load_zamowienia(self):
        zamowienia = self.db_session.query(Zamowienie).all()
        zamowienia_data = []

        for zamow in zamowienia:
            zamow_id = zamow.id
            zamow_data = zamow.data
            zamow_kupujacy = zamow.kupujacy.nazwa if zamow.kupujacy else None
            zamow_sklep = zamow.sklep.nazwa if zamow.sklep else None
            rabat_j = f"{zamow.rabat_j:.2f} PLN"
            rabat_proc = f"{zamow.rabat_procent :.0f} %"
            zamow_cena = f"{zamow.oblicz_cene(self.db_session):,.2f} PLN".replace(",", " ")
            zamow_cena_rabat = f"{zamow.oblicz_cene_rabat(self.db_session):,.2f} PLN".replace(",", " ")
            zamowienia_data.append((zamow_id, zamow_data, zamow_kupujacy, zamow_sklep, rabat_j, rabat_proc, zamow_cena, zamow_cena_rabat))

        zamowienia_data.sort(key=lambda x:x[0], reverse=True)
        zamowienia_data.sort(key=lambda x:x[1], reverse=True)
        self.zamowienia_tree.delete(*self.zamowienia_tree.get_children())

        for z_id, data, kupujacy, sklep, rabat_1, rabat_2, cena, cena_rabat in zamowienia_data:
            self.zamowienia_tree.insert('', 'end', values=(z_id, data, kupujacy, sklep, rabat_1, rabat_2, cena, cena_rabat))


    def load_sklepy(self):
        sklepy = self.db_session.query(Sklep).all()
        sklepy_data = []

        for sklep in sklepy:
            sklep_id = sklep.id
            sklep_nazwa = sklep.nazwa
            sklepy_data.append((sklep_id, sklep_nazwa))

        self.sklepy_tree.delete(*self.sklepy_tree.get_children())
        sklepy_data.sort(key=lambda x:x[1])


        for sklep_id, sklep_nazwa in sklepy_data:
            self.sklepy_tree.insert('', 'end', values=(sklep_id, sklep_nazwa))
     

    def load_kupujacy(self):
        kupujacy = self.db_session.query(Kupujacy).all()
        kupujacy_data = []

        for kup in kupujacy:
            kup_id = kup.id
            kup_nazwa = kup.nazwa
            kupujacy_data.append((kup_id, kup_nazwa))

        self.kupujacy_tree.delete(*self.kupujacy_tree.get_children())
        kupujacy_data.sort(key=lambda x:x[1])


        for kup_id, kup_nazwa in kupujacy_data:
            self.kupujacy_tree.insert('', 'end', values=(kup_id, kup_nazwa))

    def load_kategorie(self):
        kategorie = self.db_session.query(Kategoria).all()
        kategorie_data = []

        for kategoria in kategorie:
            kategoria_id = kategoria.id
            kategoria_name = kategoria.nazwa
            kategorie_data.append((kategoria_id, kategoria_name))

        self.kategorie_tree.delete(*self.kategorie_tree.get_children())
        kategorie_data.sort(key=lambda x:x[1])


        for kategoria_id, kategoria_name in kategorie_data:
            self.kategorie_tree.insert('', 'end', values=(kategoria_id, kategoria_name))    

    def load_firmy(self):
        firmy = self.db_session.query(Firma).all()
        firmy_data = []

        for firma in firmy:
            firma_id = firma.id
            firma_name = firma.nazwa
            firmy_data.append((firma_id, firma_name))

        self.firmy_tree.delete(*self.firmy_tree.get_children())

        for firma_id, firma_name in firmy_data:
            self.firmy_tree.insert('', 'end', values=(firma_id, firma_name))  
            
    def load_artykuly(self):
        artykuly = self.db_session.query(Artykul_Lista).all()
        artykuly_data = []

        for art in artykuly:
            art_id = art.id
            art_kategoria = art.kategoria.nazwa if art.kategoria else None
            art_firma = art.firma.nazwa if art.firma else None
            art_nazwa = art.artykul
            art_kolor = art.kolor
            art_szczegoly = art.szczegoly
            artykuly_data.append((art_id, art_kategoria, art_firma, art_nazwa, art_kolor, art_szczegoly))

        self.artykuly_tree.delete(*self.artykuly_tree.get_children())

        for id, kategoria, firma, nazwa, kolor, szczegoly in artykuly_data:
            self.artykuly_tree.insert('', 'end', values=(id, kategoria, firma, nazwa, kolor, szczegoly))


    def load_inside_zamowienie(self, id_zamowienia):
        self.delete_all_widgets()
        self.inside_frame("lista dodanych do zamowienia")
        self.inside_tree = self.create_inside_tree(self.main_frame, 'Lista artykułów dodatych do zamówienia') 
        self.inside_tree.delete(*self.inside_tree.get_children())

        wynik_all = self.db_session.execute(
            select(
                artykuly_relacja.c.artykul_id,
                artykuly_relacja.c.cena_jednostkowa,
                artykuly_relacja.c.ilosc_artykulu
            ).where(artykuly_relacja.c.zamowienie_id == id_zamowienia)
        ).fetchall()

        existing_iids = set(self.inside_tree.get_children())

        artykul_data = []

        for wynik in wynik_all:
            id_art = wynik.artykul_id
            cena = f"{wynik.cena_jednostkowa if wynik.cena_jednostkowa else 0:.2f} PLN"
            ilosc = wynik.ilosc_artykulu if wynik.ilosc_artykulu else 1

            artykul = self.db_session.query(Artykul_Lista).filter_by(id=id_art).first()
            kategoria = artykul.kategoria.nazwa if artykul.kategoria else None
            firma = artykul.firma.nazwa if artykul.firma else None
            nazwa = artykul.artykul
            kolor = artykul.kolor
            szczegoly = artykul.szczegoly

            unique_id = f"{id_art}-{ilosc}"
            counter = 1
            while unique_id in existing_iids:
                unique_id = f"{id_art}-{ilosc}-{counter}"
                counter += 1

            existing_iids.add(unique_id)
            artykul_data.append((unique_id, id_art, cena, ilosc, kategoria, firma, nazwa, kolor, szczegoly))

        artykul_data.sort(key=lambda x: x[6].lower())
        for row in artykul_data:
            self.inside_tree.insert('', 'end', iid=row[0], values=row[1:])

    def on_double_click(self, event):
        """Handle double-click event on a project folder."""
        selected_item = self.zamowienia_tree.selection()
        self.zamowienie_id = selected_item

        if selected_item:
            self.zamowienie_id = self.zamowienia_tree.item(selected_item[0], 'values')[0]
            self.load_inside_zamowienie(self.zamowienie_id)

    def on_double_click_inside(self, event):
        """Handle double-click event on a project folder."""
        selected_item = self.artykuly_tree.selection()

        if selected_item:
            artykul_id = self.artykuly_tree.item(selected_item[0], 'values')[0]
            self.add_artykul_do_zamowienie(self.zamowienie_id, artykul_id)
            self.load_inside_zamowienie(self.zamowienie_id)

    def add_zamowienie(self):
        self.secend_frame = ttk.Frame(self.master, padding=5)
        self.third_frame = ttk.Frame(self.master, padding=5)

        self.inside_frame("add_zamowienie")

        self.main_frame.grid(row=0, column=1, columnspan=2, rowspan=1, sticky="nsew", padx=5, pady=5, ipadx=5)
        self.secend_frame.grid(row=1, column=1, columnspan=2, rowspan=3, sticky="nsew", padx=5, pady=5, ipadx=5)
        self.third_frame.grid(row=0, column=3, columnspan=1, rowspan=4, sticky="nsew", padx=5, pady=5, ipadx=5)
                
        self.kupujacy_tree = self.create_name_tree(self.main_frame, "Kupujacy", False)
        self.sklepy_tree = self.create_name_tree(self.secend_frame, "Sklepy", True)
        
        self.load_kupujacy()
        self.load_sklepy()

        date_label = ttk.Label(self.third_frame, text = 'Data:', font=('calibre', 10, 'bold'), anchor='w')
       
        rabat_j_label = ttk.Label(self.third_frame, text = 'Rabat jednostkowy:', font=('calibre', 10, 'bold'), anchor='w')
        rabat_p_label = ttk.Label(self.third_frame, text = 'Rabat procentowy:', font=('calibre',10, 'bold'), anchor='w')

        self.rabat_j_var = tk.DoubleVar()
        self.rabat_p_var = tk.DoubleVar()

        rabat_j_entry = ttk.Entry(self.third_frame, textvariable = self.rabat_j_var, font=('calibre',10,'normal'), width=10)
        rabat_p_entry = ttk.Entry(self.third_frame, textvariable = self.rabat_p_var, font=('calibre',10,'normal'), width=10)

        self.date = tk.StringVar()
        date_entry = DateEntry(self.third_frame, localestr='pl_PL', date_pattern="yyyy-mm-dd", textvariable=self.date)

        
        self.third_frame.grid_rowconfigure(0, weight=400)
        self.third_frame.grid_rowconfigure(1, weight=1)
        self.third_frame.grid_rowconfigure(2, weight=1)
        self.third_frame.grid_rowconfigure(3, weight=1)
        self.third_frame.grid_rowconfigure(4, weight=400)

        self.third_frame.grid_columnconfigure(0, weight=1)
        self.third_frame.grid_columnconfigure(1, weight=10)


        date_label.grid(row=1,column=0)
        date_entry.grid(row=1,column=1)

        rabat_j_label.grid(row=2,column=0)
        rabat_j_entry.grid(row=2,column=1)
        rabat_p_label.grid(row=3,column=0)
        rabat_p_entry.grid(row=3,column=1)

    def konwersja_string_do_data(self, date):
        format = "%Y-%m-%d"
        date = datetime.datetime.strptime(date, format).date()
        return date

    def zatwierdz_zamowienie(self):
        selected_item = self.kupujacy_tree.selection()
        if not selected_item:
            messagebox.showerror("Błąd", "Brak wybranego kupującego! Wybierz kupującego.")
            return
        
        selected_item = self.sklepy_tree.selection()
        if not selected_item:
            messagebox.showerror("Błąd", "Brak wybranego sklepu! Wybierz sklep.")
            return

        try:
            rabat_j = self.rabat_j_var.get()
        except tk.TclError:
            messagebox.showerror("Błąd", "Nieprawidłowa wartość rabatu! Wpisz liczbę.")
            return

        try:
            rabat_procentowy = self.rabat_p_var.get()
        except tk.TclError:
            messagebox.showerror("Błąd", "Nieprawidłowa wartość rabatu! Wpisz liczbę.")
            return
        
        kupujacy_id = int(self.kupujacy_tree.item(self.kupujacy_tree.selection()[0], 'values')[0])
        sklep_id = int(self.sklepy_tree.item(self.sklepy_tree.selection()[0], 'values')[0])
        data = self.konwersja_string_do_data(self.date.get())
        

        zamowienie = Zamowienie(data=data, kupujacy_id=kupujacy_id, sklep_id=sklep_id, rabat_j=rabat_j, rabat_procent=rabat_procentowy)
        
        self.db_session.add(zamowienie)
        self.db_session.commit()

        self.powrot_do_glownego_okna()

    def mod_zamowienie(self):
        zamowienie_id = self.zamowienia_tree.item(self.zamowienia_tree.selection()[0], 'values')[0]
        obj = self.db_session.query(Zamowienie).filter_by(id=zamowienie_id).first()

    def delete_zamowienie(self):
        selected_item = self.zamowienia_tree.selection()
        if not selected_item:
            return
        
        dialog = simpledialog.askstring("Usuń", "Czy jesteś pewien usunięcia projektu:\n\nCzynność NIE odwracalna\n\nNapisz YES lub TAK \t\t\t")
        if dialog == "YES" or dialog == "TAK" or dialog == "tak" or dialog == "yes":
            zamowienie_id = self.zamowienia_tree.item(self.zamowienia_tree.selection()[0], 'values')[0]
            obj = self.db_session.query(Zamowienie).filter_by(id=zamowienie_id).first()
            self.db_session.delete(obj)
            self.db_session.commit()

    def del_artykul_do_zamowienie(self):
        selected_item = self.inside_tree.selection()
        if not selected_item:
            return
        
        relacja_name = self.inside_tree.item(self.inside_tree.selection()[0], 'values')
        dialog = simpledialog.askstring("Usuń folder", "Czy jesteś pewien usunięcia projektu:\n\nCzynność NIE odwracalna\n\nNapisz YES lub TAK \t\t\t")
        if dialog == "YES" or dialog == "TAK" or dialog == "tak" or dialog == "yes":
            self.db_session.execute(
                artykuly_relacja.delete()
                .where(artykuly_relacja.c.zamowienie_id == self.zamowienie_id,
                artykuly_relacja.c.artykul_id == relacja_name[0],
                artykuly_relacja.c.ilosc_artykulu == relacja_name[2]
                )
            )
            self.db_session.commit()
            self.load_inside_zamowienie(self.zamowienie_id)

        self.load_zamowienia()

    def create_artykul(self):
        self.delete_all_widgets()
        self.secend_frame = ttk.Frame(self.master, padding=5)
        self.third_frame = ttk.Frame(self.master, padding=5)

        self.inside_frame("tworzenie_artykuly")
        self.main_frame.grid(row=0, column=1, columnspan=2, rowspan=2, sticky="nsew", padx=5, pady=5, ipadx=5)
        self.secend_frame.grid(row=2, column=1, columnspan=2, rowspan=2, sticky="nsew", padx=5, pady=5, ipadx=5)
        self.third_frame.grid(row=0, column=3, columnspan=1, rowspan=2, sticky="nsew", padx=5, pady=5, ipadx=5)
        
        self.firmy_tree = self.create_name_tree(self.main_frame, "Lista Firm", True)
        self.kategorie_tree = self.create_name_tree(self.secend_frame, "Kategorie Lista", True)
        self.artykuly_tree = self.create_name_tree(self.third_frame, "Kategorie Lista", True)
        
        self.load_kategorie()
        self.load_firmy()


    def add_artykul_do_zamowienie(self, zamowienie, id_art):
        self.db_session.execute(artykuly_relacja.insert().values(
            zamowienie_id = zamowienie,
            artykul_id = id_art,
            cena_jednostkowa=21

        ))
        self.db_session.commit()

    def add_kupujacy(self):
        kupujacy_name = simpledialog.askstring("Dodaj Kupującego", "Podaj nazwę KUPUJACEGO: \t\t\t")
        if kupujacy_name is not None:
            kupujacy = Kupujacy(nazwa=kupujacy_name)
            self.db_session.add(kupujacy)
            self.db_session.commit()
        self.load_kupujacy()    

    def add_sklep(self):
        sklep_name = simpledialog.askstring("Dodaj Sklep", "Podaj nazwę SKLEPU: \t\t\t")
        if sklep_name is not None:
            sklep = Sklep(nazwa=sklep_name)
            self.db_session.add(sklep)
            self.db_session.commit()
        self.load_sklepy()    

    def add_firma(self):
        firma_name = simpledialog.askstring("Dodaj firme", "Podaj nazwę FIRMY: \t\t\t")
        if firma_name is not None:
            firma = Firma(nazwa=firma_name)
            self.db_session.add(firma)
            self.db_session.commit()
        self.load_firmy()    

    def add_kategoria(self):
        kategoria_name = simpledialog.askstring("Dodaj kategorie", "Podaj nazwę KATEGORII: \t\t\t")
        if kategoria_name is not None:
            kategoria = Kategoria(nazwa=kategoria_name)
            self.db_session.add(kategoria)
            self.db_session.commit()
        self.load_kategorie()    

    def add_list_artykulow(self):
        self.list_artykulow()
        self.artykuly_tree.bind("<Double-1>", self.on_double_click_inside)

    def list_kupujacy(self):
        self.inside_frame("kupujacy")
        self.kupujacy_tree = self.create_name_tree(self.main_frame, "Kupujacy", True)
        self.load_kupujacy()

    def list_firmy(self):
        self.inside_frame("firmy")
        self.firmy_tree = self.create_name_tree(self.main_frame, "Kupujacy", True)
        self.load_kupujacy()

    def list_sklepy(self):
        self.inside_frame("sklepy")
        self.sklepy_tree = self.create_name_tree(self.main_frame, "Sklepy", True)
        self.load_sklepy()

    def list_artykulow(self):
        self.secend_frame = ttk.Frame(self.master, padding=5)

        self.inside_frame("artykuly")
        self.main_frame.grid(row=0, column=1, columnspan=1, rowspan=5, sticky="nsew", padx=5, pady=5, ipadx=5)
        self.secend_frame.grid(row=0, column=2, columnspan=2, rowspan=5, sticky="nsew", padx=5, pady=5, ipadx=5)
        
        self.kategorie_tree = self.create_name_tree(self.main_frame, "Kategorie Lista", True)
        self.artykuly_tree = self.create_artykuly_tree(self.secend_frame, "Artykuły Lista")
        self.load_kategorie()
        self.load_artykuly()

    def refresh(self):
        pass

    def delete_all_widgets(self):
        if self.secend_frame:
            self.secend_frame.destroy()

        if self.third_frame:
            self.third_frame.destroy()

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        for widget in self.button_frame.winfo_children():
            widget.destroy()

    def button_icon_pack(self):
        self.add_zamowienie_icon = PhotoImage(file=os.path.join(self.dsc, "image", "add_project_icon.png")).subsample(20, 20)
        self.edit_zamowienie_icon = PhotoImage(file=os.path.join(self.dsc, "image", "edit_project_icon.png")).subsample(20, 20)
        self.add_art_icon = PhotoImage(file=os.path.join(self.dsc, "image", "edit_project_icon.png")).subsample(20, 20)
        self.delete_zamowienie_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_project_icon.png")).subsample(20, 20)
        self.add_zamowienie_inside_icon = PhotoImage(file=os.path.join(self.dsc, "image", "edit_project_icon.png")).subsample(20, 20)
        self.backButton_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_project_icon.png")).subsample(20, 20)
        self.dodaj_kupujacego_inside_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_project_icon.png")).subsample(20, 20)
        self.dodaj_sklep_inside_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_project_icon.png")).subsample(20, 20)
        self.refresh_element_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_project_icon.png")).subsample(20, 20)

    def button_back_pack(self, frame, commend = "main"):
        if commend == "main":
            commend = self.powrot_do_glownego_okna
        elif commend == "lista_artykułów":
            commend = self.powrot_do_lista_artykulow

        self.add_button = ttk.Button(frame, text="Wróć", command=commend, width = 10, image=self.backButton_icon, compound="left")
        self.add_button.pack(side='bottom', padx=1, pady=3) 

    def powrot_do_glownego_okna(self):
        self.delete_all_widgets()

        self.start_frame()
        self.load_zamowienia()

    def powrot_do_lista_artykulow(self):
        self.delete_all_widgets()

        self.start_frame()
        self.list_artykulow()

    def button_dodaj_zamowienie(self, frame):
        self.add_button = ttk.Button(frame, text="Dodaj\nzamówienie", command=self.add_zamowienie, width = 10, image=self.add_zamowienie_icon, compound="left",)
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_modyfikuj_zamowienie(self, frame):
        self.add_button = ttk.Button(frame, text="Edytuj\nzamówienie", command=self.mod_zamowienie, width = 10, image=self.edit_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_usun_zamowienie(self, frame):
        self.add_button = ttk.Button(frame, text="Usuń\nzamówienie", command=self.delete_zamowienie, width = 10, image=self.delete_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)
        
    def buttons_zatwierdz_zamowienia(self, frame):
        self.add_button = ttk.Button(frame, text="Zatwierdź\nzamówienie", command=self.zatwierdz_zamowienie, width = 10, image=self.add_zamowienie_inside_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_lista_artykulow(self, frame):
        self.add_button = ttk.Button(frame, text="Lista\nartykułów", command=self.list_artykulow, width = 10, image=self.delete_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=(30,3))

    def button_lista_sklepow(self, frame):
        self.add_button = ttk.Button(frame, text="Lista\nsklepów", command=self.list_sklepy, width = 10, image=self.delete_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_lista_kupujacych(self, frame):
        self.add_button = ttk.Button(frame, text="Lista\nkupujących", command=self.list_kupujacy, width = 10, image=self.delete_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_create_artykul(self, frame):
        self.add_button = ttk.Button(frame, text="Stwórz\nartykuł", command=self.create_artykul, width = 10, image=self.add_art_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)       

    def button_dodaj_artykul_zamowienie(self, frame):
        self.add_button = ttk.Button(frame, text="Dodaj\nartykuł do\nzamowienia", command=self.add_list_artykulow, width = 10, image=self.add_art_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_usun_artykul_zamowienie(self, frame):
        self.add_button = ttk.Button(frame, text="Usuń\nartykuł z\nzamówienia", command=self.del_artykul_do_zamowienie, width = 10, image=self.delete_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_dodaj_kupujacy(self, frame):
        self.add_button = ttk.Button(frame, text="Dodaj\nkupującego", command=self.add_kupujacy, width = 10, image=self.dodaj_kupujacego_inside_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)        

    def button_usun_kupujacy(self, frame):
        self.add_button = ttk.Button(frame, text="Usuń\nkupującego", command=self.refresh, width = 10, image=self.dodaj_kupujacego_inside_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3) 

    def button_dodaj_sklep(self, frame):
        self.add_button = ttk.Button(frame, text="Dodaj\nsklep", command=self.add_sklep, width = 10, image=self.dodaj_sklep_inside_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_usun_sklep(self, frame):
        self.add_button = ttk.Button(frame, text="Usuń\nsklep", command=self.refresh, width = 10, image=self.dodaj_kupujacego_inside_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_dodaj_firma(self, frame):
        self.add_button = ttk.Button(frame, text="Dodaj\nfirma", command=self.add_firma, width = 10, image=self.add_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_dodaj_kategoria(self, frame):
        self.add_button = ttk.Button(frame, text="Dodaj\nkategoria", command=self.add_kategoria, width = 10, image=self.add_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_usun_kategorie(self, frame):
        self.add_button = ttk.Button(frame, text="Usuń\nkategorie", command=self.refresh, width = 10, image=self.dodaj_kupujacego_inside_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_refresh_zamowienia(self, frame):
        self.add_button = ttk.Button(frame, text="Odśwież", command=self.load_zamowienia, width = 10, image=self.refresh_element_icon, compound="left")
        self.add_button.pack(side='bottom', padx=1, pady=3)

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Use TkinterDnD for DnD
    root.geometry("1280x720+0+0")
    app = FolderApp(root)
    root.mainloop()

