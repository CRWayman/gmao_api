import requests

# Define the base URL of the FastAPI application
base_url = "http://127.0.0.1:8000"

# Test the root endpoint
response = requests.get(f"{base_url}/")
print("Root endpoint response:", response.json())

# Test the data endpoint with single parameter
params = {
    "parameters": "NO2"
}
response = requests.get(f"{base_url}/data/40.7128/-74.0060", params=params)
print("Data endpoint response with single parameter:", response.json())

# Test the data endpoint with multiple parameters
params = {
    "parameters": ["NO2", "O3"]
}
response = requests.get(f"{base_url}/data/33/22", params=params)
print("Data endpoint response with multiple parameters:", response.json())