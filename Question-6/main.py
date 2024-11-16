import requests
import json
from typing import Dict, List
from dotenv import load_dotenv
import os


def fetch_blueprints(base_url, headers):
    """
    Fetches all blueprints from the Port API.
    """
    url = f"{base_url}/v1/blueprints"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['blueprints'] 


def fetch_service_entities(base_url, headers, blueprint_id):
    """
    Fetches all service entities for a given blueprint.
    """
    url = f"{base_url}/v1/blueprints/{blueprint_id}/entities"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['entities']
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 422:
            print(f"422 Error for Blueprint ID {blueprint_id}: {err.response.text}")
        else:
            print(f"HTTPError for Blueprint ID {blueprint_id}: {err.response.status_code} - {err.response.text}")
        raise  # Re-raise the exception to halt further execution
    except requests.exceptions.RequestException as e:
        print(f"RequestException for Blueprint ID {blueprint_id}: {str(e)}")
        raise


def fetch_frameworks_entities(base_url, headers, blueprint_id):
    """
    Fetches all framework entities for a given blueprint.
    """
    url = f"{base_url}/v1/blueprints/{blueprint_id}/entities"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['entities']

def count_eol(base_url, blueprint_id, headers):
    """Count the number of entities marked as EOL."""
    url = f"{base_url}/v1/blueprints/{blueprint_id}/entities-count"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("count", 0)

def add_new_framework_to_service(entity_id, base_url, access_token, new_framework_id, blueprint_id):
    url = f"{base_url}/v1/blueprints/{blueprint_id}/entities/{entity_id}"
    payload = {
        "relations": {
            "framework": new_framework_id
        }
    }
    response = requests.patch(url, headers=access_token, json=payload)
    response.raise_for_status()  # Will raise an error if request fails
    print(f"Service {entity_id} updated with new framework: {new_framework_id}")
    return response

def update_service_eol_count(base_url, headers, blueprint_id, entity_id, eol_count):
    """
    Updates the EOL count for a specific service entity in a given blueprint.
    """
    url = f"{base_url}/v1/blueprints/{blueprint_id}/entities/{entity_id}"
    payload = {
        "properties": {
            "Number of EOL packages": eol_count
        }
    }
    response = requests.patch(url, headers=headers, json=payload)
    response.raise_for_status()
    print(f"Updated {entity_id} with EOL count: {eol_count}")
    return response


def main():
    load_dotenv()

    jwt_token = os.getenv("jwt_token")
    PORT_BASE_URL = os.getenv("base_url")
    HEADERS = {
        'Authorization': jwt_token,
        'Content-Type': 'application/json'
    }

    try:
        # Fetch all blueprints
        blueprints = fetch_blueprints(PORT_BASE_URL, HEADERS)
        print("Available Blueprints:")
        for blueprint in blueprints:
            print(f"ID: {blueprint['identifier']}")
            blueprint_id = blueprint['identifier']
            new_framework_id = "tes"  # Replace with the actual framework ID eol_count = count_eol(PORT_BASE_URL, HEADERS, blueprint_id)
        for blueprint in blueprints:
            blueprint_id = blueprint['identifier']
            print(f"\nProcessing Blueprint ID: {blueprint_id}")
            

            try:
                # Get all services for the blueprint
                services = fetch_service_entities(PORT_BASE_URL, HEADERS, blueprint_id)
                frameworks = fetch_frameworks_entities(PORT_BASE_URL, HEADERS, blueprint_id)
                eol_framework_ids = {
                    framework['identifier'] for framework in frameworks if framework['properties'].get('state') == 'EOL'
                }
                # Process each service in the blueprint
                for service in services:
                    service_id = service['identifier']
                    print(f"Processing Service {service_id} ")
                    
                    # Check if 'framework' relation is missing and add a new framework
                    if 'relations' not in service or 'framework' not in service['relations']:
                        print(f"Service {service_id} missing 'framework' relation, adding new framework")
                        used_frameworks = add_new_framework_to_service(service, PORT_BASE_URL, HEADERS, new_framework_id, blueprint_id)
                    else:
                        used_frameworks = service['relations']['framework']
                    eol_count = count_eol(PORT_BASE_URL, blueprint_id, HEADERS)
                    # eol_count = sum(1 for fw in used_frameworks if fw in eol_framework_ids)
                    print(f"Updating Service {service} with EOL count: {eol_count}")
                    update_service_eol_count(PORT_BASE_URL, HEADERS, blueprint_id, service_id, eol_count)
  

            except requests.exceptions.RequestException as e:
                print(f"Request error for Blueprint ID {blueprint_id}: {str(e)}")
            except KeyError as e:
                print(f"Data structure error in Blueprint ID {blueprint_id}: {str(e)}")
            except Exception as e:
                print(f"Unexpected error for Blueprint ID {blueprint_id}: {str(e)}")


    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
    except KeyError as e:
        print(f"Data structure error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
