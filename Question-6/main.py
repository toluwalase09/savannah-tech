import requests
import json
from typing import Dict, List
from dotenv import load_dotenv
import os


def get_token(auth_url: str, client_id: str, client_secret: str) -> str:
    """
    Requests an access token using client ID and client secret.
    
    Args:
        auth_url (str): The URL to request the token.
        client_id (str): The client ID.
        client_secret (str): The client secret.
    
    Returns:
        str: The access token.
    """
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    response = requests.post(auth_url, data=payload)
    response.raise_for_status()
    token_data = response.json()
    
    return token_data['access_token']

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
    client_id = os.getenv("CLIENT_ID")  
    client_secret = os.getenv("CLIENT_SECRET")
    PORT_BASE_URL = os.getenv("base_url")
    AUTH_URL = os.getenv("base_url")

    jwt_token = get_token(AUTH_URL, client_id, client_secret)
    HEADERS = {
        'Authorization': jwt_token,
        'Content-Type': 'application/json'
    }

    # try:
        # Fetch all blueprints
    blueprints = fetch_blueprints(PORT_BASE_URL, HEADERS)
        # print("Available Blueprints:")
        # for blueprint in blueprints:
        #     print(f"ID: {blueprint['identifier']}")
        #     blueprint_id = blueprint['identifier']
        #     new_framework_id = "tes"  # Replace with the actual framework ID eol_count = count_eol(PORT_BASE_URL, HEADERS, blueprint_id)
    for blueprint in blueprints:
        blueprint_id = blueprint['identifier']
        print(f"\nProcessing Blueprint ID: {blueprint_id}")
        

        try:
            # Fetch services and frameworks
            services = fetch_service_entities(PORT_BASE_URL, HEADERS, blueprint_id)
            frameworks = fetch_frameworks_entities(PORT_BASE_URL, HEADERS, blueprint_id)
            
            # Identify EOL frameworks
            eol_framework_ids = {
                framework['identifier'] 
                for framework in frameworks 
                if framework['properties'].get('state') == 'EOL'
            }
            
            # Process each service in the blueprint
            for service in services:
                service_id = service['identifier']
                print(f"Processing Service {service_id}")
                
                # Check if 'framework' relation is missing
                if 'relations' not in service or 'framework' not in service['relations']:
                    print(f"Service {service_id} missing 'framework' relation. Adding new framework.")
                    add_new_framework_to_service(service_id, PORT_BASE_URL, HEADERS, new_framework_id, blueprint_id)
                
                # Count and update EOL frameworks
                eol_count = sum(1 for fw in service.get('relations', {}).get('framework', []) if fw in eol_framework_ids)
                print(f"Updating Service {service_id} with EOL count: {eol_count}")
                update_service_eol_count(PORT_BASE_URL, HEADERS, blueprint_id, service_id, eol_count)
    

        except Exception as e:
            print(f"Error processing Blueprint ID {blueprint_id}: {str(e)}")


if __name__ == "__main__":
    main()
