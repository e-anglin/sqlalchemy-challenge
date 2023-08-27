# Import Flask
from flask import Flask, jsonify

# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt


# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all the available routes."""
    return(
        f"Use the browser's address bar to navigate to the data you seek:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature from last twelve months: /api/v1.0/tobs<br/>"
        f"Temperature statistics from the start date (enter date as: yyyy-mm-dd): /api/v1.0/start<br/>"
        f"Temperature statistics from start to end dates (enter date as: yyyy-mm-dd/yyyy-mm-dd): /api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
   
    session = Session(engine)
 
    date_results = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    convert_results = dt.datetime.strptime(date_results, '%Y-%m-%d').date()
    last_year = convert_results - dt.timedelta(days=365)
    sel = [measurement.date, measurement.prcp]
    query_result = session.query(*sel).filter(measurement.date <= convert_results).filter(measurement.date > last_year).all()    
    session.close()

   
    precipitation_list = []
    for prcp, date in query_result:
        prcp_dict = {}
        prcp_dict['precipitation'] = prcp
        prcp_dict['date'] = date
        precipitation_list.append(prcp_dict)
    return jsonify(precipitation_list)

    

@app.route("/api/v1.0/stations")
def stations():
    station = Base.classes.station
    
    session = Session(engine)
    
    stations_list_query = session.query(measurement.station, station.name, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    session.close()

    
    stations_list = []
    for station, name, count in stations_list_query:
         stations_dict = {}
         stations_dict['station'] = station
         stations_dict['name'] = name
         stations_dict['count'] = count
         stations_list.append(stations_dict)
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    station_data = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    active = station_data[0][0]
    latest = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    
    conv_latest = dt.datetime.strptime(latest, '%Y-%m-%d').date()
    
    twelve_mo = conv_latest - dt.timedelta(days=365)
    
    tobs_data = session.query(measurement.date, measurement.tobs).order_by(measurement.date.desc()).\
    filter(measurement.station == active).\
    filter(measurement.date <= conv_latest).\
    filter(measurement.date > twelve_mo).all()    
    session.close()

   
    tobs_list = []
    for date, tobs in tobs_data:
         tobs_dict = {}
         tobs_dict['date'] = date
         tobs_dict['tobs'] = tobs
         tobs_list.append(tobs_dict)
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    
    start_tobs_data  = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()

    
    start_tobs_list = []
    for min, avg, max in start_tobs_data:
        start_tobs_dict = {}
        start_tobs_dict['min'] = min
        start_tobs_dict['avg'] = avg
        start_tobs_dict['max'] = max
        start_tobs_list.append(start_tobs_dict)
    return jsonify(start_tobs_list)



@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    session = Session(engine)
   
    start_end_tobs_data  = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <=end).all()
    session.close()

    
    start_end_tobs_list = []
    for min, avg, max in start_end_tobs_data:
        start_end_tobs_dict = {}
        start_end_tobs_dict['min'] = min
        start_end_tobs_dict['avg'] = avg
        start_end_tobs_dict['max'] = max
        start_end_tobs_list.append(start_end_tobs_dict)
    return jsonify(start_end_tobs_list)

if __name__ == "__main__":
    app.run(debug=True)