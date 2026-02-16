import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="Gestor de Validades", layout="wide")

# Simulação de Base de Dados (Em produção, usaríamos um ficheiro SQL ou CSV)
if 'produtos' not in st.session_state:
    st.session_state.produtos = []
if 'registos' not in st.session_state:
    st.session_state.registos = []

# --- FUNÇÕES DE LOGIN ---
def login():
    st.title("🔐 Acesso à Equipa")
    utilizador = st.text_input("Utilizador")
    senha = st.text_input("Password", type="password")
    
    if st.button("Entrar"):
        if utilizador == "admin" and senha == "admin123":
            st.session_state.logged_in = True
            st.session_state.perfil = "admin"
            st.rerun()
        elif utilizador == "user" and senha == "user123":
            st.session_state.logged_in = True
            st.session_state.perfil = "user"
            st.rerun()
        else:
            st.error("Credenciais incorretas")

# --- INTERFACE ADMIN ---
def interface_admin():
    st.header("🛠 Painel Administrativo")
    
    tab1, tab2 = st.tabs(["Cadastrar Produto", "Dashboard"])
    
    with tab1:
        st.subheader("Novo Produto")
        nome = st.text_input("Nome do Produto")
        desc = st.text_area("Descrição/Vida Útil")
        foto = st.file_uploader("Carregar Foto", type=['png', 'jpg', 'jpeg'])
        
        if st.button("Guardar Produto"):
            st.session_state.produtos.append({"nome": nome, "desc": desc, "foto": foto})
            st.success(f"Produto {nome} criado!")

    with tab2:
        st.subheader("Gestão de Dados")
        if st.session_state.registos:
            df = pd.DataFrame(st.session_state.registos)
            st.table(df)
        else:
            st.info("Ainda não existem registos de validades.")

# --- INTERFACE USER ---
def interface_user():
    st.header("📦 Registo de Validades")
    
    if not st.session_state.produtos:
        st.warning("O Admin ainda não cadastrou produtos.")
        return

    # Seleção por foto (Simulada por colunas)
    cols = st.columns(3)
    for idx, prod in enumerate(st.session_state.produtos):
        with cols[idx % 3]:
            if prod['foto']:
                st.image(prod['foto'], width=150)
            if st.button(f"Selecionar {prod['nome']}", key=idx):
                st.session_state.selecionado = prod['nome']

    if 'selecionado' in st.session_state:
        st.divider()
        st.subheader(f"Registar: {st.session_state.selecionado}")
        
        data_val = st.date_input("Data de Validade")
        sem_hora = st.checkbox("Registar sem hora")
        
        hora_val = None
        if not sem_hora:
            hora_val = st.time_input("Hora de Validade")
            
        if st.button("Confirmar Registo"):
            novo_registo = {
                "produto": st.session_state.selecionado,
                "data": data_val,
                "hora": hora_val if not sem_hora else "N/A",
                "timestamp": datetime.now()
            }
            st.session_state.registos.append(novo_registo)
            st.success("Registo guardado com sucesso!")

# --- FLUXO PRINCIPAL ---
if 'logged_in' not in st.session_state:
    login()
else:
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()
        
    if st.session_state.perfil == "admin":
        interface_admin()
    else:
        interface_user()
