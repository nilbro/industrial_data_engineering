'''
Created Date: Saturday, October 17th 2020, 6:25:37 pm
Author: Nilabhra

'''


import pandas as pd
import joblib 
from sqlalchemy import create_engine
import warnings
import time
from tqdm import tqdm
warnings.filterwarnings("ignore")

def transform(raw_data):
    """Takes Raw Dataframe and does the following:
        * Substite Missing Values with 0
        * Feature Enrichment
        * Normalization (Mean=0, SD=1) 
    Returns normalized dataframe and a subset of transformed dataframe"""

    # Substitute missisng values with 0
    data = raw_data.fillna(0)

    # create new feature columns 
    data['boom_long'] = data[['boom_lift', 'boom_lower']].mean(axis=1)
    data['boom_lati'] = data[['boom_forward', 'boom_backward']].mean(axis=1)
    data['drill_boom_long'] = data[['drill_boom_turn_left', 'drill_boom_turn_right']].mean(axis=1)
    data['drill_boom_lati'] = data[['drill_boom_turn_forward', 'drill_boom_turn_backward']].mean(axis=1)
    data['beam'] = data[['beam_left', 'beam_right']].mean(axis=1)

    #select a subset of transformed dataframe
    transformed_data = data[['engine_speed', 'hydraulic_drive_off','drill_boom_in_anchor_position','pvalve_drill_forward', 'bolt', 'boom_long', 'boom_lati', 'drill_boom_long', 'drill_boom_lati', 'beam']]
    
    #normalize transformed dataframe
    normalized_data=(transformed_data-transformed_data.mean())/transformed_data.std()
    return transformed_data,normalized_data



def predict(normalized_data,raw_data):
    """"Takes in normalized dataframe and does the following:
            * Predict Activites with the trained classification model provided
        Returns a dataframe with timestamp and predicted activity"""

    # load model
    loaded_model = joblib.load('model.pkl')

    # predict activity
    predicted_activity = loaded_model.predict(normalized_data)

    # create new dataframe with timestamp and predicted activity
    predicted_activity_df = pd.DataFrame(data=predicted_activity,columns=['predicted_activity'])
    predicted_df = raw_data[['timestamp']].join(predicted_activity_df)
    return predicted_df



def compute_results_activity(predicted_df):
    """Takes in predicted dataframe and does the following:
            * Finds out the start_time, end_time and duration of each activity
        Returns a dataframe with the same information"""

    # specify the columns of the final dataset
    activity_cols = ['start_time','end_time', 'activity_type', 'duration in seconds']
    activity_lst = []

    # find out initial activity and start timestamp of the activity
    initial_activity = predicted_df['predicted_activity'][0]
    start_timestamp = predicted_df['timestamp'][0]
    duration=0

    for index, row in tqdm(predicted_df.iterrows(),desc ="Calculating Duration of Each Activity", total=predicted_df.shape[0]):
        #print(index)
        if row['predicted_activity']!=initial_activity:
            end_timestamp=row['timestamp']
            duration=end_timestamp-start_timestamp
            activity_lst.append([start_timestamp,end_timestamp,initial_activity,duration])
            start_timestamp=end_timestamp
        initial_activity=row['predicted_activity']

    # build activity dataframe with start_time, end_time and duration of each activity
    activity_data = pd.DataFrame(activity_lst, columns=activity_cols)
    return activity_data


def compute_results_speed(raw_data):
    """Takes in raw dataframe and does the following:
        * Compute 5 min average speed
        Returns dataframe with 5 min timestamps and average speed"""

    # Select subset of original dataframe
    speed_data = raw_data[['timestamp','engine_speed']]

    # Find average speed for the first 5 mins
    initial_mean_speed = speed_data['engine_speed'].head(300).mean().round(decimals=5)

    # Compute 5-min average speed over all records
    speed_data['average_speed'] = speed_data['engine_speed'].rolling(300,center=False).mean()

    # select records every 5 minutes
    speed_data = speed_data.iloc[::300, :]
    speed_data['average_speed']=speed_data['average_speed'].round(decimals=5)

    # fill first missing average speed
    speed_data=speed_data.fillna(initial_mean_speed)

    # build speed dataframe with 5-min timestamp and average_speed
    average_speed_data = speed_data[['timestamp','average_speed']]
    average_speed_data = average_speed_data.set_index('timestamp')
    return average_speed_data


def write_to_db(engine,average_speed_data,activity_data):
    """Write outputs to two tables in SQLite:
        * SPEED: 5-min timestamp and average_speed
        * ACTIVITY: start_time, end_time and duration of each activity """
    
    engine.connect()
    average_speed_data.to_sql('SPEED', con=engine, if_exists='replace')
    activity_data.to_sql('ACTIVITY', con=engine, if_exists='replace')
    engine.dispose()



# Read data
print("Reading data from csv...")
raw_data = pd.read_csv('data_case_study.csv',parse_dates=True)

# transform and normalize data
print("Transforming and normalizing data...")
transformed_data, normalized_data = transform(raw_data)

# predict using model
print("Predicting activity...")
predicted_df = predict(normalized_data,raw_data)

# compute 5-minute average speed
print("Computing 5-min average speed...")
average_speed_data = compute_results_speed(raw_data)

# compute start_time, end_time, activity and duration of activity
print("Computing start time, end time, duration of each activity...")
activity_data = compute_results_activity(predicted_df)

# create connection to sqlite and save the data
print("Writing to sqlite database mydb.db...")
engine = create_engine('sqlite:///mydb.db', echo=False)
write_to_db(engine,average_speed_data,activity_data)


