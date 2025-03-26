
import streamlit as st
import folium
from folium import plugins
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

# Function to calculate the distance between two locations using geopy
def calculate_distance(start, end):
    return geodesic(start, end).km

# Function to generate the route using OSRM API
def get_route(start_lat, start_lon, end_lat, end_lon):
    url = f"{OSRM_SERVER}/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=false"
    response = requests.get(url)
    data = response.json()
    route = data['routes'][0]['geometry']
    return route

# Streamlit UI
st.title("Tankstations Routeplanner")

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
    map = folium.Map(location=[start_lat, start_lon], zoom_start=6)
    folium.Marker([start_lat, start_lon], popup="Start Location", icon=folium.Icon(color="blue")).add_to(map)

    # Adding tankstation markers to map
    for name, lat, lon in tankstations:
        distance = calculate_distance((start_lat, start_lon), (lat, lon))
        if distance <= max_distance:
            folium.Marker([lat, lon], popup=f"{name} ({distance:.1f} km)", icon=folium.Icon(color="green")).add_to(map)

    # Display map
    folium_static(map)

    # Route planning between start and nearest tankstation
    if st.button("Plan Route to Nearest Tankstation"):
        nearest_station = min(tankstations, key=lambda x: calculate_distance((start_lat, start_lon), (x[1], x[2])))
        route = get_route(start_lat, start_lon, nearest_station[1], nearest_station[2])

        # Display route and distance
        st.write(f"Route to {nearest_station[0]} (Distance: {calculate_distance((start_lat, start_lon), (nearest_station[1], nearest_station[2])):.1f} km)")

        # Route plotting (for now just print the route)
        st.write(route)

else:
    st.warning("Location not found. Please enter a valid city or address.")
