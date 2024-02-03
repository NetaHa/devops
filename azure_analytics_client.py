import requests
from joblib import Parallel, delayed

# Define the Azure analytics server URL
azure_server_url = "https://my-containerapp.jollyforest-8bfb57eb.eastus.azurecontainerapps.io/process_event/"

# Define the JSON data to send in the request
event_data = {
    "userid": "12345",
    "eventname": "testevent"
}


def make_request(url, data):
    response = requests.post(url, json=data)
    return response.status_code

if __name__ == "__main__":
    # Number of parallel requests
    num_requests = 1000

    # Use joblib to parallelize the requests
    results = Parallel(n_jobs=-1)(delayed(make_request)(azure_server_url, event_data) for _ in range(num_requests))

    # Count successful responses (HTTP status code 200)
    successful_requests = sum(1 for status_code in results if status_code == 200)

    print(f"Total successful requests: {successful_requests}")
