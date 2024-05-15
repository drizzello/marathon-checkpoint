import base64
import altair as alt
import streamlit as st
import strava
from pandas.api.types import is_numeric_dtype
import pred_functions as pf
import pandas as pd
import guidelines
from datetime import datetime, date
import  numpy as np


st.set_page_config(
    page_title="Maratona CheckPoint",
    page_icon=":runner:",
)

st.image("https://analytics.gssns.io/pixel.png")

strava_header = strava.header()

strava_auth = strava.authenticate(header=strava_header, stop_if_unauthenticated=False)

if strava_auth is None:

    st.title(":runner: Maratona CheckPoint :stopwatch:")
    st.markdown("Clicca sul tasto \"Connect with Strava\" in alto per effettuare il login con il tuo account strava e cominciare.")
    st.image(
        "https://files.gssns.io/public/streamlit-activity-viewer-demo.gif",
        caption="Streamlit Activity Viewer demo",
        use_column_width="always",
    )
    st.stop()


df = strava.process_strava_data(strava_auth['access_token'])

num_sessions_last_two_weeks = pf.count_recent_sessions(df, 'start_date_local', 2)
num_sessions_last_week = pf.count_recent_sessions(df, 'start_date_local', 1)

# Verify condition: at least 6 sessions in last two weeks or 4 in last week
if num_sessions_last_two_weeks >= 1 or num_sessions_last_week >= 4:
    # Creating a DataFrame for cumulative data
    weekly_km, avg_weekly_pace = pf.weekly_totals(df,"start_date_local", 'distance_km', 'sec_per_km')
    weeks = pd.DataFrame({
         'Settimana': [f"{i+1}" for i in range(len(weekly_km))],
         'Km Totali': weekly_km,
         'Passo Medio': avg_weekly_pace
   })


    # Calcolo delle medie cumulative
    weeks['Km Totali Cumulativi'] = weeks['Km Totali'].replace(0, np.nan).expanding().mean()
    weeks['Passo Medio Cumulativo'] = weeks['Passo Medio'].replace(0, np.nan).expanding().mean()

    # Applicazione della funzione di previsione
    weeks['Tempo Previsto Maratona_int'] = weeks.apply(
        lambda row: pf.predict_marathon_time(row['Km Totali Cumulativi'], row['Passo Medio Cumulativo']), axis=1
    )

    # Converting hours, minutes, seconds to a string format if needed for display
    weeks['Tempo Previsto Maratona'] = weeks['Tempo Previsto Maratona_int'].apply(lambda x: f"{x[0]:02}:{x[1]:02}:{x[2]:02}")
    km_per_week = weeks["Km Totali Cumulativi"].iloc[-1]  # kilometers run per week
    previous_pace = weeks["Passo Medio Cumulativo"].iloc[-1]  # previous pace in seconds per kilometer
    pred_hh, pred_mm, pred_ss= pf.predict_marathon_time(km_per_week, previous_pace)

    with st.sidebar:
        link1 = st.header("[:orange[Il tuo tempo maratona oggi :runner:]](#tempo_oggi)")
        link2 = st.header("[:orange[Come ti qualificheresti in una maratona? :first_place_medal:]](#ranking)")
        link3 = st.header("[:orange[Un mese fa come eri messo? :rewind:]](#tempo_ieri)")
        link4 = st.header("[:orange[Guarda i tuoi progressi :chart_with_upwards_trend:]](#progressi)")
        link5 = st.header("[:orange[Vai alle tips :mega:]](#tips)")
        link6 = st.header("[:orange[Contattaci :memo:]](#contattaci)")

    with st.container():
        st.markdown("<a id='home'></a>", unsafe_allow_html=True)
        style_title = "<style>h1 {text-align: center;}</style>"
        st.markdown(style_title, unsafe_allow_html=True)
        st.title(':runner: IL TUO TEMPO MARATONA OGGI', anchor="tempo_oggi")
        # Three columns with different widths

        accuracy_column, mpt_column, how_column = st.columns(3)
        style_time = "<style>h1 {text-align: center;}</style>"
        st.markdown(style_time,unsafe_allow_html=True)


        with mpt_column:
                st.title(f"{pred_hh:02}:{pred_mm:02}:{pred_ss:02}", help="Come viene calcolato il tempo?")
                accuracy = pf.accuracy_time_pred(df)
                text_accuracy = "Accuratezza previsione: "+str(accuracy)+"%"
                bar = st.progress(accuracy)
                st.caption(text_accuracy)
                st.caption("Più corri Più diventa accurato!", help = "Accuratezza massima X")


    weeks["predicted_marathon_time_in_seconds"] = weeks['Tempo Previsto Maratona'].apply(pf.time_to_seconds) 
    predicted_time_sec = weeks.iloc[-1]['predicted_marathon_time_in_seconds']


    df_venezia = pd.read_excel("/Users/daviderizzello/Documents/Progetto_AI/Running_AI/Marathon_Results/VENEZIA.xls")
    df_venezia["tempo_sec"] = df_venezia['TEMPO_UFFICIALE'].apply(pf.time_to_seconds)   
    df_venezia['position'] = df_venezia['tempo_sec'].rank(method='min').astype(int)
    predicted_position_venezia = (df_venezia['tempo_sec'] < predicted_time_sec).sum() + 1

    df_milano = pd.read_excel("/Users/daviderizzello/Documents/Progetto_AI/Running_AI/Marathon_Results/MILANO.xls")
    df_milano["tempo_sec"] = df_milano['TEMPO_UFFICIALE'].apply(pf.time_to_seconds)   
    df_milano['position'] = df_milano['tempo_sec'].rank(method='min').astype(int)
    predicted_position_milano = (df_milano['tempo_sec'] < predicted_time_sec).sum() + 1

    df_roma = pd.read_excel("/Users/daviderizzello/Documents/Progetto_AI/Running_AI/Marathon_Results/ROMA2024.xls")
    df_roma["tempo_sec"] = df_roma['TEMPO_UFFICIALE'].apply(pf.time_to_seconds)   
    df_roma['position'] = df_roma['tempo_sec'].rank(method='min').astype(int)
    predicted_position_roma = (df_roma['tempo_sec'] < predicted_time_sec).sum() + 1

    with st.container():
        st.title("COME TI QUALIFICHERESTI IN QUESTE 3 MARATONE :first_place_medal:", anchor="ranking")
        marathon1_column, marathon2_column, marathon3_column= st.columns(3)
        with marathon1_column:  
            st.header(f"{predicted_position_milano}°/{len(df_milano)}")
            st.write("Maratona di [Milano](https://www.milanomarathon.it/) 🌫")

        with marathon2_column:
            st.header(f"{predicted_position_venezia}°/{len(df_venezia)}")
            st.write("Maratona di [Venezia](https://www.venicemarathon.it/it/) 🛶")


        with marathon3_column:
            st.header(f"{predicted_position_roma}°/{len(df_roma)}")
            st.write("Maratona di [Roma](https://www.runromethemarathon.com/) 🏛️")
    
    
    st.divider()
    #SECTION OLD MPT
    with st.container():
        if len(weeks) >= 4:
            style_title = "<style>h1 {text-align: center;}</style>"
            st.markdown(style_title, unsafe_allow_html=True)
            st.title(":rewind: UN MESE FA ERI QUI", anchor="tempo_ieri")
            # Three columns with different widths

            col1, old_mpt_column, col2 = st.columns(3)
            st.markdown(style_time, unsafe_allow_html=True)

            with old_mpt_column:
                old_mpt_hh, old_mpt_mm,old_mpt_ss = weeks.iloc[-4]['Tempo Previsto Maratona']
                difference_minutes = pf.delta_mpt(old_mpt_hh, old_mpt_mm, old_mpt_ss, pred_hh, pred_mm, pred_ss)
                st.title(f"{old_mpt_hh:02}:{old_mpt_mm:02}:{old_mpt_ss:02}", help="Come viene calcolato il tempo?")
                if difference_minutes < 0:
                    st.write(f":stopwatch: Hai conquistato {difference_minutes:.0f} minuti.")
                elif difference_minutes == 0:
                    st.write(f":stopwatch: Il tuo tempo non è cambiato.")
                else:
                    st.write(f":stopwatch: Hai perso {difference_minutes:.0f} minuti.")


            with col2:
                if difference_minutes < 0:
                    st.title(":green[DAJE!]")
                else:
                    st.title(":green[NON MOLLARE!]")

    #SECTION PROGRESS

    with st.container():
        st.markdown("<a id='progress'></a>", unsafe_allow_html=True)
        st.title("GUARDA IL TUO PROGRESSO SETTIMANA PER SETTIMANA :chart_with_upwards_trend:", anchor="progressi")

        #Sample conversion from hh:mm:ss to total minutes
        def time_to_minutes(time_str):
            h, m, s = map(int, time_str.split(':'))
            return h * 60 + m + s / 60
        
        weeks['Settimana'] = weeks['Settimana'].astype(str)
        weeks['Passo Medio (min/km)'] = weeks['Passo Medio'].apply(pf.convert_sec_per_km_to_min_per_km)
        weeks['Passo Medio cumulativo (min/km)'] = weeks['Passo Medio Cumulativo'].apply(pf.convert_sec_per_km_to_min_per_km)

        #Apply this conversion to the DataFrame
        weeks['predicted_marathon_time_minutes'] = weeks['Tempo Previsto Maratona'].apply(time_to_minutes)
        # User options to choose which lines to display
        col_options = st.columns([1,1,1])
        with col_options[0]:
            show_km_total = st.checkbox(':blue[Mostra Km Totali]', value=True)
        with col_options[1]:         
            show_avg_pace = st.checkbox(':red[Mostra Passo Medio]', value=True)
        with col_options[2]:
            show_predicted_time = st.checkbox(':green[Mostra Tempo Previsto Maratona (minuti)]', value=True)

        base = alt.Chart(weeks).encode(
            alt.X('Settimana:O', sort=weeks['Settimana'].tolist(), axis=alt.Axis(title='Settimana', labelAngle=0))
        )

        layers = []

        if show_km_total:
            km_total = base.mark_line(color='blue', strokeWidth=3).encode(
                alt.Y('Km Totali:Q', axis=alt.Axis(title='', titleColor='blue'))
            )
            layers.append(km_total)

        if show_avg_pace:
            avg_pace = base.mark_line(color='red', strokeWidth=3).encode(
                alt.Y('Passo Medio:Q', axis=alt.Axis(title='', titleColor='red')),
                        tooltip=['Settimana', 'Passo Medio (min/km)']
                
            )
            layers.append(avg_pace)

        if show_predicted_time:
            predicted_time = base.mark_line(color='green', strokeWidth=3).encode(
                alt.Y('predicted_marathon_time_minutes:Q', axis=alt.Axis(title='', titleColor='green', offset = 30)),
                        tooltip=['Settimana', 'Tempo Previsto Maratona']

            )
            layers.append(predicted_time)

        # Combine the charts with independent y scales
        if layers:
            chart = alt.layer(*layers).resolve_scale(y='independent')
            st.altair_chart(chart, use_container_width=True)
        with st.expander("Guarda la tabella:"):
            selected_df_weeks = weeks[["Km Totali","Passo Medio (min/km)","Passo Medio cumulativo (min/km)","Km Totali Cumulativi", "Tempo Previsto Maratona"]]
            st.dataframe(selected_df_weeks)

    #tips
    with st.container():
        cols = st.columns([0.2,1,0.2])
        with cols[1]:
                st.title(":mega: Ecco alcune tips!", anchor = "tips")
                # Marathon date input
                marathon_date = st.date_input("Fammi sapere in che data prevedi di correre la tua prossima maratona :point_down:", date.today(), min_value=date.today(), format="DD/MM/YYYY")

                # Calculate difference in days between today and the marathon date
                delta_marathon = marathon_date - date.today()

                # Calculate the number of weeks
                weeks_to_marathon = delta_marathon.days // 7
                days_remaining = delta_marathon.days % 7
                last_week_avg_kms =  weeks["Km Totali Cumulativi"].iloc[-1]
                last_weeks_avg_pace = weeks["Passo Medio (min/km)"].iloc[-1]
                frequency = pf.training_frequency(df, weeks)
                # Display the number of weeks and remaining days
                guidelines.provide_guidelines(weeks_to_marathon, last_week_avg_kms, frequency, last_weeks_avg_pace)
    
    #contact us
    with st.container():
        cols = st.columns([0.2,1,0.2])
        with cols[1]:
                st.title("Hai qualche dubbio sul tuo allenamento? Contattaci!:memo:", anchor = "contattaci")
                contact_us = st.form("contact")
                with contact_us:
                    st.text_area("Inserisci il tuo nome:", placeholder="Nome")
                    st.text_area("Inserisci la tua mail:", placeholder="Mail")
                    st.text_area("Fai la tua domanda:", placeholder="Ho qualche dubbio su...")
                    st.form_submit_button("Invia")
else:
    st.warning("Non ci sono abbastanza allenamenti recenti per fare una previsione. Torna qui quando avrai almeno 4 allenamenti nell'ultima settimana o 6 nelle ultime 2.")
   #contact us

    st.divider()
    with st.container():
      cols = st.columns([0.2,1,0.2])
      with cols[1]:
            st.title("Se non sai come iniziare ad allenarti siamo qui per te. Contattaci!:memo:")
            contact_us = st.form("contact")
            with contact_us:
               st.text_area("Inserisci il tuo nome:", placeholder="Nome")
               st.text_area("Inserisci la tua mail:", placeholder="Mail")
               st.text_area("Fai la tua domanda:", placeholder="Ho qualche dubbio su...")
               st.form_submit_button("Invia")


               





#data = strava.download_activity(activity, strava_auth)




#columns = []
#for column in data.columns:
#    if is_numeric_dtype(data[column]):
#        columns.append(column)

#selected_columns = st.multiselect(
#    label="Select columns to plot",
#    options=columns
#)

#data["index"] = data.index

#if selected_columns:
#    for column in selected_columns:
#        altair_chart = alt.Chart(data).mark_line(color=strava.STRAVA_ORANGE).encode(
#            x="index:T",
#            y=f"{column}:Q",
#        )
#        st.altair_chart(altair_chart, use_container_width=True)
#else:
#    st.write("No column(s) selected")