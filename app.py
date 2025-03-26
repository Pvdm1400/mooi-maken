
import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import folium_static

OSRM_SERVER = "https://router.project-osrm.org"

# List of tankstations with their names and coordinates
tankstations = [
    ("ADRIANO OLIVETTI SNC 13048", 45.38002020650739, 8.14634168147584),
    ("LUIGI GHERZI 15 28100", 45.454214522946366, 8.648874406509199),
    ("MEZZACAMPAGNA SNC 37135", 45.38885497663997, 10.993260597366502),
    ("Via Gramsci 45 15061", 44.69849229353388, 8.884370036245732),
    ("Korendreef 16 1530", 52.3813141, 4.8785029),
    # Add your own tankstations here
]

# Streamlit UI - Set the app's theme and page config
st.set_page_config(page_title="Tankstations Routeplanner", page_icon="🚗", layout="wide")

# Page title and introductory text
st.title("🚗 Tankstations Routeplanner")
st.markdown("Welcome to the route planner! Enter your start and end locations, set the distance to tankstations, and plan your route.")

# User input for start and end location (can be a city or address)
geolocator = Nominatim(user_agent="tankstations_route_planner")

start_location = st.text_input("Enter a starting location (e.g., city or address)", "Amsterdam")
end_location = st.text_input("Enter an end location (e.g., city or address)", "Rotterdam")
start_loc = geolocator.geocode(start_location)
end_loc = geolocator.geocode(end_location)

if start_loc and end_loc:
    start_lat, start_lon = start_loc.latitude, start_loc.longitude
    end_lat, end_lon = end_loc.latitude, end_loc.longitude
    st.write(f"Start location: {start_location} ({start_lat}, {start_lon})")
    st.write(f"End location: {end_location} ({end_lat}, {end_lon})")

    # User input for max distance to tankstations and max route deviation
    max_distance = st.slider("Max distance to next station (km)", 50, 500, 250)
    max_deviation = st.slider("Max deviation from route (km)", 0, 100, 50)

    # Map with start and end location
    map = folium.Map(location=[start_lat, start_lon], zoom_start=6, tiles="cartodb positron")
    folium.Marker([start_lat, start_lon], popup="Start Location", icon=folium.Icon(color="blue")).add_to(map)
    folium.Marker([end_lat, end_lon], popup="End Location", icon=folium.Icon(color="red")).add_to(map)

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
    st.warning("Please enter valid start and end locations.")
