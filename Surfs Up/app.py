# Import the dependencies.
from flask import Flask, jsonify
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, inspect, func
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine('sqlite:///Resources/hawaii.sqlite')
Base = automap_base()


# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f'Welcome to the Hawaii Weather Website <br/>' 
        f'Available Routes: <br/>'
        f'/api/v1.0/precipitation <br/>'
        f'/api/v1.0/stations <br/>'
        f'/api/v1.0/tobs <br/>'
        f'/api/v1.0/yyyy-mm-dd <br/>'
        f'/api/v1.0/yyyy-mm-dd/yyyy-mm-dd'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Starting from the most recent data point in the database. 
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    date_recent = dt.datetime.strptime(recent_date[0], '%Y-%m-%d').date()
    # Calculate the date one year from the last date in data set.
    year_ago = date_recent - dt.timedelta(days=365)

    # Perform a query to retrieve the precipitation scores
    precipitation_data = session.query(measurement.date, measurement.prcp).filter(measurement.date>=year_ago).all()

    # Convert list of tuples into normal list
    return jsonify (('Precipitation Data'),list(np.ravel(precipitation_data)))

@app.route('/api/v1.0/stations')
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
        
    # Query stations
    stations = session.query(station.station).all()
    
    # Convert list of tuples into normal list & JSONify
    return jsonify (('Stations'),list(np.ravel(stations)))


@app.route('/api/v1.0/tobs')
def temperature():
      # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query for active station
    most_active = session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    top_active = most_active[0][0]
    top_active


    #Recent date of that active station
    recent_date_top_station = session.query(measurement.date).filter(measurement.station == top_active).order_by(measurement.date.desc()).first()
    date_recent = dt.datetime.strptime(recent_date_top_station[0], '%Y-%m-%d').date()
    #Y-1
    year_ago = date_recent - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    top_station = session.query(measurement.date,measurement.tobs).filter(measurement.station == top_active).filter(measurement.date >= year_ago).all()
    top_station

    #return the JSON
    return jsonify (('Most Active Station Temp Data'),list(np.ravel(top_station)))


@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def dates(start = None, end = None):
   # Create our session (link) from Python to the DB
    session = Session(engine)

    #Converts dates to right format
    start = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end = dt.datetime.strptime(end, '%Y-%m-%d').date()

    # no end date, do this     
    if not end:
        lowest_temperature = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).all()
        highest_temperature = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).all()
        average_temperature = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).all()
        
        return jsonify({'Lowest Temperature':lowest_temperature, 
                        'Highest Temperature': highest_temperature, 
                        'Average Temperaqture' :average_temperature})
    #else, do this
    else: 
        lowest_temperature = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
        highest_temperature = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
        average_temperature = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
        
        return jsonify({'Lowest Temperature':lowest_temperature, 
                        'Highest Temperature': highest_temperature, 
                        'Average Temperaqture' :average_temperature})


if __name__ == "__main__":
    app.run(debug=True)