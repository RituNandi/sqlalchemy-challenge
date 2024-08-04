# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Define a function which calculates and returns the the date one year from the most recent date
def date_prev_year():
    
    # Define the most recent date in the Measurement dataset
    # Then use the most recent date to calculate the date one year from the last date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    first_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Return the date
    return(first_date)


# Define what to do when the user hits the homepage
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Honolulu, Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"To retrieve the minimum, average, and maximum temperatures for a specific start date, use /api/v1.0/2016-08-24 (replace start date in yyyy-mm-dd format)<br/>"
        f"To retrieve the minimum, average, and maximum temperatures for a specific start-end daterange, use /api/v1.0/2016-08-24/2017-08-23 (replace start and end date in yyyy-mm-dd format)"

    )

# Define what to do when the user hits the precipitation URL
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Perform a query to retrieve the data and precipitation scores
    one_year_pcp = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= date_prev_year()).all()
    
    # Create a dictionary from the row data and append to a list of all_data
    all_data = []
    for date, prcp in one_year_pcp:
        data_dict = {}
        data_dict["date"] = date
        data_dict["prcp"] = prcp
        all_data.append(data_dict)
        
    return jsonify(all_data)

# Define what to do when the user hits the station URL
@app.route("/api/v1.0/stations")
def stations():
    
    # Perform a query to retrieve the data and precipitation scores
    station = session.query(Station.station).group_by(Station.station).all()
    
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station))
    
    return jsonify(all_stations)

# Define what to do when the user hits the temperature observation URL
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Query the last 12 months of temperature observation data for most active station
    most_active_tobs = session.query(Measurement.date, Measurement.tobs).\
                 filter(Measurement.station == 'USC00519281').\
                 filter(Measurement.date >= date_prev_year()).all()
    
    # Create a dictionary from the row data and append to a list 
    all_tobs = []
    for date, tobs in most_active_tobs:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)
    
    return jsonify(all_tobs)

# Define what to do when the user hits the URL with a specific start date or start-end range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def startdate(start, end=None):

    # Convert the start and end dates to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    if end:
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    else:
        end_date = dt.datetime.now()  # Use current date if end date is not provided

    
    # Perform a query to retrieve the data where start date is present 
    start_end_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                 filter(Measurement.date >= start_date).\
                 filter(Measurement.date <= end_date).all()
    
        
    # Create a dictionary from the row data and append to a list 
    all_start_end_data = []
    for min, avg, max in start_end_data:
        start_dict = {}
        start_dict["TMIN"] = min
        start_dict["TAVG"] = avg
        start_dict["TMAX"] = max
        all_start_end_data.append(start_dict)
        
    return jsonify( all_start_end_data)

# Close Session
session.close()

if __name__ == '__main__':
    app.run(debug=True)