import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime
import json

# Page Title
st.title("Risky Predictive Front")

# Introduction
st.markdown(
    """
    Welcome to the **Risky Predictive Front**! This app allows you to interact with a predictive model for predicting offenses.
    Simply provide the required parameters below, and you'll receive a prediction instantly.

    ### How It Works
    1. Click on the map to select a ward.
    2. Specify the necessary details.
    3. We call the predictive API to estimate.
    4. View the prediction right here!

    Let's get started
    """
)

# Input Parameters
st.sidebar.header("Configure Input Parameters")

# Initialize session state for coordinates and selected ward
if 'coords' not in st.session_state:
    st.session_state.coords = None

if 'selected_ward' not in st.session_state:
    st.session_state.selected_ward = None

# Load ward boundaries (replace with an actual GeoJSON URL or file)
def load_ward_data():
    try:
        with open(r"C:\Users\1\Downloads\custom.geo", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Ward data file not found. Please check the file path.")
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse ward data: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    return None

ward_data = load_ward_data()

# Display interactive map
m = folium.Map(location=[41.8781, -87.6298], zoom_start=10)  # Centered at Chicago

if ward_data and ward_data.get("features"):
    for feature in ward_data["features"]:
        ward_number = feature["properties"].get("ward", "Unknown")
        folium.GeoJson(
            feature,
            style_function=lambda x: {
                "fillColor": "blue" if st.session_state.selected_ward == x["properties"].get("ward") else "green",
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.5,
            },
            tooltip=f"Ward {ward_number}",
            highlight_function=lambda x: {"fillColor": "orange", "fillOpacity": 0.7},
            name=f"Ward {ward_number}"
        ).add_child(folium.ClickForMarker(popup=f"Ward {ward_number}")).add_to(m)

    folium.LatLngPopup().add_to(m)  # Add LatLng popup to capture clicks

    # Show the map in Streamlit
    map_data = st_folium(m, height=500, width=700, returned_objects=["last_clicked"])

    # Process map clicks
    if map_data and map_data.get("last_clicked"):
        lat, lng = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
        st.session_state.coords = (lat, lng)
        for feature in ward_data["features"]:
            # Determine if clicked coordinates fall within this ward (this requires a proper spatial check, placeholder for now)
            st.session_state.selected_ward = feature["properties"].get("ward")
            break

    # Display selected ward
    if st.session_state.selected_ward:
        st.sidebar.success(f"Selected Ward: {st.session_state.selected_ward}")
    else:
        st.sidebar.warning("Click on a ward on the map to select it.")

# Time category selection
time_category = st.sidebar.selectbox(
    "Time Category",
    ["Early Morning", "Late Morning", "Early Noon", "Late Noon", "Early Evening", "Late Evening"],
    index=0
)

# Date input
date = st.sidebar.date_input("Date")

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
    if api_url and st.session_state.coords:
        latitude, longitude = st.session
