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

        # Iterate through each blueprint and process its services and frameworks
        for blueprint in blueprints:
            blueprint_id = blueprint['identifier']
            print(f"\nProcessing Blueprint ID: {blueprint_id}")

            try:
                # Fetch services and frameworks for the current blueprint
                services = fetch_service_entities(PORT_BASE_URL, HEADERS, blueprint_id)
                frameworks = fetch_frameworks_entities(PORT_BASE_URL, HEADERS, blueprint_id)

                # Create a set of EOL framework IDs
                eol_framework_ids = {
                    framework['identifier'] for framework in frameworks if framework['properties'].get('state') == 'EOL'
                }

                # Update service EOL counts
                for service in services:
                    service_id = service['identifier']
                    if 'relations' not in service or 'framework' not in service['relations']:
                        print(f"Skipping Service {service_id}: Missing 'framework' relation")
                        continue

                    used_frameworks = service['relations']['framework']
                    eol_count = sum(1 for fw in used_frameworks if fw in eol_framework_ids)
                    update_service_eol_count(PORT_BASE_URL, HEADERS, blueprint_id, service_id, eol_count)

            except requests.exceptions.RequestException as e:
                print(f"Request error for Blueprint ID {blueprint_id}: {str(e)}")
            except KeyError as e:
                print(f"Data structure error in Blueprint ID {blueprint_id}: {str(e)}")
            except Exception as e:
                print(f"Unexpected error for Blueprint ID {blueprint_id}: {str(e)}")

        print("Successfully updated all services with EOL package counts.")

    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
    except KeyError as e:
        print(f"Data structure error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
