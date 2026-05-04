import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- AYARLAR ---
ANAHTAR_SUTUN = "KURUM KODU"
ORTAK_SIFRE = "İSGVERİ35"

st.set_page_config(page_title="İSG VERİ SİSTEMİ", page_icon="🛡️", layout="centered")

# --- BAŞLIK ---
st.markdown("<h1 style='text-align: center;'>🛡️ İSG VERİ TOPLAMA SİSTEMİ</h1>", unsafe_allow_html=True)

# --- ŞİFRE KONTROLÜ ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    with st.container():
        st.warning("Bu sisteme erişmek için yetkili şifresi gereklidir.")
        girilen_sifre = st.text_input("Sistem Şifresini Giriniz:", type="password")
        if st.button("Giriş Yap"):
            if girilen_sifre == ORTAK_SIFRE:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre! Lütfen tekrar deneyiniz.")
    st.stop()

# --- GOOGLE SHEETS BAĞLANTISI (Şifre Doğruysa Çalışır) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    @st.cache_data(ttl=5)
    def veri_yukle():
        data = conn.read()
        data.columns = [str(c).replace('\n', ' ').strip() for c in data.columns]
        return data.astype(object)

    df = veri_yukle()

except Exception as e:
    st.error(f"⚠️ Bağlantı Hatası: {e}")
    st.info("Secrets ayarlarını ve Google Tablo paylaşım izinlerini kontrol edin.")
    st.stop()

# --- SORGULAMA VE VERİ GİRİŞİ ---
st.subheader("🔍 Kurum Sorgulama")
kurum_kodu = st.text_input("Kurum Kodunu Giriniz:", placeholder="Örn: 776379")

if kurum_kodu:
    df[ANAHTAR_SUTUN] = df[ANAHTAR_SUTUN].astype(str).str.strip()
    sonuc = df[df[ANAHTAR_SUTUN] == kurum_kodu.strip()]
    
    if not sonuc.empty:
        idx = sonuc.index[0]
        st.success(f"🏫 **KURUM:** {df.at[idx, 'OKUL ADI']}")
        
        with st.form("isg_guncelleme_formu"):
            st.markdown("### 📝 Güncel Bilgileri Giriniz")
            
            col1 = 'ÖZEL GÜVENLİK GÖREVLİSİ SAYISI'
            col2 = 'SABİT OKUL GÖREVLİSİ (VAR/YOK)'
            col3 = 'ELEKTRONİK İNCELEME CİHAZI (VAR/YOK)'
            col4 = 'GÜVENLİK AMAÇLI TURNİKE (VAR/YOK)'

            def safe_val(c):
                v = df.at[idx, c]
                return v if pd.notna(v) else ""

            v_g_sayisi = st.number_input("Özel Güvenlik Görevlisi Sayısı", 
                                         min_value=0, 
                                         value=int(df.at[idx, col1]) if str(df.at[idx, col1]).isdigit() else 0)
            
            v_sabit = st.selectbox("Sabit Okul Görevlisi", ["VAR", "YOK"], 
                                   index=0 if str(safe_val(col2)).upper() == "VAR" else 1)
            
            v_cihaz = st.selectbox("Elektronik İnceleme Cihazı", ["VAR", "YOK"], 
                                   index=0 if str(safe_val(col3)).upper() == "VAR" else 1)
            
            v_turnike = st.selectbox("Güvenlik Amaçlı Turnike", ["VAR", "YOK"], 
                                     index=0 if str(safe_val(col4)).upper() == "VAR" else 1)

            if st.form_submit_button("💾 SİSTEME İŞLE VE KAYDET", use_container_width=True):
                df.at[idx, col1] = v_g_sayisi
                df.at[idx, col2] = v_sabit
                df.at[idx, col3] = v_cihaz
                df.at[idx, col4] = v_turnike
                
                conn.update(data=df)
                st.cache_data.clear()
                st.balloons()
                st.success("✅ Veriler başarıyla güncellendi!")
    else:
        st.error("❌ Bu kurum koduna ait bir kayıt bulunamadı.")

# Oturumu Kapat Butonu
if st.sidebar.button("Güvenli Çıkış"):
    st.session_state["auth"] = False
    st.rerun()
