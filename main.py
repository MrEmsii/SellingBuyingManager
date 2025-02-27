import os, shutil
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, PhotoImage, Listbox
from tkinterdnd2 import DND_FILES, TkinterDnD
from dbControler import SQLconnect, select, Kupujacy, Kategoria, Sklep, Firma, Zamowienie, Artykul_Lista, artykuly_relacja

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
        self.buttom_frame = ttk.Frame(master, padding=5)

        self.main_frame = ttk.Frame(master, padding=5)

        self.start_frame()

        # Grid ustawienia
        self.buttom_frame.grid(row=0, column=0, rowspan=5, sticky="nsew", padx=5, pady=5)

        master.grid_rowconfigure(0, weight=2)
        master.grid_rowconfigure(1, weight=2)
        master.grid_rowconfigure(2, weight=2)
        master.grid_rowconfigure(3, weight=8)

        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=20)
        master.grid_columnconfigure(2, weight=20)
        master.grid_columnconfigure(3, weight=20)

    def start_frame(self):
        self.zamowienia_tree = self.create_zamowienie_tree(self.main_frame, 'Zamowienia') 
        self.buttons_main()
        self.load_zamowienia()
        
        self.zamowienia_tree.bind("<Double-1>", self.on_double_click)
        self.main_frame.grid(row=0, column=1, columnspan=3, rowspan=5, sticky="nsew", padx=5, pady=5, ipadx=5)

    def inside_frame(self, frame):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        for widget in self.buttom_frame.winfo_children():
            widget.destroy()
            
        if frame == "zamowienia":
            self.buttons_inside()
        elif frame == "kupujacy":
            self.button_add_kupujacy(self.buttom_frame)
        elif frame == "sklepy":
            self.button_add_sklep(self.buttom_frame) 
        elif frame == "artykuly":
            pass                       

        self.button_back(self.buttom_frame)
        self.main_frame.grid(row=0, column=1, columnspan=3, rowspan=5, sticky="nsew", padx=5, pady=5, ipadx=5)

    def backButton(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        for widget in self.buttom_frame.winfo_children():
            widget.destroy()

        self.start_frame()
        self.load_zamowienia()

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

        tree.column('artykul', width=100, anchor='e')
        tree.heading('artykul', text='Artykuł', anchor='e')        

        tree.column('Kolor', width=100, anchor='e')
        tree.heading('Kolor', text='Kolor', anchor='e')

        tree.column('szczegoly', width=100, anchor='e')
        tree.heading('szczegoly', text='Szczegoly', anchor='e')
       
        tree.pack(expand=True, fill='both')

        return tree       

    def create_name_tree(self, parent_frame, label_text, status):
        label = ttk.Label(parent_frame, text=label_text, font=("Arial", 12))
        label.pack(pady=5)

        tree = ttk.Treeview(parent_frame, columns=('id', 'name'), show='headings')
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

        for kategoria_id, kategoria_name in kategorie_data:
            self.kategorie_tree.insert('', 'end', values=(kategoria_id, kategoria_name))    

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
        self.inside_frame("zamowienia")
        self.inside_tree = self.create_inside_tree(self.main_frame, 'Zamowienia') 
        self.inside_tree.delete(*self.inside_tree.get_children())

        inside = self.db_session.query(Zamowienie).filter_by(id=id_zamowienia).first()

        for zamowienie in inside.artykuly:
            id_art = zamowienie.id
            ilosc = inside.get_ilosc_artykul(zamowienie, self.db_session)
            kategoria = zamowienie.kategoria.nazwa if zamowienie.kategoria else None
            firma = zamowienie.firma.nazwa if zamowienie.firma else None
            nazwa = zamowienie.artykul
            kolor = zamowienie.kolor
            szczegoly = zamowienie.szczegoly

            wynik = self.db_session.execute(
                select(artykuly_relacja.c.cena_jednostkowa)
                .where(
                    artykuly_relacja.c.zamowienie_id == id_zamowienia,
                    artykuly_relacja.c.artykul_id == id_art
                )
            ).fetchone()
            cena = f"{wynik[0] if wynik else 0:.2f} PLN" # Jeśli brak wyniku, domyślnie 0 
            
            self.inside_tree.insert('', 'end', values=(id_art, cena, ilosc, kategoria, firma, nazwa, kolor, szczegoly))

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



    def add_zamowienie_window(self):
        self.window = tk.Toplevel(self.master)
        self.window.geometry("900x700+0+0")
        self.background_label = tk.Label(self.window, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1) 
        
        self.buttom_frame_add_zamowienia = ttk.Frame(self.window, padding=(0,5))

        self.kupujacy_frame = ttk.Frame(self.window, padding=5)
        self.sklepy_frame = ttk.Frame(self.window, padding=5)

        self.kupujacy_tree = self.create_name_tree(self.kupujacy_frame, "Kupujący", True)
        self.sklepy_tree = self.create_name_tree(self.sklepy_frame, "Sklepy", True)

        self.buttons_add_zamowienia()
        self.load_kupujacy()
        self.load_sklepy()

        self.kupujacy_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5, ipadx=5)
        self.sklepy_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5, ipadx=5)
        self.buttom_frame_add_zamowienia.grid(row=0, column=0, rowspan=5, sticky="nsew",pady=5)


        self.window.grid_rowconfigure(0, weight=2)
        self.window.grid_rowconfigure(1, weight=2)

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=10)
        self.window.grid_columnconfigure(2, weight=10)

    def add_zamowienie(self):
        self.add_zamowienie_window()


    def add_artykul(self):
        artykul = simpledialog.askstring("Dodaj Kupującego", "Podaj nazwę KUPUJACEGO: \t\t\t")

        if artykul is not None:
            art_1 = Artykul_Lista(artykul=artykul, kategoria=kategoria_1, firma=firma_1)
            selected_kategoria = self.folder_tree.selection()[0]
            selected_firma = self.folder_tree.selection()[0]


            kupujacy = Kupujacy(nazwa=kupujacy_name)
            self.db_session.add(kupujacy)
            self.db_session.commit()
            
        self.load_kupujacy()    

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

    def mod_zamowienie(self):
        zamowienie_id = self.zamowienia_tree.item(self.zamowienia_tree.selection()[0], 'values')[0]
        obj = self.db_session.query(Zamowienie).filter_by(id=zamowienie_id).first()

    def delete_zamowienie(self):
        dialog = simpledialog.askstring("Usuń", "Czy jesteś pewien usunięcia projektu:\n\nCzynność NIE odwracalna\n\nNapisz YES lub TAK \t\t\t")
        if dialog == "YES" or dialog == "TAK" or dialog == "tak" or dialog == "yes":
            zamowienie_id = self.zamowienia_tree.item(self.zamowienia_tree.selection()[0], 'values')[0]
            obj = self.db_session.query(Zamowienie).filter_by(id=zamowienie_id).first()
            self.db_session.delete(obj)
            self.db_session.commit()

        self.load_zamowienia()

    def refresh(self):
        pass

    def list_sklepy(self):
        self.inside_frame("sklepy")
        self.sklepy_tree = self.create_name_tree(self.main_frame, "Sklepy", True)
        self.load_sklepy()

    def list_kupujacy(self):
        self.inside_frame("kupujacy")
        self.kupujacy_tree = self.create_name_tree(self.main_frame, "Kupujacy", True)
        self.load_kupujacy()

    def add_list_artykulow(self):
        self.list_artykulow()
        self.artykuly_tree.bind("<Double-1>", self.on_double_click_inside)

    def list_artykulow(self):
        self.inside_frame("artykuly")
        self.kategorie_tree = self.create_name_tree(self.main_frame, "Kategorie Lista", False)
        self.artykuly_tree = self.create_artykuly_tree(self.main_frame, "Artykuły Lista")
        self.load_kategorie()
        self.load_artykuly()


    def buttons_main(self):
        #tworzenie przycisków w głównym menu
        self.add_zamowienie_icon = PhotoImage(file=os.path.join(self.dsc, "image", "add_project_icon.png")).subsample(20, 20)
        self.edit_zamowienie_icon = PhotoImage(file=os.path.join(self.dsc, "image", "edit_project_icon.png")).subsample(20, 20)
        self.delete_zamowienie_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_project_icon.png")).subsample(20, 20)
        
        self.add_button = ttk.Button(self.buttom_frame, text="Dodaj\nzamowienie", command=self.add_zamowienie, width = 10, image=self.add_zamowienie_icon, compound="left",)
        self.add_button.pack(side='top', padx=1, pady=3)
        self.add_button = ttk.Button(self.buttom_frame, text="Edytuj\nzamowienie", command=self.mod_zamowienie, width = 10, image=self.edit_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)
        self.add_button = ttk.Button(self.buttom_frame, text="Usuń\nzamowienie", command=self.delete_zamowienie, width = 10, image=self.delete_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

        self.add_button = ttk.Button(self.buttom_frame, text="Lista\nartykułów", command=self.list_artykulow, width = 10, image=self.delete_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=(30,3))
        self.add_button = ttk.Button(self.buttom_frame, text="Lista\nsklepów", command=self.list_sklepy, width = 10, image=self.delete_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)
        self.add_button = ttk.Button(self.buttom_frame, text="Lista\nkupujacych", command=self.list_kupujacy, width = 10, image=self.delete_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

        self.button_refresh_zamowienia(self.buttom_frame)

    def buttons_inside(self):
        self.add_art_icon = PhotoImage(file=os.path.join(self.dsc, "image", "edit_project_icon.png")).subsample(20, 20)
        self.delete_zamowienie_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_project_icon.png")).subsample(20, 20)
        
        self.add_button = ttk.Button(self.buttom_frame, text="Dodaj\nartykuł do \nzamowienia", command=self.add_list_artykulow, width = 10, image=self.add_art_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)
        self.add_button = ttk.Button(self.buttom_frame, text="Usuń\nartykuł", command=self.refresh, width = 10, image=self.delete_zamowienie_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def buttons_add_zamowienia(self):
        self.add_zamowienie_inside_icon = PhotoImage(file=os.path.join(self.dsc, "image", "edit_project_icon.png")).subsample(20, 20)
        self.add_button = ttk.Button(self.buttom_frame_add_zamowienia, text="Zatwierdź", command=self.refresh, width = 10, image=self.add_zamowienie_inside_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

        self.button_add_kupujacy(self.buttom_frame_add_zamowienia)
        self.button_add_sklep(self.buttom_frame_add_zamowienia)
        # self.button_refresh() # do dodania

    def button_add_artykul(self, frame):
        self.add_art_icon = PhotoImage(file=os.path.join(self.dsc, "image", "edit_project_icon.png")).subsample(20, 20)
        self.add_button = ttk.Button(frame, text="Dodaj\nartykuł", command=self.refresh, width = 10, image=self.add_art_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)

    def button_back(self, frame):
        self.backButton_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_project_icon.png")).subsample(20, 20)
        self.add_button = ttk.Button(frame, text="Wróć", command=self.backButton, width = 10, image=self.backButton_icon, compound="left")
        self.add_button.pack(side='bottom', padx=1, pady=3) 

    def button_add_kupujacy(self, frame):
        self.dodaj_kupujacego_inside_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_project_icon.png")).subsample(20, 20)
        self.add_button = ttk.Button(frame, text="Dodaj\nkupującego", command=self.add_kupujacy, width = 10, image=self.dodaj_kupujacego_inside_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)        

    def button_add_sklep(self, frame):
        self.dodaj_sklep_inside_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_project_icon.png")).subsample(20, 20)
        self.add_button = ttk.Button(frame, text="Dodaj\nsklep", command=self.add_sklep, width = 10, image=self.dodaj_sklep_inside_icon, compound="left")
        self.add_button.pack(side='top', padx=1, pady=3)
        

    def button_refresh_zamowienia(self, frame):
        self.refresh_element_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_project_icon.png")).subsample(20, 20)
        self.add_button = ttk.Button(frame, text="Odśwież", command=self.load_zamowienia, width = 10, image=self.refresh_element_icon, compound="left")
        self.add_button.pack(side='bottom', padx=1, pady=3)

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Use TkinterDnD for DnD
    root.geometry("1280x720+0+0")
    app = FolderApp(root)
    root.mainloop()

