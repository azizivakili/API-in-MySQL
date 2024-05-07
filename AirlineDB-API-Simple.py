from fastapi import FastAPI, HTTPException, Query, Body, Depends
from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict

app = FastAPI()

# Connect to MongoDB
client = MongoClient(
    host="127.0.0.1",
    port=27017,
    username="admin",
    password="pass",
    authSource="admin"
)

# Access the database and collection
database_name = "AirlineDB"
database = client[database_name]
collection = database["AirlinesDelay"]

# Define dependency to check credentials
def check_credentials(username: str, password: str):
    if username == "admin" and password == "pass":
        return True
    else:
        return False

# Define dependency to get MongoDB client
def get_db_client(username: str = "", password: str = "", verified: bool = Depends(check_credentials)):
    if verified:
        return client
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


# SowTable: Display all flight entries
@app.get("/show-table")
def show_table():
    return list(collection.find({}, {"_id": 0}))

# SowTable: Display all flight entries
#@app.get("/show-table-csv")
#def show_table():
#    flights = list(collection.find({}, {"_id": 0}))
#    if not flights:
#        raise HTTPException(status_code=404, detail="No flights found")

    # Prepare CSV data
    csv_data = StringIO()
    csv_writer = csv.DictWriter(csv_data, fieldnames=flights[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(flights)

    # Return CSV response
    response = Response(content=csv_data.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=flights.csv"
    return response

# TableColumns: Display column names
@app.get("/table-columns")
def table_columns():
    return list(collection.find_one().keys())

# Filter: Filter data based on column name
@app.get("/filter")
def filter_data(column_name: str = Query(..., title="Column Name")):
    if column_name not in collection.find_one().keys():
        raise HTTPException(status_code=404, detail="Column not found")
    return [document[column_name] for document in collection.find({}, {column_name: 1, "_id": 0})]


# AddFlight: Add a new flight entry
@app.post("/add-flight")
def add_flight(flight_data: Dict[str, str], db: MongoClient = Depends(get_db_client)):
    try:
        # Insert the flight data into the collection
        result = collection.insert_one(flight_data)
        inserted_id = result.inserted_id
        return {"message": "Flight added successfully", "flight_id": str(inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
# SearchFlight endpoint to search flight by Aircraft name
@app.get("/search-flight")
def search_flight(aircraft_name: str = Query(..., title="Aircraft Name")):
    flights = list(collection.find({"Aircraft": aircraft_name}, {"_id": 0}))
    if not flights:
        raise HTTPException(status_code=404, detail=f"No flights found for Aircraft: {aircraft_name}")
    return flights
    
    
# DeleteFlight: Delete a flight based on Aircraft
@app.delete("/delete-flight")
def delete_flight(aircraft_name: str = Query(..., title="Aircraft Name"), db: MongoClient = Depends(get_db_client)):
    # Delete the flight(s) with the specified Aircraft name
    result = collection.delete_many({"Aircraft": aircraft_name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"No flights found for Aircraft: {aircraft_name}")
    return {"message": f"{result.deleted_count} flight(s) deleted successfully for Aircraft: {aircraft_name}"}

