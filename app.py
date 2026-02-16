import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÕES E FICHEIROS ---
ARQUIVO_PRODUTOS = "produtos.csv"
ARQUIVO_REGISTOS = "registos_validade.csv"

def carregar_dados(arquivo, colunas):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return pd.DataFrame(columns=colunas)

def guardar_dados(df, arquivo):
    df.to_csv(arquivo, index=False)

# --- INICIALIZAÇÃO ---
st.set_page_config(page_title="Gestor de Validades Pro", layout="wide")

# Carregar dados existentes
if 'df_produtos' not in st.session_state:
    st.session_state.df_produtos = carregar_dados(ARQUIVO_PRODUTOS, ["nome", "descricao"])
if 'df_registos' not in st.session_state:
    st.session_state.df_registos = carregar_dados(ARQUIVO_REGISTOS, ["produto", "data", "hora", "data_registo"])

# --- INTERFACE DE LOGIN ---
def login():
    st.title("🔐 Login de Equipa")
    user = st.text_input("Utilizador")
    pw = st.text_input("Password", type="password")
    if st.button("Entrar"):
        if user == "admin" and pw == "admin123":
            st.session_state.logged_in = True
            st.session_state.perfil = "admin"
            st.rerun()
        elif user == "user" and pw == "user123":
            st.session_state.logged_in = True
            st.session_state.perfil = "user"
            st.rerun()
        else:
            st.error("Dados inválidos!")

# --- PAINEL ADMIN ---
def interface_admin():
    st.title("🛠 Gestão Administrativa")
    tab1, tab2 = st.tabs(["➕ Cadastrar Produtos", "📊 Dashboard de Controlo"])

    with tab1:
        with st.form("novo_produto"):
            nome = st.text_input("Nome do Produto")
            desc = st.text_input("Tempo de vida (ex: 30 dias)")
            submeter = st.form_submit_button("Gravar Produto")
            
            if submeter and nome:
                nova_linha = pd.DataFrame([{"nome": nome, "descricao": desc}])
                st.session_state.df_produtos = pd.concat([st.session_state.df_produtos, nova_linha], ignore_index=True)
                guardar_dados(st.session_state.df_produtos, ARQUIVO_PRODUTOS)
                st.success("Produto guardado no ficheiro!")

    with tab2:
        st.subheader("Histórico de Registos")
        st.dataframe(st.session_state.df_registos, use_container_width=True)
        # Botão para o Admin baixar o relatório
        csv = st.session_state.df_registos.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descarregar Excel (CSV)", csv, "relatorio_validades.csv", "text/csv")

# --- PAINEL USER ---
def interface_user():
    st.title("📦 Registo de Validade")
    if st.session_state.df_produtos.empty:
        st.info("Nenhum produto disponível. Contacte o Admin.")
        return

    produto_sel = st.selectbox("Selecione o Produto", st.session_state.df_produtos["nome"])
    data_val = st.date_input("Data de Validade")
    sem_hora = st.checkbox("Registar sem hora")
    hora_val = st.time_input("Hora") if not sem_hora else "00:00"

    if st.button("Submeter Registo"):
        novo_registo = pd.DataFrame([{
            "produto": produto_sel,
            "data": data_val,
            "hora": "N/A" if sem_hora else hora_val,
            "data_registo": datetime.now().strftime("%d/%m/%Y %H:%M")
        }])
        st.session_state.df_registos = pd.concat([st.session_state.df_registos, novo_registo], ignore_index=True)
        guardar_dados(st.session_state.df_registos, ARQUIVO_REGISTOS)
        st.success(f"Registo de {produto_sel} efetuado!")

# --- LÓGICA PRINCIPAL ---
if 'logged_in' not in st.session_state:
    login()
else:
    if st.sidebar.button("Terminar Sessão"):
        st.session_state.clear()
        st.rerun()
    
    if st.session_state.perfil == "admin":
        interface_admin()
    else:
        interface_user()
