def test_check_database(client):
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"database": "ok"}
