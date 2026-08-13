# Boomi Automation Pipeline

This repository contains a Jenkins pipeline for automatically installing or registering Boomi Flow connectors. 

## Structure

- `Jenkinsfile`: The main Jenkins pipeline script, structured as a Declarative Pipeline.
- `config/config.json`: The central configuration file defining parameters and the list of connectors.

## Configuration

To add, update, or remove connectors, you simply need to edit `config/config.json`. The pipeline parses this file during the build process to dynamically retrieve all necessary parameters.

### `config.json` properties:
- `tenantId`: Your Boomi Flow Tenant ID.
- `flowBaseUrl`: The base URL of the Boomi Flow environment.
- `flowUsername`: HTTP Authentication Username.
- `flowPassword`: HTTP Authentication Password.
- `connectors`: An array of connector objects, each containing:
  - `id`: The connector ID.
  - `uri`: The endpoint URI for the connector.
  - `developerName`: The descriptive name of the connector service.
  - `developerSummary`: (Optional) Summary of the service.

Example `config.json`:
```json
{
  "tenantId": "85c2ac30-08cd-48d1-baf8-d66e05b9cb29",
  "flowBaseUrl": "https://us.flow-prod.boomi.com",
  "flowUsername": "username",
  "flowPassword": "password",
  "connectors": [
    {
      "id": "bbb6a4c7-c0a8-4323-a4ec-292001ed27fe",
      "uri": "https://mizuho-dev.boomi.cloud/fs/RegisterBeneficiary",
      "developerName": "Register Beneficiary Service",
      "developerSummary": null
    }
  ]
}
```

## Jenkins Requirements

1. **Pipeline Utility Steps Plugin**: This pipeline utilizes the `readJSON` step to parse the JSON configuration. You must have this plugin installed on your Jenkins controller.
2. **HTTP Request Plugin**: Used by `httpRequest` step for sending POST requests.
3. **Credentials**: Make sure a 'Secret text' credential with the ID `boomi-flow-api-key` is configured in Jenkins. This is used by the pipeline to authenticate with the Boomi Flow API securely.

## Execution

If you have configured Jenkins to build on pushes, the pipeline will execute automatically whenever changes are merged. It will read `config/config.json` and attempt to install or update the defined connectors.
