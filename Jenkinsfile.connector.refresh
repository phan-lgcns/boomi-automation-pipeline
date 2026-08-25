pipeline { 
    agent any 

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
                        // Read configuration from config/config.connector.json
                        def config = readJSON file: 'config/config.connector.json'
                        def connectors = config.connectors 
                        
                        echo "Found ${connectors.size()} connector(s) in configuration." 
                        
                        for (int i = 0; i < connectors.size(); i++) { 
                            def connector = connectors[i]
                            echo "Installing connector: ${connector.id}" 
                            
                            def payload = [ 
                                uri: connector.uri as String, 
                                developerName: connector.developerName as String, 
                                developerSummary: connector.developerSummary ? connector.developerSummary as String : null, 
                                httpAuthenticationUsername: config.flowUsername as String, 
                                httpAuthenticationPassword: config.flowPassword as String, 
                                HttpAuthenticationClientCertificate: '', 
                                HttpAuthenticationClientCertificatePassword: '', 
                                configurationValues: [], 
                                id: connector.id as String, 
                                identityProviderId: null 
                            ] 
                            
                            def response = httpRequest( 
                                httpMode: 'POST', 
                                ignoreSslErrors: true, 
                                url: "${config.flowBaseUrl}/api/draw/1/element/service/install", 
                                contentType: 'APPLICATION_JSON', 
                                requestBody: groovy.json.JsonOutput.toJson(payload), 
                                customHeaders: [ 
                                    [ 
                                        name: 'manywhotenant', 
                                        value: config.tenantId as String 
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
                                error("Connector installation failed for ${connector.id}. Status=${response.status}") 
                            } 
                            echo "✅ Successfully installed connector ${connector.id}" 
                        } 
                        echo "✅ All connector installations completed successfully" 
                    } 
                } 
            } 
        } 
    } 
}