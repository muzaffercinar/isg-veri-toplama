import os

import pandas as pd
import streamlit as st


# --- AYARLAR ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERI_KLASORU = os.path.join(BASE_DIR, "veri")
ESKI_DOSYA_ADI = "öncelikdereceliokulbilgi.xls"
YENI_DOSYA_ADI = "öncelikdereceliokulbilgi.xlsx"
KAYIT_DOSYA_ADI = "isg_kayitlari.tsv"
ESKI_DOSYA_YOLU = os.path.join(VERI_KLASORU, ESKI_DOSYA_ADI)
YENI_DOSYA_YOLU = os.path.join(VERI_KLASORU, YENI_DOSYA_ADI)
KAYIT_DOSYA_YOLU = os.path.join(VERI_KLASORU, KAYIT_DOSYA_ADI)
ANAHTAR_SUTUN = "KURUM KODU"
ORTAK_SIFRE = "İSGVERİ35"
OKUL_ADI_SUTUNU = "OKUL ADI"
SECENEKLER = ["VAR", "YOK"]

st.set_page_config(
    page_title="İSG VERİ TOPLAMA",
    page_icon="🛡️",
    layout="centered",
)


def veri_dosyasi_bul():
    if os.path.exists(YENI_DOSYA_YOLU):
        return YENI_DOSYA_YOLU
    if os.path.exists(ESKI_DOSYA_YOLU):
        return ESKI_DOSYA_YOLU
    return None


def veri_klasorunu_hazirla():
    os.makedirs(VERI_KLASORU, exist_ok=True)


def yuklenen_dosyayi_kaydet(yuklenen_dosya):
    veri_klasorunu_hazirla()
    dosya_adi = yuklenen_dosya.name.lower()
    hedef_yol = YENI_DOSYA_YOLU if dosya_adi.endswith(".xlsx") else ESKI_DOSYA_YOLU

    with open(hedef_yol, "wb") as dosya:
        dosya.write(yuklenen_dosya.getbuffer())

    veri_yukle.clear()
    return hedef_yol


def sayi_degeri_al(deger):
    if pd.isna(deger):
        return 0

    try:
        return int(float(str(deger).strip()))
    except (TypeError, ValueError):
        return 0


def metin_degeri_al(deger):
    if pd.isna(deger):
        return ""
    return str(deger).strip()


def veri_kaydet(kurum_kodu, okul_adi, guvenlik_sayisi, sabit, cihaz, turnike):
    veri_klasorunu_hazirla()

    baslik = (
        "Kurum Kodu\tOkul Adı\tÖzel Güvenlik Görevlisi Sayısı\t"
        "Sabit Okul Görevlisi\tElektronik İnceleme Cihazı\t"
        "Güvenlik Amaçlı Turnike\n"
    )
    kayit_satiri = (
        f"{kurum_kodu}\t{okul_adi}\t{guvenlik_sayisi}\t"
        f"{sabit}\t{cihaz}\t{turnike}\n"
    )

    with open(KAYIT_DOSYA_YOLU, "a", encoding="utf-8") as dosya:
        if dosya.tell() == 0:
            dosya.write(baslik)
        dosya.write(kayit_satiri)

    return f"Bilgiler başarıyla kaydedildi: {KAYIT_DOSYA_YOLU}"


# --- BAŞLIK ---
st.title("🛡️ İSG VERİ TOPLAMA")
st.caption(f"Yerel veri klasoru: {VERI_KLASORU}")
st.caption(f"Kayıt dosyası: {KAYIT_DOSYA_YOLU}")


# --- 1. ADIM: ANA EKRANDA ŞİFRE KONTROLÜ ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Yetkili Girişi")
        girilen_sifre = st.text_input("Sistem Şifresini Giriniz:", type="password")
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if girilen_sifre == ORTAK_SIFRE:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre!")
    st.stop()


# --- 2. ADIM: VERİ YÜKLEME ---
@st.cache_data
def veri_yukle():
    veri_yolu = veri_dosyasi_bul()
    if veri_yolu is None:
        return None

    try:
        data = pd.read_excel(veri_yolu)
        return data.astype(object)
    except Exception as exc:
        st.error(f"Excel okuma hatası: {exc}")
        return None


df = veri_yukle()

if df is not None:
    st.success("✅ Erişim Onaylandı.")

    if ANAHTAR_SUTUN not in df.columns:
        st.error(f"Excel dosyasında beklenen sütun bulunamadı: {ANAHTAR_SUTUN}")
        st.stop()

    kurum_kodu = st.text_input("Kurum Kodunuzu Giriniz:", placeholder="Örn: 776379")

    if kurum_kodu:
        df[ANAHTAR_SUTUN] = df[ANAHTAR_SUTUN].astype(str).str.strip()
        sonuc = df[df[ANAHTAR_SUTUN] == kurum_kodu.strip()]

        if not sonuc.empty:
            idx = sonuc.index[0]

            if OKUL_ADI_SUTUNU not in df.columns:
                st.error("Excel dosyasında OKUL ADI sütunu bulunamadı.")
                st.stop()

            st.info(f"🏫 Okul: {df.at[idx, OKUL_ADI_SUTUNU]}")

            with st.form("isg_form_yeni"):
                st.subheader("Güncellenecek Bilgiler")

                c1 = "ÖZEL GÜVENLİK \nGÖREVLİSİ SAYISI"
                c2 = "SABİT OKUL GÖREVLİSİ\n(VAR/YOK)"
                c3 = "ELEKTRONİK İNCELEME CİHAZI\n(VAR/YOK)"
                c4 = "GÜVENLİK AMAÇLI TURNİKE\n(VAR/YOK)"

                eksik_sutunlar = [
                    sutun for sutun in [c1, c2, c3, c4] if sutun not in df.columns
                ]

       
