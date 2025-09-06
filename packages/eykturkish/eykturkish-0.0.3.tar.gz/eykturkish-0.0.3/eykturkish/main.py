# This code is published under the Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0) license.
# For more information, please see the LICENSE.md file in the project's root directory. And this is turkish utility

import time 
import datetime
import random 
import socket
import threading 
import string 
active_clients = []
# active_clients listesine erişimi senkronize etmek için bir kilit nesnesi oluşturulur.
# Bu, birden fazla iş parçacığı aynı anda listeyi değiştirmeye çalıştığında veri bozulmasını önler.
client_lock = threading.Lock()
def yazdirabilirkarakterler():
    return string.printable

def connect(host, port):
    """
    Belirtilen ana bilgisayara (host) ve bağlantı noktasına (port) bir TCP bağlantısı kurar.

    Args:
        host (str): Bağlanılacak ana bilgisayarın IP adresi veya alan adı.
        port (int): Bağlanılacak bağlantı noktası numarası.

    Returns:
        socket.socket or None: Başarılı olursa bağlantı nesnesi, aksi takdirde None.
    """
    try:
        # Belirtilen ana bilgisayara ve bağlantı noktasına bir bağlantı oluşturur.
        # socket.create_connection, ad çözümlemesi ve bağlantı kurma işlemlerini halleder.
        sock = socket.create_connection((host, port), timeout=5) # 5 saniye zaman aşımı eklendi
        print(f"[{host}:{port}] adresine başarıyla bağlandı.")
        return sock
    except socket.timeout:
        # Bağlantı zaman aşımına uğradığında oluşur.
        print(f"[{host}:{port}] bağlantı zaman aşımına uğradı.")
        return None
    except socket.error as e:
        # Diğer soketle ilgili hatalar (örn. bağlantı reddedildi, ana bilgisayar bulunamadı).
        print(f"[{host}:{port}] adresine bağlanırken bir hata oluştu: {e}")
        return None
    except Exception as e:
        # Beklenmeyen diğer hatalar.
        print(f"Beklenmeyen bir hata oluştu: {e}")
        return None


def send_data(sock, data):
    """
    Verilen soket üzerinden veri gönderir.

    Args:
        sock (socket.socket): Verinin gönderileceği soket nesnesi.
        data (str): Gönderilecek metin verisi.

    Returns:
        bool: Veri başarıyla gönderilirse True, aksi takdirde False.
    """
    if not sock:
        print("Geçersiz soket nesnesi. Veri gönderilemedi.")
        return False
    try:
        # Metin verisini baytlara dönüştürerek gönderir (UTF-8 kodlaması kullanılır).
        sock.sendall(data.encode('utf-8'))
        print(f"Veri gönderildi: '{data[:50]}...'") # Gönderilen verinin ilk 50 karakterini göster
        return True
    except socket.error as e:
        print(f"Veri gönderilirken bir hata oluştu: {e}")
        return False
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu veri gönderirken: {e}")
        return False


def receive_data(sock, buffer_size=4096):
    """
    Verilen soket üzerinden veri alır.

    Args:
        sock (socket.socket): Verinin alınacağı soket nesnesi.
        buffer_size (int): Alınacak veri bloğunun boyutu (bayt cinsinden).

    Returns:
        str or None: Alınan metin verisi, hata durumunda None.
    """
    if not sock:
        print("Geçersiz soket nesnesi. Veri alınamadı.")
        return None
    try:
        # Soketten belirtilen boyutta veri alır.
        data = sock.recv(buffer_size)
        if data:
            # Alınan bayt verisini UTF-8 olarak metne dönüştürür.
            # 'errors='ignore'' parametresi, çözme hatalarında karakterleri yoksayar.
            decoded_data = data.decode('utf-8', errors='ignore')
            print(f"Veri alındı (İlk 50 karakter): '{decoded_data[:50]}...'")
            return decoded_data
        else:
            # Eğer veri alınamazsa (soket kapatılmış olabilir).
            print("Soketten veri alınamadı (bağlantı kapatılmış olabilir).")
            return None
    except socket.timeout:
        # Zaman aşımına uğradığında sessizce None döndürülür, çıktıya mesaj basılmaz.
        return None
    except socket.error as e:
        print(f"Veri alınırken bir hata oluştu: {e}")
        return None
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu veri alırken: {e}")
        return None


def create_server_socket(host, port, backlog=5):
    """
    Bir sunucu soketi oluşturur, belirtilen ana bilgisayara ve bağlantı noktasına bağlar
    ve gelen bağlantılar için dinlemeye başlar.

    Args:
        host (str): Sunucunun dinleyeceği IP adresi (örn. '0.0.0.0' tüm arayüzler için).
        port (int): Sunucunun dinleyeceği bağlantı noktası numarası.
        backlog (int): Bekleyen bağlantı kuyruğunun maksimum boyutu.
                         Kaç adet eşzamanlı bağlantının beklenebileceğini belirtir.

    Returns:
        socket.socket or None: Başarılı olursa sunucu soket nesnesi, aksi takdirde None.
    """
    try:
        # Bir TCP/IP soketi oluştur (AF_INET IPv4, SOCK_STREAM TCP için).
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # setsockopt ile soket seçenekleri ayarlanır. SO_REUSEADDR, adresin hemen yeniden
        # kullanılabilmesini sağlar, bu da sunucuyu hızlıca yeniden başlatırken faydalıdır.
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Soketi belirtilen ana bilgisayar ve bağlantı noktasına bağla.
        server_sock.bind((host, port))
        # Gelen bağlantılar için dinlemeye başla. backlog, eşzamanlı bağlantı kuyruğu boyutudur.
        server_sock.listen(backlog)
        print(f"Sunucu [{host}:{port}] adresinde dinliyor...")
        return server_sock
    except socket.error as e:
        print(f"Sunucu soketi oluşturulurken veya bağlanırken hata oluştu: {e}")
        return None
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu sunucu soketi oluştururken: {e}")
        return None


def accept_connection(server_sock):
    """
    Bir sunucu soketinde gelen bir istemci bağlantısını kabul eder.

    Args:
        server_sock (socket.socket): Gelen bağlantıları dinleyen sunucu soketi.

    Returns:
        tuple or None: (client_socket, client_address) tuple'ı veya hata durumunda None.
    """
    if not server_sock:
        print("Geçersiz sunucu soketi. Bağlantı kabul edilemedi.")
        return None
    try:
        # Gelen bir bağlantıyı kabul et. client_sock, yeni bir soket nesnesidir
        # ve istemciyle iletişim kurmak için kullanılır. client_address ise istemcinin adresidir.
        client_sock, client_address = server_sock.accept()
        print(f"[{client_address[0]}:{client_address[1]}] adresinden bağlantı kabul edildi.")
        return client_sock, client_address
    except socket.timeout:
        # Zaman aşımına uğradığında sessizce None döndürülür, çıktıya mesaj basılmaz.
        return None
    except socket.error as e:
        print(f"Bağlantı kabul edilirken hata oluştu: {e}")
        return None
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu bağlantı kabul ederken: {e}")
        return None


def broadcast_message(sender_sock, message):
    """
    Belirli bir mesajı tüm bağlı istemcilere (gönderen hariç) yayınlar.
    Bu, bir sohbet uygulamasında mesajın tüm kullanıcılara gönderilmesi için kullanılır.
    """
    # client_lock'ı kullanarak active_clients listesine güvenli erişim sağlar.
    with client_lock:
        # active_clients listesi üzerinde döngü yaparken, listeyi kopyalayarak
        # olası değişikliklerden (bir istemcinin ayrılması gibi) kaçınırız.
        clients_to_send = list(active_clients)
        for client_sock, _ in clients_to_send:
            # Mesajı gönderen istemciye tekrar göndermeyi atla.
            if client_sock != sender_sock:
                try:
                    # Mesajı bayt formatına dönüştürüp gönderir.
                    client_sock.sendall(message.encode('utf-8'))
                except socket.error as e:
                    # Eğer bir istemciye gönderirken hata olursa (örn. bağlantı kesildi),
                    # hata mesajı yazdırılır. Bu istemcinin listeden çıkarılması gerekebilir
                    # ancak bu örnekte daha basit tutulmuştur.
                    print(f"Yayın sırasında istemciye ({client_sock.getpeername()}) gönderirken hata oluştu: {e}")
                except Exception as e:
                    print(f"Yayın sırasında beklenmeyen hata: {e}")


def handle_client(client_sock, client_address):
    """
    Gelen bir istemci bağlantısını işler (bir sohbet istemcisi gibi).
    Bu fonksiyon, her yeni istemci için ayrı bir iş parçacığında çalıştırılmalıdır.
    """
    client_id = f"{client_address[0]}:{client_address[1]}" # İstemcinin IP ve portundan bir kimlik oluşturulur.
    print(f"[{client_id}] istemci işleniyor.")

    # İstemciyi aktif istemciler listesine ekle ve diğerlerine duyur.
    with client_lock:
        active_clients.append((client_sock, client_address))
        print(f"Aktif istemciler: {len(active_clients)}")
        # Yeni bağlantıyı diğer tüm istemcilere duyur.
        broadcast_message(client_sock, f"[{client_id}] sohbete katıldı.")

    try:
        while True: # İstemci bağlı olduğu sürece veri almaya devam et.
            received_message = receive_data(client_sock) # İstemciden veri al.
            if received_message:
                full_message = f"[{client_id}]: {received_message}" # Gelen mesajı istemci kimliğiyle birleştir.
                print(f"Yayınlanıyor: {full_message}") # Mesajı sunucu konsoluna yazdır.
                broadcast_message(client_sock, full_message) # Mesajı diğer tüm istemcilere yayınla.
            else:
                # Eğer veri alınamazsa (istemci bağlantıyı kapatmış olabilir), döngüden çık.
                break
    except Exception as e:
        print(f"İstemci ({client_id}) işlenirken hata: {e}")
    finally:
        # İstemci bağlantısı sona erdiğinde (hata veya normal ayrılma), cleanup işlemleri yapılır.
        with client_lock:
            # İstemciyi aktif istemciler listesinden kaldır.
            if (client_sock, client_address) in active_clients:
                active_clients.remove((client_sock, client_address))
                print(f"[{client_id}] sohbettan ayrıldı.")
                # Herkese ayrıldığını duyur (gönderen yok, bu yüzden None).
                broadcast_message(None, f"[{client_id}] sohbettan ayrıldı.")
            print(f"İstemci bağlantısı ({client_id}) kapatılıyor. Kalan aktif istemciler: {len(active_clients)}")
        client_sock.close() # Soket bağlantısını kapat.


def sifrele(text):
    """
    Metni, her karakterin Unicode (ordinal) değerine dönüştürerek şifreler.
    Her sayı, rastgele seçilen farklı bir ayırıcı ile ayrılır.
    Şifrelenmiş metnin başına kullanılan ayırıcı karakter eklenmez.
    """
    # Şifreleme için kullanılabilecek olası ayırıcı karakterler listesi.
    possible_separators = ['!', "'", '^', '+', '%']

    # Metindeki her karakterin Unicode (ordinal) değerini alır, 100 ekler
    # ve stringe dönüştürür.
    ordinal_values = [str(ord(char) + 100) for char in text]

    encoded_parts = []
    for i, val in enumerate(ordinal_values):
        encoded_parts.append(val)
        if i < len(ordinal_values) - 1: # Son sayı değilse araya rastgele bir ayırıcı ekle
            encoded_parts.append(random.choice(possible_separators))

    return "".join(encoded_parts) # Şifrelenmiş parçaları birleştirerek tek bir string döndürür.


def sifrecoz(encoded_text):
    """
    Metni, rastgele ayırıcılarla bölünen sayısal değerlerden deşifreler.
    Her sayısal değerden 100 çıkarılır (çünkü şifreleme sırasında 100 eklenmişti).
    Ayırıcılar, mümkün olan ayırıcılar listesinden tanınır.
    """
    # Deşifreleme için kullanılabilecek olası ayırıcı karakterler listesi.
    # Şifreleme fonksiyonundaki ile aynı olmalıdır.
    possible_separators = ['!', "'", '^', '+', '%']
    decoded_chars = [] # Deşifrelenmiş karakterleri tutacak liste.

    current_number_str = "" # Şu anki sayı stringini geçici olarak tutar.
    for char in encoded_text:
        # Eğer karakter bir ayırıcı ise
        if char in possible_separators:
            # Eğer bir sayı stringi toplamışsak, onu deşifre et
            if current_number_str:
                try:
                    # Sayı stringini integer'a dönüştür, 100 çıkar ve karakteri elde et.
                    decoded_chars.append(chr(int(current_number_str) - 100))
                except ValueError:
                    # Eğer sayıya dönüştürmede hata olursa (geçersiz sayısal değer), uyarı ver.
                    print(f"UYARI: Deşifreleme hatası! Geçersiz sayısal değer: '{current_number_str}'.")
                    return "DEŞİFRELEME HATASI!" # Hata durumunda özel bir string döndür.
                current_number_str = "" # Bir sonraki sayı için sıfırla
            # Ayırıcıyı atla, sadece bölücü olarak kullanıldı, deşifrelenmiş metne eklenmez.
        else:
            # Eğer karakter bir ayırıcı değilse, şu anki sayı stringine ekle.
            current_number_str += char

    # Döngü bittikten sonra kalan son sayıyı deşifre et (eğer varsa, çünkü son karakter ayırıcı olmayabilir).
    if current_number_str:
        try:
            # Sayı stringini integer'a dönüştür, 100 çıkar ve karakteri elde et.
            decoded_chars.append(chr(int(current_number_str) - 100))
        except ValueError:
            print(f"UYARI: Deşifreleme hatası! Geçersiz sayısal değer: '{current_number_str}'.")
            return "DEŞİFRELEME HATASI!"

    return "".join(decoded_chars) # Deşifrelenmiş karakterleri birleştirerek tek bir string döndürür.


# library.py olarak ayrılması planlanan kısım
# Bu kısım, çeşitli genel amaçlı yardımcı fonksiyonları içerir.

# Matematiksel İşlemler
def topla(a, b):
    """İki sayıyı toplar."""
    return a + b


def cikar(a, b):
    """İki sayıyı birbirinden çıkarır."""
    return a - b


def carp(a, b):
    """İki sayıyı çarpar."""
    return a * b


def bol(a, b):
    """İki sayıyı böler. Bölen sıfırsa hata verir."""
    if b == 0:
        # Sıfıra bölme hatasında özel bir ValueError yükseltilir.
        raise ValueError("0/0=E")
    return a / b

def pisayisi():
    return "3,141592653589793"
# Tarih ve Zaman İşlemleri
# datetime modülü yukarıda import edildi
# time modülü yukarıda import edildi
def bekle(saniye): # Parametre adı daha açıklayıcı yapıldı: 'klmn' yerine 'saniye'
    """Verilen süre kadar bekler."""
    time.sleep(saniye)


def simdiki_zaman():
    """Şu anki zamanı döndürür."""
    return datetime.datetime.now() # datetime modülünden datetime sınıfı kullanılır.


def tarih_bilgisi():
    """Bugünün tarih bilgisini 'GG-AA-YYYY' formatında döndürür."""
    return datetime.datetime.now().strftime("%d-%m-%Y") # datetime modülünden datetime sınıfı kullanılır.


def saat_bilgisi():
    """Saat bilgisini 'HH:MM:SS' formatında döndürür."""
    return datetime.datetime.now().strftime("%H:%M:%S") # datetime modülünden datetime sınıfı kullanılır.


# Dosya İşlemleri
def dosya_oku(dosya_adi):
    """Belirtilen dosyayı okur ve içeriğini döndürür."""
    try:
        # Dosyayı okuma modunda ('r') ve UTF-8 kodlamasıyla açar.
        with open(dosya_adi, 'r', encoding='utf-8') as dosya:
            return dosya.read() # Dosyanın tüm içeriğini oku.
    except FileNotFoundError:
        # Eğer dosya bulunamazsa özel bir mesaj döndür.
        return "Dosya bulunamadı."
    except Exception as e:
        # Diğer olası dosya hataları için.
        return f"Dosya okunurken bir hata oluştu: {e}"


def dosya_yaz(dosya_adi, icerik):
    """Belirtilen dosyaya içerik ekler (append)."""
    try:
        # Dosyayı ekleme modunda ('a') ve UTF-8 kodlamasıyla açar.
        # Eğer dosya yoksa oluşturulur.
        with open(dosya_adi, 'a', encoding='utf-8') as dosya:
            dosya.write(icerik) # İçeriği dosyanın sonuna yaz.
        return f"{dosya_adi} dosyasına başarıyla yazıldı."
    except Exception as e:
        return f"Dosya yazılırken bir hata oluştu: {e}"


def dosya_satiri_duzenle(dosya_adi: str, satir_numarasi: int, yeni_icerik: str):
    """
    Belirtilen dosyanın belirli bir satırını yeni içerikle değiştirir.

    Args:
        dosya_adi (str): Düzenlenecek dosyanın adı.
        satir_numarasi (int): Düzenlenecek satırın numarası (1 tabanlı).
        yeni_icerik (str): Satıra yazılacak yeni içerik.

    Returns:
        str: İşlemin başarılı olup olmadığını veya bir hata mesajını belirten bir dize.
    """
    try:
        # Dosyanın tüm satırlarını okur.
        with open(dosya_adi, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Satır numarasının geçerli olup olmadığını kontrol et.
        if 0 < satir_numarasi <= len(lines):
            # Belirtilen satırı yeni içerikle güncelle.
            # Satırlar 0 tabanlı olduğu için satir_numarasi - 1 kullanılır.
            # Yeni içeriğin sonuna bir yeni satır karakteri ekle eğer yoksa ve orijinal satırda varsa.
            lines[satir_numarasi - 1] = yeni_icerik.rstrip('\n') + '\n'

            # Güncellenmiş satırları dosyaya geri yaz.
            with open(dosya_adi, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return f"'{dosya_adi}' dosyasının {satir_numarasi}. satırı başarıyla güncellendi."
        elif satir_numarasi > len(lines):
            return f"Hata: '{dosya_adi}' dosyasında {satir_numarasi}. satır bulunmuyor. Dosyada {len(lines)} satır var."
        else:
            return "Hata: Satır numarası 1 veya daha büyük olmalıdır."

    except FileNotFoundError:
        return f"Hata: '{dosya_adi}' dosyası bulunamadı."
    except Exception as e:
        return f"Dosya satırı düzenlenirken bir hata oluştu: {e}"


def dosya_satir_sil(dosya_adi: str, satir_numarasi: int):
    """
    Belirtilen dosyanın belirli bir satırını siler.

    Args:
        dosya_adi (str): Silinecek dosyanın adı.
        satir_numarasi (int): Silinecek satırın numarası (1 tabanlı).

    Returns:
        str: İşlemin başarılı olup olmadığını veya bir hata mesajını belirten bir dize.
    """
    try:
        # Dosyanın tüm satırlarını okur.
        with open(dosya_adi, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Satır numarasının geçerli olup olmadığını kontrol et.
        if 0 < satir_numarasi <= len(lines):
            # Belirtilen satırı listeden kaldır.
            del lines[satir_numarasi - 1]

            # Güncellenmiş satırları dosyaya geri yaz.
            with open(dosya_adi, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return f"'{dosya_adi}' dosyasının {satir_numarasi}. satırı başarıyla silindi."
        elif satir_numarasi > len(lines):
            return f"Hata: '{dosya_adi}' dosyasında {satir_numarasi}. satır bulunmuyor. Dosyada {len(lines)} satır var."
        else:
            return "Hata: Satır numarası 1 veya daha büyük olmalıdır."

    except FileNotFoundError:
        return f"Hata: '{dosya_adi}' dosyası bulunamadı."
    except Exception as e:
        return f"Dosya satırı silinirken bir hata oluştu: {e}"


def dosya_icerik_ara(dosya_adi: str, aranan_metin: str) -> list[str]:
    """
    Belirtilen dosyada aranan metni içeren satırları bulur ve bir liste olarak döndürür.

    Args:
        dosya_adi (str): Aranacak dosyanın adı.
        aranan_metin (str): Dosya içinde aranacak metin.

    Returns:
        list[str]: Aranan metni içeren satırların bir listesi. Dosya bulunamazsa veya metin bulunamazsa boş liste.
    """
    found_lines = []
    try:
        with open(dosya_adi, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1): # Satır numaraları ile birlikte oku.
                if aranan_metin in line:
                    found_lines.append(f"Satır {line_num}: {line.strip()}")
    except FileNotFoundError:
        return [f"Hata: '{dosya_adi}' dosyası bulunamadı."]
    except Exception as e:
        return [f"Dosya içinde arama yapılırken bir hata oluştu: {e}"]

    if not found_lines:
        return [f"'{dosya_adi}' dosyasında '{aranan_metin}' metni bulunamadı."]
    return found_lines


# Liste İşlemleri
def listeye_ekle(liste, deger):
    """Listeye yeni bir eleman ekler."""
    liste.append(deger) # listenin sonuna değeri ekle.
    return liste


def listeyi_ara(liste, deger):
    """Listede bir elemanın var olup olmadığını kontrol eder."""
    if deger in liste: # 'in' operatörü ile elemanın listede olup olmadığını kontrol et.
        return True
    return False


def listeyi_tersten_sirala(liste):
    """Listeyi tersten sıralar."""
    # Slicing kullanarak listenin ters çevrilmiş bir kopyasını döndürür.
    return liste[::-1]


# Karakter Dizisi İşlemleri
def metni_bul(metin, kelime):
    """Bir metinde belirli bir kelimenin olup olmadığını kontrol eder."""
    return kelime in metin # 'in' operatörü ile kelimenin metinde olup olmadığını kontrol et.


def metni_degistir(metin, eski, yeni):
    """Bir metindeki belirli bir kelimeyi (veya alt diziyi) değiştirir."""
    # replace() metodu ile metindeki tüm eşleşmeleri değiştirir.
    return metin.replace(eski, yeni)


def metinmini(metin):
    """Bir metni küçük harflerle döndürür."""
    return metin.lower() # lower() metodu ile tüm karakterleri küçük harfe dönüştürür.


def metindev(metin):
    """Bir metni büyük harflerle döndürür."""
    return metin.upper() # upper() metodu ile tüm karakterleri büyük harfe dönüştürür.

def basit_cevir(metin):
    """
    Belirtilen metni basit bir sözlüğe göre İngilizce'ye çevirir.
    Bu fonksiyon harici bir kütüphane gerektirmez.

    Args:
        metin (str): Çevrilecek metin.

    Returns:
        str: Çevrilmiş metin veya hata mesajı.
    """
    # Basit bir Türkçe-İngilizce sözlük.
    sozluk = {
        "merhaba": "hello",
        "nasılsın": "how are you",
        "teşekkürler": "thank you",
        "evet": "yes",
        "hayır": "no",
        "elma": "apple",
        "bilgisayar": "computer",
        "kitap": "book"
    }
    ceviri = sozluk.get(metin.lower())
    
    if ceviri:
        return ceviri
    else:
        return "Bu kelime sözlükte bulunmuyor."


def metin_tek_cift_mi(metin):
    """
    Verilen metnin karakter uzunluğunun tek mi çift mi olduğunu kontrol eder.

    Args:
        metin (str): Kontrol edilecek metin.

    Returns:
        str: 'Çift' veya 'Tek'.
    """
    if len(metin) % 2 == 0:
        return "Çift"
    else:
        return "Tek"


# Rastgele Sayı Üretimi
# random modülü yukarıda import edildi
def rastgele_sayi(alt, ust):
    """Belirtilen aralıkta (alt dahil, ust dahil) rastgele bir tam sayı döndürür."""
    return random.randint(alt, ust)


def rastgele_secim(secenekler):
    """Verilen seçenekler listesinden rastgele bir eleman seçer."""
    return random.choice(secenekler)


# Zamanlayıcı (Timer) - bekle fonksiyonuyla aynı işi yapar, tekilleştirilebilir.
# Şu an için ayrı bırakıldı.
def zamanlayici_sayac(saniye):
    """Verilen süre kadar (saniye cinsinden) programın çalışmasını durdurur."""
    time.sleep(saniye)