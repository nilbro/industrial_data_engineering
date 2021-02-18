FROM python:3.8-buster

# create work directory
WORKDIR /bro

#install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install sqlite3
#copy data
COPY data_case_study.csv .

#copy model
COPY model.pkl .

#copy source code
COPY main.py .

#run application
RUN python main.py

#open sqlite3-cli
ENTRYPOINT [ "sqlite3" ]

