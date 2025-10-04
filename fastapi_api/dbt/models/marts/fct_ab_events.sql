select
  e.event_id,
  e.patient_id,
  e."group",
  e.event_name,
  e.event_datetime
from {{ ref('stg_ab_event') }} e
