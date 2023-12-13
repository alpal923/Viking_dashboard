import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point

# Read the data
war_full = pd.read_csv('war_translated.csv')
war_data = war_full[['Föremålsbenämning_translated', 'Plats', 'Museum', 'Catalog Link', 'plats_latitude', 'plats_longitude', 'Material_translated', 'year_uncovered', 'Era Start Year', 'Era End Year', 'Width', 'Length', 'Thickness', 'Diameter', 'Weight']]
war_data.rename(columns={"plats_latitude": "latitude", "plats_longitude": "longitude"})
trade_full = pd.read_csv('trade_translated.csv')
trade_data = trade_full[['Föremålsbenämning_translated', 'Plats', 'Museum', 'Catalog Link', 'latitude', 'longitude', 'Material_translated', 'year_uncovered', 'Era Start Year', 'Era End Year', 'Width', 'Length', 'Thickness', 'Diameter', 'Weight']]

# Function to extract unique values from a DataFrame column
def extract_unique_values(df, column):
    materials = set()
    for items in df[column].dropna().unique():
        # Split by space and remove commas
        for item in str(items).split():
            materials.add(item.replace(',', '').strip())
    return materials

# Function to plot a bar chart of materials
def plot_materials_bar_chart(df):
    material_counts = df['Material_translated'].str.split(',\s*').explode().value_counts()
    plt.figure(figsize=(10, 6))
    material_counts.plot(kind='bar')
    st.pyplot(plt)

# Updated Function to plot and display the map
def plot_map(df_filtered, lat_col, lon_col):
    # Convert DataFrame to GeoDataFrame
    geometry = [Point(xy) for xy in zip(df_filtered[lon_col], df_filtered[lat_col])]
    geo_df = gpd.GeoDataFrame(df_filtered, geometry=geometry)

    # Load world basemap (update path to your shapefile)
    world = gpd.read_file('path/to/ne_110m_admin_0_countries.shp')

    # Europe boundaries
    europe_bounds = {
        "min_lon": -25.0,
        "max_lon": 40.0,
        "min_lat": 34.0,
        "max_lat": 71.0
    }

    fig, ax = plt.subplots(figsize=(15, 10))
    world.plot(ax=ax, color='lightgrey', edgecolor='black')
    geo_df.plot(ax=ax, color='blue', markersize=5)
    ax.set_xlim(europe_bounds["min_lon"], europe_bounds["max_lon"])
    ax.set_ylim(europe_bounds["min_lat"], europe_bounds["max_lat"])
    plt.title('Locations in Europe')
    return fig

# Function to plot the count of objects found per year
def plot_objects_per_year(df):
    yearly_counts = df['year_uncovered'].value_counts().sort_index()
    plt.figure(figsize=(10, 6))
    yearly_counts.plot(kind='line')
    plt.xlabel('Year Uncovered')
    plt.ylabel('Number of Objects Found')
    plt.title('Count of Objects Found Per Year')
    st.pyplot(plt)

# Streamlit app
def main():
    st.title('Viking Artifacts')

    # Choose between war data and trade data
    data_choice = st.radio("Choose the dataset", ('War Data', 'Trade Data'))

    if data_choice == 'War Data':
        data_to_display = war_data
    else:
        data_to_display = trade_data

    # Extract unique materials and places
    unique_materials = extract_unique_values(data_to_display, 'Material_translated')
    unique_places = extract_unique_values(data_to_display, 'Plats')

    all_materials = list(unique_materials)
    all_places = list(unique_places)

    # Set default to all materials
    selected_materials = st.multiselect('Select Materials', all_materials, default=all_materials)
    selected_places = st.multiselect('Select Places', all_places, default=all_places)

    # Filter data based on selected materials and places
    if len(selected_materials) == len(all_materials):
        material_filter = True
    else:
        material_filter = data_to_display['Material_translated'].apply(lambda x: any(material in str(x) for material in selected_materials))

    if len(selected_places) == len(all_places):
        place_filter = True
    else:
        place_filter = data_to_display['Plats'].isin(selected_places)

    filtered_data = data_to_display[material_filter & place_filter]

    # Displaying the map
    if not filtered_data[[lat_column, lon_column]].dropna().empty:
        fig = plot_map(filtered_data, lat_column, lon_column)
        st.pyplot(fig)

    # Displaying the bar chart for materials
    plot_materials_bar_chart(filtered_data)

    # Displaying the bar chart for objects found per year
    plot_objects_per_year(filtered_data)

    st.dataframe(filtered_data)

if __name__ == '__main__':
    main()
