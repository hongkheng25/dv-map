import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import folium
from streamlit_folium import st_folium

# Load the Natural Earth dataset (update the path to your downloaded file)
@st.cache_data
def load_data():
    gdf = gpd.read_file("ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")
    
    # Check if 'pop_est' column exists; if not, create it with dummy data
    if 'pop_est' not in gdf.columns:
        import numpy as np
        np.random.seed(0)
        gdf['pop_est'] = np.random.randint(1e6, 1e9, size=len(gdf))  # Random population estimates for demonstration
    return gdf

gdf = load_data()

st.title("Interactive Map Visualization Examples")
st.markdown("_By Chua Hong Kheng - 20001081 - CS_")

# Sidebar for options
st.sidebar.header("Choose a Map Type")
map_type = st.sidebar.radio("Select Map Type", [
    "Map Cosmetics",
    "Map Visual Hierarchy",
    "Choropleth Map",
    "Geo Projection",
    "Home Location",
    "Locate Most Dense Population in Malaysia",
    "Election Result"
])

# 1. Map Cosmetics Example
if map_type == "Map Cosmetics":
    st.header("Map Cosmetics Example")
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(ax=ax, color='skyblue', edgecolor='black', linewidth=0.5)
    ax.set_title("Styled Map Example", fontsize=15, fontweight="bold")
    ax.set_facecolor("lightgrey")
    st.pyplot(fig)

# 2. Map Visual Hierarchy Example
# 2. Interactive Map Visual Hierarchy Example
elif map_type == "Map Visual Hierarchy":
    # Display column names to confirm the column with country names
    # st.write("Columns in GeoDataFrame:", gdf.columns)
    
    # Try possible column names that might contain country names
    if 'name' in gdf.columns:
        country_col = 'name'
    elif 'NAME' in gdf.columns:
        country_col = 'NAME'
    elif 'country' in gdf.columns:
        country_col = 'country'
    else:
        st.error("Country name column not found in dataset.")
        country_col = None
    
    if country_col:
        # 2. Interactive Map Visual Hierarchy Example
        st.header("Interactive Map Visual Hierarchy Example")
        st.write("Highlight selected countries in red and keep the rest in a neutral color (sky blue).")
    
        # List of countries for user to choose from
        all_countries = gdf[country_col].unique()
        highlighted_countries = st.multiselect(
            "Select countries to highlight in red",
            all_countries,
            # default=["United States", "Brazil", "India", "China", "Australia", "South Africa", "Russia"]
            default=["Brazil", "India", "China", "Australia", "South Africa", "Russia"]
        )
    
        # Add a new column 'color' to specify color based on selected countries
        gdf['color'] = gdf[country_col].apply(lambda x: 'red' if x in highlighted_countries else 'skyblue')
    
        # Plot the map with the selected visual hierarchy
        fig, ax = plt.subplots(figsize=(10, 6))
        gdf.plot(color=gdf['color'], edgecolor='black', linewidth=0.5, ax=ax)
        ax.set_title("Map Visual Hierarchy with Selected Countries Highlighted in Red")
        st.pyplot(fig)


# 3. Interactive Choropleth Map
elif map_type == "Choropleth Map":
    st.header("Interactive Choropleth Map Example")
    st.write("Select a color scheme for the choropleth map and toggle data transformation options.")

    # Color schemes for the choropleth map
    color_options = ['OrRd', 'YlGn', 'Blues', 'Purples', 'Greens']
    color_choice = st.selectbox("Choose Color Scheme", color_options, index=0)

    # Toggle for logarithmic transformation
    use_log_scale = st.checkbox("Use Log Transformation", value=True)

    # Calculate population density
    gdf['pop_density'] = gdf['pop_est'] / gdf['geometry'].area

    # Apply log transformation if selected
    if use_log_scale:
        gdf['pop_density'] = np.log1p(gdf['pop_density'])  # log(1 + x) to avoid log(0)

    # Display the map with the chosen color scheme and transformation
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(column='pop_density', cmap=color_choice, linewidth=0.5, edgecolor='black', legend=True, ax=ax)
    ax.set_title(f"Population Density by Country (Color Scheme: {color_choice}, {'Log Scale' if use_log_scale else 'Linear Scale'})")
    st.pyplot(fig)


# 4. Interactive Geo Projection Example
elif map_type == "Geo Projection":
    st.header("Interactive Geo Projection Example")
    st.write("Choose a projection and color scheme to see how it affects the map.")

    # Dropdown for different projections
    projection_options = {
        "WGS84 (Geographic)": "EPSG:4326",
        "Mercator": "EPSG:3395",
        "Robinson": "ESRI:54030",
        "Mollweide": "ESRI:54009",
        "Lambert Conformal Conic": "EPSG:3347"
    }
    proj_choice = st.selectbox("Select a Projection", list(projection_options.keys()))

    # Color schemes for the map
    color_options = ['OrRd', 'YlGn', 'Blues', 'Purples', 'Greens']
    color_choice = st.selectbox("Choose Color Scheme", color_options, index=0)

    # Toggle for logarithmic transformation of population density
    use_log_scale = st.checkbox("Use Log Transformation for Population Density", value=True)

    # Calculate population density if not done already
    gdf['pop_density'] = gdf['pop_est'] / gdf['geometry'].area

    # Apply log transformation if selected
    if use_log_scale:
        gdf['pop_density'] = np.log1p(gdf['pop_density'])  # log(1 + x) to handle zero values

    # Convert the GeoDataFrame to the selected projection
    gdf_proj = gdf.to_crs(projection_options[proj_choice])

    # Plot the map with the chosen projection, color scheme, and density scale
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf_proj.plot(column='pop_density', cmap=color_choice, edgecolor='black', legend=True, linewidth=0.5, ax=ax)
    ax.set_title(f"Map in {proj_choice} Projection (Color by Population Density)")
    st.pyplot(fig)

elif map_type == "Home Location": 
    # Load the Malaysia state GeoJSON file
    malaysia_states = gpd.read_file("malaysia.state.geojson")

    # Define the coordinates of your university
    university_lat = 6.120212702697463
    university_lon = 102.1949518982108
    university_name = "Chua's House"

    # Initialize a folium map centered on Malaysia
    m = folium.Map(location=[4.2105, 101.9758], zoom_start=6)

    # Add the GeoJSON layer to the map
    folium.GeoJson(malaysia_states).add_to(m)

    # Add a marker for the university
    folium.Marker(
        location=[university_lat, university_lon],
        popup=university_name,
        tooltip="University Location",
        icon=folium.Icon(color="red", icon="university", prefix="fa")
    ).add_to(m)

    # Display the map in Streamlit
    st.header("Home Location Map")
    st.write(f"Showing location for {university_name}")
    st.write("My house is located at Wakaf Bharu, Kelantan, Malaysia.")
    st_folium(m, width=700, height=500)

elif map_type == "Locate Most Dense Population in Malaysia": 
    
    # Load the Malaysia state GeoJSON file
    malaysia_states = gpd.read_file("malaysia.state.geojson")

    # Define the population for each state in Malaysia
    population_data = {
        "Johor": 3781000,
        "Kedah": 2185000,
        "Kelantan": 1960000,
        "Melaka": 932700,
        "Negeri Sembilan": 1230000,
        "Pahang": 1700000,
        "Perak": 2516000,
        "Perlis": 254900,
        "Pulau Pinang": 1776000,
        "Sabah": 3901000,
        "Sarawak": 2807000,
        "Selangor": 6560000,
        "Terengganu": 1253000,
        "W.P. Kuala Lumpur": 1795000,
        "W.P. Labuan": 99500,
        "W.P. Putrajaya": 92000
    }

    # Determine the state with the highest population
    most_populated_state = max(population_data, key=population_data.get)
    highest_population = population_data[most_populated_state]

    # Find the center of the most populated state
    state_geometry = malaysia_states[malaysia_states['name'] == most_populated_state].geometry
    state_center = state_geometry.centroid.iloc[0].coords[0]  # Get the centroid coordinates

    # Initialize a folium map centered on Malaysia
    m = folium.Map(location=[4.2105, 101.9758], zoom_start=6)

    # Define a style function to highlight the most populated state
    def style_function(feature):
        if feature['properties']['name'] == most_populated_state:
            return {'fillColor': 'blue', 'color': 'blue', 'fillOpacity': 0.6, 'weight': 2}
        else:
            return {'fillColor': 'gray', 'color': 'black', 'fillOpacity': 0.3, 'weight': 1}

    # Add the GeoJSON layer to the map with the custom style function
    folium.GeoJson(
        malaysia_states,
        style_function=style_function,
        tooltip=folium.features.GeoJsonTooltip(fields=['name'], aliases=['State:'])
    ).add_to(m)

    # Add a marker for the most populated state
    folium.Marker(
        location=state_center,
        popup=f"{most_populated_state} (Population: {highest_population})",
        tooltip="Most Populated State",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    # Display the map in Streamlit
    st.title("Most Populated State in Malaysia")
    st.write(f"The most populated state is {most_populated_state} with a population of {highest_population}.")
    st_folium(m, width=700, height=500)

elif map_type == "Election Result": 
    # Load the Malaysia state GeoJSON file
    malaysia_states = gpd.read_file("malaysia.state.geojson")

    # Define election results data: assign the winning party for each state
    election_results = {
        "Johor": "Pakatan Harapan",
        "Kedah": "Perikatan Nasional",
        "Kelantan": "Perikatan Nasional",
        "Melaka": "Pakatan Harapan",
        "Negeri Sembilan": "Pakatan Harapan",
        "Pahang": "Perikatan Nasional",
        "Perak": "Pakatan Harapan",
        "Perlis": "Perikatan Nasional",
        "Pulau Pinang": "Pakatan Harapan",
        "Sabah": "Pakatan Harapan",
        "Sarawak": "Pakatan Harapan",
        "Selangor": "Pakatan Harapan",
        "Terengganu": "Perikatan Nasional",
        "W.P. Kuala Lumpur": "Pakatan Harapan",
        "W.P. Labuan": "Perikatan Nasional",
        "W.P. Putrajaya": "Perikatan Nasional"
    }

    # Define a style function to color states by the winning party
    def election_style_function(feature):
        state_name = feature['properties']['name']
        winning_party = election_results.get(state_name, None)
        
        if winning_party == "Pakatan Harapan":
            return {'fillColor': 'red', 'color': 'red', 'fillOpacity': 0.6, 'weight': 1}
        elif winning_party == "Perikatan Nasional":
            return {'fillColor': 'blue', 'color': 'blue', 'fillOpacity': 0.6, 'weight': 1}
        else:
            # Default styling for states with no data
            return {'fillColor': 'gray', 'color': 'black', 'fillOpacity': 0.3, 'weight': 1}

    # Initialize a folium map centered on Malaysia
    m = folium.Map(location=[4.2105, 101.9758], zoom_start=6)

    # Add the GeoJSON layer to the map with the custom style function for election results
    folium.GeoJson(
        malaysia_states,
        style_function=election_style_function,
        tooltip=folium.features.GeoJsonTooltip(fields=['name'], aliases=['State:'])
    ).add_to(m)

    # Display the map in Streamlit
    st.title("Malaysia Election Results Map")
    st.write("Showing election results by state: Pakatan Harapan (Red), Perikatan Nasional (Blue)")
    st_folium(m, width=700, height=500)