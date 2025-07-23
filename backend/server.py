from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class DepartmentType(str, Enum):
    ADMINISTRATION = "Administration's/Domestic workers"
    BUSINESS_DEV = "Business Development Department"
    PROJECT_MGMT = "Projects Management"
    PROJECT_WORKERS = "Projects workers"
    FINANCIAL = "Financial Management & Accounts"
    BOARD = "Board of Directors"
    HR = "Human Resources"

class InsuranceTier(str, Enum):
    SENIOR_PREMIUM_4_0 = "Senior Premium 4.0"
    PREMIUM_4_0 = "Premium 4.0"
    PREMIUM_4_1 = "Premium 4.1"
    SENIOR_PREMIUM_2_1 = "Senior Premium 2.1"
    PREMIUM_2_1 = "Premium 2.1"
    PREMIUM_1_1 = "Premium 1.1"
    BASIC = "Basic"
    CLASSIC = "Classic"

class VehicleInsuranceType(str, Enum):
    COMPREHENSIVE = "Comprehensive insurance"
    THIRD_PARTY = "Third party \"against third parties\""

class ClaimStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PROCESSING = "Processing"

class FlightClass(str, Enum):
    ECONOMY = "Economy"
    BUSINESS = "Business"
    FIRST = "First Class"

# Models
class Employee(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    department: DepartmentType
    position: str
    hire_date: date
    medical_insurance_tier: InsuranceTier
    passport_number: Optional[str] = None
    passport_expiry: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EmployeeCreate(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    department: DepartmentType
    position: str
    hire_date: date
    medical_insurance_tier: InsuranceTier
    passport_number: Optional[str] = None
    passport_expiry: Optional[date] = None

class Vehicle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    license_plate: str
    make: str
    model: str
    year: int
    vin: str
    assigned_employee_id: Optional[str] = None
    insurance_type: VehicleInsuranceType
    insurance_policy_number: str
    insurance_expiry: date
    is_fleet: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class VehicleCreate(BaseModel):
    license_plate: str
    make: str
    model: str
    year: int
    vin: str
    assigned_employee_id: Optional[str] = None
    insurance_type: VehicleInsuranceType
    insurance_policy_number: str
    insurance_expiry: date
    is_fleet: bool = True

class MedicalClaim(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    claim_number: str
    provider_name: str
    service_date: date
    amount: float
    description: str
    status: ClaimStatus
    submitted_date: datetime = Field(default_factory=datetime.utcnow)
    processed_date: Optional[datetime] = None
    notes: Optional[str] = None

class MedicalClaimCreate(BaseModel):
    employee_id: str
    provider_name: str
    service_date: date
    amount: float
    description: str

class VehicleClaim(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vehicle_id: str
    claim_number: str
    incident_date: date
    description: str
    amount: float
    status: ClaimStatus
    submitted_date: datetime = Field(default_factory=datetime.utcnow)
    processed_date: Optional[datetime] = None
    notes: Optional[str] = None

class VehicleClaimCreate(BaseModel):
    vehicle_id: str
    incident_date: date
    description: str
    amount: float

class ServiceProvider(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # hospital, clinic, lab, etc.
    address: str
    phone: str
    email: Optional[str] = None
    network_tier: InsuranceTier
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ServiceProviderCreate(BaseModel):
    name: str
    type: str
    address: str
    phone: str
    email: Optional[str] = None
    network_tier: InsuranceTier
    is_active: bool = True

class FlightReservation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    departure_city: str
    arrival_city: str
    departure_date: date
    return_date: Optional[date] = None
    flight_class: FlightClass
    purpose: str
    status: str = "Pending"
    estimated_cost: float
    booking_reference: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FlightReservationCreate(BaseModel):
    employee_id: str
    departure_city: str
    arrival_city: str
    departure_date: date
    return_date: Optional[date] = None
    flight_class: FlightClass
    purpose: str
    estimated_cost: float

# Dashboard Stats Model
class DashboardStats(BaseModel):
    total_employees: int
    total_vehicles: int
    pending_medical_claims: int
    pending_vehicle_claims: int
    pending_flights: int
    employees_by_department: Dict[str, int]
    claims_by_status: Dict[str, int]

# Employee endpoints
@api_router.post("/employees", response_model=Employee)
async def create_employee(employee: EmployeeCreate):
    employee_dict = employee.dict()
    employee_obj = Employee(**employee_dict)
    await db.employees.insert_one(employee_obj.dict())
    return employee_obj

@api_router.get("/employees", response_model=List[Employee])
async def get_employees(department: Optional[DepartmentType] = None):
    query = {}
    if department:
        query["department"] = department
    employees = await db.employees.find(query).to_list(1000)
    return [Employee(**employee) for employee in employees]

@api_router.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    employee = await db.employees.find_one({"id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return Employee(**employee)

@api_router.put("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee_id: str, employee_update: EmployeeCreate):
    employee_dict = employee_update.dict()
    employee_dict["updated_at"] = datetime.utcnow()
    
    result = await db.employees.update_one(
        {"id": employee_id}, 
        {"$set": employee_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    updated_employee = await db.employees.find_one({"id": employee_id})
    return Employee(**updated_employee)

# Vehicle endpoints
@api_router.post("/vehicles", response_model=Vehicle)
async def create_vehicle(vehicle: VehicleCreate):
    vehicle_dict = vehicle.dict()
    vehicle_obj = Vehicle(**vehicle_dict)
    await db.vehicles.insert_one(vehicle_obj.dict())
    return vehicle_obj

@api_router.get("/vehicles", response_model=List[Vehicle])
async def get_vehicles(assigned_only: Optional[bool] = None):
    query = {}
    if assigned_only is not None:
        if assigned_only:
            query["assigned_employee_id"] = {"$ne": None}
        else:
            query["assigned_employee_id"] = None
    vehicles = await db.vehicles.find(query).to_list(1000)
    return [Vehicle(**vehicle) for vehicle in vehicles]

@api_router.put("/vehicles/{vehicle_id}/assign", response_model=Vehicle)
async def assign_vehicle(vehicle_id: str, employee_id: str):
    result = await db.vehicles.update_one(
        {"id": vehicle_id},
        {"$set": {"assigned_employee_id": employee_id}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    updated_vehicle = await db.vehicles.find_one({"id": vehicle_id})
    return Vehicle(**updated_vehicle)

# Medical Claims endpoints
@api_router.post("/medical-claims", response_model=MedicalClaim)
async def create_medical_claim(claim: MedicalClaimCreate):
    claim_dict = claim.dict()
    claim_dict["claim_number"] = f"MED-{str(uuid.uuid4())[:8].upper()}"
    claim_dict["status"] = ClaimStatus.PENDING
    claim_obj = MedicalClaim(**claim_dict)
    await db.medical_claims.insert_one(claim_obj.dict())
    return claim_obj

@api_router.get("/medical-claims", response_model=List[MedicalClaim])
async def get_medical_claims(employee_id: Optional[str] = None, status: Optional[ClaimStatus] = None):
    query = {}
    if employee_id:
        query["employee_id"] = employee_id
    if status:
        query["status"] = status
    claims = await db.medical_claims.find(query).sort("submitted_date", -1).to_list(1000)
    return [MedicalClaim(**claim) for claim in claims]

@api_router.put("/medical-claims/{claim_id}/status")
async def update_claim_status(claim_id: str, status: ClaimStatus, notes: Optional[str] = None):
    update_dict = {"status": status, "processed_date": datetime.utcnow()}
    if notes:
        update_dict["notes"] = notes
    
    result = await db.medical_claims.update_one(
        {"id": claim_id},
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Claim not found")
    return {"message": "Claim status updated successfully"}

# Vehicle Claims endpoints
@api_router.post("/vehicle-claims", response_model=VehicleClaim)
async def create_vehicle_claim(claim: VehicleClaimCreate):
    claim_dict = claim.dict()
    claim_dict["claim_number"] = f"VEH-{str(uuid.uuid4())[:8].upper()}"
    claim_dict["status"] = ClaimStatus.PENDING
    claim_obj = VehicleClaim(**claim_dict)
    await db.vehicle_claims.insert_one(claim_obj.dict())
    return claim_obj

@api_router.get("/vehicle-claims", response_model=List[VehicleClaim])
async def get_vehicle_claims(vehicle_id: Optional[str] = None, status: Optional[ClaimStatus] = None):
    query = {}
    if vehicle_id:
        query["vehicle_id"] = vehicle_id
    if status:
        query["status"] = status
    claims = await db.vehicle_claims.find(query).sort("submitted_date", -1).to_list(1000)
    return [VehicleClaim(**claim) for claim in claims]

# Service Provider endpoints
@api_router.post("/service-providers", response_model=ServiceProvider)
async def create_service_provider(provider: ServiceProviderCreate):
    provider_dict = provider.dict()
    provider_obj = ServiceProvider(**provider_dict)
    await db.service_providers.insert_one(provider_obj.dict())
    return provider_obj

@api_router.get("/service-providers", response_model=List[ServiceProvider])
async def get_service_providers(network_tier: Optional[InsuranceTier] = None, active_only: bool = True):
    query = {}
    if network_tier:
        query["network_tier"] = network_tier
    if active_only:
        query["is_active"] = True
    providers = await db.service_providers.find(query).to_list(1000)
    return [ServiceProvider(**provider) for provider in providers]

# Flight Reservation endpoints
@api_router.post("/flight-reservations", response_model=FlightReservation)
async def create_flight_reservation(reservation: FlightReservationCreate):
    reservation_dict = reservation.dict()
    reservation_obj = FlightReservation(**reservation_dict)
    await db.flight_reservations.insert_one(reservation_obj.dict())
    return reservation_obj

@api_router.get("/flight-reservations", response_model=List[FlightReservation])
async def get_flight_reservations(employee_id: Optional[str] = None, status: Optional[str] = None):
    query = {}
    if employee_id:
        query["employee_id"] = employee_id
    if status:
        query["status"] = status
    reservations = await db.flight_reservations.find(query).sort("created_at", -1).to_list(1000)
    return [FlightReservation(**reservation) for reservation in reservations]

@api_router.put("/flight-reservations/{reservation_id}/status")
async def update_flight_status(reservation_id: str, status: str, booking_reference: Optional[str] = None):
    update_dict = {"status": status}
    if booking_reference:
        update_dict["booking_reference"] = booking_reference
    
    result = await db.flight_reservations.update_one(
        {"id": reservation_id},
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return {"message": "Flight status updated successfully"}

# Dashboard endpoint
@api_router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats():
    # Get counts
    total_employees = await db.employees.count_documents({})
    total_vehicles = await db.vehicles.count_documents({})
    pending_medical_claims = await db.medical_claims.count_documents({"status": ClaimStatus.PENDING})
    pending_vehicle_claims = await db.vehicle_claims.count_documents({"status": ClaimStatus.PENDING})
    pending_flights = await db.flight_reservations.count_documents({"status": "Pending"})
    
    # Get employees by department
    dept_pipeline = [
        {"$group": {"_id": "$department", "count": {"$sum": 1}}}
    ]
    dept_result = await db.employees.aggregate(dept_pipeline).to_list(None)
    employees_by_department = {item["_id"]: item["count"] for item in dept_result}
    
    # Get claims by status
    claims_pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    med_claims = await db.medical_claims.aggregate(claims_pipeline).to_list(None)
    veh_claims = await db.vehicle_claims.aggregate(claims_pipeline).to_list(None)
    
    claims_by_status = {}
    for item in med_claims + veh_claims:
        status = item["_id"]
        if status in claims_by_status:
            claims_by_status[status] += item["count"]
        else:
            claims_by_status[status] = item["count"]
    
    return DashboardStats(
        total_employees=total_employees,
        total_vehicles=total_vehicles,
        pending_medical_claims=pending_medical_claims,
        pending_vehicle_claims=pending_vehicle_claims,
        pending_flights=pending_flights,
        employees_by_department=employees_by_department,
        claims_by_status=claims_by_status
    )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()