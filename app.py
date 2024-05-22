# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


#################################################
# Database Setup
#################################################

# Create engine to connect to SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Flask Routes
# Define homepage route
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Define precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of precipitation data for the last 12 months."""
    # Calculate the date 12 months ago from the last date in the database
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date_dt = dt.datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date_dt - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert query results to dictionary
    precipitation_dict = {}
    for date, prcp in results:
        precipitation_dict[date] = prcp

    return jsonify(precipitation_dict)

# Define stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    # Query all stations
    results = session.query(Station.station).all()
    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

# Define temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""
    # Calculate the date 12 months ago from the last date in the database
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date_dt = dt.datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date_dt - dt.timedelta(days=365)

    # Query temperature observations for the most active station for the last 12 months
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert query results to list of dictionaries
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

# Define start date route
@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return a JSON list of the minimum, average, and maximum temperature for dates greater than or equal to the start date."""
    # Query for TMIN, TAVG, and TMAX for dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Convert query results to list of dictionaries
    temp_stats_list = []
    for min_temp, avg_temp, max_temp in results:
        temp_stats_dict = {}
        temp_stats_dict["TMIN"] = min_temp
        temp_stats_dict["TAVG"] = avg_temp
        temp_stats_dict["TMAX"] = max_temp
        temp_stats_list.append(temp_stats_dict)

    return jsonify(temp_stats_list)

# Define start-end date route
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return a JSON list of the minimum, average, and maximum temperature for a specified start-end date range."""
    # Query for TMIN, TAVG, and TMAX for dates between start and end date (inclusive)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Convert query results to list of dictionaries
    temp_stats_list = []
    for min_temp, avg_temp, max_temp in results:
        temp_stats_dict = {}
        temp_stats_dict["TMIN"] = min_temp
        temp_stats_dict["TAVG"] = avg_temp
        temp_stats_dict["TMAX"] = max_temp
        temp_stats_list.append(temp_stats_dict)

    return jsonify(temp_stats_list)

if __name__ == '__main__':
    app.run(debug=True)