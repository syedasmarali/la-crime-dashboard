import os.path
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit as st
from data_processing import load_data, preprocess_data, create_edited_csv, filter_dataframe
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# Set page layout to wide
st.set_page_config(layout="wide")

# Dashboard title
st.markdown("<h1 style='text-align: center;'>LA Crime Data Visualization</h1>", unsafe_allow_html=True)

# Add a divider
st.divider()

# Create edited csv if not present
output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'edited.csv')
if not os.path.exists(output_path):
    create_edited_csv()

# Load the dataset
df = load_data()

# Preprocess the dataset
df = preprocess_data(df)

# --- Date filter logic ---
st.sidebar.header("Select Date")

# Sidebar with a collapsible expander
with st.sidebar.expander("Date", expanded=False):
    # Convert 'Date_occured' to datetime
    df['Date_occured'] = pd.to_datetime(df['Date_occured'], format='%d.%m.%Y', errors='coerce')

    # Get the earliest and latest dates
    min_date = df['Date_occured'].min().date()
    max_date = df['Date_occured'].max().date()

    # Date inputs in Streamlit with default values
    start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

    # Get filtered date df
    #df_date = filter_dataframe(df, date_range=(start_date, end_date), date_col='Date_occured')

# --- Crime & date filter logic ---
st.sidebar.header("Select Crime Type")

# Sidebar with a collapsible expander
with st.sidebar.expander("Crime Type", expanded=False):
    # Sidebar for selecting Crime_Code
    crime_codes = df['Crime_Code'].unique()
    selected_crime_codes = st.multiselect('', crime_codes, default=crime_codes)

    # Get filtered date and crime code df
    #df_date_crime = filter_dataframe(df, col_filters={'Crime_Code': selected_crime_codes}, date_range=(start_date, end_date), date_col='Date_occured')

# --- Crime & date & gender filter logic ---
st.sidebar.header("Select Gender")

# Sidebar with a collapsible expander
with st.sidebar.expander("Gender", expanded=False):
    # Sidebar for selecting Crime_Code
    genders = df['Victim_sex'].unique()
    selected_gender = st.multiselect('', genders, default=genders)

    # Get filtered date and crime and gender df
    df_date_crime_gender = filter_dataframe(df, col_filters={'Crime_Code': selected_crime_codes, 'Victim_sex': selected_gender}, date_range=(start_date, end_date),
                                     date_col='Date_occured')

# 2 Columns
col1, col2 = st.columns(2)

# --- Map of crimes ---
with col1:
    st.markdown("<h3 style='text-align: center;'>Crime Map</h1>",
                    unsafe_allow_html=True)

    # Count the number of crimes for each location
    crime_counts = df_date_crime_gender['LOCATION'].value_counts().reset_index()
    crime_counts.columns = ['LOCATION', 'crime_count']

    # Merge the counts back to the original DataFrame
    df_date_crime_gender = df_date_crime_gender.merge(crime_counts, on='LOCATION')

    # Calculate the mean latitude and longitude for centering the map
    center_lat = df_date_crime_gender['LAT'].mean()
    center_lon = df_date_crime_gender['LON'].mean()

    # Create a Plotly map with color scale based on crime count
    fig = px.scatter_mapbox(
        df_date_crime_gender,
        lat='LAT',
        lon='LON',
        hover_name='LOCATION',
        color='crime_count',
        color_continuous_scale=px.colors.sequential.Plasma[::-1],  # You can change the color scale
        size='crime_count',  # Optional: Adjust point size based on crime count
        size_max=20,  # Maximum size of the points
        zoom=10,
        center=dict(lat=center_lat, lon=center_lon),  # Center the map
        height=400,
        width=1200,
        mapbox_style="carto-positron"
    )

    fig.update_layout(height=700, width=2000)

    st.plotly_chart(fig)

# --- Crime over time ---
with col2:
    # Assuming df is your DataFrame and 'Date_occured' is in datetime format
    df_date_crime_gender['Date_occured'] = pd.to_datetime(df_date_crime_gender['Date_occured'], format='%d.%m.%Y', errors='coerce')

    # Resample the data to group by month/year and Crime_Code for time series analysis
    df_date_crime_gender['YearMonth'] = df_date_crime_gender['Date_occured'].dt.to_period('M')  # Group by month
    crime_trends_by_type = df_date_crime_gender.groupby(['YearMonth', 'Crime_Code']).size().reset_index(name='Crime Count')

    # Convert 'YearMonth' to string format for Plotly
    crime_trends_by_type['YearMonth'] = crime_trends_by_type['YearMonth'].astype(str)

    # Create a line chart for crime trends over time by crime type
    st.markdown("<h3 style='text-align: center;'>Crime Trends Over Time by Crime Type</h3>", unsafe_allow_html=True)
    fig_line = px.line(crime_trends_by_type,
                       x='YearMonth',
                       y='Crime Count',
                       color='Crime_Code',  # Different line for each Crime_Code
                       markers=True,
                       template='plotly')

    # Set figure size for better visibility
    fig_line.update_layout(height=600, width=1200, xaxis_title="Time (Monthly)", yaxis_title="Number of Crimes")

    # Show the line chart in Streamlit
    st.plotly_chart(fig_line)

# --- Dumbell plot for comparison ---
st.markdown("<h3 style='text-align: center;'>No. of Crimes in a Defined Period</h3>", unsafe_allow_html=True)

# Convert start_date and end_date to pandas datetime for comparison
start_date_dumbell = pd.to_datetime(start_date)
end_date_dumbell = pd.to_datetime(end_date)

# Filter the DataFrame based on selected dates
filtered_df = df_date_crime_gender[(df_date_crime_gender['Date_occured'] >= start_date_dumbell) & (df_date_crime_gender['Date_occured'] <= end_date_dumbell)]

# Count the occurrences of each crime code for the selected date range
crime_counts = df_date_crime_gender['Crime_Code'].value_counts().reset_index()
crime_counts.columns = ['Crime_Code', 'Count']

# Assuming you want to compare two different periods, you can define another date range
# You might want to create another date input for a different range or set a previous date range
previous_start_date = start_date_dumbell - pd.DateOffset(years=1)
previous_end_date = end_date_dumbell - pd.DateOffset(years=1)

# Filter the DataFrame for the previous period
previous_filtered_df = df_date_crime_gender[(df_date_crime_gender['Date_occured'] >= previous_start_date) & (df_date_crime_gender['Date_occured'] <= previous_end_date)]

# Count the occurrences of each crime code for the previous date range
previous_crime_counts = previous_filtered_df['Crime_Code'].value_counts().reset_index()
previous_crime_counts.columns = ['Crime_Code', 'Previous_Count']

# Merge the two counts into a single DataFrame
merged_counts = pd.merge(crime_counts, previous_crime_counts, on='Crime_Code', how='outer').fillna(0)

# Create the dumbbell plot
fig = go.Figure()

# Add lines connecting the two points for each crime code
for index, row in merged_counts.iterrows():
    fig.add_trace(go.Scatter(
        x=[row['Previous_Count'], row['Count']],
        y=[row['Crime_Code'], row['Crime_Code']],
        mode='lines',
        line=dict(color='grey'),
        showlegend=False
    ))

# Add markers for the previous counts with the selected previous date
fig.add_trace(go.Scatter(
    x=merged_counts['Previous_Count'],
    y=merged_counts['Crime_Code'],
    mode='markers',
    name=start_date.strftime('%d.%m-%y'),
    marker=dict(color='green', size=10)
))

# Add markers for the current counts with the selected current date
fig.add_trace(go.Scatter(
    x=merged_counts['Count'],
    y=merged_counts['Crime_Code'],
    mode='markers',
    name=end_date.strftime('%d.%m.%y'),
    marker=dict(color='blue', size=10)
))

# Update layout
fig.update_layout(
    xaxis_title='Count',
    yaxis_title='Crime Code',
    height=800,
    legend_itemclick=False
)

# Display the plot in Streamlit
st.plotly_chart(fig)

# 2 Columns
col1, col2 = st.columns(2)

# --- Area wise crime ---
with col1:
    st.markdown("<h3 style='text-align: center;'>Area-wise Crime Distribution</h1>",
                unsafe_allow_html=True)

    # Count area-wise crimes
    area_crime_counts = df_date_crime_gender['Area'].value_counts().reset_index()
    area_crime_counts.columns = ['Area', 'Crime Count']

    # Treemap for area-wise crime distribution
    fig = px.treemap(area_crime_counts,
                     path=['Area'],
                     values='Crime Count',)
    st.plotly_chart(fig)

# --- Premise wise crime distribution
with col2:
    st.markdown("<h3 style='text-align: center;'>Premise-wise Crime Distribution</h1>",
                unsafe_allow_html=True)

    # Premis-wise crimes
    premis_crime_counts = df_date_crime_gender['Premis'].value_counts().reset_index()
    premis_crime_counts.columns = ['Premis', 'Crime Count']

    # Treemap for area-wise crime distribution
    fig = px.treemap(premis_crime_counts,
                     path=['Premis'],
                     values='Crime Count',)
    st.plotly_chart(fig)

# 3 Columns
col1, col2, col3 = st.columns(3)

# --- Count of victims by gender ---
with col1:
    st.markdown("<h3 style='text-align: center;'>Count of Victims by Gender</h1>",
                unsafe_allow_html=True)

    gender_counts = df_date_crime_gender['Victim_sex'].value_counts().reset_index()
    gender_counts.columns = ['Victim_sex', 'Count']

    # Plot: Count of victims by gender
    fig2 = px.bar(gender_counts, x='Victim_sex', y='Count',
                  labels={'Victim_sex': 'Gender', 'Count': 'Number of Victims'})
    st.plotly_chart(fig2)

# --- Age distribution histogram ---
with col2:
    st.markdown("<h3 style='text-align: center;'>Age Distribution of Victims by Gender</h1>",
                unsafe_allow_html=True)

    # Update colors for male and female
    color_map = {'M': 'blue', 'F': 'red', 'X': 'yellow', 'H': 'black'}

    fig = px.histogram(df_date_crime_gender, x='Victim_age', color='Victim_sex', barmode='overlay',
                       labels={'Victim_age': 'Age', 'Victim_sex': 'Gender'},
                       opacity=0.75,
                       color_discrete_map=color_map)
    st.plotly_chart(fig)

# --- Age group analysis by gender ---
with col3:
    st.markdown("<h3 style='text-align: center;'>Age Group of Victims by Gender</h1>",
                unsafe_allow_html=True)

    bins = [0, 18, 25, 35, 45, 55, 65, 100]
    labels = ['0-18', '19-25', '26-35', '36-45', '46-55', '56-65', '66+']
    df_date_crime_gender['Age_Group'] = pd.cut(df_date_crime_gender['Victim_age'], bins=bins, labels=labels)

    # Count of victims by age group and gender
    age_gender_counts = df_date_crime_gender.groupby(['Age_Group', 'Victim_sex']).size().reset_index(name='Count')

    # Plot: Pie chart of age groups by gender
    fig3 = px.sunburst(age_gender_counts, path=['Age_Group', 'Victim_sex'], values='Count')
    st.plotly_chart(fig3)

# 3 columns
col1, col2, col3 = st.columns(3)

# --- Count of victims by descent ---
with col1:
    st.markdown("<h3 style='text-align: center;'>Count of Victims by Descent</h1>",
                unsafe_allow_html=True)

    # Count the occurrences of each descent category
    descent_counts = df_date_crime_gender['Victim_descent'].value_counts().reset_index()
    descent_counts.columns = ['Victim_descent', 'Count']

    # Plot: Count of victims by descent
    fig = px.bar(descent_counts, x='Victim_descent', y='Count',
                 labels={'Victim_descent': 'Descent', 'Count': 'Number of Victims'},
                 color='Victim_descent',
                 color_discrete_map={'H': 'orange', 'W': 'blue', 'B': 'green', 'A': 'purple', 'X': 'gray'})

    st.plotly_chart(fig)

# --- Count of crimes by time ---
with col2:
    st.markdown("<h3 style='text-align: center;'>Count of Crimes by Time</h1>",
                unsafe_allow_html=True)

    # Count occurrences for each hour
    hour_counts = df_date_crime_gender['Time_occured'].value_counts().sort_index()

    # Prepare data for line chart
    hour_counts = hour_counts.reset_index()
    hour_counts.columns = ['Hour', 'Count']

    # Create line chart
    fig = px.line(
        hour_counts,
        x='Hour',
        y='Count',
        labels={'Hour': 'Hour of Day', 'Count': 'Number of Crimes'},
        markers=True
    )
    st.plotly_chart(fig)

# --- Crime status ---
with col3:
    st.markdown("<h3 style='text-align: center;'>Crime Status</h1>",
                unsafe_allow_html=True)

    # Count the occurrences of each status
    status_counts = df_date_crime_gender['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']

    # Create a pie chart for the status distribution
    fig = px.pie(status_counts, names='Status', values='Count',
                 color='Count',
                 color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig)

# 2 columns
col1, col2 = st.columns(2)

# --- Wordcloud  for crime type ---
with col1:
    st.markdown("<h3 style='text-align: center;'>Crime Types</h1>",
                unsafe_allow_html=True)

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(df_date_crime_gender['Crime_Code']))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

# --- Wordcloud  for weapon type ---
with col2:
    st.markdown("<h3 style='text-align: center;'>Weapon Types</h1>",
                unsafe_allow_html=True)

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(df_date_crime_gender['Weapon']))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

# --- Bubble chart ---
# Create a count of incidents by Premise and Crime Type
bubble_data = df_date_crime_gender.groupby(['Premis', 'Crime_Code']).size().reset_index(name='Incident Count')

# Create a bubble chart
st.markdown("<h3 style='text-align: center;'>Crime Incidents by Premises and Crime Type</h3>", unsafe_allow_html=True)
fig_bubble = px.scatter(bubble_data,
                         x='Premis',
                         y='Crime_Code',
                         size='Incident Count',
                         color='Crime_Code',  # Color by crime type
                         hover_name='Premis',
                         size_max=100,
                         template='plotly',
                         color_continuous_scale=px.colors.sequential.Viridis)

# Set figure size
fig_bubble.update_layout(height=1000, width=2000)

# Show the bubble chart in Streamlit
st.plotly_chart(fig_bubble)

# --- Violin plot ---
# Create a violin plot for Victim Age vs. Crime Type
st.markdown("<h3 style='text-align: center;'>Victim Age Distribution by Crime Type</h3>", unsafe_allow_html=True)
fig_violin = px.violin(df_date_crime_gender,
                       y='Victim_age',
                       x='Crime_Code',
                       box=True,  # Show box plot inside the violin
                       points='all',  # Show all points
                       template='plotly',
                       color='Crime_Code',  # Optional: color by Crime Type
                       color_discrete_sequence=px.colors.qualitative.Vivid)

# Set figure size
fig_violin.update_layout(height=1000, width=2000)

# Show the violin plot in Streamlit
st.plotly_chart(fig_violin)

# Print the dataset
#st.dataframe(df)