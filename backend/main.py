from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models, schemas, crud, induction
from database import engine, SessionLocal, Base

from fastapi import File,UploadFile
import csv
from io import StringIO

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/trains", response_model=list[schemas.TrainResponse])
def read_trains(db: Session = Depends(get_db)):
    return crud.get_trains(db)

@app.post("/trains")
def add_train(train: schemas.TrainBase, db: Session = Depends(get_db)):
    return crud.create_train(db, train)

from fastapi import Query

@app.get("/generate-induction")
def generate_induction(
    branding_weight: int = Query(2),
    mileage_weight: int = Query(3),
    risk_weight: int = Query(5),
    db: Session = Depends(get_db)
):
    trains = crud.get_trains(db)
    
    selected, rejected = induction.evaluate_trains(
        trains,
        branding_weight=branding_weight,
        mileage_weight=mileage_weight,
        risk_weight=risk_weight
    )
    
    return {
        "weights_used": {
            "branding_weight": branding_weight,
            "mileage_weight": mileage_weight,
            "risk_weight": risk_weight
        },
        "selected": selected[:15],
        "rejected": rejected
    }

@app.post("/upload-trains")
async def upload_trains(file: UploadFile = File(...), db: Session = Depends(get_db)):
    
    contents = await file.read()
    decoded = contents.decode("utf-8")
    csv_reader = csv.DictReader(StringIO(decoded))

    count = 0

    for row in csv_reader:
        train_data = {
            "name": row["name"],
            "fitness_valid": row["fitness_valid"].lower() == "true",
            "open_job_card": row["open_job_card"].lower() == "true",
            "cleaning_available": row["cleaning_available"].lower() == "true",
            "mileage": float(row["mileage"]),
            "branding_priority": int(row["branding_priority"])
        }

        crud.create_train(db, schemas.TrainBase(**train_data))
        count += 1

    return {"message": f"{count} trains uploaded successfully"}