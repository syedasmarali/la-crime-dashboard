# LA Crime Data Visualization Dashboard

This project is an interactive **Streamlit** dashboard that provides insightful visualizations of Los Angeles Police Department (LAPD) crime data. It includes **15 visualizations**, such as wordclouds, violin plots, and location maps, offering a deep dive into crime patterns across the city.

## Project Features:
- **Wordcloud Plots**: Visualize the frequency of crime types.
- **Violin Plots**: Analyze the distribution of crimes across areas.
- **Location Maps**: View crime hotspots using latitude (LAN) and longitude (LON) data.
- **Interactive Filters**: Explore data by crime category, location, and date range.
- **CSV Data Integration**: The dashboard uses crime data from a CSV file.

## Getting Started:

- Clone the Repository:
  To get started, clone the repository to your local machine:
  ```bash
  git clone https://github.com/syedasmarali/la-crime-dashboard.git
  cd la-crime-dashboard

- Create a Virtual Environment:
  ```bash
  python -m venv .venv

- Activate the virtual environment:
  - On Windows:
    ```bash
    python -m venv .venv
  - On macOS/Linux:
    ```bash
    Source .venv/bin/activate

- Install the required packages:
  ```bash
  pip install -r requirements.txt

- Setup data Directory and Add the CSV File:
  - Create a data directory in the root folder of the project:
    ```bash
    mkdir data
  - Dpownload the LAPD Crime data from kaggle and place the downloaded CSV file inside the data directory.

- Run the streamlit app:
  ```bash
  streamlit run src/app.py

  Now, you can view and interact with the LA Crime Data dashboard in your web browser!
