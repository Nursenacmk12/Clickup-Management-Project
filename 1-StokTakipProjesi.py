import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from decimal import Decimal

# SQL Server bağlantı bilgileri
SERVER = 'NURSENA-LAPTOP\\Cicegim'
DATABASE = 'Db_Pastane'
DRIVER = 'ODBC Driver 17 for SQL Server'

def get_connection():
    """SQL Server'a bağlantı oluştur."""
    try:
        conn = pyodbc.connect(
            f'Driver={DRIVER};'
            f'Server={SERVER};'
            f'Database={DATABASE};'
            f'Trusted_Connection=yes;'
        )
        return conn
    except Exception as e:
        messagebox.showerror('Bağlantı Hatası', f'SQL Server bağlantısı başarısız:\n{e}')
        return None

def create_table():
    """Stoklar tablosunu oluştur."""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    try:
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Stoklar')
            CREATE TABLE [dbo].[Stoklar] (
                id INT PRIMARY KEY IDENTITY(1,1),
                urun_cinsi NVARCHAR(100) NOT NULL,
                kategori CHAR(1) NOT NULL CHECK (kategori IN ('A', 'B', 'C')),
                miktar_kg DECIMAL(10, 2) NOT NULL,
                gunluk_tuketim_kg DECIMAL(10, 2) NOT NULL,
                tedarik_suresi_gun INT NOT NULL,
                kritik_esik_kg DECIMAL(10, 2) NOT NULL,
                alis_tarihi DATETIME DEFAULT GETDATE()
            )
        ''')
        conn.commit()
    except Exception as e:
        pass
    finally:
        conn.close()

class StokTakipApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Stok Takip Sistemi')
        self.root.geometry('900x600')
        self.root.resizable(False, False)
        
        # Tablo oluştur
        create_table()
        
        # Sekme oluştur
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sekmeleri oluştur
        self.create_urun_ekle_tab()
        self.create_kullanim_tab()
        self.create_stok_listesi_tab()
    
    def create_urun_ekle_tab(self):
        """Ürün ekleme sekmesi."""
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text='➕ Ürün Ekle')
        
        # Ürün Adı
        ttk.Label(frame, text='Ürün Adı:', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=10)
        self.urun_entry = ttk.Entry(frame, width=30)
        self.urun_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Kategori
        ttk.Label(frame, text='Kategori (A/B/C):', font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=10)
        self.kategori_var = tk.StringVar(value='A')
        self.kategori_combo = ttk.Combobox(frame, textvariable=self.kategori_var, values=['A', 'B', 'C'], width=27, state='readonly')
        self.kategori_combo.grid(row=1, column=1, pady=10, padx=10)
        
        # İlk Miktar
        ttk.Label(frame, text='İlk Miktar (kg):', font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=10)
        self.miktar_entry = ttk.Entry(frame, width=30)
        self.miktar_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # Günlük Tüketim
        ttk.Label(frame, text='Günlük Tüketim (kg):', font=('Arial', 10)).grid(row=3, column=0, sticky='w', pady=10)
        self.tuketim_entry = ttk.Entry(frame, width=30)
        self.tuketim_entry.grid(row=3, column=1, pady=10, padx=10)
        
        # Tedarik Süresi
        ttk.Label(frame, text='Tedarik Süresi (gün):', font=('Arial', 10)).grid(row=4, column=0, sticky='w', pady=10)
        self.tedarik_entry = ttk.Entry(frame, width=30)
        self.tedarik_entry.grid(row=4, column=1, pady=10, padx=10)
        
        # Ekle Butonu
        ekle_btn = ttk.Button(frame, text='Ürün Ekle', command=self.urun_ekle)
        ekle_btn.grid(row=5, column=0, columnspan=2, pady=20, ipadx=50)
    
    def create_kullanim_tab(self):
        """Tüketim kaydı sekmesi."""
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text='📉 Tüketim Kaydı')
        
        # Ürün Adı
        ttk.Label(frame, text='Ürün Adı:', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=10)
        self.kullanim_urun_entry = ttk.Entry(frame, width=30)
        self.kullanim_urun_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Harcanan Miktar
        ttk.Label(frame, text='Harcanan Miktar (kg):', font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=10)
        self.harcanan_entry = ttk.Entry(frame, width=30)
        self.harcanan_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Tüketim Kaydı Butonu
        kaydet_btn = ttk.Button(frame, text='Tüketim Kaydet', command=self.kullanim_gir)
        kaydet_btn.grid(row=2, column=0, columnspan=2, pady=20, ipadx=50)
        
        # Sonuç göster
        ttk.Label(frame, text='Sonuç:', font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='nw', pady=10)
        self.sonuc_text = tk.Text(frame, height=10, width=50)
        self.sonuc_text.grid(row=4, column=0, columnspan=2, pady=10)
    
    def create_stok_listesi_tab(self):
        """Stok listeleme sekmesi."""
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text='📊 Stok Listesi')
        
        # Yenile Butonu
        yenile_btn = ttk.Button(frame, text='🔄 Yenile', command=self.listele_stok)
        yenile_btn.pack(pady=10)
        
        # Tablo
        self.tree = ttk.Treeview(frame, columns=('ID', 'Ürün', 'Miktar', 'Kategori', 'Kritik Eşik'), height=15)
        self.tree.column('#0', width=0, stretch='no')
        self.tree.column('ID', anchor='center', width=40)
        self.tree.column('Ürün', anchor='w', width=200)
        self.tree.column('Miktar', anchor='center', width=100)
        self.tree.column('Kategori', anchor='center', width=80)
        self.tree.column('Kritik Eşik', anchor='center', width=120)
        
        self.tree.heading('#0', text='', anchor='w')
        self.tree.heading('ID', text='ID', anchor='center')
        self.tree.heading('Ürün', text='Ürün Adı', anchor='w')
        self.tree.heading('Miktar', text='Miktar (kg)', anchor='center')
        self.tree.heading('Kategori', text='Kategori', anchor='center')
        self.tree.heading('Kritik Eşik', text='Kritik Eşik (kg)', anchor='center')
        
        self.tree.pack(fill='both', expand=True)
        
        # Başlangıçta stok listele
        self.listele_stok()
    
    def urun_ekle(self):
        """Ürün ekle."""
        try:
            urun_cinsi = self.urun_entry.get().strip()
            kategori = self.kategori_var.get()
            ilk_miktar = Decimal(self.miktar_entry.get())
            gunluk_tuketim = Decimal(self.tuketim_entry.get())
            tedarik_suresi = int(self.tedarik_entry.get())
            
            if not urun_cinsi:
                messagebox.showwarning('Uyarı', 'Ürün adı boş olamaz!')
                return
            
            # Güvenlik marjı hesapla (Düzeltilen kısım)
            if kategori == 'A':
                guvenlik_marji = Decimal('0.20')
            elif kategori == 'B':
                guvenlik_marji = Decimal('0.10')
            else:
                guvenlik_marji = Decimal('0.05')
            
            kritik_esik = (gunluk_tuketim * tedarik_suresi) + (ilk_miktar * guvenlik_marji)
            
            conn = get_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO [dbo].[Stoklar] (urun_cinsi, kategori, miktar_kg, gunluk_tuketim_kg, tedarik_suresi_gun, kritik_esik_kg)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (urun_cinsi, kategori, ilk_miktar, gunluk_tuketim, tedarik_suresi, kritik_esik))
            conn.commit()
            conn.close()
            
            messagebox.showinfo('Başarılı', f'✓ {urun_cinsi} başarıyla eklendi!\nKritik Eşik: {kritik_esik:.2f} kg')
            
            # Formu temizle
            self.urun_entry.delete(0, 'end')
            self.miktar_entry.delete(0, 'end')
            self.tuketim_entry.delete(0, 'end')
            self.tedarik_entry.delete(0, 'end')
            
        except ValueError:
            messagebox.showerror('Hata', 'Lütfen sayısal değerleri doğru giriniz!')
        except Exception as e:
            messagebox.showerror('Hata', f'Ürün ekleme hatası:\n{e}')
    
    def kullanim_gir(self):
        """Tüketim kaydet."""
        try:
            urun_cinsi = self.kullanim_urun_entry.get().strip()
            harcanan_kg = Decimal(self.harcanan_entry.get())
            
            if not urun_cinsi:
                messagebox.showwarning('Uyarı', 'Ürün adı boş olamaz!')
                return
            
            conn = get_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, kritik_esik_kg, miktar_kg FROM [dbo].[Stoklar] WHERE urun_cinsi = ?
            ''', (urun_cinsi,))
            row = cursor.fetchone()
            
            if not row:
                messagebox.showerror('Hata', f'Ürün bulunamadı: {urun_cinsi}')
                conn.close()
                return
            
            product_id, critical_threshold, current_quantity = row
            new_quantity = current_quantity - harcanan_kg
            
            cursor.execute('''
                UPDATE [dbo].[Stoklar] SET miktar_kg = ? WHERE id = ?
            ''', (new_quantity, product_id))
            conn.commit()
            conn.close()
            
            # Sonuç göster
            self.sonuc_text.delete('1.0', 'end')
            sonuc = f'✓ Kullanım Kaydedildi!\n\n'
            sonuc += f'Ürün: {urun_cinsi}\n'
            sonuc += f'Harcanan Miktar: {float(harcanan_kg)} kg\n'
            sonuc += f'Yeni Stok: {float(new_quantity):.2f} kg\n'
            sonuc += f'Kritik Eşik: {float(critical_threshold):.2f} kg\n'
            
            if new_quantity <= critical_threshold:
                sonuc += f'\n⚠ DİKKAT: STOK YENİLENMESİ GEREKLİ!'
                self.sonuc_text.insert('end', sonuc)
                self.sonuc_text.tag_configure('warning', foreground='red', font=('Arial', 10, 'bold'))
                self.sonuc_text.tag_add('warning', '4.0', '4.end')
            else:
                self.sonuc_text.insert('end', sonuc)
            
            # Listeyi yenile
            self.listele_stok()
            
            # Formu temizle
            self.kullanim_urun_entry.delete(0, 'end')
            self.harcanan_entry.delete(0, 'end')
            
        except ValueError:
            messagebox.showerror('Hata', 'Lütfen sayısal değeri doğru giriniz!')
        except Exception as e:
            messagebox.showerror('Hata', f'Tüketim kaydı hatası:\n{e}')
    
    def listele_stok(self):
        """Stok listesini göster."""
        try:
            # Eski verileri temizle
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            conn = get_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, urun_cinsi, miktar_kg, kategori, kritik_esik_kg FROM [dbo].[Stoklar]
            ''')
            rows = cursor.fetchall()
            conn.close()
            
            # Verileri ekle
            for row in rows:
                values = (row[0], row[1], f'{float(row[2]):.2f}', row[3], f'{float(row[4]):.2f}')
                self.tree.insert('', 'end', values=values)
        
        except Exception as e:
            messagebox.showerror('Hata', f'Stok listeleme hatası:\n{e}')

if __name__ == '__main__':
    root = tk.Tk()
    app = StokTakipApp(root)
    root.mainloop()