-- Initial database schema for CarePoint (v1)
--  2024-01-01

-- Patient table
CREATE TABLE patient (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    address VARCHAR(200),
    gender VARCHAR(10),
    date_of_birth DATE,
    blood_type VARCHAR(5),
    height VARCHAR(20),
    age INTEGER,
    country_origin VARCHAR(50),
    password VARCHAR(200) NOT NULL
);

-- Staff table
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE,
    phone_number VARCHAR(20),
    password VARCHAR(200) NOT NULL,
    role VARCHAR(20) DEFAULT 'staff',
    specialization VARCHAR(100)
);

-- Appointment table
CREATE TABLE appointment (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patient(id),
    doctor_id INTEGER NOT NULL REFERENCES staff(id),
    staff_id INTEGER REFERENCES staff(id),
    doctor_name VARCHAR(120) NOT NULL,
    date DATE NOT NULL,
    time VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending'
);

-- MedicalRecord table
CREATE TABLE medical_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patient(id),
    diagnosis TEXT,
    prescription TEXT,
    lab_result TEXT,
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

