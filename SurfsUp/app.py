# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify
MAX_DATE = dt.date(dt.MAXYEAR, 12, 31).isoformat()

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
MeasurementClass = Base.classes.measurement
StationClass = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Front End Routes
#################################################
@app.route("/")
def home():
    content = (
        "Welcome to Maria's Hawaii Climate API!<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/tstats/&lt;start&gt;<br/>"
        "/api/v1.0/tstats/&lt;start&gt;/&lt;end&gt;<br/>"
    )
    return content


#################################################
# API Routes
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    recent_date_str = session.query(func.max(MeasurementClass.date)).scalar()     
    prev_year = dt.date.fromisoformat(recent_date_str)- dt.timedelta(days=365)
    precipitation_results=session.query(MeasurementClass.date,MeasurementClass.prcp).\
        filter(MeasurementClass.date>=prev_year).all()

    session.close()
    prcp_data = [{"date": date, "prcp": prcp} for date, prcp in precipitation_results]
    #prcp_data = list(np.ravel(precipitation_results))
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    all_stations = session.query(StationClass.station, StationClass.name).all()
    
    session.close()
    station_data = [{"station": station, "name": name} for station, name in all_stations]
    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date_str = session.query(func.max(MeasurementClass.date)).scalar()     
    prev_year = dt.date.fromisoformat(recent_date_str)- dt.timedelta(days=365)
    temp_results = session.query(MeasurementClass.date,MeasurementClass.tobs).\
        filter(MeasurementClass.date>=prev_year).\
        filter(MeasurementClass.station == 'USC00519281').\
        all()

    session.close()
    temp_data = [dict(row._mapping) for row in temp_results]
    return jsonify(temp_data)

@app.route("/api/v1.0/tstats/<start>")
@app.route("/api/v1.0/tstats/<start>/<end>")
def tstats(start, end=MAX_DATE):
    session = Session(engine)
    
    temps_active = session.query(
    func.min(MeasurementClass.tobs),
    func.max(MeasurementClass.tobs),
    func.avg(MeasurementClass.tobs)
    ).filter(MeasurementClass.date >= start).all()
    
    session.close()
    min_temp, max_temp, avg_temp = temps_active[0]
    ##return jsonify([start, end]) 
    return jsonify({
        "start_date": start,
        "end_date": end,
        "tstats": {
            "min_temperature": min_temp,
            "max_temperature": max_temp,
            "avg_temperature": avg_temp
        }
    })



if __name__ =="__main__":
    app.run()





















