import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- AYARLAR ---
ANAHTAR_SUTUN = "KURUM KODU"
ORTAK_SIFRE = "İSGVERİ35"

st.set_page_config(page_title="İSG VERİ SİSTEMİ", page_icon="🛡️", layout="centered")

# --- BAŞLIK ---
st.markdown("<h1 style='text-align: center;'>🛡️ İSG VERİ TOPLAMA SİSTEMİ</h1>", unsafe_allow_html=True)

# --- ŞİFRE KONTROLÜ (Session State ile) ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    with st.container():
        st.warning("Lütfen sisteme erişmek için yetkili şifresini giriniz.")
        girilen_sifre = st.text_input("Sistem Şifresi:", type="password")
        if st.button("Giriş Yap"):
            if girilen_sifre == ORTAK_SIFRE:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre!")
    st.stop()

# --- GOOGLE SHEETS BAĞLANTISI ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    @st.cache_data(ttl=5)
    def veri_yukle():
        data = conn.read()
        # Başlıkları temizle (Gizli Enter ve boşluklar için)
        data.columns = [str(c).replace('\n', ' ').strip() for c in data.columns]
        return data.astype(object)

    df = veri_yukle()

except Exception as e:
    st.error(f"⚠️ Bağlantı Hatası: {e}")
    st.info("Lütfen Secrets ayarlarındaki linki ve Google Tablo paylaşım izinlerini kontrol edin.")
    st.stop()

# --- KURUM SORGULAMA ---
st.subheader("🔍 Kurum Sorgulama")
kurum_kodu = st.text_input("Kurum Kodunu Giriniz:", placeholder="Örn: 776379")

if kurum_kodu:
    df[ANAHTAR_SUTUN] = df[ANAHTAR_SUTUN].astype(str).str.strip()
    sonuc = df[df[ANAHTAR_SUTUN] == kurum_kodu.strip()]
    
    if not sonuc.empty:
        idx = sonuc.index[0]
        st.success(f"🏫 **KURUM:** {df.at[idx, 'OKUL ADI']}")
        
        with st.form("isg_final_form"):
            st.markdown("### 📝 Bilgi Güncelleme")
            
            c1 = 'ÖZEL GÜVENLİK GÖREVLİSİ SAYISI'
            c2 = 'SABİT OKUL GÖREVLİSİ (VAR/YOK)'
            c3 = 'ELEKTRONİK İNCELEME CİHAZI (VAR/YOK)'
            c4 = 'GÜVENLİK AMAÇLI TURNİKE (VAR/YOK)'

            def g_val(col):
                val = df.at[idx, col]
                return val if pd.notna(val) else ""

            v1 = st.number_input("Güvenlik Sayısı", min_value=0, 
                                 value=int(df.at[idx, c1]) if str(df.at[idx, c1]).isdigit() else 0)
            v2 = st.selectbox("Sabit Görevli", ["VAR", "YOK"], index=0 if str(g_val(c2)).upper() == "VAR" else 1)
            v3 = st.selectbox("E-İnceleme Cihazı", ["VAR", "YOK"], index=0 if str(g_val(c3)).upper() == "VAR" else 1)
            v4 = st.selectbox("Turnike", ["VAR", "YOK"], index=0 if str(g_val(c4)).upper() == "VAR" else 1)

            if st.form_submit_button("💾 KAYDET"):
                df.at[idx, c1] = v1
                df.at[idx, c2] = v2
                df.at[idx, c3] = v3
                df.at[idx, c4] = v4
                
                conn.update(data=df)
                st.cache_data.clear()
                st.balloons()
                st.success(f"✅ {df.at[idx, 'OKUL ADI']} verileri güncellendi.")
    else:
        st.error("❌ Kurum kodu bulunamadı.")

# Çıkış Butonu
if st.sidebar.button("Güvenli Çıkış"):
    st.session_state["auth"] = False
    st.rerun()
