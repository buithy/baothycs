'''
Name:        Bao Thy Bui
CS230:       Section 5
Data:        Motor Vehicle Crashes in MA in 2017
URL:         http://localhost:8503/

Description:

This program is designed for Motor Vehicle Crash Detection.
It allows users to explore and visualize data related to car crashes in Massachusetts.
The application provides various functionalities, including displaying raw data,
analyzing car crash distribution by city through interactive pie charts, plotting car crash locations on a map,
visualizing the monthly distribution of crashes based on different criteria (such as non-fatalities, fatalities, or both),
and conducting an analysis of crash causes with insights presented in bar charts.
'''


import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import pydeck as pdk
import numpy as np
from PIL import Image

# Set Streamlit option to suppress deprecation warnings related to matplotlib
st.set_option('deprecation.showPyplotGlobalUse', False)
# Write HTML to display a title for the Streamlit app
st.write("<h1 style='text-align: center; color: #ADD8E6;'>Motor Vehicle Crash Detection</h1>", unsafe_allow_html=True)

# Open and resize an image
img=Image.open('C:/Users/Bao Thy Bui/OneDrive - Bentley University/Spring 24/CS 230/img_final.jpg')
img_width, img_height = img.size
new_width = 600  # Set the desired width for the image
new_height = int((img_height / img_width) * new_width)
# Resize the image
resized_img = img.resize((new_width, new_height))
# Display the resized image
st.image(resized_img, use_column_width=True)



# Function to read data from a CSV file, convert column names to lowercase, and set "objectid" as index
def read_data(): #[PY3]
    df_data=pd.read_csv(
        "C:/Users/Bao Thy Bui/OneDrive - Bentley University/Spring 24/CS 230/2017_Crashes_10000_sample.csv")
    lowercase=lambda x: str(x).lower()    # Lambda function to convert column names to lowercase  #[DA1]
    df_data.rename(lowercase, axis='columns', inplace=True)
    df_data = df_data.set_index("objectid")  # Set "objectid" as index
    return df_data
# Read data from CSV file and display raw data if checkbox is checked
df_data = read_data()
if st.checkbox("Show Raw Data"):  #[ST1]
    st.subheader('Raw Data')
    st.write(df_data)



# Function to plot a pie chart showing car crash distribution by city
def plot_car_crash_distribution(df, num_cities=10): #[PY1]
    st.header('Where are the most car crashes in MA?')
    num_cities = st.slider("Select number of cities to display:", min_value=1, max_value=20, value=num_cities) # Slider widget #[ST2]
    injuries_by_city = df.groupby('city_town_name')['crash_numb'].sum().sort_values(ascending=False).head(num_cities)  #[DA6] # Group by city and sum crashes
    fig, ax = plt.subplots()   # Create a subplot
    pie = injuries_by_city.plot(kind='pie', ax=ax, autopct='%1.1f%%',
                                explode=[0.1 if i == 0 else 0 for i in range(len(injuries_by_city))])  #[VIZ1]
    ax.set_ylabel('')
    # Get the highest percentage slice
    highest_percentage_index = injuries_by_city.argmax()
    highest_percentage_city = injuries_by_city.index[highest_percentage_index]
    # Streamlit page design feature [ST4]
    st.pyplot(fig)
    # Function returns more than one value [PY2]
    return injuries_by_city, num_cities # Return data and number of cities selected #[PY2]



# Function to plot car crash locations on a map
def plot_car_crash_map(df, selected_cities):
    st.header("Map Showing Car Crashes in Selected Cities")
    # Filter data for selected cities
    filtered_df = df[df['city_town_name'].isin(selected_cities)]
    # Create view state
    view_state = pdk.ViewState(
        latitude=filtered_df['lat'].mean(),
        longitude=filtered_df['lon'].mean(),
        zoom=10
    )
    city_colors = {
        city: [np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256)]  #[PY4]uses a list comprehension to generate random colors for each city selected on the map.
        # Random color for each city
        for city in selected_cities #[PY5]
    }
    # Add a color column based on city
    filtered_df['color'] = filtered_df['city_town_name'].map(city_colors)  #[DA9] adding a new column named 'color' to the DataFrame
    # Create scatterplot layer for crashes
    scatterplot_layer = pdk.Layer(
        type="ScatterplotLayer",
        data=filtered_df,
        get_position="[lon, lat]",
        get_radius=100,
        get_color="color",  # Assign color based on city
        pickable=True
    )
    # Create map based on view state and layers
    map = pdk.Deck(
        map_style='mapbox://styles/mapbox/outdoors-v11',
        initial_view_state=view_state,
        layers=[scatterplot_layer],
        tooltip={
            "text": "Crash Location: {lat}, {lon}\nRoadway: {rdwy}",
            "style": {
                "backgroundColor": "orange",
                "color": "white"
            }
        }
    ) #[VIZ4]
    # Display the map
    st.pydeck_chart(map)



# Function to display overview of road incidents
def display_road_incidents_overview(df, selection):
    data_to_plot = pd.Series() # Initialize empty series
    if selection == "Non-Fatalities Injuries": # Check user selection
        total_data = df['numb_nonfatal_injr'].sum()  # Calculate total number of non-fatal injuries
        data_to_plot_nonfatal = df[df['numb_nonfatal_injr'] > 0]['crash_datetime'].apply(
            lambda x: pd.to_datetime(x).month).value_counts().sort_index()    # Calculate monthly distribution of non-fatal injuries
        data_to_plot_fatal = pd.Series()  # Empty series for fatal injuries
    elif selection == "Fatalities Injuries":
        total_data = df['numb_fatal_injr'].sum()
        data_to_plot_fatal = df[df['numb_fatal_injr'] > 0]['crash_datetime'].apply(
            lambda x: pd.to_datetime(x).month).value_counts().sort_index()
        data_to_plot_nonfatal = pd.Series()
    else:
        total_data = df['numb_nonfatal_injr'].sum() + df['numb_fatal_injr'].sum()
        data_to_plot_nonfatal = df[df['numb_nonfatal_injr'] > 0]['crash_datetime'].apply(
            lambda x: pd.to_datetime(x).month).value_counts().sort_index()
        data_to_plot_fatal = df[df['numb_fatal_injr'] > 0]['crash_datetime'].apply(
            lambda x: pd.to_datetime(x).month).value_counts().sort_index()

    num_bars = max(len(data_to_plot_nonfatal), len(data_to_plot_fatal)) # Determine the number of bars for plotting
    plt.figure(figsize=(10, 6))  # Set figure size
    color_palette = plt.cm.tab10.colors[:num_bars]
    # Plotting the distribution of crashes over time [DA5]
    if selection == "Non-Fatalities & Fatalities Injuries":
        if not data_to_plot_nonfatal.empty:
            plt.plot(data_to_plot_nonfatal.index, data_to_plot_nonfatal.values, marker='o', color='b', linestyle='-',
                     label='Nonfatal Injuries') #[VIZ2]
            max_nonfatal_month = data_to_plot_nonfatal.idxmax()
            max_nonfatal_value = data_to_plot_nonfatal.max()
            plt.annotate(f'Max: {max_nonfatal_value}', xy=(max_nonfatal_month, max_nonfatal_value),
                         xytext=(max_nonfatal_month, max_nonfatal_value + 10),
                         arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8, headlength=5),color='blue')
        if not data_to_plot_fatal.empty:
            plt.plot(data_to_plot_fatal.index, data_to_plot_fatal.values, marker='o', color='r', linestyle='-',
                     label='Fatal Injuries') #[VIZ2]
            max_fatal_month = data_to_plot_fatal.idxmax()
            max_fatal_value = data_to_plot_fatal.max()
            plt.annotate(f'Max: {max_fatal_value}', xy=(max_fatal_month, max_fatal_value),
                         xytext=(max_fatal_month, max_fatal_value + 10),
                         arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8, headlength=5),color='red')
    else: # For individual selections
        if not data_to_plot_nonfatal.empty:
            plt.plot(data_to_plot_nonfatal.index, data_to_plot_nonfatal.values, marker='o', color='b', linestyle='-',
                     label='Nonfatal Injuries') #[VIZ2]
        if not data_to_plot_fatal.empty:
            plt.plot(data_to_plot_fatal.index, data_to_plot_fatal.values, marker='o', color='r', linestyle='-',
                     label='Fatal Injuries')   #[VIZ2]
    plt.xlabel("Month")
    plt.ylabel("Number of Crashes")
    plt.title(f"Monthly Distribution of Crashes based on {selection}")
    plt.grid(True)
    plt.legend()
    st.pyplot()
    return total_data



# Function to analyze crash causes and display insights
def analyze_crash_causes(df):
    st.header("Analysis of Crash Causes")    # Streamlit widgets
    selected_cause = st.selectbox("Select Crash Cause:", df['vehc_seq_events_cl'].unique())
    if selected_cause:
        filtered_df = df[df['vehc_seq_events_cl'] == selected_cause]  # Filter data for selected cause
        rdwy_jnct_counts = filtered_df.groupby('rdwy_jnct_type_descr').size().reset_index(name='count') #[DA7]  # Group by roadway junction type and count crashes
        fig, ax = plt.subplots(figsize=(10, 6))  # Create subplot
        # Plotting the bar chart with custom styling
        fig, ax = plt.subplots(figsize=(10, 6))
        rdwy_jnct_counts.set_index('rdwy_jnct_type_descr').plot(kind='bar', ax=ax, color='skyblue') #[VIZ3]
        ax.set_xlabel("Roadway Junction Type")
        ax.set_ylabel("Number of Crashes")
        ax.set_title(f"Roadway Injunction Type and Crash Cause")
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.legend().set_visible(False)
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
# Analytical Insights
        st.subheader("Analytical Insights:")
        st.write(
            f"From the selected crash cause {selected_cause}, the most common types of roadway junctions associated with this crash cause are:")
        rdwy_jnct_counts_sorted = rdwy_jnct_counts.sort_values(by='count', ascending=False) # Sort counts in descending order
        for index, row in rdwy_jnct_counts_sorted.iterrows(): # Iterate over rows #[DA8] [DA2]
            st.write(f"  - {row['rdwy_jnct_type_descr']}: {row['count']} crashes")



# Main function to run the Streamlit app
def main():
    # Sidebar navigation
    st.sidebar.write("# Navigation") #[ST4]
    pages = st.sidebar.multiselect("Select pages", ["Car Crash Distribution", "Car Crash Map", "Road Incidents Overview", "Crash Causes Analysis"])

    if "Car Crash Distribution" in pages:
        injuries_by_city_data, num_cities_selected = plot_car_crash_distribution(df_data)
        st.write(f"Top {num_cities_selected} cities with the most car crashes:") #[DA3]
        st.table(injuries_by_city_data)

    if "Car Crash Map" in pages:
        selected_cities = st.multiselect("Select cities to display on the map:", df_data['city_town_name'].unique()) #[ST2]
        if selected_cities:
            plot_car_crash_map(df_data, selected_cities)

    if "Road Incidents Overview" in pages:
        st.header("Overview of Road Incidents")
        selection = st.radio("Select data to visualize:", ["Non-Fatalities Injuries", "Fatalities Injuries","Non-Fatalities & Fatalities Injuries"]) #[ST3]
        total_data = display_road_incidents_overview(df_data, selection) #[DA4]
        st.write(f"Total number of {selection}: {total_data}")

    if "Crash Causes Analysis" in pages:
        analyze_crash_causes(df_data)
# Run the main function if the script is executed directly
if __name__ == "__main__":
    df_data = read_data()
    main()

