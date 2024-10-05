import os
import sys
import time
import json
import pyfiglet
import random
import requests
import subprocess
import threading
import traceback
import logging
from colorama import init, Fore, Back, Style
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


logging.basicConfig(filename='error_log.txt', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

init(autoreset=True)


stop_color_flag = False
current_color = Fore.WHITE

def random_color():
    return random.choice([Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE])


def print_colored_ascii():
    global stop_color_flag
    colors = {
        'white': Fore.WHITE,
        'red': Fore.RED
    }

    while not stop_color_flag:
        os.system('cls' if os.name == 'nt' else 'clear')
        colored_ascii = ""

        for line in ASCII_ART.split('\n'):
            colored_line = ''
            for char in line:
                if char == '░':   
                    colored_line += f"{colors['white']}{char}"
                elif char == '█':  
                    colored_line += f"{colors['red']}{char}"
                else:
                    colored_line += char  
            colored_ascii += colored_line + '\n'

        print(colored_ascii)
        time.sleep(0.1)

ASCII_ART = r"""
 ██████   ██████         ███████████     █████       █████     █████                             
░░██████ ██████         ░░███░░░░░███  ███░░░███   ███░░░███  ░░███                              
 ░███░█████░███ ████████ ░███    ░███ ███   ░░███ ███   ░░███ ███████   █████ █████ ███ ██████████
 ░███░░███ ░███░░███░░███░██████████ ░███    ░███░███    ░███░░░███░   ███░░ ░░███ ░███░ █░░░░███ 
 ░███ ░░░  ░███ ░███ ░░░ ░███░░░░░███░███    ░███░███    ░███  ░███   ░░█████ ░███ ░███░    ███░  
 ░███      ░███ ░███     ░███    ░███░░███   ███ ░░███   ███   ░███ ███░░░░███░███ ░███   ███░   █
 █████     ██████████    █████   █████░░░█████░   ░░░█████░    ░░█████ ██████ ░░████████ █████████
░░░░░     ░░░░░░░░░░    ░░░░░   ░░░░░   ░░░░░░      ░░░░░░      ░░░░░ ░░░░░░   ░░░░░░░░ ░░░░░░░░░ 
                                                                                                 
                                                                                                 
                                                                                                  
"""

def start_color_change():
    global stop_color_flag
    stop_color_flag = False
    threading.Thread(target=print_colored_ascii, daemon=True).start()

def stop_color_change():
    global stop_color_flag
    stop_color_flag = True
    time.sleep(0.2)   

def print_info(message):
    print(f"{Fore.CYAN}{Style.BRIGHT}[INFO] {message}")

def print_success(message):
    print(f"{Fore.GREEN}{Style.BRIGHT}[SUCCESS] {message}")

def print_error(message):
    print(f"{Fore.RED}{Style.BRIGHT}[ERROR] {message}")

def print_warning(message):
    print(f"{Fore.YELLOW}{Style.BRIGHT}[WARNING] {message}")

def install_requirements():
    print_info("Gereksinimler kontrol ediliyor ve yükleniyor...")
    requirements = [
        "colorama",
        "selenium",
        "requests",
        "webdriver_manager"
    ]
    for req in requirements:
        try:
            __import__(req)
        except ImportError:
            print_info(f"{req} yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
    print_success("Tüm gereksinimler yüklendi.")

def load_cookies(file_path):
    """JSON dosyasından çerezleri yükler."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print_error(f"Çerez dosyası bulunamadı: {file_path}")
        return []
    except json.JSONDecodeError:
        print_error(f"Çerez dosyası geçerli bir JSON formatında değil: {file_path}")
        return []

def close_notification_popup(driver):
    """Bildirim popup'ını kapatmaya çalışır."""
    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Bildirimleri kapat']"))
        )
        close_button.click()
    except:
        print_warning("Bildirim popup'ı bulunamadı veya kapatılamadı.")

def download_image(url, folder, filename):
    """Belirtilen URL'den resmi indirir ve kaydeder."""
    global current_color  
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(os.path.join(folder, filename), 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            current_color = random_color()  
            print_success(f"{current_color}{filename} başarıyla indirildi.")
        else:
            print_error(f"{current_color}{filename} indirilemedi. Durum kodu: {response.status_code}")
    except Exception as e:
        print_error(f"{current_color}{filename} indirilirken hata oluştu: {str(e)}")

def scroll_to_bottom(driver, max_scrolls=50):
    """Sayfayı en alta kadar otomatik olarak kaydırır."""
    scrolls = 0
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while scrolls < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            time.sleep(random.uniform(2, 4))
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print_info("Sayfa sonuna ulaşıldı.")
                break
        
        last_height = new_height
        scrolls += 1
        
        if scrolls % 5 == 0:
            photo_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='photo.php']")
            print_info(f"Şu ana kadar yüklenen fotoğraf sayısı: {len(photo_links)}")

def get_chrome_driver():
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service

    current_dir = os.path.dirname(os.path.abspath(__file__))
    profile_dir = os.path.join(current_dir, "chrome_profile")
    
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={profile_dir}")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-notifications')

    service = Service(ChromeDriverManager().install())
    
    return webdriver.Chrome(service=service, options=chrome_options)

def facebook_photo_downloader(user_input):
    print_info(f"Facebook fotoğraf indirme işlemi başlatılıyor. Kullanıcı girişi: {user_input}")

    driver = get_chrome_driver()

    try:
        driver.get("https://www.facebook.com")
        time.sleep(random.uniform(5, 10))

        cookies = load_cookies('cookie.json')
        for cookie in cookies:
            try:
                driver.add_cookie({k: v for k, v in cookie.items() if k in ['name', 'value', 'domain', 'path']})
            except Exception as e:
                print_error(f"Çerezi eklerken hata: {cookie['name']} - Hata: {str(e)}")

        driver.refresh()
        time.sleep(random.uniform(5, 10))

        if user_input.isdigit():
            profile_url = f"https://www.facebook.com/profile.php?id={user_input}&sk=photos"
        else:
            profile_url = f"https://www.facebook.com/{user_input}/photos"

        driver.get(profile_url)
        time.sleep(random.uniform(5, 10))

        if "login" in driver.current_url:
            print_warning("Facebook oturumu açık değil. Lütfen tarayıcıda manuel olarak giriş yapın.")
            input("Giriş yaptıktan sonra Enter tuşuna basın...")
            driver.get(profile_url)
            time.sleep(random.uniform(5, 10))

        close_notification_popup(driver)

        print_info("Sayfayı otomatik olarak aşağı kaydırma işlemi başlatılıyor...")
        scroll_to_bottom(driver)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        download_folder = os.path.join(current_dir, f"photos_{user_input}")
        os.makedirs(download_folder, exist_ok=True)

        photo_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='photo.php']")
        print_info(f"Toplam bulunan fotoğraf sayısı: {len(photo_links)}")

        for index, link in enumerate(photo_links):
            try:
                driver.execute_script("window.open(arguments[0]);", link.get_attribute('href'))
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(random.uniform(3, 7))

                script = """
                return document.querySelector('img[data-visualcompletion="media-vc-image"]').src;
                """
                img_url = driver.execute_script(script)

                if img_url:
                    print_info(f"Fotoğraf {index+1} URL'si: {img_url}")
                    filename = f"photo_{index+1}.jpg"
                    download_image(img_url, download_folder, filename)
                else:
                    print_warning(f"Fotoğraf {index+1} URL'si bulunamadı.")

            except Exception as e:
                print_error(f"Fotoğraf {index+1} işlenirken hata oluştu: {str(e)}")

            finally:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(random.uniform(2, 5))

        print_success("İşlem tamamlandı.")

    finally:
        driver.quit()

def display_menu():
    print(f"{Fore.BLUE}{Style.BRIGHT}===== Facebook Fotoğraf İndirici =====")
    print("1. Fotoğraf İndir")
    print("2. Çıkış")
    print("==========================================")

def main():
    try:
        install_requirements()
        start_color_change()
        
        while True:
            stop_color_change()
            display_menu()
            choice = input(f"{Fore.GREEN}Lütfen bir seçenek girin (1-2): ")

            if choice == '1':
                user_input = input(f"{Fore.YELLOW}Lütfen Facebook kullanıcı ID'sini veya kullanıcı adını girin: ")
                facebook_photo_downloader(user_input)
            elif choice == '2':
                print_info("Programdan çıkılıyor...")
                break
            else:
                print_error("Geçersiz seçenek. Lütfen tekrar deneyin.")
            
            start_color_change()
            time.sleep(2)  
    except Exception as e:
        print_error(f"Beklenmeyen bir hata oluştu: {str(e)}")
        logging.error(f"Beklenmeyen hata: {str(e)}\n{traceback.format_exc()}")
    finally:
        stop_color_change()
        input("Programı kapatmak için bir tuşa basın...")

if __name__ == "__main__":
    main()