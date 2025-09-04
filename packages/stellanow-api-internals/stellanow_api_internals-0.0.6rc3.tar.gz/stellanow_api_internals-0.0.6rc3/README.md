# StellaNow API Internals

StellaNow API Internals is a Python library used to communicate with Workflow-Manager and Notification Config services. It enables performing GET, POST, PATCH, and DELETE operations through a simple and consistent interface. This library is designed to help developers interact with StellaNow services via APIs.

## Installation

To install the StellaNow API Internals library, you can use pip:

    pip install stellanow-api-internals

## Usage

Once installed, you can use this library to communicate with StellaNow Workflow-Manager and Notification Config APIs. Below are examples of how to use the library.

### Example Usage

```python
from stellanow_api_internals.clients.workflow_manager import WorkflowManagerClient

client = WorkflowManagerClient(
    base_url="https://api.stellanow.com",
    username="your_username",
    password="your_password",
    organization_id="your_org_id",
)
```

### Example: Fetch all projects
```projects = client.get_projects()```

### Example: Create a new project
```
new_project = client.create_project({
    "name": "New Project",
    "description": "Description of the new project"
    })
```

## Authentication
The library uses the Keycloak authentication system. The WorkflowManagerClient and NotificationConfigClient classes handle authentication automatically. Once the client is initialized with the correct credentials (username, password, organization ID), it will generate and refresh tokens as needed.

## Workflow Manager API
The Workflow Manager API allows you to manage projects, events, entities, models, workflows, and DAGs (Directed Acyclic Graphs) related to the StellaNow workflow system.

Example: Creating a New Workflow
```python
workflow_data = {
    "name": "New Workflow",
    "description": "This is a test workflow",
}
new_workflow = client.create_workflow(workflow_data)
```

## Notification Config API
The Notification Config API allows you to manage services, channels, and destinations related to notifications within the StellaNow system.

Example: Fetching Notification Services
```python
from stellanow_api_internals.clients.notification_config import NotificationConfigClient

client = NotificationConfigClient(
    base_url="https://api.stellanow.com",
    username="your_username",
    password="your_password",
    organization_id="your_org_id"
)

services = client.get_services()
```

## Key Features
### Workflow Management: 
Perform operations like creating workflows, managing DAGs, and handling entities in StellaNow's workflow system.
### Notification Configurations: 
Manage notification services, channels, and destinations.
### Keycloak Authentication: 
Automatically handles authentication and token refresh via Keycloak.

## Contact and Licensing
For further assistance and support, please contact us at ***help@stella.systems***

The StellaNow Internal API is now open-source software, licensed under the terms of the MIT License. This allows for authorized copying, modification, and redistribution of the CLI tool, subject to the terms outlined in the license.

Please note that while the StellaNow CLI is open-source, the StellaNow platform and its associated code remain proprietary software. Unauthorized copying, modification, redistribution, and use of the StellaNow platform is prohibited without a proper license agreement. For inquiries about the licensing of the StellaNow platform, please contact us via the above email.