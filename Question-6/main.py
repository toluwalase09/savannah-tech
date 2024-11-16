import requests
from dotenv import load_dotenv
import os


def fetch_service_entities(base_url, headers):
    """Fetch all service entities."""
    url = f"{base_url}/v1/blueprints/service/entities"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('entities', [])


def fetch_frameworks_entities(base_url, headers):
    """Fetch all framework entities."""
    url = f"{base_url}/v1/blueprints/framework/entities"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('entities', [])


def count_eol(base_url, blueprint_id, headers):
    """Count the number of entities marked as EOL."""
    url = f"{base_url}/v1/blueprints/{blueprint_id}/entities-count"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("count", 0)


def update_service_eol_count(service_id, eol_count, base_url, headers):
    """Update a service entity with the EOL count."""
    url = f"{base_url}/v1/blueprints/service/entities/{service_id}"
    payload = {"properties": {"Number of EOL packages": eol_count}}
    # Log the request details
    print(f"PATCH Request URL: {url}")
    print(f"Payload: {payload}")

    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Updated Service {service_id}: EOL count set to {eol_count}")
    except requests.exceptions.RequestException as req_err:
        print(f"Failed to update Service {service_id}: {req_err}")
        print(f"Skipping Service {service_id}...")

def main():
    load_dotenv()

    jwt_token = os.getenv("jwt_token")
    # Headers for Port API requests
    HEADERS = {
        'Authorization': jwt_token,
        'Content-Type': 'application/json'
    }
    PORT_BASE_URL = os.getenv("base_url")

    blueprint_id = "Integer"
    eol_no = count_eol(PORT_BASE_URL, blueprint_id, HEADERS)
    print(f"Total EOL entities: {eol_no}")

    # Get all services and frameworks
    services = fetch_service_entities(PORT_BASE_URL, HEADERS)
    frameworks = fetch_frameworks_entities(PORT_BASE_URL, HEADERS)

    # Create a set of EOL framework IDs for efficient lookup
    eol_framework_ids = {
        framework['identifier']
        for framework in frameworks
        if framework['properties']['state'] == 'EOL'
    }

    # Update service EOL counts
    for service in services:
        service_id = service['identifier']
        try:
            # Ensure 'relations' and 'framework' keys exist
            if 'relations' not in service or 'framework' not in service['relations']:
                print(f"Skipping Service {service_id}: Missing 'framework' relation")
                continue

            # Count EOL frameworks related to the service
            used_frameworks = service['relations']['framework']


            # Update the service with the EOL count
            update_service_eol_count(service_id, eol_no, PORT_BASE_URL, HEADERS)
            print(f"Updated Service {service_id} with EOL count: {eol_no}")
        except KeyError as key_err:
            print(f"Data structure error for Service {service_id}: {key_err}")
            continue
        except Exception as ex:
            print(f"Unexpected error for Service {service_id}: {ex}")
            continue

    print("Successfully updated all services with EOL package counts")


if __name__ == "__main__":
    main()
