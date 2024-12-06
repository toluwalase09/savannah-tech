from typing import Dict, List
from dotenv import load_dotenv
import os
import requests

load_dotenv()

PORT_BASE_URL = "https://api.getport.io"
PORT_JWT_TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJvcmdJZCI6Im9yZ19RS1BVMHJxaW5iVWppeXk2IiwiaXNzIjoiaHR0cHM6Ly9hcGkuZ2V0cG9ydC5pbyIsImlzTWFjaGluZSI6ZmFsc2UsInBlcnNvbmFsVG9rZW4iOnRydWUsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTA1MjQ2MzM5Njk0ODY5MzYzOTIzIiwicG9ydF91c2VyX2lkIjoiZ29vZ2xlLW9hdXRoMnwxMDUyNDYzMzk2OTQ4NjkzNjM5MjMiLCJqdGkiOiI0Yjc3MGYzOC1iYTgyLTRkMmItOTZhNy1kOGM5NzM1OTE0ODYiLCJpYXQiOjE3MzIyOTU5NDMsImV4cCI6MTczMjMwNjc0M30.enQQQZlF9AokA7TNubGTSVcBCb9mP8sM8twPdO8WJi8"


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


def update_service_eol_count(blueprint_id: str, entity_id: str, data: dict) -> None:
    """
    Updates the EOL count for a specific service entity in a given blueprint.
    """
    url = f"{PORT_BASE_URL}/v1/blueprints/{blueprint_id}/entities/{entity_id}"
    HEADERS = {
        'Authorization': PORT_JWT_TOKEN,
        'Content-Type': 'application/json'
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    print(response)
    response.raise_for_status()
    print(f"Updated {entity_id} with data of {data}")
    return response


def main() -> None:
    eol_frameworks = []
    active_frameworks = []

    blueprints = fetch_blueprints("framework")
    for entity in blueprints["entities"]:
        entity_id = entity["identifier"]
        print(entity_id)
        entity_state = entity["properties"]["state"]

        if entity_state == "EOL":
            eol_frameworks.append(entity_id)
            print(eol_frameworks)
        elif entity_state == "Active":
            active_frameworks.append(entity_id)
            print(active_frameworks)

    service_blueprints = fetch_blueprints("service")
    for entity in service_blueprints["entities"]:
        entity_id = entity["identifier"]

        used_frameworks = entity.get("relations", {}).get("used_frameworks", [])
        eol_count = len([fw for fw in used_frameworks if fw in eol_frameworks])
        print(eol_count)
        payload = {
            "properties": {
                "number_of_eol_packages": eol_count
            }
        }
        # update_service_eol_count("service", entity_id, payload)

if __name__ == "__main__":
    main()

                