with src as (
  select
    id::int as event_id,
    patient_id::int as patient_id,
    nullif("group",'') as "group",
    nullif(event_name,'') as event_name,
    event_datetime::timestamp as event_datetime
  from {{ source('public','ab_event') }}
)
select * from src
