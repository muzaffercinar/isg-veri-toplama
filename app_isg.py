import os

import pandas as pd
import streamlit as st


# --- AYARLAR ---
ESKI_DOSYA_YOLU = "öncelikdereceliokulbilgi.xls"
YENI_DOSYA_YOLU = "öncelikdereceliokulbilgi.xlsx"
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


def veri_kaydet(df):
    df.to_excel(YENI_DOSYA_YOLU, index=False)
    veri_yukle.clear()

    if os.path.exists(ESKI_DOSYA_YOLU):
        return (
            "Bilgiler başarıyla kaydedildi. .xls yazma hatasını önlemek için kayıt "
            ".xlsx dosyasına yapıldı."
        )

    return "Bilgiler başarıyla kaydedildi!"


# --- BAŞLIK ---
st.title("🛡️ İSG VERİ TOPLAMA")


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

                if eksik_sutunlar:
                    st.error(
                        "Excel dosyasında eksik sütunlar var: "
                        + ", ".join(eksik_sutunlar)
                    )
                else:
                    g_sayisi = st.number_input(
                        "Özel Güvenlik Görevlisi Sayısı",
                        min_value=0,
                        value=sayi_degeri_al(df.at[idx, c1]),
                    )

                    sabit = st.selectbox(
                        "Sabit Okul Görevlisi",
                        SECENEKLER,
                        index=0
                        if metin_degeri_al(df.at[idx, c2]).upper() == "VAR"
                        else 1,
                    )

                    cihaz = st.selectbox(
                        "Elektronik İnceleme Cihazı",
                        SECENEKLER,
                        index=0
                        if metin_degeri_al(df.at[idx, c3]).upper() == "VAR"
                        else 1,
                    )

                    turnike = st.selectbox(
                        "Güvenlik Amaçlı Turnike",
                        SECENEKLER,
                        index=0
                        if metin_degeri_al(df.at[idx, c4]).upper() == "VAR"
                        else 1,
                    )

                    if st.form_submit_button(
                        "Verileri Kaydet", use_container_width=True
                    ):
                        df.at[idx, c1] = g_sayisi
                        df.at[idx, c2] = sabit
                        df.at[idx, c3] = cihaz
                        df.at[idx, c4] = turnike

                        try:
                            mesaj = veri_kaydet(df)
                        except Exception as exc:
                            st.error(f"Kaydetme hatası: {exc}")
                        else:
                            st.balloons()
                            st.success(mesaj)
        else:
            st.warning("Bu kurum koduna ait bir okul bulunamadı.")
else:
    st.error(
        f"Sistem dosyası bulunamadı. Önce {ESKI_DOSYA_YOLU} veya {YENI_DOSYA_YOLU} dosyasını ekleyin."
    )
