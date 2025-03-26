
import streamlit as st
import folium
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import requests
import pandas as pd
from streamlit_folium import folium_static

# Define the OSRM route service URL
OSRM_SERVER = "https://router.project-osrm.org"

# List of tankstations with their names and coordinates
tankstations = [
    ("ADRIANO OLIVETTI SNC 13048", 45.38002020650739, 8.14634168147584),
    ("LUIGI GHERZI 15 28100", 45.454214522946366, 8.648874406509199),
    ("MEZZACAMPAGNA SNC 37135", 45.38885497663997, 10.993260597366502),
    ("Via Gramsci 45 15061", 44.69849229353388, 8.884370036245732),
    ("Korendreef 16 1530", 52.3813141, 4.8785029),
    # Add more tankstations here
]

# Streamlit UI - Set the app's theme and page config
st.set_page_config(page_title="Tankstations Routeplanner", page_icon="🚗", layout="wide")

# Page title and introductory text
st.title("🚗 Tankstations Routeplanner")
st.markdown("Find the best route to the nearest tankstation with ease. Enter your starting location and get an optimal route.")

# User input for start location (can be a city or address)
geolocator = Nominatim(user_agent="tankstations_route_planner")

start_location = st.text_input("Enter a starting location (e.g., city or address)", "Amsterdam")
location = geolocator.geocode(start_location)

if location:
    start_lat, start_lon = location.latitude, location.longitude
    st.write(f"Start location: {start_location} ({start_lat}, {start_lon})")

    # Filter by distance
    max_distance = st.slider("Max distance to next station (km)", 50, 500, 250)

    # Map with tankstations
    map = folium.Map(location=[start_lat, start_lon], zoom_start=6, tiles="cartodb positron")
    folium.Marker([start_lat, start_lon], popup="Start Location", icon=folium.Icon(color="blue")).add_to(map)

    # Adding tankstation markers to map (only those within max_distance)
    filtered_stations = [
        (name, lat, lon) for name, lat, lon in tankstations
        if geodesic((start_lat, start_lon), (lat, lon)).km <= max_distance
    ]
    
    for name, lat, lon in filtered_stations:
        distance = geodesic((start_lat, start_lon), (lat, lon)).km
        folium.Marker([lat, lon], popup=f"{name} ({distance:.1f} km)", icon=folium.Icon(color="green")).add_to(map)

    # Display map
    folium_static(map)

    # Route planning between start and nearest tankstation
    if st.button("Plan Route to Nearest Tankstation"):
        st.spinner('Calculating route...')
        # Find the nearest station
        nearest_station = min(filtered_stations, key=lambda x: geodesic((start_lat, start_lon), (x[1], x[2])).km)
        route = get_route(start_lat, start_lon, nearest_station[1], nearest_station[2])

        # Display route and distance
        st.write(f"Route to {nearest_station[0]} (Distance: {geodesic((start_lat, start_lon), (nearest_station[1], nearest_station[2])):.1f} km)")
        st.write(route)

else:
    st.warning("Location not found. Please enter a valid city or address.")
