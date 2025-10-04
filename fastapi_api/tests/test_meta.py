def test_health(client):
    r = client.get("/api/v1/meta/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_counts(client):
    r = client.get("/api/v1/meta/counts")
    assert r.status_code == 200
    j = r.json()
    assert {"app_profile", "appointment", "ab_event"}.issubset(set(j.keys()))
    assert all(isinstance(v, int) and v >= 0 for v in j.values())
