import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- AYARLAR ---
ANAHTAR_SUTUN = "KURUM KODU"

st.set_page_config(page_title="İSG VERİ SİSTEMİ", page_icon="🛡️")

# Başlık ve Açıklama
st.title("🛡️ İSG VERİ TOPLAMA SİSTEMİ")
st.info("Lütfen kurum kodunuzu girerek bilgilerinizi güncelleyiniz. Hatalı giriş yaparsanız doğru bilgileri yazıp tekrar göndermeniz yeterlidir.")

# Google Sheets Bağlantısı
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5) # Hızlı güncelleme için cache süresini düşürdük
def veri_getir():
    data = conn.read()
    data.columns = [str(c).replace('\n', ' ').strip() for c in data.columns]
    data = data.astype(object)
    return data

try:
    df = veri_getir()
except Exception as e:
    st.error("⚠️ Veri tabanına bağlanılamadı. Lütfen internet bağlantınızı veya sistem ayarlarını kontrol edin.")
    st.stop()

# --- KURUM SORGULAMA BÖLÜMÜ ---
st.subheader("🔍 Kurum Sorgulama")
col_input, col_button = st.columns([3, 1])

with col_input:
    kurum_kodu = st.text_input("Kurum Kodunu Yazınız:", placeholder="Örn: 776379", label_visibility="collapsed")

with col_button:
    sorgula = st.button("✅ KURUMLARI GETİR", use_container_width=True)

# Sorgulama tetiklendiğinde veya kod girildiğinde
if kurum_kodu:
    df[ANAHTAR_SUTUN] = df[ANAHTAR_SUTUN].astype(str).str.strip()
    sonuc = df[df[ANAHTAR_SUTUN] == kurum_kodu.strip()]
    
    if not sonuc.empty:
        idx = sonuc.index[0]
        st.success(f"🏫 **KURUM:** {df.at[idx, 'OKUL ADI']}")
        st.divider()
        
        # --- VERİ GİRİŞ FORMU ---
        with st.form("isg_guncelleme_formu"):
            st.markdown("### 📝 Güncel Bilgileri Giriniz")
            
            col1_name = 'ÖZEL GÜVENLİK GÖREVLİSİ SAYISI'
            col2_name = 'SABİT OKUL GÖREVLİSİ (VAR/YOK)'
            col3_name = 'ELEKTRONİK İNCELEME CİHAZI (VAR/YOK)'
            col4_name = 'GÜVENLİK AMAÇLI TURNİKE (VAR/YOK)'

            def get_val(column):
                val = df.at[idx, column]
                return val if pd.notna(val) else ""

            g_sayisi = st.number_input("Özel Güvenlik Görevlisi Sayısı", 
                                       min_value=0,
                                       value=int(df.at[idx, col1_name]) if pd.notna(df.at[idx, col1_name]) and str(df.at[idx, col1_name]).isdigit() else 0)
            
            sabit = st.selectbox("Sabit Okul Görevlisi", ["VAR", "YOK"], 
                                 index=0 if str(get_val(col2_name)).upper() == "VAR" else 1)
            
            cihaz = st.selectbox("Elektronik İnceleme Cihazı", ["VAR", "YOK"], 
                                 index=0 if str(get_val(col3_name)).upper() == "VAR" else 1)
            
            turnike = st.selectbox("Güvenlik Amaçlı Turnike", ["VAR", "YOK"], 
                                   index=0 if str(get_val(col4_name)).upper() == "VAR" else 1)
            
            # Form Gönderme Butonu
            submit = st.form_submit_button("💾 SİSTEME İŞLE VE KAYDET", use_container_width=True)
            
            if submit:
                # Verileri DataFrame'e işle (Üzerine yazar)
                df.at[idx, col1_name] = g_sayisi
                df.at[idx, col2_name] = sabit
                df.at[idx, col3_name] = cihaz
                df.at[idx, col4_name] = turnike
                
                # Google Sheets Güncelleme
                conn.update(data=df)
                st.cache_data.clear()
                
                # Onay Mesajları
                st.balloons()
                st.info(f"✅ KAYDEDİLDİ: {df.at[idx, 'OKUL ADI']} verileri başarıyla güncellenmiştir.")
                st.toast("Veritabanı güncellendi!", icon='💾')
    else:
        if sorgula:
            st.error("❌ Hata: Bu kurum koduna ait bir okul bulunamadı. Lütfen kodu kontrol ediniz.")

# Admin Paneli (Opsiyonel - Alt kısımda gizli)
with st.expander("📊 Mevcut Veri Durumu (Yalnızca Görüntüleme)"):
    st.dataframe(df)
