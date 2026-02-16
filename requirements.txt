import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="App Validades Google", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
# Nota: O URL da folha deve ser colocado nos "Secrets" do Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES DE DADOS ---
def ler_produtos():
    return conn.read(worksheet="produtos", ttl=0) # ttl=0 força a ler dados frescos

def ler_registos():
    return conn.read(worksheet="registos", ttl=0)

# --- LOGIN (Simplificado) ---
if 'logged_in' not in st.session_state:
    st.title("🔐 Login")
    user = st.text_input("Utilizador")
    if st.button("Entrar"):
        st.session_state.logged_in = True
        st.session_state.perfil = "admin" if user == "admin" else "user"
        st.rerun()

# --- LOGICA ADMIN ---
elif st.session_state.perfil == "admin":
    st.title("🛠 Admin - Google Sheets Mode")
    
    # Criar Novo Produto
    with st.form("add_produto"):
        nome = st.text_input("Nome do Produto")
        desc = st.text_input("Validade Padrão")
        if st.form_submit_button("Gravar no Google Sheets"):
            df_atual = ler_produtos()
            novo_p = pd.DataFrame([{"nome": nome, "descricao": desc}])
            df_final = pd.concat([df_atual, novo_p], ignore_index=True)
            conn.update(worksheet="produtos", data=df_final)
            st.success("Guardado na Nuvem!")

# --- LOGICA USER ---
else:
    st.title("📦 Registo de Equipa")
    df_p = ler_produtos()
    
    produto_sel = st.selectbox("Escolha o Produto", df_p["nome"])
    data_v = st.date_input("Validade")
    sem_hora = st.checkbox("Sem hora")
    
    if st.button("Enviar Registo"):
        df_r = ler_registos()
        novo_r = pd.DataFrame([{
            "produto": produto_sel,
            "data": str(data_v),
            "hora": "N/A" if sem_hora else datetime.now().strftime("%H:%M"),
            "data_registo": datetime.now().strftime("%d/%m/%Y %H:%M")
        }])
        df_f = pd.concat([df_r, novo_r], ignore_index=True)
        conn.update(worksheet="registos", data=df_f)
        st.success("Registo enviado para o Google Sheets!")
