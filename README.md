# A sample Case Study for Data Engineers 

## Introduction
In this task your're asked to write a pipeline that does the following:
+ read raw data from a csv file
+ transform the data to be used as input for a classification model
+ load a saved model and predict activities of a machine
+ write the results to a database of your choice

Additionally, you will need to setup the database and provide a dockerfile to enable us to run your project

## Raw Data
The raw signal data is provided in the attached file 'data_case_study.csv'. The column 'timestamp' contains the epoch timestamp in seconds of the measurement

## Transforming the data
To be usable as input for the model the following transformations need to be done:
+ Create a new column 'boom_long' which is defined as the average of 'boom_lift' and 'boom_lower'
+ Create a new column 'boom_lati' which is defined as the average of 'boom_forward' and 'boom_backward'
+ Create a new column 'drill_boom_long' which is defined as the average of 'drill_boom_turn_left' and 'drill_boom_turn_right'
+ Create a new column 'drill_boom_lati' which is defined as the average of 'drill_boom_turn_forward' and 'drill_boom_turn_backward'
+ Create a new column 'beam' which is defined as the average of 'beam_left' and 'beam_right'
+ Keep only the following columns of the data: 'engine_speed', 'hydraulic_drive_off',
  'drill_boom_in_anchor_position', 'pvalve_drill_forward', 'bolt',
  'boom_long', 'boom_lati', 'drill_boom_long', 'drill_boom_lati', 'beam'
+ Impute the data. Set missing values to 0
+ Scale the data in such a way that the mean is shifted to 0 and the standard deviation equals 1

## Classification Model
+ Load the model, which was dumped with the joblib module, from the attached file 'model.pkl'
+ Predict the activity types for each timestamp using the predict method of the model

## Save the data
Two datasets shall be written to the database of your choice:
+ 5 minute average of 'engine_speed' in a table called 'SPEED' containing the 5 minute timestamps and the average speeds
+ Activities predicted by the model to a table called 'ACTIVITY' containing the start and end timestamp, duration in seconds and the type (the classification predicted by the model) of the activity. An activity is a time period in which the activity type doesn't change. Eg.
+-----+--------+-----+
| ts  | type   | ID  |
+-----+--------+-----+
|  1  |   A    |  1  |
+-----+--------+-----+
|  2  |   A    |  1  |
+-----+--------+-----+
|  3  |   B    |  2  |
+-----+--------+-----+
|  4  |   B    |  2  |
+-----+--------+-----+
|  5  |   A    |  3  |
+-----+--------+-----+
|  6  |   A    |  3  |
+-----+--------+-----+
ts = timestamp, type = Activity Type, ID = Unique Activity

