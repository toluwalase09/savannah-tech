import requests
import json
from typing import Dict, List
from dotenv import load_dotenv
import os




def fetch_service_entities(base_url, access_token):
    url = f"{base_url}/v1/blueprints/service/entities"

    response = requests.get( url, headers=access_token)

    # print(response.text)
    response.raise_for_status()
    return response.json()['entities']

def fetch_frameworks_entities(base_url, access_token):
    url = f"{base_url}/v1/blueprints/framework/entities"

    response = requests.get( url, headers=access_token)

    print(response.text)
    response.raise_for_status()
    return response.json()['entities']

def count_eol(base_url, blueprint_id, access_token):
    url = f"{base_url}/v1/blueprints/{blueprint_id}/entities-count"
  
    # Perform the GET request
    response = requests.get(url, headers=access_token)

    # Raise an exception for any HTTP error
    response.raise_for_status()

    # Parse the JSON response directly
    json_response = response.json()

    # Access the 'count' value
    count_value = json_response["count"]
    print(count_value)
    return count_value


def update_service_eol_count(service_id, eol_count, base_url, access_token):
    url = f"{base_url}/v1/blueprints/service/entities/{service_id}"
    payload = {
        "properties": {
            "Number of EOL packages": eol_count
        }
    }
    response = requests.patch(url, headers=access_token, json=payload)
    response.raise_for_status()
    print(response)
    return response






# Main function
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


    try:
        # Get all services and frameworks
        services = fetch_service_entities(PORT_BASE_URL, jwt_token)
        frameworks = fetch_frameworks_entities(PORT_BASE_URL, jwt_token)

        # Create a lookup dictionary for frameworks
        framework_state_map = {
            framework['identifier']: framework['properties']['state']
            for framework in frameworks
        }

        # Process each service
        for service in services:
            # Get the frameworks related to this service
            service_frameworks = service['relations']['used_framework']
            
            # Count EOL frameworks
            eol_count = sum(
                1 for framework_id in service_frameworks
                if framework_state_map.get(framework_id) == 'EOL'
            )

            # Update the service with the EOL count
            print(f"Updating service {service['identifier']} with EOL count: {eol_count}")
            client.update_service_eol_count(service['identifier'], eol_count)

        print("Successfully updated all services with EOL package counts")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while communicating with Port API: {str(e)}")
    except KeyError as e:
        print(f"Error accessing data structure: {str(e)}")
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")

   

if __name__ == "__main__":
    main()

