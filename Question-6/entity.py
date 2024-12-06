import requests
import json
from typing import Dict, List
from dotenv import load_dotenv
import os

load_dotenv()
PORT_BASE_URL = "https://api.getport.io"
PORT_JWT_TOKEN = os.getenv("token")

def fetch_blueprints(blueprint_id: str) -> dict:
    """
    Fetches all blueprints from the Port API.
    """
    url = f"{PORT_BASE_URL}/v1/blueprints/{blueprint_id}/entities"
    HEADERS = {
        'Authorization': PORT_JWT_TOKEN 
    }
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def update_service_eol_count(blueprint_id: str, entity_id: str, eol_count: int) -> None:
    """
    Updates the EOL count for a specific service entity in a given blueprint.
    """
    url = f"{PORT_BASE_URL}/v1/blueprints/{blueprint_id}/entities/{entity_id}"
    HEADERS = {
        'Authorization': PORT_JWT_TOKEN ,
        'Content-Type': 'application/json'
    }
    payload = {
        "properties": {
            "number_of_eol_packages": eol_count
        }
    }
    response = requests.patch(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    print(f"Updated {entity_id} with data of {payload}")
    return response


def main() -> None:
    eol_frameworks = []
    active_frameworks = []
    entity_state_list = {}

    framework_blueprints = fetch_blueprints("framework")
    for entity in framework_blueprints["entities"]:
        entity_id = entity["identifier"]
        entity_state = entity["properties"]["state"]
        if isinstance(entity_state, list) and entity_state:
            entity_state = entity_state[0]
        entity_state_list[entity_id] = entity_state
    # print(entity_state_list)
    for entity_id, state in entity_state_list.items():
        if state == "Active":
            active_frameworks.append(entity_id)
        elif state == "EOL":
            eol_frameworks.append(entity_id)
    # print(f"active_frameworks: {active_frameworks}, eol frameworks: {eol_frameworks}")
    eol_count = len(eol_frameworks)
    service_blueprints = fetch_blueprints("service")
    for entity in service_blueprints["entities"]:
        entity_id = entity["identifier"]
        update_service_eol_count("service", entity_id, eol_count)


if __name__ == "__main__":
    main()
