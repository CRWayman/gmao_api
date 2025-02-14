from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_data():
    lat = 40.7128
    lon = -74.0060
    parameters = ["no2", "o3"]
    response = client.get(f"/data/{lat}/{lon}", params={"parameters": parameters})
    assert response.status_code == 200
    # Add more assertions based on the expected structure of the response
    # For example, you can check if the response contains the expected keys
    result = response.json()
    assert "coords" in result
    assert "data_vars" in result