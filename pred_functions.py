import math
import pandas as pd
import datetime 
import streamlit as st

# Predict pace
@st.cache_data
def predict_marathon_time(km_per_week, previous_pace):
    # Calculate pace in seconds per kilometer
    pace_sec_per_km = 17.1 + 140.0 * math.exp(-0.0053 * km_per_week) + 0.55 * previous_pace

    # Calculate total seconds for the marathon
    total_seconds = pace_sec_per_km * 42.195

    # Convert total seconds to hours, minutes, and seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    #return f"{hours:02}:{minutes:02}:{seconds:02}"
    return hours, minutes, seconds

st.cache_data
def marathon_pace_min_per_km(total_seconds):
    pace_sec_per_km = total_seconds / 42.195  # average seconds per kilometer
    
    # Convert seconds to minutes and seconds
    minutes_per_km = int(pace_sec_per_km // 60)
    seconds_per_km = int(pace_sec_per_km % 60)

    return f"{minutes_per_km}:{seconds_per_km:02}"

def check_number_of_trainings(number):
    if number < 4:
        return 0
    else:
        return 1

def weekly_totals(df, date_col, dist_col, pace_col):
    # Convert the date column to datetime if not already
    df[date_col] = pd.to_datetime(df[date_col])

    # Set the date column as the DataFrame index
    df.set_index(date_col, inplace=True)

    # Group data by weekly intervals
    weekly_data = df.resample('W').agg({dist_col: 'sum', pace_col: 'mean'}).fillna(0)

    return weekly_data[dist_col].values, weekly_data[pace_col].values

def delta_mpt(old_mpt_hh, old_mpt_mm, old_mpt_ss, pred_hh, pred_mm, pred_ss):
    # Convert both times to total seconds
    old_total_seconds = old_mpt_hh * 3600 + old_mpt_mm * 60 + old_mpt_ss
    pred_total_seconds = pred_hh * 3600 + pred_mm * 60 + pred_ss

    # Calculate the difference in seconds
    delta_seconds = old_total_seconds - pred_total_seconds

    # Convert the difference to minutes and adjust the sign accordingly
    delta_minutes = delta_seconds / 60

    return delta_minutes

def accuracy_time_pred(df):
    optimal_number_trainings = 4*8
    accuracy = (math.ceil((len(df)*100)/optimal_number_trainings))-10
    if accuracy <= 90:
        return accuracy
    elif accuracy <= 0:
        return 10
    else:
        return 90

def convert_sec_per_km_to_min_per_km(sec_per_km):
    """
    Converte il passo da sec/km a min/km.
    
    Args:
        sec_per_km (float): Passo medio in secondi per chilometro.
    
    Returns:
        str: Passo medio in formato 'min/km'.
    """
    # Converti il tempo in minuti (1 minuto = 60 secondi)
    minutes = sec_per_km // 60
    seconds = sec_per_km % 60
    
    return f"{int(minutes)}:{int(seconds):02d}"

def time_to_seconds(time_str):
    """Convert hh:mm:ss or mm:ss into total seconds."""
    try:
        if pd.isna(time_str):
            return 0  # Handle NaN values by returning 0 seconds
        parts = list(map(int, str(time_str).split(':')))
        if len(parts) == 3:
            hours, minutes, seconds = parts
        else:
            hours = 0
            minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    except Exception as e:
        print(f"Error converting time: {time_str}, Error: {e}")
        return 0  # Default to 0 seconds for any conversion errors
    
def training_frequency(df_training, df_weeks):
    number_of_trainings = len(df_training)
    number_of_weeks = len(df_weeks)
    frequency = round(number_of_trainings / number_of_weeks,0)
    return frequency

def count_recent_sessions(df, date_col, weeks_back=2):
    """
    Conta il numero di allenamenti nelle ultime settimane.

    Args:
        df (pd.DataFrame): Il DataFrame contenente i dati relativi all'allenamento.
        date_col (str): Nome della colonna che contiene le date degli allenamenti.
        weeks_back (int): Numero di settimane da contare indietro.

    Returns:
        int: Numero di allenamenti nelle ultime settimane specificate.
    """
    df[date_col] = pd.to_datetime(df[date_col])
    recent_date = df[date_col].max() - pd.Timedelta(weeks=weeks_back * 7)
    return len(df[df[date_col] > recent_date])
