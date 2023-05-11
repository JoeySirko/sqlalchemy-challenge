# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C:/Users/Joey/Documents/GitHub/School/Week 10/sqlalchemy-challenge/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
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
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    year_ago_date = most_recent_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago_date).\
        filter(Measurement.date <= most_recent_date).all()

    session.close()

    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    year_ago_date = most_recent_date - dt.timedelta(days=365)

    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= year_ago_date).\
        filter(Measurement.date <= most_recent_date).all()

    session.close()

    tobs_data = list(np.ravel(results))
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start_only(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    temperatures = list(np.ravel(results))
    return jsonify(temperatures)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    temperatures = list(np.ravel(results))
    return jsonify(temperatures)

if __name__ == '__main__':
    app.run(debug=True)