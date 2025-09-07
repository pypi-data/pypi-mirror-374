def turkce_karakterleri_ascii_yap(metin: str) -> str:
    """
    Türkçe karakterleri ASCII eşdeğerleriyle değiştirir.

    Örnek: "ışİğüç" -> "isIguc"

    Args:
        metin (str): Dönüştürülecek metin.

    Returns:
        str: ASCII'ye dönüştürülmüş metin.
    """
    turkce_karakterler = {
        'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'U': 'U', 'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'
    }
    
    yeni_metin = ""
    for karakter in metin:
        yeni_metin += turkce_karakterler.get(karakter, karakter)
    
    return yeni_metin

def buyuk_harflere_cevir(metin: str) -> str:
    """
    Verilen metnin tamamını Türkçe büyük harflere dönüştürür.
    
    Args:
        metin (str): Dönüştürülecek metin.
        
    Returns:
        str: Büyük harflere dönüştürülmüş metin.
    """
    return metin.upper()

def kucuk_harflere_cevir(metin: str) -> str:
    """
    Verilen metnin tamamını Türkçe küçük harflere dönüştürür.

    Args:
        metin (str): Dönüştürülecek metin.

    Returns:
        str: Küçük harflere dönüştürülmüş metin.
    """
    return metin.lower()
