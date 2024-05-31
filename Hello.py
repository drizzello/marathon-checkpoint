import os
import altair as alt
import streamlit as st
from datetime import date
import numpy as np
import pandas as pd
import requests
import strava
import pred_functions as pf
import guidelines
from streamlit_float import *

# Load API Key from environment variable for security
API_KEY = st.secrets["MAILER_LITE_API_KEY"]
MAILERLITE_API_URL = st.secrets["MAILERLITE_API_URL"]

# Page Configuration
st.set_page_config(
    page_title="Maratona CheckPoint",
    page_icon=":runner:",
)

#st.image("https://analytics.gssns.io/pixel.png")
strava_header = strava.header()
strava_auth = strava.authenticate(header=strava_header, stop_if_unauthenticated=False)

if strava_auth is None:
    st.title(":runner: Maratona CheckPoint :stopwatch:")
    st.markdown("Clicca sul tasto \"Connect with Strava\" in alto per effettuare il login con il tuo account strava e cominciare.")
    st.stop()

df = strava.process_strava_data(strava_auth['access_token'])
df_training = df[['start_date_local','name', 'distance_km', 'average_heartrate']]

num_sessions_last_two_weeks = pf.count_recent_sessions(df, 'start_date_local', 2)
num_sessions_last_week = pf.count_recent_sessions(df, 'start_date_local', 1)

# Float feature initialization
float_init()

# Initialize session variable to show/hide Float Box
if "show" not in st.session_state:
    st.session_state.show = True

def show_sidebar():
    with st.sidebar:
        st.markdown("""
            <style>
            .sidebar-button {
                background-color: #F8F9FA;
                color: #404143 !important;
                border: none;
                padding: 10px 10px;
                text-align: center;
                text-decoration: none;
                display: block;
                font-size: 2rm;
                margin: 4px 0;
                cursor: pointer;
                border-radius: 15px;
                box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.1);
                font-weight: bold;
            }
            .sidebar-button:hover {
                background-color: #F8F9FA;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<a href="#tempo_oggi" class="sidebar-button">IL TUO TEMPO MARATONA OGGI 🏃</a>', unsafe_allow_html=True)
        st.markdown('<a href="#ranking" class="sidebar-button">COME TI QUALIFICHERESTI IN UNA MARATONA? 🥇</a>', unsafe_allow_html=True)
        st.markdown('<a href="#tempo_ieri" class="sidebar-button">UN MESE FA COME ERI MESSO? ⏪</a>', unsafe_allow_html=True)
        st.markdown('<a href="#progressi" class="sidebar-button">GUARDA I TUOI PROGRESSI 📈</a>', unsafe_allow_html=True)
        st.markdown('<a href="#tips" class="sidebar-button">QUALCHE CONSIGLIO 📣</a>', unsafe_allow_html=True)
        st.markdown('<a href="#contattaci" class="sidebar-button">UNISCITI A NOI 📝</a>', unsafe_allow_html=True)



def calculate_and_display_predictions(df):
    weekly_km, avg_weekly_pace = pf.weekly_totals(df, "start_date_local", 'distance_km', 'sec_per_km')
    weeks = pd.DataFrame({
        'Settimana': [f"{i+1}" for i in range(len(weekly_km))],
        'Km Totali': weekly_km,
        'Passo Medio': avg_weekly_pace
    })
    weeks['Km Totali Cumulativi'] = weeks['Km Totali'].replace(0, np.nan).expanding().mean()
    weeks['Passo Medio Cumulativo'] = weeks['Passo Medio'].replace(0, np.nan).expanding().mean()
    weeks['Tempo Previsto Maratona_int'] = weeks.apply(
        lambda row: pf.predict_marathon_time(row['Km Totali Cumulativi'], row['Passo Medio Cumulativo']), axis=1
    )
    weeks['Tempo Previsto Maratona'] = weeks['Tempo Previsto Maratona_int'].apply(lambda x: f"{x[0]:02}:{x[1]:02}:{x[2]:02}")
    
    km_per_week = weeks["Km Totali Cumulativi"].iloc[-1]
    previous_pace = weeks["Passo Medio Cumulativo"].iloc[-1]
    pred_hh, pred_mm, pred_ss = pf.predict_marathon_time(km_per_week, previous_pace)
    
    st.title(':runner: IL TUO TEMPO MARATONA OGGI', anchor="tempo_oggi")
    accuracy = pf.accuracy_time_pred(df)
    predicted_time_sec = pf.time_to_seconds(weeks.iloc[-1]['Tempo Previsto Maratona'])
    predicted_pace = pf.marathon_pace_min_per_km(predicted_time_sec)

    col1, col2, col3 = st.columns(3)
    with col2:
        st.title(f"{pred_hh:02}:{pred_mm:02}:{pred_ss:02}", help="Come viene calcolato il tempo?")
        st.caption(f"Passo Gara: {predicted_pace} min/km")
        st.progress(accuracy)
        st.caption(f"Accuratezza previsione: {accuracy}%")
        st.caption("Più corri Più diventa accurato!", help="Accuratezza massima X")
    
    return weeks, predicted_time_sec, pred_hh, pred_mm, pred_ss, predicted_pace

st.cache_data()
def display_ranking(predicted_time_sec):
    marathon_files = [
        ("Milano", "marathon_results/MILANO.xls", "https://www.milanomarathon.it/"),
        ("Venezia", "marathon_results/VENEZIA.xls", "https://www.venicemarathon.it/")
        #("Roma", "marathon_results/ROMA2024.xls", "https://www.runromethemarathon.com/")
    ]
    
    st.title("COME TI QUALIFICHERESTI IN QUESTE 3 MARATONE :first_place_medal:", anchor="ranking")
    col1, col2 = st.columns(2)
    
    for col, (name, file_path, site_path) in zip([col1, col2], marathon_files):
        position, df = strava.marathon_ranking(file_path, predicted_time_sec)
        with col:
            st.header(f"{position}°/{len(df)}")
            st.write(f"Maratona di [{name}]({site_path})")

def display_one_month_ago_progress(weeks, pred_hh, pred_mm, pred_ss):
    # SECTION ONE MONTH AGO OLD MPT
    with st.container():
        if len(weeks) >= 4:
            style_title = "<style>h1 {text-align: center;}</style>"
            st.markdown(style_title, unsafe_allow_html=True)
            st.title(":rewind: UN MESE FA ERI QUI", anchor="tempo_ieri")
            # Three columns with different widths

            col1, old_mpt_column, col2 = st.columns(3)
            st.markdown(style_title, unsafe_allow_html=True)

            with old_mpt_column:
                old_mpt_hh, old_mpt_mm, old_mpt_ss = weeks.iloc[-4]['Tempo Previsto Maratona_int']
                difference_minutes = pf.delta_mpt(old_mpt_hh, old_mpt_mm, old_mpt_ss, pred_hh, pred_mm, pred_ss)
                st.title(f"{old_mpt_hh:02}:{old_mpt_mm:02}:{old_mpt_ss:02}" )
                if difference_minutes < 0:
                    st.write(f":stopwatch: Hai :red[perso] **{str(round(difference_minutes, 0)).split(sep='-')[1]}** minuti.")
                elif difference_minutes == 0:
                    st.write(f":stopwatch: Il tuo tempo non è cambiato.")
                else:
                    st.write(f":stopwatch: Hai :green[conquistato] **{str(round(difference_minutes, 0)).split(sep='-')[1]}** minuti.")

            with col2:
                if difference_minutes > 0:
                    st.title(":green[DAJE!]")
                else:
                    st.title(":green[NON MOLLARE!]")



def display_progress(weeks):
    st.title("GUARDA IL TUO PROGRESSO SETTIMANA PER SETTIMANA :chart_with_upwards_trend:", anchor="progressi")
    
    weeks['Passo Medio (min/km)'] = weeks['Passo Medio'].apply(pf.convert_sec_per_km_to_min_per_km)
    weeks['Passo Medio cumulativo (min/km)'] = weeks['Passo Medio Cumulativo'].apply(pf.convert_sec_per_km_to_min_per_km)
    weeks['predicted_marathon_time_minutes'] = weeks['Tempo Previsto Maratona'].apply(lambda x: sum(int(t) * 60**i for i, t in enumerate(x.split(':')[::-1])))
    
    col = st.columns(3)
    with col[0]:
        show_km_total = st.checkbox(':blue[Mostra Km Totali]', value=True)
    with col[1]:
        show_avg_pace = st.checkbox(':red[Mostra Passo Medio]', value=True)
    with col[2]:
        show_predicted_time = st.checkbox(':green[Mostra Tempo Previsto Maratona (minuti)]', value=True)
    
    base = alt.Chart(weeks).encode(
        alt.X('Settimana:O', axis=alt.Axis(title='Settimana', labelAngle=0))
    )
    layers = []

    if show_km_total:
        line = base.mark_line(color='blue', interpolate='monotone').encode(
            alt.Y('Km Totali:Q', axis=None)
        )
        points = base.mark_point(color='blue', size=100, filled=True).encode(
            alt.Y('Km Totali:Q', axis=None)
        )
        layers.extend([line, points])

    if show_avg_pace:
        line = base.mark_line(color='red', interpolate='monotone').encode(
            alt.Y('Passo Medio:Q', axis=None),
            tooltip=['Settimana', 'Passo Medio (min/km)']
        )
        points = base.mark_point(color='red', size=100, filled=True).encode(
            alt.Y('Passo Medio:Q', axis=None),
            tooltip=['Settimana', 'Passo Medio (min/km)']
        )
        layers.extend([line, points])

    if show_predicted_time:
        line = base.mark_line(color='green', interpolate='monotone').encode(
            alt.Y('predicted_marathon_time_minutes:Q', axis=None),
            tooltip=['Settimana', 'Tempo Previsto Maratona']
        )
        points = base.mark_point(color='green', size=100, filled=True).encode(
            alt.Y('predicted_marathon_time_minutes:Q', axis=None),
            tooltip=['Settimana', 'Tempo Previsto Maratona']
        )
        layers.extend([line, points])

    if layers:
        st.altair_chart(alt.layer(*layers).resolve_scale(y='independent'), use_container_width=True)
        
    with st.expander("Guarda le tabelle con le tue medie settimanali e le tue attività:"): 
        st.dataframe(weeks[["Km Totali", "Passo Medio (min/km)", "Passo Medio cumulativo (min/km)", "Km Totali Cumulativi", "Tempo Previsto Maratona"]])
        st.dataframe(df_training)

def display_tips():
    st.title(":mega: Ecco alcuni consigli per te!", anchor = "tips")
    first_name = strava_auth["athlete"]["firstname"]
    st.write(f"{first_name}, fammi sapere in che data prevedi di correre la tua prossima maratona!")
    
    marathon_date = st.date_input(":point_down:", date.today(), min_value=date.today(), format="DD/MM/YYYY")
    delta_marathon = marathon_date - date.today()
    weeks_to_marathon = delta_marathon.days // 7
    days_remaining = delta_marathon.days % 7
    
    last_week_avg_kms = weeks["Km Totali Cumulativi"].iloc[-1]
    last_weeks_avg_pace = weeks["Passo Medio (min/km)"].iloc[-1]
    frequency = pf.training_frequency(df, weeks)
    
    guidelines.provide_guidelines(weeks_to_marathon, last_week_avg_kms, frequency, last_weeks_avg_pace)



def contact_us_form():
    with st.container():
        st.title("Hai qualche dubbio sul tuo allenamento? Contattaci!:memo:", anchor="contattaci")
        contact_us = st.form("contact")
        with contact_us:
            nome = st.text_input("Inserisci il tuo nome:", placeholder="Nome")
            mail = st.text_input("Inserisci la tua mail:", placeholder="Mail")
            submit_button = st.form_submit_button("Invia")
            
            if submit_button:
                if nome and mail:
                    subscriber_data = {
                        "email": mail,
                        "fields": {
                            "name": nome,
                        }
                    }
                    headers = {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {API_KEY}'
                    }
                    response = requests.post(MAILERLITE_API_URL, json=subscriber_data, headers=headers)
                    if response.status_code in {200, 201}:
                        st.success("Messaggio Inviato!")
                    else:
                        st.error(f"C'è stato un errore, prova a ricaricare la pagina. Error: {response.text}")
                else:
                    st.error("Compila tutti i campi.")

if num_sessions_last_two_weeks >= 6 or num_sessions_last_week >= 4:
    show_sidebar()
    weeks, predicted_time_sec, pred_hh, pred_mm, pred_ss, predicted_pace = calculate_and_display_predictions(df)
    display_ranking(predicted_time_sec)
    display_one_month_ago_progress(weeks, pred_hh, pred_mm, pred_ss)
    display_progress(weeks)
    display_tips()
    contact_us_form()
else:
    st.warning("Non ci sono abbastanza allenamenti recenti per fare una previsione. Torna qui quando avrai almeno 4 allenamenti nell'ultima settimana o 6 nelle ultime 2.")
    contact_us_form()

# Container with expand/collapse button
#button_container = st.container()
#with button_container:
#    if st.session_state.show:
#        if st.button(":wave:", type="primary"):
#            st.session_state.show = False
#            st.rerun()
#    else:
#        if st.button(":wave:", type="primary"):
#            st.session_state.show = True
#            st.rerun()
    
# Alter CSS based on expand/collapse state
#if st.session_state.show:
#    vid_y_pos = "2rem"
#    button_b_pos = "21rem"
#else:
#    vid_y_pos = "-19.5rem"
#    button_b_pos = "1rem"

#button_css = float_css_helper(width="2.2rem", right="2rem", bottom=button_b_pos, transition=0)

# Float button container
#button_container.float(button_css)

# Add Float Box with embedded Youtube video
#float_box('<iframe width="100%" height="100%" src="https://insigh.to/b/maratona-checkpoint" title="Maratona CheckPoint Feedback" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>',width="29rem", right="2rem", bottom=vid_y_pos, css="padding: 0;transition-property: all;transition-duration: .5s;transition-timing-function: cubic-bezier(0, 1, 0.5, 1);", shadow=12)
