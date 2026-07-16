from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
import models as models
import schemas as schemas

def create_clinic(db: Session, clinic_data: schemas.ClinicCreate) -> models.Clinic:
    try:
        db_clinic = models.Clinic(**clinic_data.model_dump())
        db.add(db_clinic)
        db.commit()
        db.refresh(db_clinic)
        return db_clinic
    except Exception as e:
        db.rollback()
        raise e

def get_clinic_by_id(db: Session, clinic_id: int) -> Optional[models.Clinic]:
    return db.query(models.Clinic).filter(models.Clinic.id == clinic_id).first()

def get_clinics(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    query = db.query(models.Clinic)
    if search:
        query = query.filter(models.Clinic.clinic_name.ilike(f"%{search}%"))
    total = query.count()
    clinics = query.offset(skip).limit(limit).all()
    return total, clinics

def create_doctor(db: Session, doctor_data: schemas.DoctorCreate) -> models.Doctor:
    try:
        db_doctor = models.Doctor(**doctor_data.model_dump())
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        db.rollback()
        raise e

def get_doctor_by_id(db: Session, doctor_id: int) -> Optional[models.Doctor]:
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()

def get_doctors_by_clinic(db: Session, clinic_id: int):
    return db.query(models.Doctor).filter(models.Doctor.clinic_id == clinic_id).all()

def update_doctor(db: Session, doctor_id: int, doctor_update: schemas.DoctorUpdate) -> Optional[models.Doctor]:
    try:
        db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
        if not db_doctor:
            return None
        
        update_data = doctor_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_doctor, key, value)
            
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        db.rollback()
        raise e

def delete_license(db: Session, license_id: int) -> bool:
    try:
        db_license = db.query(models.License).filter(models.License.id == license_id).first()
        if not db_license:
            return False
            
        db.delete(db_license)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
