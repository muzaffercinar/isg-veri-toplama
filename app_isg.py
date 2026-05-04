import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- AYARLAR ---
ANAHTAR_SUTUN = "KURUM KODU"
ORTAK_SIFRE = "İSGVERİ35" 

st.set_page_config(page_title="İSG VERİ TOPLAMA", page_icon="🛡️", layout="centered")

# --- BAŞLIK ---
st.markdown("<h1 style='text-align: center;'>🛡️ İSG VERİ TOPLAMA SİSTEMİ</h1>", unsafe_allow_html=True)

# --- 1. ADIM: ŞİFRE KONTROLÜ ---
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

# --- 2. ADIM: GOOGLE SHEETS BAĞLANTISI ---
@st.cache_resource
def baglanti_kur():
    return st.connection("gsheets", type=GSheetsConnection)

try:
    conn = baglanti_kur()
    
    @st.cache_data(ttl=5)
    def veri_yukle():
        # Veriyi oku
        raw_data = conn.read()
        # Sütun isimlerini temizle (Hata veren \n karakterlerini siler)
        raw_data.columns = [str(c).replace('\n', ' ').strip() for c in raw_data.columns]
        # KRİTİK: Tüm tabloyu esnek veri tipine çevir (TypeError hatasını önler)
        return raw_data.astype(object)

    df = veri_yukle()
except Exception as e:
    st.error("Veri tabanı bağlantı hatası.")
    st.stop()

# --- 3. ADIM: SORGULAMA VE FORM ---
st.success("✅ Bağlantı Aktif.")
kurum_kodu = st.text_input("Kurum Kodunu Giriniz:", placeholder="Örn: 776379")

if kurum_kodu:
    df[ANAHTAR_SUTUN] = df[ANAHTAR_SUTUN].astype(str).str.strip()
    sonuc = df[df[ANAHTAR_SUTUN] == kurum_kodu.strip()]
    
    if not sonuc.empty:
        idx = sonuc.index[0]
        okul_adi = df.at[idx, 'OKUL ADI']
        st.info(f"🏫 **Kurum:** {okul_adi}")
        
        with st.form("isg_fix_form"):
            st.markdown("### 📝 Bilgi Güncelleme")
            
            # Sütun isimleri (Temizlenmiş halleri)
            c1 = 'ÖZEL GÜVENLİK GÖREVLİSİ SAYISI'
            c2 = 'SABİT OKUL GÖREVLİSİ (VAR/YOK)'
            c3 = 'ELEKTRONİK İNCELEME CİHAZI (VAR/YOK)'
            c4 = 'GÜVENLİK AMAÇLI TURNİKE (VAR/YOK)'

            # Hata almamak için değerleri güvenli çek
            def safe_int(val):
                try: return int(float(val)) if pd.notna(val) else 0
                except: return 0

            v_sayi = st.number_input("Güvenlik Sayısı", min_value=0, value=safe_int(df.at[idx, c1]))
            v_sabit = st.selectbox("Sabit Görevli", ["VAR", "YOK"], index=0 if str(df.at[idx, c2]).upper() == "VAR" else 1)
            v_cihaz = st.selectbox("E-Cihaz", ["VAR", "YOK"], index=0 if str(df.at[idx, c3]).upper() == "VAR" else 1)
            v_turnike = st.selectbox("Turnike", ["VAR", "YOK"], index=0 if str(df.at[idx, c4]).upper() == "VAR" else 1)

            if st.form_submit_button("💾 BİLGİLERİ KAYDET", use_container_width=True):
                # DataFrame'i güncelle
                df.at[idx, c1] = v_sayi
                df.at[idx, c2] = v_sabit
                df.at[idx, c3] = v_cihaz
                df.at[idx, c4] = v_turnike
                
                # Google Sheets'e gönder
                conn.update(data=df)
                st.cache_data.clear()
                st.balloons()
                st.success("Veriler başarıyla güncellendi!")
    else:
        st.warning("Kurum kodu bulunamadı.")
