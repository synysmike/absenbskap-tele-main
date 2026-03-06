import telebot
from telebot.types import Message
from time import sleep
from seleniumbase import Driver
from time import sleep
import requests
import base64
from bs4 import BeautifulSoup
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import math
from telebot import apihelper
from PIL import Image, ImageDraw, ImageOps
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Retrieve the API token and user credentials from environment variables
API_TOKEN = os.getenv("API_TOKEN")
USER_CREDENTIALS = {
    "/teguhmasuk": {
        "check": os.getenv("TEGUH_MASUK_CHECK"),
        "nama": os.getenv("TEGUH_MASUK_NAME"),
        "email": os.getenv("TEGUH_MASUK_EMAIL"),
        "password": os.getenv("TEGUH_MASUK_PASSWORD")
    },
    "/teguhkeluar": {
        "check": os.getenv("TEGUH_KELUAR_CHECK"),
        "nama": os.getenv("TEGUH_KELUAR_NAME"),
        "email": os.getenv("TEGUH_KELUAR_EMAIL"),
        "password": os.getenv("TEGUH_KELUAR_PASSWORD")
    },
    "/gunturmasuk": {
        "check": os.getenv("GUNTUR_MASUK_CHECK"),
        "nama": os.getenv("GUNTUR_MASUK_NAME"),
        "email": os.getenv("GUNTUR_MASUK_EMAIL"),
        "password": os.getenv("GUNTUR_MASUK_PASSWORD")
    },
    "/gunturkeluar": {
        "check": os.getenv("GUNTUR_KELUAR_CHECK"),
        "nama": os.getenv("GUNTUR_KELUAR_NAME"),
        "email": os.getenv("GUNTUR_KELUAR_EMAIL"),
        "password": os.getenv("GUNTUR_KELUAR_PASSWORD")
    },
    "/ayumasuk": {
        "check": os.getenv("AYU_MASUK_CHECK"),
        "nama": os.getenv("AYU_MASUK_NAME"),
        "email": os.getenv("AYU_MASUK_EMAIL"),
        "password": os.getenv("AYU_MASUK_PASSWORD")
    },
    "/ayukeluar": {
        "check": os.getenv("AYU_KELUAR_CHECK"),
        "nama": os.getenv("AYU_KELUAR_NAME"),
        "email": os.getenv("AYU_KELUAR_EMAIL"),
        "password": os.getenv("AYU_KELUAR_PASSWORD")
    },
    "/hisahmasuk": {
        "check": os.getenv("HISAH_MASUK_CHECK"),
        "nama": os.getenv("HISAH_MASUK_NAME"),
        "email": os.getenv("HISAH_MASUK_EMAIL"),
        "password": os.getenv("HISAH_MASUK_PASSWORD")
    },
    "/hisahkeluar": {
        "check": os.getenv("HISAH_KELUAR_CHECK"),
        "nama": os.getenv("HISAH_KELUAR_NAME"),
        "email": os.getenv("HISAH_KELUAR_EMAIL"),
        "password": os.getenv("HISAH_KELUAR_PASSWORD")
    },
    "/widhimasuk": {
        "check": os.getenv("WIDHI_MASUK_CHECK"),
        "nama": os.getenv("WIDHI_MASUK_NAME"),
        "email": os.getenv("WIDHI_MASUK_EMAIL"),
        "password": os.getenv("WIDHI_MASUK_PASSWORD")
    },
    "/widhikeluar": {
        "check": os.getenv("WIDHI_KELUAR_CHECK"),
        "nama": os.getenv("WIDHI_KELUAR_NAME"),
        "email": os.getenv("WIDHI_KELUAR_EMAIL"),
        "password": os.getenv("WIDHI_KELUAR_PASSWORD")
    },
    # Add other users similarly
}


# Original coordinates
lat = -7.316532782737108
long = 112.7243205774913

# Earth's approximate radius in meters
EARTH_RADIUS = 6371000  

def add_random_offset(latitude, longitude, min_radius, max_radius):
    # Convert the radius from meters to degrees
    def meters_to_degrees(meters):
        return meters / (EARTH_RADIUS * (math.pi / 180))  # 1 degree latitude ~ 111,320 meters

    # Random distance in meters within the specified range
    distance = random.uniform(min_radius, max_radius)
    
    # Random angle in radians
    angle = random.uniform(0, 2 * math.pi)

    # Calculate offsets
    delta_lat = meters_to_degrees(distance * math.cos(angle))
    delta_long = meters_to_degrees(distance * math.sin(angle)) / math.cos(math.radians(latitude))

    # Apply the offsets
    new_lat = latitude + delta_lat
    new_long = longitude + delta_long

    return new_lat, new_long





bot = telebot.TeleBot(API_TOKEN)
apihelper.delete_webhook(API_TOKEN)
print("Webhook has been cleared.")
# Global dictionary to manage user states
user_states = {}




# Initialize Selenium Driver
def initialize_driver():
    return Driver(uc=True, headless=False)

def login(driver, email, password):
    try:
        print("Logging in...")
        driver.uc_open_with_reconnect("https://absensi.bskap.id/", reconnect_time=6)

        # Tunggu dan masukkan username
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
        ).send_keys(email)

        # Tunggu dan masukkan password
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
        ).send_keys(password)

        # Tunggu dan klik tombol Login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Login')]"))
        ).click()

        # Validasi login berhasil
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(),'BAN-PDM Provinsi Jawa Timur')]"))
        )
        print("Login successful!")

        # Ambil cookies dari Selenium
        selenium_cookies = driver.get_cookies()
        print("Extracted Cookies:", selenium_cookies)

        # Konversi cookies ke format dictionary untuk `requests`
        cookies_dict = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        print("Cookies Dictionary:", cookies_dict)

        # Tambahkan User-Agent ke headers
        headers = {
            "User-Agent": driver.execute_script("return navigator.userAgent;")
        }
        session = requests.Session()
        session.headers.update(headers)

        # Uji cookies dengan `GET`
        response = session.get("https://absensi.bskap.id", cookies=cookies_dict)
        print("Response Status Code:", response.status_code)
        print("Response Content:", response.text)

        return driver, session, cookies_dict
    except Exception as e:
        print(f"[ERROR] Login process failed: {e}")
        driver.quit()
        raise
# Serialize and post profile data
def serialize_and_post_profile(session, cookies, location):
    try:
        # Ambil data profil dari server
        profil = session.get("https://absensi.bskap.id/profile", cookies=cookies)
        if profil.status_code != 200:
            print(f"[ERROR] Gagal mengambil data profil. Status code: {profil.status_code}")
            return False, "Gagal mengambil data profil dari server."

        # Parse HTML profil menggunakan BeautifulSoup
        html_form = profil.text
        soup = BeautifulSoup(html_form, "html.parser")
        form_data = {}

        # Ekstrak input fields
        for input_tag in soup.find_all("input"):
            name = input_tag.get("name")
            value = input_tag.get("value", "")
            if name:
                form_data[name] = value

        # Ekstrak select fields
        for select_tag in soup.find_all("select"):
            name = select_tag.get("name")
            selected_option = select_tag.find("option", selected=True)
            value = selected_option.get("value", "") if selected_option else ""
            if name:
                form_data[name] = value

        # Ekstrak textarea fields
        for textarea_tag in soup.find_all("textarea"):
            name = textarea_tag.get("name")
            value = textarea_tag.text
            if name:
                form_data[name] = value

        # Ubah lokasi berdasarkan input pengguna
        form_data["lokasi"] = location  # Update lokasi ("46" untuk /kdk, "12" untuk /kdm)
        print(f"[LOG] Data profil yang diperbarui: {form_data}")

        # Kirim data profil yang telah diperbarui ke server
        prfl_url = "https://absensi.bskap.id/module/profile/sw-proses.php?action=update"
        response = session.post(prfl_url, data=form_data, cookies=cookies)

        # Periksa respons dari server
        if response.status_code == 200 and response.text.strip() == "success":
            print("[LOG] Profil berhasil diperbarui.")
            return True, "Profil berhasil diperbarui."
        else:
            print(f"[ERROR] Gagal memperbarui profil: {response.text}")
            return False, f"Error saat memperbarui profil: {response.text}"
    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat memproses profil: {e}")
        return False, f"Kesalahan saat memproses profil: {e}"


def activate_work_hours(session, cookies, work_hours_data):
    try:
        url_jam = "https://absensi.bskap.id/module/jam-kerja/sw-proses.php?action=active"

        # Kirim data jam kerja secara individual
        for work_hour in work_hours_data:
            response = session.post(url_jam, data=work_hour, cookies=cookies)
            
            # Log hasil POST request
            if response.status_code == 200:
                print(f"[LOG] Aktivasi jam kerja berhasil: {work_hour['id']}, Status: {response.text}")
            else:
                print(f"[ERROR] Gagal mengaktifkan jam kerja: {work_hour['id']}, Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat mengaktifkan jam kerja: {e}")




# ====== Handle Commands ======
@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.reply_to(message, "Selamat datang di bot absensi! Kirimkan nama Anda seperti '/teguhmasuk' untuk memulai login.")

# Handle user name (e.g., "/teguhmasuk")
@bot.message_handler(func=lambda msg: msg.text in USER_CREDENTIALS.keys())
def handle_user_login(message: Message):
    user_name = message.text
    chat_id = message.chat.id
    user_states[chat_id] = {"user_name": user_name}
    bot.reply_to(message, f"Nama diterima: {user_name}. Sedang memproses login...")

    # Perform login
    try:
        driver = initialize_driver()
        email = USER_CREDENTIALS[user_name]["email"]
        password = USER_CREDENTIALS[user_name]["password"]

        # Login dan extract cookies
        bot.reply_to(message, f"Bentar, tak cobae login dulu ya... kalo bisa nanti tak kabarin, kalo gagal, coba perintah '{user_name}'' lagi ya...")
        driver, session, cookies = login(driver, email, password)
        user_states[chat_id]["driver"] = driver
        user_states[chat_id]["session"] = session
        user_states[chat_id]["cookies"] = cookies

        bot.reply_to(message, "Yess!!!! Login berhasil! Silahkan pilih lokasi: /kdk apa /kdm hayooo...")

    except Exception as e:
        bot.reply_to(message, f"Gagal login: browser bermasalah atau situs bskap lagi anjing, coba cek dulu di browser lalu coba lagi")
        if "driver" in locals():
            driver.quit()



@bot.message_handler(commands=['kdk', 'kdm'])
def handle_location_selection(message: Message):
    chat_id = message.chat.id 

    # Validasi apakah nama pengguna sudah diberikan
    if chat_id not in user_states or "user_name" not in user_states[chat_id]:
        bot.reply_to(message, "Anda belum memberikan nama! Kirimkan nama Anda terlebih dahulu seperti '/teguhmasuk'.")
        print(f"[WARNING] User {chat_id} mencoba memilih lokasi tanpa memberikan nama.")
        return

    try:
        # Tentukan lokasi berdasarkan perintah (12 untuk kdk, 46 untuk kdm)
        location = "46" if message.text == "/kdm" else "12"
        user_states[chat_id]["location"] = location

        # Set data jam kerja berdasarkan lokasi
        work_hours_data = [
            {"id": "1125", "active": "Y"} if location == "12" else {"id": "1264", "active": "Y"},
            {"id": "1264", "active": "N"} if location == "12" else {"id": "1125", "active": "N"}
        ]
        user_states[chat_id]["work_hours_data"] = work_hours_data

        # Ambil session dan cookies dari user_states
        session = user_states[chat_id]["session"]
        cookies = user_states[chat_id]["cookies"]

        # Aktivasi jam kerja
        activate_work_hours(session, cookies, work_hours_data)

        # Panggil fungsi untuk serialisasi dan pengiriman data profil
        success, response_message = serialize_and_post_profile(session, cookies, location)

        if success:
            bot.reply_to(message, f"SIPPP!! Profil berhasil diperbarui dan jam kerja diaktifkan sesuai {message.text}.")
            bot.reply_to(message, f"Sekarang Selfie dooolo dong...")
        else:
            bot.reply_to(message, f"Gagal memperbarui profil: {response_message}")
    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat memproses lokasi: {e}")
        bot.reply_to(message, f"Terjadi kesalahan: {e}")




# Handle photo input
@bot.message_handler(content_types=['photo'])
def handle_photo_upload(message: Message):
    chat_id = message.chat.id

    # Validasi apakah nama pengguna sudah diberikan nama
    if chat_id not in user_states or "user_name" not in user_states[chat_id]:
        bot.reply_to(message, f"Anda belum memberikan nama! Kirimkan nama Anda terlebih dahulu seperti '{user_states[chat_id]['user_name']}'.")
        print(f"[WARNING] User {chat_id} mencoba memilih lokasi tanpa memberikan nama.")
        return

    # Download the photo
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    # Save the original image
    original_image_path = f"{chat_id}_selfie_original.jpg"
    with open(original_image_path, "wb") as img_file:
        img_file.write(downloaded_file)

    # Resize or crop the image    
    modified_image_path = f"{chat_id}_selfie_modified.jpg"
    resized_image_path = f"{chat_id}_selfie_resized.jpg"
    try:
        with Image.open(original_image_path) as img:
            # Tentukan area crop (disesuaikan ke fokus gambar)
            crop_box = (0, 400, 576, 880)  # Contoh area crop (disesuaikan dengan konten)
            img_cropped = img.crop(crop_box)  # Crop gambar
            img_cropped = img_cropped.resize((640, 480))  # Resize hasil crop ke 640x480
            img_cropped.save(resized_image_path)  # Simpan gambar hasil crop
            print(f"[LOG] Image successfully cropped and saved at: {resized_image_path}")

        with Image.open(resized_image_path) as img:
            img_resized = img.resize((600, 450))  # Resize to 640x480 pixels
            img_resized.save(modified_image_path)
            
            print(f"[LOG] Arc successfully added and saved at: {modified_image_path}")
    except Exception as e:
        bot.reply_to(message, f"Terjadi kesalahan saat memproses gambar: {str(e)}")
        return

    bot.reply_to(message, "Foto diterima dan berhasil diproses dengan penanda. Sedang memproses absensi...")

    # Convert the modified image to Base64
    with open(modified_image_path, "rb") as img_file:
        enc = base64.b64encode(img_file.read()).decode('utf-8')
        img_base64 = f"data:image/png;base64,{enc}"

    # Absensi processing
    try:
        driver = user_states[chat_id]["driver"]
        session = user_states[chat_id]["session"]
        cookies = user_states[chat_id]["cookies"]
        location = user_states[chat_id]["location"]
        check_status = USER_CREDENTIALS[user_states[chat_id]["user_name"]]["check"]
        # Lokasi bangunan


        # Generate random latitude
        # Generate random sliding within 5-7 meters
        random_lat, random_long = add_random_offset(lat, long, 1, 2)
        print(f"Original: ({lat}, {long})")
        print(f"Randomized: ({random_lat}, {random_long})")

        #set latitude and longitude
        latitude = f"{random_lat},{random_long}"
        rad = random.randint(37, 97)
        radius = f"{rad}"
        lokasi = "46" if location == "/kdm" else "12"

        # Pilih URL berdasarkan check_status
        if check_status == "in":
            absensi_url = "https://absensi.bskap.id/module/absen-in/sw-proses.php?action=absen-selfie-radius"
        elif check_status == "out":
            absensi_url = "https://absensi.bskap.id/module/absen-out/sw-proses.php?action=absen-selfie-radius"
        else:
            print("Status check tidak valid!")
            bot.reply_to(message, "Terjadi kesalahan pada status check.")
            return

        # Kirim data ke URL yang sesuai
        data = {
            "img": img_base64,
            "latitude": latitude,
            "radius": radius,
            "lokasi": lokasi
        }
        res = f"Absensi berhasil. Lokasi: {latitude}, Radius: {radius}"
        print(f"[DEBUG] Absensi URL: {absensi_url}")
        # print(f"[DEBUG] Data POST: {data}")
        with open(modified_image_path, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=res)
            
        # Kirim permintaan POST ke server
        response = session.post(absensi_url, data=data, cookies=cookies)

        # Tanggapi berdasarkan respons server
        if response.status_code == 200:
            bot.reply_to(message, f"Absensi berhasil. Respon server: {response.text}")
            user_states[chat_id]["driver"].quit()
        else:
            bot.reply_to(message, f"Absensi gagal. Status: {response.status_code}")
            user_states[chat_id]["driver"].quit()

    except Exception as e:
        bot.reply_to(message, f"Terjadi kesalahan: {str(e)}")
        if "driver" in user_states[chat_id]:
            user_states[chat_id]["driver"].quit()

# Start polling the bot
print("Bot is running...")
bot.infinity_polling()

