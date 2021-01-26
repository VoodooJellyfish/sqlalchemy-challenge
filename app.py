import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from dateutil.relativedelta import relativedelta

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement

Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station

#################################################
# Flask Routes
#################################################
@app.route("/")
def Home():
    """List all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start_date>/<end_date><br/>")


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns Precipitation Data by Date"""
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = recent_date[0]
    start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= recent_date).order_by(Measurement.date).all()
    prcp_dict = [r._asdict() for r in precip_data]   
    session.close()
    return jsonify(prcp_dict)
    

@app.route("/api/v1.0/stations")
def station():
    """Returns List of Stations"""
    session = Session(engine)
    stations = session.query(Measurement.station).group_by(Measurement.station).all()
    station_list = list(np.ravel(stations))
    session.close()
    return jsonify(station_list)
    
    
@app.route("/api/v1.0/tobs")
def tobs():
    """Returns List of Observed Temperatures"""
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = recent_date[0]
    start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    station_counts = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_id = station_counts[0][0]
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= recent_date).\
        filter(Measurement.station == most_active_id)
    tobs_list = [r._asdict() for r in tobs_data]
    session.close()
    return jsonify(tobs_list)
    

@app.route("/api/v1.0/<start_date>")
def start(start_date):
    """Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date """
    session = Session(engine)
    min_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date)
    min_temp = min_temp[0][0]
    max_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date)
    max_temp = max_temp[0][0]
    avg_temp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date)
    avg_temp = avg_temp[0][0]
    summary = {
        "Min Temp:": min_temp,
        "Max Temp:": max_temp,
        "Avg Temp:": avg_temp
        }
    session.close()    
    return jsonify(summary)
    

@app.route("/api/v1.0/<start_date>/<end_date>")
def end(start_date, end_date):
    """Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for date range"""
    session = Session(engine)
    min_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date)
    min_temp = min_temp[0][0]
    max_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date)
    max_temp = max_temp[0][0]
    avg_temp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date)
    avg_temp = avg_temp[0][0]
    summary = {
        "Min Temp:": min_temp,
        "Max Temp:": max_temp,
        "Avg Temp:": avg_temp
        }
    session.close()
    return jsonify(summary)
    


if __name__ == "__main__":
    app.run(debug=True)
