pip install streamlit mysql-connector-python

import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Configuração da conexão com o banco de dados
def create_connection():
    return mysql.connector.connect(
        host="MU.Fest",
        user="root",
        password="0606",
        database="MU_Fest"
    )

# Função para verificar login
def check_login(email, senha):
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM usuarios WHERE email = %s AND senha = %s"
    cursor.execute(query, (email, senha))
    user = cursor.fetchone()
    conn.close()
    return user

# Função para visualizar eventos
def get_eventos(tipo=None):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM eventos"
    if tipo:
        query += " WHERE id_tipo = %s ORDER BY data, horario"
        cursor.execute(query, (tipo,))
    else:
        query += " ORDER BY data, horario"
        cursor.execute(query)
    eventos = cursor.fetchall()
    conn.close()
    return eventos

# Função para obter tipos de eventos
def get_tipos():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM tipo"
    cursor.execute(query)
    tipos = cursor.fetchall()
    conn.close()
    return tipos

# Função para adicionar evento
def add_evento(nome, data, horario, localizacao, descricao, onde_comprar, id_tipo, id_usuario):
    conn = create_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO eventos (nome, data, horario, localizacao, descricao, onde_comprar, id_tipo, id_usuario)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (nome, data, horario, localizacao, descricao, onde_comprar, id_tipo, id_usuario))
    conn.commit()
    conn.close()

# Função para adicionar avaliação
def add_avaliacao(nota, comentario, id_evento, id_usuario):
    conn = create_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO avaliacao (nota, comentario, id_evento, id_usuario)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (nota, comentario, id_evento, id_usuario))
    conn.commit()
    conn.close()

# Função para adicionar denúncia
def add_denuncia(justificativa, id_usuario, id_evento):
    conn = create_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO denuncia (justificativa, id_usuario, id_evento)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (justificativa, id_usuario, id_evento))
    conn.commit()
    conn.close()

# Configuração da interface do Streamlit
st.set_page_config(page_title="MU Fest")
st.image("mu_fest.png")
st.title("Bem-vindo ao MU.Fest!")
st.write("Se conecte aos melhores eventos e aproveite ao máximo todas as experiências!")

# Login
st.title("Login")
email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Login"):
    user = check_login(email, senha)
    if user:
        st.success(f"Bem-vindo {user[1]}!")
        st.session_state["user"] = user
    else:
        st.error("Email ou senha inválidos.")

# Se o usuário estiver logado
if "user" in st.session_state:
    user = st.session_state["user"]

    # Exibir eventos
    st.title("Eventos")
    tipos = get_tipos()
    tipo_evento = st.selectbox("Filtrar por tipo de evento", [None] + [tipo["tipo"] for tipo in tipos])
    tipo_id = None
    for tipo in tipos:
        if tipo["tipo"] == tipo_evento:
            tipo_id = tipo["id_tipo"]
            break

    eventos = get_eventos(tipo_id)
    for evento in eventos:
        st.subheader(evento["nome"])
        st.write(f"Data: {evento['data']} Horário: {evento['horario']}")
        st.write(f"Localização: {evento['localizacao']}")
        st.write(f"Descrição: {evento['descricao']}")
        st.write(f"Onde comprar: {evento['onde_comprar']}")

    # Adicionar novo evento
    st.title("Adicionar Evento")
    with st.form("form_evento"):
        nome = st.text_input("Nome")
        data = st.date_input("Data")
        horario = st.time_input("Horário")
        localizacao = st.text_input("Localização")
        descricao = st.text_area("Descrição")
        onde_comprar = st.text_input("Onde comprar")
        tipo_evento = st.selectbox("Tipo de Evento", [tipo["tipo"] for tipo in tipos])
        tipo_id = None
        for tipo in tipos:
            if tipo["tipo"] == tipo_evento:
                tipo_id = tipo["id_tipo"]
                break
        submitted = st.form_submit_button("Adicionar Evento")
        if submitted:
            add_evento(nome, data, horario, localizacao, descricao, onde_comprar, tipo_id, user[0])
            st.success("Evento adicionado com sucesso!")

    # Adicionar avaliação
    st.title("Adicionar Avaliação")
    with st.form("form_avaliacao"):
        nota = st.slider("Nota", 1, 10)
        comentario = st.text_area("Comentário")
        evento_id = st.selectbox("Evento", [evento["id_evento"] for evento in eventos])
        submitted = st.form_submit_button("Adicionar Avaliação")
        if submitted:
            add_avaliacao(nota, comentario, evento_id, user[0])
            st.success("Avaliação adicionada com sucesso!")

    # Adicionar denúncia
    st.title("Adicionar Denúncia")
    with st.form("form_denuncia"):
        justificativa = st.text_area("Justificativa")
        evento_id = st.selectbox("Evento", [evento["id_evento"] for evento in eventos], key="denuncia_evento")
        submitted = st.form_submit_button("Adicionar Denúncia")
        if submitted:
            add_denuncia(justificativa, user[0], evento_id)
            st.success("Denúncia adicionada com sucesso!")
            
