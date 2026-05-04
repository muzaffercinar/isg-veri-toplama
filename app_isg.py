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
        
        if st.button("Giriş Yap", use_container_width=True):
            if girilen_sifre == ORTAK_SIFRE:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre!")
    st.stop()

# --- 2. ADIM: GOOGLE SHEETS BAĞLANTISI (Burayı Kararlı Hale Getirdik) ---
@st.cache_resource # Bağlantıyı hafızada tutar, kopmaları önler
def baglanti_kur():
    return st.connection("gsheets", type=GSheetsConnection)

try:
    conn = baglanti_kur()
    
    @st.cache_data(ttl=10) # 10 saniyede bir veriyi tazeler
    def veri_yukle():
        data = conn.read()
        # Başlıkları temizle (Gizli karakterler için)
        data.columns = [str(c).replace('\n', ' ').strip() for c in data.columns]
        return data.astype(object)

    df = veri_yukle()
except Exception as e:
    st.error("⚠️ Veri tabanı bağlantısı şu an kurulamıyor.")
    st.info("Lütfen Secrets ayarlarındaki linkin doğruluğunu ve Google Tablo paylaşım izinlerini kontrol edin.")
    if st.button("Bağlantıyı Tekrar Dene"):
        st.cache_resource.clear()
        st.rerun()
    st.stop()

# --- 3. ADIM: SORGULAMA VE FORM ---
st.success("✅ Bağlantı Aktif. Kurum Kodunuzu Yazabilirsiniz.")
kurum_kodu = st.text_input("Kurum Kodunuzu Giriniz:", placeholder="Örn: 776379")

if kurum_kodu:
    df[ANAHTAR_SUTUN] = df[ANAHTAR_SUTUN].astype(str).str.strip()
    sonuc = df[df[ANAHTAR_SUTUN] == kurum_kodu.strip()]
    
    if not sonuc.empty:
        idx = sonuc.index[0]
        okul_adi = df.at[idx, 'OKUL ADI']
        st.info(f"🏫 **Kurum:** {okul_adi}")
        
        with st.form("isg_guncelleme"):
            st.markdown("### 📝 Bilgi Güncelleme")
            
            # Sütun isimleri
            c1 = 'ÖZEL GÜVENLİK GÖREVLİSİ SAYISI'
            c2 = 'SABİT OKUL GÖREVLİSİ (VAR/YOK)'
            c3 = 'ELEKTRONİK İNCELEME CİHAZI (VAR/YOK)'
            c4 = 'GÜVENLİK AMAÇLI TURNİKE (VAR/YOK)'

            def safe_get(col):
                return df.at[idx, col] if pd.notna(df.at[idx, col]) else ""

            v_sayi = st.number_input("Güvenlik Sayısı", min_value=0, 
                                     value=int(df.at[idx, c1]) if str(df.at[idx, c1]).isdigit() else 0)
            
            v_sabit = st.selectbox("Sabit Görevli", ["VAR", "YOK"], index=0 if str(safe_get(c2)).upper() == "VAR" else 1)
            v_cihaz = st.selectbox("E-Cihaz", ["VAR", "YOK"], index=0 if str(safe_get(c3)).upper() == "VAR" else 1)
            v_turnike = st.selectbox("Turnike", ["VAR", "YOK"], index=0 if str(safe_get(c4)).upper() == "VAR" else 1)

            if st.form_submit_button("💾 KAYDET VE GÖNDER", use_container_width=True):
                df.at[idx, c1] = v_sayi
                df.at[idx, c2] = v_sabit
                df.at[idx, c3] = v_cihaz
                df.at[idx, c4] = v_turnike
                
                conn.update(data=df)
                st.cache_data.clear()
                st.balloons()
                st.success("Veriler başarıyla tabloya işlendi!")
    else:
        st.warning("Kurum kodu bulunamadı.")

# Çıkış
if st.sidebar.button("Güvenli Çıkış"):
    st.session_state["auth"] = False
    st.rerun()
