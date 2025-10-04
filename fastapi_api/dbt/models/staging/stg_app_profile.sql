with src as (
  select
    patient_id::int as patient_id,
    nullif(traffic_source,'') as traffic_source,
    nullif(device,'') as device
  from {{ source('public','app_profile') }}
)
select * from src
