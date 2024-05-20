import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import requests
from bs4 import BeautifulSoup
import csv
import re
import os
import io
from PIL import Image, ImageTk
import urllib.request


class HotelListingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Find the Best Hotel for You")
        self.root.geometry("905x1200")  # Pencere boyutunu ayarlama

        self.mode = "light"  # Varsayılan mod açık

        # Stil nesnesi oluştur
        self.style = ttk.Style()

        # Başlık etiketi
        self.title_label = ttk.Label(root, text="              HOTEL SEARCH", font=("Arial", 27, "bold"))
        self.title_label.grid(row=1, column=0, columnspan=2, pady=10, sticky="wn")

        # Şehir seçimi açılır menüsü
        self.city_label = ttk.Label(root, text="                    Cities :")
        self.city_label.grid(row=2, column=0, sticky="w", pady=5)
        self.city_var = tk.StringVar()
        self.city_dropdown = ttk.Combobox(root, textvariable=self.city_var)
        self.city_dropdown['values'] = ["Rome", "Paris", "Berlin", "London", "Madrid", "Amsterdam", "Vienna", "Athens",
                                        "Prague", "Istanbul", "Oslo", "Lisbon", "Dublin", "Stockholm", "Warsaw"]
        self.city_dropdown.grid(row=2, column=1, sticky="w", pady=5)

        # Giriş tarihi için etiketler ve giriş kutuları
        self.checkin_label = ttk.Label(root, text="    Check-in Date :")
        self.checkin_label.grid(row=3, column=0, sticky="w", pady=5)
        self.checkin_cal = DateEntry(root, width=12, borderwidth=2)
        self.checkin_cal.grid(row=3, column=1, sticky="w", pady=5)

        # Çıkış tarihi için etiketler ve giriş kutuları
        self.checkout_label = ttk.Label(root, text="  Check-out Date :")
        self.checkout_label.grid(row=4, column=0, sticky="w", pady=5)
        self.checkout_cal = DateEntry(root, width=12, borderwidth=2)
        self.checkout_cal.grid(row=4, column=1, sticky="w", pady=5)

        # Check-in ve Check-out zamanını seçmek için düğmeler
        self.checkin_time_label = ttk.Label(root, text="   Check-in Time  :")
        self.checkin_time_label.grid(row=5, column=0, sticky="w", pady=5)
        self.checkin_time_var = tk.StringVar()
        self.checkin_time_spinbox = ttk.Spinbox(root, from_=0, to=23, textvariable=self.checkin_time_var)
        self.checkin_time_spinbox.grid(row=5, column=1, sticky="w", pady=5)

        self.checkout_time_label = ttk.Label(root, text=" Check-out Time :")
        self.checkout_time_label.grid(row=6, column=0, sticky="w", pady=5)
        self.checkout_time_var = tk.StringVar()
        self.checkout_time_spinbox = ttk.Spinbox(root, from_=0, to=23, textvariable=self.checkout_time_var)
        self.checkout_time_spinbox.grid(row=6, column=1, sticky="w", pady=5)

        # Para birimi seçmek için radyo düğmesi
        self.city_label = ttk.Label(root, text="             Currency :")
        self.city_label.grid(row=7, column=0, sticky="w", pady=5)
        self.currency_var = tk.StringVar()
        self.currency_var.set("Euro")  # Varsayılan para birimi Euro
        self.currency_frame = ttk.LabelFrame(root, text="1 € = 30 ₺")
        self.currency_frame.grid(row=7, column=1, columnspan=2, sticky="w", pady=5)

        self.euro_radio = ttk.Radiobutton(self.currency_frame, text="€", variable=self.currency_var, value="Euro")
        self.euro_radio.grid(row=0, column=0, padx=5, sticky="w")
        self.tl_radio = ttk.Radiobutton(self.currency_frame, text="₺", variable=self.currency_var, value="TL")
        self.tl_radio.grid(row=0, column=1, padx=5, sticky="w")

        # Otelleri getirme ve para birimine dönüştürme düğmeleri
        self.retrieve_button = ttk.Button(root, text="Show Top Rated Hotels", command=self.retrieve_hotels)
        self.retrieve_button.grid(row=8, column=1, columnspan=2, pady=10, sticky="w")

        # Otellerin listeleneceği çerçeve
        self.style.configure("Hotels.TLabelframe.Label", font=("Arial", 12, "bold"))
        self.hotels_frame = ttk.LabelFrame(root, text="Top 5 Hotels for You", style="Hotels.TLabelframe")
        self.hotels_frame.grid(row=10, column=0, columnspan=2, sticky="e", pady=10)

        self.hotels_text = tk.Text(self.hotels_frame, height=50, width=110)
        self.hotels_text.pack(padx=5, pady=5, fill="both", expand=True)

        # Mod seçme düğmesi
        self.mode_button = ttk.Button(root, text="Dark Mode", command=self.toggle_mode)
        self.mode_button.grid(row=11, column=0, sticky="w")

        # Menü çubuğu
        self.menu_bar = tk.Menu(root)
        self.info_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.info_menu.add_command(label="About", command=self.show_info)
        self.info_menu.add_command(label="Contact Us", command=self.open_linkedin)
        self.menu_bar.add_cascade(label="Info", menu=self.info_menu)
        self.root.config(menu=self.menu_bar)

        self.set_light_mode()  # Başlangıçta modu ayarla

    def toggle_mode(self):
        # Koyu ve açık modlar arasında geçiş yapmak için fonksiyon
        if self.mode == "dark":
            self.mode = "light"
            self.set_light_mode()
        else:
            self.mode = "dark"
            self.set_dark_mode()

    def set_light_mode(self):
        # Açık modu ayarlamak için fonksiyon
        self.root.configure(background="darkgreen")
        self.title_label.configure(background="brown", foreground="white")
        # Diğer widget'ları açık moda ayarla

    def retrieve_hotels(self):
        # Kullanıcı girişlerine dayanarak otelleri getiren fonksiyon
        city_name = self.city_var.get()
        checkin_date = self.checkin_cal.get_date()
        checkout_date = self.checkout_cal.get_date()
        checkin_time = self.checkin_time_var.get()
        checkout_time = self.checkout_time_var.get()

        # Giriş ve çıkış saatleriyle ilgili yapmanız gerekenleri yapın

        # Booking.com'dan otel verilerini çekme
        hotels_data = self.scrape_booking(city_name, checkin_date, checkout_date)

        # Öğrenci kimliğinin son basamağı tek ise otelleri derecelendirmeye göre sırala
        student_id = "20200601021"
        last_digit = int(student_id[-1])
        if last_digit % 2 != 0:
            hotels_data.sort(key=lambda x: self.extract_rating(x['Hotel Rating']), reverse=True)

        # Otelleri GUI'de göster
        self.display_hotels(hotels_data)

        # Otel verilerini CSV dosyasına kaydet
        self.save_to_csv(hotels_data)

    def scrape_booking(self, city_name, checkin_date, checkout_date):
        # Booking.com'dan otel verilerini çekmek için fonksiyon
        base_url = "https://www.booking.com/searchresults.en-gb.html"
        query_params = {
            'label': 'gen173nr-1FCAEoggI46AdIM1gEaOQBiAEBmAEouAEHyAEM2AEB6AEB-AELiAIBqAIDuAKmksuxBsACAdICJDkwMzNiODdlLTdmYjYtNGMxMy1hYWZjLWI5NDM5NGI3MzdhN9gCBuACAQ',
            'sid': '75e30209011abe1aa1c492edf1647de4',
            'sb': '1',
            'sb_lp': '1',
            'src': 'index',
            'src_elem': 'sb',
            'error_url': 'https://www.booking.com/index.en-gb.html',
            'ss': city_name,
            'is_ski_area': '0',
            'checkin_year': checkin_date.year,
            'checkin_month': checkin_date.month,
            'checkin_monthday': checkin_date.day,
            'checkout_year': checkout_date.year,
            'checkout_month': checkout_date.month,
            'checkout_monthday': checkout_date.day,
            'group_adults': '2',
            'no_rooms': '1',
            'b_h4u_keep_filters': '',
            'from_sf': '1',
            'search_pageview_id': 'e911a5e88e8f024b',
            'order': 'class',  # Eklenen parametre
            'selected_currency': 'EUR'  # Eklenen parametre
        }

        url = f"{base_url}?{requests.compat.urlencode(query_params)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.9'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(url)

        hotels_data = []

        for hotel in soup.findAll('div', {'data-testid': 'property-card'}):
            name_element = hotel.find('div', {'data-testid': 'title'})
            address_element = hotel.find('span', {'data-testid': 'address'})
            distance_element = hotel.find('span', {'data-testid': 'distance'})
            rating_element = hotel.find('div', {'data-testid': 'review-score'})

            price_element = hotel.find('span', {'data-testid': 'price-and-discounted-price',
                                                'class': 'f6431b446c fbfd7c1165 e84eb96b1f'})
            image_element = hotel.find('img', {'class': 'f9671d49b1'})

            hotel_data = {
                'Hotel Title': name_element.text.strip() if name_element else 'Not Given!',
                'Hotel Address': address_element.text.strip() if address_element else 'Not Given!',
                'Distance to City Center': distance_element.text.strip() if distance_element else 'Not Given!',
                'Hotel Rating': rating_element.text.strip() if rating_element else 'Not Given!',
                'Price': price_element.text.strip() if price_element else 'Not Given!',
                'Image URL': image_element['src'] if image_element else 'NOT GIVEN'
            }

            hotels_data.append(hotel_data)

        for hotel_data in hotels_data:
            if self.currency_var.get() == "TL":  # Seçilen para biriminin TL olup olmadığını kontrol edin
                euro_price = float(hotel_data['Price'].replace('€', '').replace(',', '').strip())
                tl_price = euro_price * 30  # 1 Euro = 30 TL dönüşümü
                hotel_data['Price'] = f'{tl_price:.2f} TL'

        return hotels_data

    def extract_rating(self, rating_string):
        # Derelemeyi dize içinden çıkarıp float olarak döndüren fonksiyon
        ratings = re.findall(r'\d+\.\d+', rating_string)
        if ratings:
            return float(ratings[0])
        else:
            return 0.0

    def display_hotels(self, hotels):
        # Otelleri GUI'de göstermek için fonksiyon
        self.hotels_text.delete(1.0, tk.END)

        # Otelleri göstermek için yeni bir çerçeve oluşturun
        hotels_frame = tk.Frame(root)
        hotels_frame.grid(row=10, column=0, columnspan=2, sticky="e", pady=10)

        if hotels:
            for i, hotel in enumerate(hotels[:5], start=1):
                # Otel bilgilerini metin alanına ekleyin
                self.hotels_text.insert(tk.END,
                                        f"{i}. Hotel Name: {hotel['Hotel Title']}\n"
                                        f"   Address: {hotel['Hotel Address']}\n"
                                        f"   Distance to City Center: {hotel['Distance to City Center']}\n"
                                        f"   Rating: {hotel['Hotel Rating']}\n"
                                        f"   Price: {hotel['Price']}\n\n\n",
                                        ("custom_font",))  # custom_font etiketi stil için

                # Otel resimlerini yükle ve göster
                if hotel['Image URL']:
                    response = requests.get(hotel['Image URL'])
                    image_data = response.content
                    image = Image.open(io.BytesIO(image_data))
                    image = image.resize((112, 98), Image.LANCZOS)  
                    photo = ImageTk.PhotoImage(image)

                    image_label = tk.Label(hotels_frame, image=photo)
                    image_label.image = photo  # Referansı saklayın
                    image_label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
        else:
            self.hotels_text.insert(tk.END, "There is no hotel that matched your criteria.")

        # Eklenen metne özel yazı tipi uygula
        self.hotels_text.tag_configure("custom_font", font=("Arial", 12))

    def save_to_csv(self, hotels):
        # Otel verilerini bir CSV dosyasına kaydetme fonksiyonu
        with open("hotels_data.csv", "w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Hotel Title", "Hotel Address", "Distance to City Center", "Hotel Rating", "Price"])
            for hotel in hotels:
                writer.writerow([hotel['Hotel Title'], hotel['Hotel Address'], hotel['Distance to City Center'],
                                 hotel['Hotel Rating'], hotel['Price']])

    def show_info(self):
        # Seçilen şehir hakkında bilgi gösterme fonksiyonu
        selected_city = self.city_var.get()
        file_path = f"C:/Users/W10/Desktop/LECTURES-IUE/3rd Grade Lectures/2nd Grade/SE226/EuropeCountries/{selected_city}.txt"

        if os.path.exists(file_path):  # Dosyanın var olup olmadığını kontrol edin
            with open(file_path, "r", encoding="utf-8") as file:
                city_info = file.read()

            info_box = tk.Toplevel(self.root)
            info_box.title(f"Information about {selected_city}")
            info_text = tk.Text(info_box, height=12, width=40)
            info_text.pack(padx=10, pady=10)
            info_text.insert(tk.END, city_info)
            info_text.config(state=tk.DISABLED)
        else:
            messagebox.showerror("Error", f"No information available for {selected_city}.")

    def open_linkedin(self):
        # LinkedIn hesabınızı açmak için fonksiyon
        import webbrowser
        linkedin_url = "www.linkedin.com/in/colaktahayasir"
        webbrowser.open_new_tab(linkedin_url)


if __name__ == "__main__":
    root = tk.Tk()
    app = HotelListingGUI(root)
    root.mainloop()
