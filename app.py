import streamlit as st
import requests
import pydeck as pdk
from datetime import datetime
import  pandas as pd 

# Page Title
st.title("Risky Predictive Front")

# Introduction
st.markdown(
    """
    Welcome to the **Risky Predictive Front**! This app allows you to interact with a predictive model for predicting offenses.
    Simply provide the required parameters below, and you'll receive a prediction instantly.

    ### How It Works
    1. Select a ward from the interactive map.
    2. Specify the necessary details.
    3. We call the predictive API to estimate.
    4. View the prediction right here!

    Let's get started 🚔
    """
)

# Input Parameters
st.sidebar.header("Configure Input Parameters")

# Load ward data (GeoJSON for Chicago wards, replace with actual GeoJSON URL or file path)
geojson_url = "https://data.cityofchicago.org/resource/igwz-8jzy.geojson"  # Updated GeoJSON URL for Chicago wards
try:
    response = requests.get(geojson_url)
    response.raise_for_status()
    wards_data = response.json()
    if 'features' in wards_data:
        wards = [
            {
                "ward": feature['properties'].get('ward', 'Unknown Ward'),
                "centroid": feature['geometry']['coordinates'][0][0] if feature['geometry'] else [0, 0]
            }
            for feature in wards_data['features']
        ]
    else:
        wards = []
        st.error("GeoJSON does not contain 'features'. Check the data source.")
except requests.RequestException as e:
    wards = []
    st.warning("Failed to load ward data. Interactive map will not display.")

# Display interactive map
if wards:
    ward_data = [
        {"ward": ward["ward"], "lon": centroid[0], "lat": centroid[1]}
        for ward, centroid in [(w, w["centroid"]) for w in wards]
    ]
    ward_df = pd.DataFrame(ward_data)

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=41.8781,  # Centered near Chicago
            longitude=-87.6298,
            zoom=10,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=ward_df,
                get_position="[lon, lat]",
                get_color="[200, 30, 0, 160]",
                get_radius=200,
                pickable=True,
            ),
        ],
    ))
    selected_ward = st.sidebar.selectbox(
        "Select Ward", [ward["ward"] for ward in wards]
    )
else:
    selected_ward = st.sidebar.selectbox("Select Ward", options=["Ward data unavailable"])

# Time category selection
time_category = st.sidebar.selectbox(
    "Time Category",
    ["Early Morning", "Late Morning", "Early Noon", "Late Noon", "Early Evening", "Late Evening"],
    index=0
)
# Date input
date = st.sidebar.date_input("Date")

# Latitude and Longitude input
latitude = st.sidebar.number_input("Latitude", format="%f")
longitude = st.sidebar.number_input("Longitude", format="%f")

# Determine if the date is a weekend
def is_weekend(date_obj):
    return "Yes" if date_obj.weekday() >= 5 else "No"

weekend = is_weekend(date)

# API URL
api_url = st.text_input("API URL", "https://rpp-589897242504.europe-west1.run.app/predict")

st.markdown(
    """
    ---
    ### Make a Prediction
    Once all parameters are set, click the button below to retrieve an offense prediction from the API.
    """
)

# Call API and Get Prediction
if st.button("Get Prediction"):
    if api_url and selected_ward and time_category and latitude and longitude:
        # Prepare API request payload
        payload = {
            "ward": selected_ward,
            "time_category": time_category,
            "date": date.strftime("%Y-%m-%d"),
            "weekend": weekend,
            "latitude": latitude,
            "longitude": longitude,
        }
        st.write(payload)
        try:
            # Make API request
            response = requests.post(api_url, json=payload)
            response_data = response.json()

            # Display Prediction
            if response.status_code == 200:
                prediction = response_data["offense_prediction"]
                st.success(f"The predicted offense likelihood is: {prediction:.2f}")
            else:
                st.error("Failed to retrieve a valid prediction. Please check your inputs or API.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please ensure all parameters are filled out correctly.")

st.markdown(
    """
    ---
    ### Notes
    - Ensure your API URL is correct.
    - Provide valid latitude and longitude for accurate predictions.
    - This app leverages the `requests` library to communicate with the API.
    - Weekend determination is automated based on the selected date.
    """
)
