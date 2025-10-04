from jsonschema import validate

COUNTS_SCHEMA = {
    "type": "object",
    "properties": {
        "app_profile": {"type": "integer", "minimum": 0},
        "appointment": {"type": "integer", "minimum": 0},
        "ab_event": {"type": "integer", "minimum": 0}
    },
    "required": ["app_profile", "appointment", "ab_event"]
}

AB_EVENTS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "patient_id": {"type": "integer"},
            "group": {"type": ["string", "null"]},
            "event_name": {"type": ["string", "null"]},
            "event_datetime": {"type": ["string", "null"]}
        },
        "required": ["id", "patient_id"]
    }
}


def test_contract_counts(client):
    r = client.get("/api/v1/meta/counts")
    r.raise_for_status()
    validate(instance=r.json(), schema=COUNTS_SCHEMA)


def test_contract_ab_events_page(client):
    r = client.get("/api/v1/ab_events?limit=5")
    r.raise_for_status()
    validate(instance=r.json(), schema=AB_EVENTS_SCHEMA)
