with src as (
  select
    id::int as appointment_id,
    patient_id::int as patient_id,
    age::int as age,
    nullif(gender,'') as gender,
    nullif(doctor_name,'') as doctor_name,
    nullif(appointment_reason,'') as appointment_reason,
    appointment_date::date as appointment_date,
    nullif(appointment_status,'') as appointment_status
  from {{ source('public','appointment') }}
)
select * from src
