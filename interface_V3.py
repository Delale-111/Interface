import streamlit as st
import pandas as pd
import time
import smtplib
import string
import random
import json
from streamlit_lottie import st_lottie

def load_data():
    base_statuts = pd.read_csv('BASE_STATUTS.csv', delimiter=";")
    return base_statuts

def update_status(id, new_status):
    base_statuts = pd.read_csv('BASE_STATUTS.csv', delimiter=";")
    base_statuts.loc[base_statuts['etalab'] == id, 'STATUT'] = new_status
    base_statuts.to_csv('BASE_STATUTS.csv', index=False, sep=';')

def authenticate_user(username, password):
    data = pd.read_excel('data_identifiants.xlsx')
    return any((data['IDENTIFIANT'] == username) & (data['MOT_DE_PASSE'] == password))

def check_username_exists(username):
    data = pd.read_csv('data_identifiants.csv', delimiter=";")
    return username in data['IDENTIFIANT'].values

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def update_password(username, new_password):
    data = pd.read_csv('data_identifiants.csv', delimiter=";")
    data.loc[data['IDENTIFIANT'] == username, 'MOT_DE_PASSE'] = new_password
    data.to_csv('data_identifiants.csv', index=False, sep=';')

def send_email(recipient, new_password):
    sender = 'jamesamigo15@outlook.fr'
    sender_password = 'Jamesamigo@15'
    subject = 'Votre nouveau mot de passe'
    body = f'Votre nouveau mot de passe est: {new_password}'
    message = f"""From: {sender}
To: {recipient}
Subject: {subject}

{body}
"""
    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(sender, sender_password)
        server.sendmail(sender, recipient, message)
        server.quit()
        return True
    except smtplib.SMTPException as e:
        st.error(f"Erreur SMTP : {e}")
        return False
    except Exception as e:
        st.error(f"Erreur générale : {e}")
        return False

st.set_page_config(layout='wide')
logo_url = "https://static.wixstatic.com/media/fec599_660c83d77fb24e00a5d45828056b063c~mv2.png"
st.image(logo_url, width=200)
col1, col2 = st.columns([3, 1])

with col2:
    with open("robo.json", "r") as file:
        data_oracle = json.load(file)
    st_lottie(data_oracle, height=400, key="oracle")

with col1:
    if 'auth_success' not in st.session_state:
        st.session_state.auth_success = False
        st.session_state.username_input = ''

    if not st.session_state.auth_success:
        st.header('Authentification', divider='rainbow')
        username_input = st.text_input('Identifiant :')
        password_input = st.text_input('Mot de passe :', type='password')
        if st.button('Se connecter'):
            if authenticate_user(username_input, password_input):
                st.success('Connexion réussie!')
                st.session_state.auth_success = True
                st.session_state.username_input = username_input
            else:
                st.error('Identifiant ou mot de passe incorrect. Veuillez réessayer.')
        st.subheader('Réinitialisation du mot de passe')
        reset_username = st.text_input('Entrez votre identifiant pour réinitialiser le mot de passe :')
        if st.button('Réinitialiser le mot de passe'):
            if check_username_exists(reset_username):
                new_password = generate_random_password()
                update_password(reset_username, new_password)
                if send_email(reset_username, new_password):
                    st.success('Un nouveau mot de passe a été envoyé à votre adresse email.')
                else:
                    st.error('Erreur lors de l\'envoi de l\'email. Veuillez réessayer.')
            else:
                st.error('Identifiant non trouvé.')
    else:
        st.header(f'Bienvenue {st.session_state.username_input}', divider='rainbow')
        data = load_data()
        if data is not None:
            selected_id = st.selectbox("Choisir l'établissement", data['etalab'])
            current_status = data[data['etalab'] == selected_id]['STATUT'].values[0]
            st.markdown(f"Statut initial : <span style='color: blue;'>{current_status}</span>", unsafe_allow_html=True)
            new_status = st.selectbox("Changement de statut", ['OUVERT', 'FERME'])
            if st.button('Mettre à jour'):
                update_status(selected_id, new_status)
                time.sleep(1)
                data = load_data()
                current_status = data[data['etalab'] == selected_id]['STATUT'].values[0]
                st.success(f"Statut actuel : {current_status}")
        if st.button('Se déconnecter'):
            st.session_state.auth_success = False
            st.session_state.username_input = ''
            st.experimental_rerun()
