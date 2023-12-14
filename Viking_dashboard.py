import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import fiona
import seaborn as sns

# Get a list of colors from the 'Set2' palette
palette = sns.color_palette("Set2")

# Read the data
war_full = pd.read_csv('war_translated.csv')
war_data = war_full[['Föremålsbenämning_translated', 'Plats', 'Museum', 'Catalog Link', 'plats_latitude', 'plats_longitude', 'Material_translated', 'year_uncovered', 'Era Start Year', 'Era End Year', 'Width', 'Length', 'Thickness', 'Diameter', 'Weight']]
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

def plot_materials_bar_chart(df):
    if not df['Material_translated'].dropna().empty:
        material_counts = df['Material_translated'].str.split(',\s*').explode().value_counts()
        plt.figure(figsize=(10, 6))
        material_counts.plot(kind='bar', color=palette)
        st.pyplot(plt)
    else:
        st.write("No material data available to display.")

def plot_map(df_filtered, lat_col, lon_col):
    if not df_filtered[[lat_col, lon_col]].dropna().empty:
        # Convert DataFrame to GeoDataFrame
        geometry = [Point(xy) for xy in zip(df_filtered[lon_col], df_filtered[lat_col])]
        geo_df = gpd.GeoDataFrame(df_filtered, geometry=geometry)

        # Load world basemap (update path to your shapefile)
        world = gpd.read_file('ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp')

        # Europe boundaries
        europe_bounds = {
            "min_lon": -25.0,
            "max_lon": 40.0,
            "min_lat": 34.0,
            "max_lat": 71.0
        }

        fig, ax = plt.subplots(figsize=(15, 10))
        world.plot(ax=ax, color='lightgreen', edgecolor='darkgreen')
        geo_df.plot(ax=ax, color='blue', markersize=5)
        ax.set_xlim(europe_bounds["min_lon"], europe_bounds["max_lon"])
        ax.set_ylim(europe_bounds["min_lat"], europe_bounds["max_lat"])
        plt.title('Locations in Europe')
        return fig
    else:
        st.write("No geographic data available to display.")

def plot_objects_per_year(df):
    if 'year_uncovered' in df.columns and not df['year_uncovered'].dropna().empty:
        yearly_counts = df['year_uncovered'].value_counts().sort_index()
        plt.figure(figsize=(10, 6))
        yearly_counts.plot(kind='line', color='purple')
        plt.xlabel('Year Uncovered')
        plt.ylabel('Number of Objects Found')
        plt.title('Count of Objects Found Per Year')
        st.pyplot(plt)
    else:
        st.write("No data on the year of object discovery available to display.")

# Streamlit app
def main():
    st.title('Viking Artifacts')

    st.header('Intro')

    st.text('This dashbaord allows users to interact with the data scraped off of the Statens Historiska Museer catalog.')

    war_data.rename(columns={"plats_latitude": "latitude", "plats_longitude": "longitude"}, inplace=True)

    # Choose between war data and trade data
    data_choice = st.radio("Choose the dataset", ('War Artifacts', 'Trade Artifacts'))

    if data_choice == 'War Artifacts':
        data_to_display = war_data
    else:
        data_to_display = trade_data

    # Extract unique materials and places
    unique_materials = extract_unique_values(data_to_display, 'Material_translated')
    unique_places = extract_unique_values(data_to_display, 'Plats')

    # Initialize filters as a boolean series
    material_filter = pd.Series([True] * len(data_to_display))
    place_filter = pd.Series([True] * len(data_to_display))

    # Dropdown to select between 'Select All' and 'Custom Select'
    material_selection_type = st.selectbox('Select Materials', ['Select All', 'Custom Select'])
    if material_selection_type == 'Custom Select':
        selected_materials = st.multiselect('Select Specific Materials', list(unique_materials))
        material_filter = data_to_display['Material_translated'].apply(lambda x: any(material in str(x) for material in selected_materials))

    place_selection_type = st.selectbox('Select Places', ['Select All', 'Custom Select'])
    if place_selection_type == 'Custom Select':
        selected_places = st.multiselect('Select Specific Places', list(unique_places))
        place_filter = data_to_display['Plats'].isin(selected_places)

    # Apply filters to data
    filtered_data = data_to_display[material_filter & place_filter]

    # Displaying the map
    if 'latitude' in filtered_data.columns and 'longitude' in filtered_data.columns:
        if not filtered_data[['latitude', 'longitude']].dropna().empty:
            fig = plot_map(filtered_data, 'latitude', 'longitude')
            st.pyplot(fig)
        else:
            st.write("Geographic coordinates are not available.")

    # Displaying the bar chart for materials
    plot_materials_bar_chart(filtered_data)

    # Displaying the bar chart for objects found per year
    plot_objects_per_year(filtered_data)

    st.dataframe(filtered_data)

    st.write('To see how this data was scraped, please see [my blog](https://alpal923.github.io/).')

    st.write('Data scraped from [here](https://samlingar.shm.se/sok?type=object&query=vikingatid)')

if __name__ == '__main__':
    main()
