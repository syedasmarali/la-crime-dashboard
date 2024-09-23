import pandas as pd
import os

def create_edited_csv():
    # Define the path to the original data
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'Crime_Data_from_2020_to_Present.csv')

    # Read the data
    df = pd.read_csv(data_path)

    # Limit the dataset to 100000 rows
    df = df.sample(100000)

    # Define the path to the edited CSV
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    output_path = os.path.join(output_dir, 'edited.csv')

    # Check if the directory exists, if not create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the edited CSV
    df.to_csv(output_path, index=False)

def load_data():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'edited.csv')
    df = pd.read_csv(data_path)
    return df

def preprocess_data(df):
    # Loading the data
    df = load_data()

    # Dropping the empty and none values
    df = df.dropna()

    # Convert Date_Reported to datetime
    df['Date_Reported'] = pd.to_datetime(df['Date_Reported'], errors='coerce')

    # Format the date to DD.MM.YYYY
    df['Date_Reported'] = df['Date_Reported'].dt.strftime('%d.%m.%Y')

    # Convert Date_occured to datetime
    df['Date_occured'] = pd.to_datetime(df['Date_occured'], errors='coerce')

    # Format the date to DD.MM.YYYY
    df['Date_occured'] = df['Date_occured'].dt.strftime('%d.%m.%Y')

    # Pad the values with leading zeros to ensure they are 4 digits long
    df['Time_occured'] = df['Time_occured'].apply(lambda x: f'{x:04d}')

    # Convert the time to HH:MM format
    df['Time_occured'] = df['Time_occured'].apply(lambda x: f'{x[:2]}:{x[2:]}')

    # Drop rows where 'Victim_age' is less than or equal to zero
    df = df[df['Victim_age'] > 0]

    # Return df
    return df