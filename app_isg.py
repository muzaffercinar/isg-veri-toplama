import streamlit as st
import pandas as pd
import os

# Ayarlar
DOSYA_YOLU = "öncelikdereceliokulbilgi.xls"
ANAHTAR_SUTUN = "KURUM KODU"

st.set_page_config(page_title="İSG VERİ TOPLAMA", page_icon="🛡️")
st.title("🛡️ İSG VERİ TOPLAMA")

def veri_yukle():
    if os.path.exists(DOSYA_YOLU):
        return pd.read_excel(DOSYA_YOLU)
    return None

df = veri_yukle()

if df is not None:
    kurum_kodu = st.text_input("Kurum Kodu:", placeholder="Örn: 776379")
    if kurum_kodu:
        df[ANAHTAR_SUTUN] = df[ANAHTAR_SUTUN].astype(str).str.strip()
        sonuc = df[df[ANAHTAR_SUTUN] == kurum_kodu.strip()]
        if not sonuc.empty:
            idx = sonuc.index[0]
            st.success(f"Kurum: {df.at[idx, 'OKUL ADI']}")
            # Form alanları... (Önceki kodun devamı)
            with st.form("isg_form"):
                g_sayisi = st.number_input("Özel Güvenlik Görevlisi Sayısı", min_value=0, value=0)
                submit = st.form_submit_button("Güncelle")
                if submit:
                    df.at[idx, 'ÖZEL GÜVENLİK \nGÖREVLİSİ SAYISI'] = g_sayisi
                    df.to_excel(DOSYA_YOLU, index=False)
                    st.success("Kayıt güncellendi!")
