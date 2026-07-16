from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
import math
import models as models
import schemas as schemas
import service as service
from database import get_db, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clinic Management API")

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Database integrity error. Possible duplicate data or invalid foreign key."}
    )

@app.post("/clinics", response_model=schemas.ClinicResponse, status_code=status.HTTP_201_CREATED)
def create_clinic(clinic: schemas.ClinicCreate, db: Session = Depends(get_db)):
    return service.create_clinic(db, clinic)

@app.get("/clinics")
def get_clinics(page: int = 1, limit: int = 10, search: Optional[str] = None, db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    total, clinics = service.get_clinics(db, skip=skip, limit=limit, search=search)
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    return {
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "clinics": clinics
    }

@app.get("/clinics/{clinic_id}", response_model=schemas.ClinicDetailResponse)
def get_clinic(clinic_id: int, db: Session = Depends(get_db)):
    db_clinic = service.get_clinic_by_id(db, clinic_id)
    if not db_clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return db_clinic

@app.post("/doctors", response_model=schemas.DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    return service.create_doctor(db, doctor)

@app.get("/doctors", response_model=list[schemas.DoctorResponse])
def get_doctors(clinic_id: int, db: Session = Depends(get_db)):
    return service.get_doctors_by_clinic(db, clinic_id)

@app.get("/doctors/{doctor_id}", response_model=schemas.DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    db_doctor = service.get_doctor_by_id(db, doctor_id)
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

@app.patch("/doctors/{doctor_id}", response_model=schemas.DoctorResponse)
def update_doctor(doctor_id: int, doctor_update: schemas.DoctorUpdate, db: Session = Depends(get_db)):
    db_doctor = service.update_doctor(db, doctor_id, doctor_update)
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

@app.delete("/licenses/{license_id}")
def delete_license(license_id: int, db: Session = Depends(get_db)):
    success = service.delete_license(db, license_id)
    if not success:
        raise HTTPException(status_code=404, detail="License not found")
    return {"message": "Deleted"}
