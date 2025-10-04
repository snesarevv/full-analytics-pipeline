select
  patient_id,
  max(traffic_source) as traffic_source,
  max(device) as device
from {{ ref('stg_app_profile') }}
group by patient_id
