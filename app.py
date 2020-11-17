#  Import dependencies
import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect Database into ORM classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<;start>;<br>"
        f"/api/v1.0/<;start>;/<;end>;<br>"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB:    
    session = Session(engine)
    # Query results:
    results = session.query(Measurement.prcp, Measurement.date).all()
    session.close()
    # Return the JSON representation of your dictionary.
    all_precip = []
    for prcp, date in results:
        precip_dict = {}
        precip_dict["prcp"] = prcp
        precip_dict["date"] = date 
        all_precip.append(precip_dict)

    return jsonify(all_precip)

# Return a JSON list of stations from the dataset:
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB:    
    session = Session(engine)
    # Query results:
    results = session.query(Station.station).all()

    station_list = []
    for station in results:
        station_list.append(station[0])

    return jsonify(station_list)


# Query the dates and temps of the most active station (USC00519281) for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB:
    session = Session(engine)
    
    # Query the dates:
    date_result = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
     # Convert results to a date:
    last_date = dt.datetime.strptime(date_result[0], '%Y-%m-%d').date()
     # Subtract a year from the last date:
    year_ago = last_date - dt.timedelta(days=365)
    
    # Query
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.station == 'USC00519281').\
        order_by(Measurement.date).all()
     # Close the session after use.
    session.close()

     # Create a dictionary from the row data and append to a list of dates and temps: 
    temp_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temp"] = tobs
        temp_list.append(tobs_dict)

    return jsonify(temp_list)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature
# for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal 
# to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between 
# the start and end date inclusive.

@app.route("/api/v1.0/<start>", defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def tempbydate(start, end):

# Create our session (link) from Python to the DB:
    session = Session(engine)

# Define functions listed above:
    TMIN = func.min(Measurement.tobs)
    TAVG = func.avg(Measurement.tobs)
    TMAX = func.max(Measurement.tobs)

# Put them all together as one selection:
    sel = [TMIN, TAVG, TMAX]

# Query based on one date or two dates:
    if end == None:
        results = session.query(*sel).filter(Measurement.date >=start).all()
    else:
        results = session.query(*sel).filter(Measurement.date.between(start, end)).all()

 # Create a dictionary from the rows and append to a list of temp data:    
    temp_list = []
    for TMIN, TAVG, TMAX in results:
        tobs_dict = {}
        tobs_dict["Low Temp"] = TMIN
        tobs_dict["Average Temp"] = TAVG
        tobs_dict["High Temp"] = TMAX
        temp_list.append(tobs_dict)
    session.close()
    return jsonify(temp_list)


if __name__ == '__main__':
    app.run(debug=True)
