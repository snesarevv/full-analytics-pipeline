select
  a.appointment_id,
  a.patient_id,
  a.age,
  a.gender,
  a.doctor_name,
  a.appointment_reason,
  a.appointment_date,
  a.appointment_status
from {{ ref('stg_appointment') }} a
