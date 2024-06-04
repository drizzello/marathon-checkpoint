import base64
import os
import arrow
import httpx
import streamlit as st
from bokeh.models.widgets import Div
from stravalib import Client
import pandas as pd
from pandas.tseries.offsets import DateOffset
import pred_functions as pf


# Define constants
STRAVA_AUTHORIZATION_URL = st.secrets["STRAVA_AUTHORIZATION_URL"]
STRAVA_CLIENT_ID = st.secrets["STRAVA_CLIENT_ID"]
STRAVA_CLIENT_SECRET = st.secrets["STRAVA_CLIENT_SECRET"]
APP_URL = st.secrets["APP_URL"]

@st.cache_data
def load_image_as_base64(image_path):
    with open(image_path, "rb") as f:
        contents = f.read()
    return base64.b64encode(contents).decode("utf-8")

def powered_by_strava_logo():
    base64_image = load_image_as_base64(".static/api_logo_cptblWith_strava_stack_light.png")
    st.markdown(
        """
        <style>
        .responsive-img {
            max-width: 20%;
            height: auto;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<img src="data:image/png;base64,{base64_image}" class="responsive-img" alt="powered by strava">',
        unsafe_allow_html=True,
    )

    
def authorization_url():
    request = httpx.Request(
        method="GET",
        url=STRAVA_AUTHORIZATION_URL,
        params={
            "client_id": STRAVA_CLIENT_ID,
            "redirect_uri": APP_URL,
            "response_type": "code",
            "approval_prompt": "auto",
            "scope": "activity:read_all"
        }
    )
    return request.url

def login_header(header=None):
    strava_authorization_url = authorization_url()

    if header is None:
        base = st
    else:
        col1, _, _, button = header
        base = button

    with col1:
        powered_by_strava_logo()

    base64_image = load_image_as_base64("./static/btn_strava_connectwith_orange@2x.png")
    base.markdown(
        (
            f"<a href=\"{strava_authorization_url}\">"
            f"  <img alt=\"strava login\" src=\"data:image/png;base64,{base64_image}\" width=\"100%\">"
            f"</a>"
        ),
        unsafe_allow_html=True,
    )

def logout_header(header=None):
    if header is None:
        base = st
    else:
        _, col2, _, button = header
        base = button

    with col2:
        powered_by_strava_logo()

    if base.button("Log out"):
        js = f"window.location.href = '{APP_URL}'"
        html = f"<img src onerror=\"{js}\">"
        div = Div(text=html)
        st.bokeh_chart(div)

def logged_in_title(strava_auth, header=None):
    if header is None:
        base = st
    else:
        col, _, _, _ = header
        base = col

    first_name = strava_auth["athlete"]["firstname"]
    last_name = strava_auth["athlete"]["lastname"]
    base.markdown(f"Ciao, {first_name} {last_name}!")

@st.cache_data
def exchange_authorization_code(authorization_code):
    response = httpx.post(
        url="https://www.strava.com/oauth/token",
        json={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "code": authorization_code,
            "grant_type": "authorization_code",
        }
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError:
        st.error("Something went wrong while authenticating with Strava. Please reload and try again")
        st.query_params.clear()
        st.stop()
        return

    strava_auth = response.json()
    return strava_auth

def authenticate(header=None, stop_if_unauthenticated=True):
    query_params = st.query_params
    authorization_code = query_params.get("code")

    if authorization_code is None:
        authorization_code = query_params.get("session")

    if authorization_code is None:
        login_header(header=header)
        if stop_if_unauthenticated:
            st.stop()
        return
    else:
        logout_header(header=header)
        strava_auth = exchange_authorization_code(authorization_code)
        logged_in_title(strava_auth, header)
        st.query_params["session"] = authorization_code
        return strava_auth

def header():
    col1, col2, col3 = st.columns(3)
    with col3:
        strava_button = st.empty()
    return col1, col2, col3, strava_button

@st.cache_data
def get_activities(auth, page=1):
    access_token = auth["access_token"]
    response = httpx.get(
        url=f"{STRAVA_API_BASE_URL}/athlete/activities",
        params={
            "page": page,
        },
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    return response.json()

def activity_label(activity):
    if activity["name"] == DEFAULT_ACTIVITY_LABEL:
        return ""

    start_date = arrow.get(activity["start_date_local"])
    human_readable_date = start_date.humanize(granularity=["day"])
    date_string = start_date.format("YYYY-MM-DD")

    return f"{activity['name']} - {date_string} ({human_readable_date})"

def select_strava_activity(auth):
    col1, col2 = st.columns([1, 3])
    with col1:
        page = st.number_input(
            label="Activities page",
            min_value=1,
            help="The Strava API returns your activities in chunks of 30. Increment this field to go to the next page.",
        )

    with col2:
        activities = get_activities(auth=auth, page=page)
        if not activities:
            st.info("This Strava account has no activities or you ran out of pages.")
            st.stop()
        default_activity = {"name": DEFAULT_ACTIVITY_LABEL, "start_date_local": ""}

        activity = st.selectbox(
            label="Select an activity",
            options=[default_activity] + activities,
            format_func=activity_label,
        )

    if activity["name"] == DEFAULT_ACTIVITY_LABEL:
        st.write("No activity selected")
        st.stop()
        return

    activity_url = f"https://www.strava.com/activities/{activity['id']}"
        
    st.markdown(
        f"<a href=\"{activity_url}\" style=\"color:{STRAVA_ORANGE};\">View on Strava</a>",
        unsafe_allow_html=True
    )

    return activity


def process_strava_data(access_token):
    client = Client(access_token=access_token)
    activities = client.get_activities(limit=1000)
    data = []
    my_cols = ['name', 'start_date_local', 'type', 'distance', 'moving_time',
               'elapsed_time', 'total_elevation_gain', 'elev_high', 'elev_low',
               'average_speed', 'max_speed', 'average_heartrate', 'max_heartrate', 'start_latlng']
    
    for activity in activities:
        my_dict = activity.to_dict()
        data.append([activity.id] + [my_dict.get(x) for x in my_cols])
    
    my_cols.insert(0, 'id')
    df = pd.DataFrame(data, columns=my_cols)
    df['type'] = df['type'].replace('Walk', 'Hike')
    df['distance_km'] = df['distance'] / 1e3
    df['start_date_local'] = pd.to_datetime(df['start_date_local'])
    df['day_of_week'] = df['start_date_local'].dt.day_name()
    df['month_of_year'] = df['start_date_local'].dt.month
    df['elapsed_time'] = pd.to_timedelta(df['elapsed_time'])
    df['elapsed_time_hr'] = df['elapsed_time'].astype(int) / 3600e9
    df['moving_time_hr'] = df['moving_time'].astype(int) / 3600e9
    df['sec_per_km'] = 1000 / df['average_speed']
    # Filter to include only the last 4 months
    four_months_ago = pd.Timestamp.now() - DateOffset(months=4)
    df = df[df['start_date_local'] >= four_months_ago]

    df = df[(df['type'] == 'Run') & (df['distance_km'] >= 2)]
    
    return df

@st.cache_data
def marathon_ranking(filepath, predicted_time_sec):
    df = pd.read_excel(filepath)
    df["tempo_sec"] = df['TEMPO_UFFICIALE'].apply(pf.time_to_seconds)   
    df['position'] = df['tempo_sec'].rank(method='min').astype(int)
    predicted_position = (df['tempo_sec'] < predicted_time_sec).sum() + 1

    return predicted_position, df
#@st.cache(show_spinner=False, max_entries=30, allow_output_mutation=True)
#def download_activity(activity, strava_auth):
#    with st.spinner(f"Downloading activity \"{activity['name']}\"..."):
#        return sweat.read_strava(activity["id"], strava_auth["access_token"])
