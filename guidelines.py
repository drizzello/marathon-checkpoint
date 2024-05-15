   
import streamlit as st
import pred_functions as pf
# Function to provide personalized guidelines
def provide_guidelines(weeks_to_marathon, last_week_avg_kms, training_frequency, previous_pace):


    if weeks_to_marathon <= 1:
        st.write("Non posso darti molti consigli. La maratona è dietro l'angolo. Mangia, bevi, riposati e DAJE TUTTA!")

    elif weeks_to_marathon < 4:
        st.write(f"-> Mancano solo {weeks_to_marathon} settimane alla maratona!")

        if last_week_avg_kms < 20:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Con così pochi km all'attivo, valuta di partecipare alla mezza maratona o ad una distanza più breve.")
        elif 20 <= last_week_avg_kms < 30:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Incrementa gradualmente il volume settimanale fino a 35-40 km, mantenendo un ritmo facile.")
        elif 30 <= last_week_avg_kms < 50:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Riduci gradualmente il volume mantenendo l'intensità con corse brevi.")
        elif last_week_avg_kms >= 50:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Mantieni alta l'intensità con allenamenti molto brevi e recupero attivo con corse facili.")

        st.write("-> Concentrati sulla nutrizione e idratazione pre-gara.")

        if training_frequency <= 3:
            st.write(f"-> Hai una frequenza {training_frequency} allenamenti alla settimana. Mantieniti su 2-3 allenamenti settimanali.")
        else:
            st.write(f"-> Hai una frequenza {training_frequency} allenamenti alla settimana. Mantieniti su 2-3 allenamenti settimanali.")


    elif 4 <= weeks_to_marathon < 8:
        st.write(f"-> Mancano {weeks_to_marathon} settimane alla maratona!")

        if last_week_avg_kms < 20:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Incrementa gradualmente fino ad almeno 30 km, mantenendo un ritmo facile.")
        elif 20 <= last_week_avg_kms < 30:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Aumenta gradualmente fino a raggiungere almeno 40-50 km.")
        elif 30 <= last_week_avg_kms < 50:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Continua ad aumentare i km di settimana in settimana del 5-10% fino ad arrivare a 70-80 km settimanali.")
        elif 50 <= last_week_avg_kms < 80:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Mantieni questo ritmo fino al tapering.")
        elif last_week_avg_kms >= 80:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Mantieni questo volume fino al tapering.")

        if training_frequency <= 4:
            st.write(f"-> Hai una frequenza {training_frequency} allenamenti alla settimana. Cerca di aumentare gradualmente la frequenza a 5-6 allenamenti a settimana.")
        else:
            st.write(f"-> Hai una frequenza {training_frequency} allenamenti alla settimana. Ottimo lavoro!")

        st.write("-> Il passo medio settimanale dovrebbe essere vicino al tuo passo obiettivo.")

    elif 8 <= weeks_to_marathon < 12:
        st.write(f"-> Mancano {weeks_to_marathon} settimane alla maratona!")

        if last_week_avg_kms < 20:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Aumenta gradualmente fino a raggiungere almeno 30 km settimanali.")
        elif 20 <= last_week_avg_kms < 30:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Incrementa fino a raggiungere almeno 50 km settimanali.")
        elif 30 <= last_week_avg_kms < 50:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Incrementa fino a 60-70 km settimanali.")
        elif 50 <= last_week_avg_kms < 80:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Continua a mantenere questo ritmo fino a raggiungere 80 km settimanali.")
        elif last_week_avg_kms >= 80:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Mantieni questo volume fino al tapering!")

        if training_frequency <= 4:
            st.write(f"-> Hai una frequenza {training_frequency} allenamenti alla settimana. Cerca di aumentare gradualmente la frequenza a 5-6 allenamenti a settimana.")
        else:
            st.write(f"-> Hai una frequenza {training_frequency} allenamenti alla settimana. Ottimo lavoro!")

        st.write("-> Il passo medio settimanale dovrebbe essere circa 5% più lento del tuo passo obiettivo.")

    elif weeks_to_marathon >= 12:
        st.write(f"-> Mancano {weeks_to_marathon} settimane alla maratona!")

        if last_week_avg_kms < 20:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Incrementa gradualmente fino ad almeno 40 km settimanali.")
        elif 20 <= last_week_avg_kms < 30:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Incrementa fino a raggiungere almeno 50 km settimanali.")
        elif 30 <= last_week_avg_kms < 50:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Incrementa fino a 60-70 km settimanali.")
        elif 50 <= last_week_avg_kms < 80:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Continua a mantenere questo ritmo fino a raggiungere 80 km settimanali.")
        elif last_week_avg_kms >= 80:
            st.write(f"-> Hai una media settimanale di km percorsi pari a {last_week_avg_kms:.0f}. Mantieni questo volume fino al tapering!")

        if training_frequency <= 4:
            st.write(f"-> Hai una frequenza {training_frequency} allenamenti alla settimana. Cerca di aumentare gradualmente la frequenza a 5-6 allenamenti a settimana.")
        else:
            st.write(f"-> Hai una frequenza {training_frequency} allenamenti alla settimana. Ottimo lavoro!")

        st.write("-> Il passo medio settimanale dovrebbe essere circa 5-10% più lento del tuo passo obiettivo.")

