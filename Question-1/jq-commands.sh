# Current Replica Count
jq '.spec.replicas' k8s-deploy.json

# Deployment Strategy
jq '.spec.strategy.type' k8s-deploy.json

# Concatenated "service" and "environment" Labels:
jq -r '.metadata.labels | "\(.service)-\(.environment)"' k8s-deploy.json

# An array of Subtask Issue IDs:
jq '[.fields.subtasks[].key]' issue-response.json