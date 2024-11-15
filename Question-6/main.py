import requests
import json


def fetch_entities(blueprint, payload, jwt_token):
    url = f"https://api.getport.io/v1/blueprints/{blueprint}/entities"

    headers = {
    'Authorization': jwt_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    json_response = response.json()

    return json_response

def count_eol_frameworks(blueprint,jwt_token):
    url = f"https://api.getport.io/v1/blueprints/{blueprint}/entities-count"
    headers = {
        'Authorization': jwt_token
    }

    # Perform the GET request
    response = requests.get(url, headers=headers)

    # Raise an exception for any HTTP error
    response.raise_for_status()

    # Parse the JSON response directly
    json_response = response.json()

    # Access the 'count' value
    count_value = json_response["count"]
    print(count_value)
    return count_value

def update_service_eol_count(blueprint, eol_count, jwt_token):
    url = f"https://api.getport.io/v1/blueprints/{blueprint}/entities/:entity_identifier"

    headers = {
    'Content-Type': 'application/json',
    'Authorization': jwt_token
    }

    payload = {
        "properties": {
            "Number of EOL packages": eol_count
        }
    }
    response = requests.request("PATCH", url, headers=headers, data=payload)
    response = requests.patch(url, headers=headers, json=payload)
    print(response)
    return response






# Main function
def main():
    jwt_token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJvcmdJZCI6Im9yZ19RS1BVMHJxaW5iVWppeXk2IiwiaXNzIjoiaHR0cHM6Ly9hcGkuZ2V0cG9ydC5pbyIsImlzTWFjaGluZSI6ZmFsc2UsInBlcnNvbmFsVG9rZW4iOnRydWUsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTA1MjQ2MzM5Njk0ODY5MzYzOTIzIiwicG9ydF91c2VyX2lkIjoiZ29vZ2xlLW9hdXRoMnwxMDUyNDYzMzk2OTQ4NjkzNjM5MjMiLCJqdGkiOiI3MmY2ODcwNi0yZGNmLTQ1MjktYmEyMi1iMTAwZDhjZTQ3OTYiLCJpYXQiOjE3MzE2OTUwNjAsImV4cCI6MTczMTcwNTg2MH0.o5MnyKuYXEdqEZ5d9FXjic3-GBqZlIWzlqmX0GYpyHE"

    payload = {
        "identifier": "new-microservice",
        "title": "MyNewMicroservice",
        "icon": "Microservice",
        "team": [],
        "properties": {
        "content": "New Framework",
        "description": "This framework supports modern applications.",
        "state": "active"
        },
        "relations": {}
    }
    blueprint = "Integer"

    print("Fetching entities..")
    entities = fetch_entities(blueprint, payload, jwt_token)
    print("Fetching correct number of EOL packages..")
    total_eol = count_eol_frameworks(blueprint,  jwt_token)

    
    update_result = update_service_eol_count(entities, total_eol, jwt_token)



 
   

if __name__ == "__main__":
    main()

