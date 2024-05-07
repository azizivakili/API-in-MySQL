from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Dict

app = FastAPI()

# Database connection URL for MySQL
DATABASE_URL = "mysql+mysqlconnector://username:password@localhost/db_name"

# Create the engine
engine = create_engine(DATABASE_URL)

# Create a session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Define Flight model
class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    aircraft = Column(String, index=True)
    destination = Column(String)
    departure_time = Column(DateTime)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# AddFlight: Add a new flight entry
@app.post("/add-flight")
def add_flight(flight_data: Dict[str, str], db: Session = Depends(get_db)):
    try:
        flight = Flight(**flight_data)
        db.add(flight)
        db.commit()
        db.refresh(flight)
        return {"message": "Flight added successfully", "flight_id": flight.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
# SearchFlight: Search flight by Aircraft name
@app.get("/search-flight")
def search_flight(aircraft_name: str = Query(..., title="Aircraft Name"), db: Session = Depends(get_db)):
    flights = db.query(Flight).filter(Flight.aircraft == aircraft_name).all()
    if not flights:
        raise HTTPException(status_code=404, detail=f"No flights found for Aircraft: {aircraft_name}")
    return flights
    
# DeleteFlight: Delete a flight based on Aircraft
@app.delete("/delete-flight")
def delete_flight(aircraft_name: str = Query(..., title="Aircraft Name"), db: Session = Depends(get_db)):
    # Delete the flight(s) with the specified Aircraft name
    deleted_count = db.query(Flight).filter(Flight.aircraft == aircraft_name).delete()
    db.commit()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"No flights found for Aircraft: {aircraft_name}")
    return {"message": f"{deleted_count} flight(s) deleted successfully for Aircraft: {aircraft_name}"}
