pipeline { 

    agent any 

    parameters { 
        string( 
            name: 'TENANT_ID', 
            defaultValue: '85c2ac30-08cd-48d1-baf8-d66e05b9cb29', 
            description: 'Boomi Flow Tenant ID' 
        ) 

        text( 
            name: 'CONNECTOR_IDS', 
            defaultValue: '''bbb6a4c7-c0a8-4323-a4ec-292001ed27fe''', 
            description: 'One connector ID per line' 
        ) 

        string( 
            name: 'FLOW_USERNAME', 
            defaultValue: 'mizuhobankltd-ECNYC6.V4O7OK', 
            description: 'HTTP Authentication Username' 
        ) 

        string( 
            name: 'FLOW_PASSWORD', 
            defaultValue: 'da028fc8-01a7-468e-b5ed-3d44438b50a8', 
            description: 'HTTP Authentication Password' 
        ) 
    } 

    environment { 
        FLOW_BASE_URL = 'https://us.flow-prod.boomi.com' 
    }

    stages { 
        stage('Install Connector') { 
            steps {
                withCredentials([ 
                    string( 
                        credentialsId: 'boomi-flow-api-key', 
                        variable: 'FLOW_API_KEY' 
                    ) 
                ]) {
                    script { 
                        def connectorIds = params.CONNECTOR_IDS 
                            .split('\n') 
                            .collect { it.trim() } 
                            .findAll { it } 
                        echo "Found ${connectorIds.size()} connector ID(s)" 
                        connectorIds.each { connectorId -> 
                            echo "Installing connector: ${connectorId}" 
                            def payload = [ 
                                uri: 'https://mizuho-dev.boomi.cloud/fs/RegisterBeneficiary', 
                                developerName: 'Register Beneficiary Service', 
                                developerSummary: null, 
                                httpAuthenticationUsername: params.FLOW_USERNAME, 
                                httpAuthenticationPassword: params.FLOW_PASSWORD, 
                                HttpAuthenticationClientCertificate: '', 
                                HttpAuthenticationClientCertificatePassword: '', 
                                configurationValues: [], 
                                id: connectorId, 
                                identityProviderId: null 
                            ] 
                            def response = httpRequest( 
                                httpMode: 'POST', 
                                ignoreSslErrors: true, 
                                url: "${env.FLOW_BASE_URL}/api/draw/1/element/service/install", 
                                contentType: 'APPLICATION_JSON', 
                                requestBody: groovy.json.JsonOutput.toJson(payload), 
                                customHeaders: [ 
                                    [ 
                                        name: 'manywhotenant', 
                                        value: params.TENANT_ID 
                                    ], 
                                    [ 

                                        name: 'x-boomi-flow-api-key', 

                                        value: FLOW_API_KEY, 

                                        maskValue: true 

                                    ] 

                                ], 

                                validResponseCodes: '100:599', 

                                consoleLogResponseBody: true 

                            ) 
                            echo "HTTP Status: ${response.status}" 
                            echo response.content 
                            if (response.status >= 300) { 

                                error("Connector installation failed for ${connectorId}. Status=${response.status}") 

                            } 
                            echo "✅ Successfully installed connector ${connectorId}" 

                        } 
                        echo "✅ All connector installations completed successfully" 
                    } 
                } 
            } 
        } 
    } 
}