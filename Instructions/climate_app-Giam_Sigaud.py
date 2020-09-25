# Import Dependencies
# ***Imported datetime due to having to manipulate dates for Routes Temp <start> and Temp <start>/<end>
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# ***Overall Flask format: From 10-Advanced-Data-Storage-and-Retrieval/3/Activities/10-Ins_Flask_with_ORM/app.py
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# ***On lines 51 & 52 I had to figure out that entering the words <start> or <end> didn't work. Instead, I am asking the recipient to input the date in the format I describe then the route does its job. This was a learning.
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start in format YYYY-m-d<br/>"
        f"/api/v1.0/temp/start/end in format YYYY-m-d/YYYY-m-d"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

#***timedelta: From 10-Advanced-Data-Storage-and-Retrieval/3/Activities/02-Ins_Dates
    # Return the precipitation data for the last year
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()

    # *** Here I was fuzzy on list comprehension so I stack-overflowed it and found the explanation below. I saved it for future reference.
    # Dictionary with date as the key and prcp as the value
    # {key: value for (key, value) in iterable} - from stack overflow - also in Emoji exercise.
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

# ***Ravel: From 10-Advanced-Data-Storage-and-Retrieval/3/Activities/03-Stu_Dates/Omar_Dates.ipynb
# ***I was fuzzy on Ravel so I sourced it to make sure I could recall this learning in the future. Turns out it is a pretty simple concept.
    # Ravel returns a contiguous flattened array - stack overflow. 
    # Ravel returns the list of stations found in each row in one line.
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    # """Return the temperature observations (tobs) for previous year."""
    # Calculate the date 1 year ago from last date in database - same as in precipitation route
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= prev_year).all()
    
    temperatures = list(np.ravel(results))

    # Return the results
    return jsonify(temps=temperatures)

@app.route("/api/v1.0/temp/<start>")
def single_date(start):
	# Set up for user to enter date
	Start_Date = dt.datetime.strptime(start,"%Y-%m-%d")
	
    # Query Min, Max, and Avg based on date
	summary_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).filter(Measurement.date >= Start_Date).all()
	
    # Close the Query
	session.close() 
	
	summary = list(np.ravel(summary_stats))

	# Jsonify summary
	return jsonify(summary)
   
@app.route("/api/v1.0/temp/<start>/<end>")
def start_end(start=None, end=None):
    
    # ***sel = (different queries) & query(*sel): From 10-Advanced-Data-Storage-and-Retrieval/3/Activities/01-Ins-Joins/Ins_joins.ipynb
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).filter(Measurement.date >= start).all()

        temperatures = list(np.ravel(results))
        return jsonify(temperatures)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temperatures = list(np.ravel(results))
    return jsonify(temperatures=temperatures)

if __name__ == '__main__':

    app.run(port=9999)
