from sqlalchemy.orm import Session
from sqlalchemy import text


# Example: funnel counts per A/B group
def ab_funnel_counts(db: Session):
    sql = """
    with ev as (
      select patient_id, "group", event_name
      from ab_event
      group by patient_id, "group", event_name
    )
    select
      "group",
      sum(case when event_name='reminder_sent' then 1 else 0 end) as sent,
      sum(case when event_name='reminder_viewed' then 1 else 0 end) as viewed,
      sum(case when event_name='appointment_confirmed' then 1 else 0 end) as confirmed
    from ev
    group by "group"
    order by "group"
    """
    return [dict(r) for r in db.execute(text(sql)).mappings().all()]
