import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- AYARLAR ---
ANAHTAR_SUTUN = "KURUM KODU"
ORTAK_SIFRE = "İSGVERİ35" 

st.set_page_config(page_title="İSG VERİ TOPLAMA", page_icon="🛡️", layout="centered")

# --- BAŞLIK ---
st.markdown("<h1 style='text-align: center;'>🛡️ İSG VERİ TOPLAMA SİSTEMİ</h1>", unsafe_allow_html=True)

# --- 1. ADIM: ANA EKRANDA ŞİFRE KONTROLÜ ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("---")
    # Şifre kutusunu merkeze almak için sütunlar kullanıyoruz
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Yetkili Girişi")
        girilen_sifre = st.text_input("Lütfen Sistem Şifresini Giriniz:", type="password", help="Verilere erişmek için yetkili şifresi gereklidir.")
        
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if girilen_sifre == ORTAK_SIFRE:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre! Tekrar deneyiniz.")
    
    st.info("⚠️ Not: Veri girişi yapabilmek için önce şifre doğrulaması yapmalısınız.")
    st.stop()

# --- 2. ADIM: GOOGLE SHEETS BAĞLANTISI (Şifreden Sonra) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    @st.cache_data(ttl=5)
    def veri_yukle():
        data = conn.read()
        # Sütun isimlerindeki gizli boşluk ve alt satırları temizle
        data.columns = [str(c).replace('\n', ' ').strip() for c in data.columns]
        return data.astype(object)

    df = veri_yukle()
except Exception as e:
    st.error(f"Veri tabanına bağlanılamadı. Lütfen internetinizi veya Secrets ayarlarını kontrol edin.")
    st.stop()

# --- 3. ADIM: KURUM SORGULAMA VE FORM ---
st.success("✅ Erişim Onaylandı. Kurum bilgilerinizi sorgulayabilirsiniz.")
kurum_kodu = st.text_input("Kurum Kodunuzu Giriniz:", placeholder="Örn: 776379")

if kurum_kodu:
    df[ANAHTAR_SUTUN] = df[ANAHTAR_SUTUN].astype(str).str.strip()
    sonuc = df[df[ANAHTAR_SUTUN] == kurum_kodu.strip()]
    
    if not sonuc.empty:
        idx = sonuc.index[0]
        okul_adi = df.at[idx, 'OKUL ADI']
        st.info(f"🏫 **Kurum:** {okul_adi}")
        
        with st.form("isg_veri_formu"):
            st.markdown("### 📝 Bilgi Güncelleme Formu")
            
            # Tablo sütun isimleri
            c1 = 'ÖZEL GÜVENLİK GÖREVLİSİ SAYISI'
            c2 = 'SABİT OKUL GÖREVLİSİ (VAR/YOK)'
            c3 = 'ELEKTRONİK İNCELEME CİHAZI (VAR/YOK)'
            c4 = 'GÜVENLİK AMAÇLI TURNİKE (VAR/YOK)'

            # Mevcut veriyi çekme fonksiyonu
            def get_old(col):
                return df.at[idx, col] if pd.notna(df.at[idx, col]) else ""

            v_sayi = st.number_input("Güvenlik Görevlisi Sayısı", min_value=0, 
                                     value=int(df.at[idx, c1]) if str(df.at[idx, c1]).isdigit() else 0)
            
            v_sabit = st.selectbox("Sabit Okul Görevlisi", ["VAR", "YOK"], 
                                   index=0 if str(get_old(c2)).upper() == "VAR" else 1)
            
            v_cihaz = st.selectbox("Elektronik İnceleme Cihazı", ["VAR", "YOK"], 
                                   index=0 if str(get_old(c3)).upper() == "VAR" else 1)
            
            v_turnike = st.selectbox("Güvenlik Amaçlı Turnike", ["VAR", "YOK"], 
                                     index=0 if str(get_old(c4)).upper() == "VAR" else 1)

            if st.form_submit_button("💾 BİLGİLERİ KAYDET VE GÜNCELLE", use_container_width=True):
                # DataFrame güncelle
                df.at[idx, c1] = v_sayi
                df.at[idx, c2] = v_sabit
                df.at[idx, c3] = v_cihaz
                df.at[idx, c4] = v_turnike
                
                # Google Sheets güncelle
                conn.update(data=df)
                st.cache_data.clear()
                st.balloons()
                st.success(f"Başarılı! {okul_adi} verileri sisteme işlendi.")
    else:
        st.warning("Bu kurum koduna ait bir kayıt bulunamadı. Lütfen kodu kontrol ediniz.")

# Güvenli Çıkış Butonu
st.sidebar.markdown("---")
if st.sidebar.button("Oturumu Kapat"):
    st.session_state["auth"] = False
    st.rerun()
