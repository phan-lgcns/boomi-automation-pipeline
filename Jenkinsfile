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
                        // Read configuration from the config folder
                        def config = readJSON file: 'config/config.json'
                        def connectors = config.connectors 
                        
                        echo "Found ${connectors.size()} connector(s) in configuration." 
                        
                        connectors.each { connector -> 
                            echo "Installing connector: ${connector.id}" 
                            
                            def payload = [ 
                                uri: connector.uri, 
                                developerName: connector.developerName, 
                                developerSummary: connector.developerSummary, 
                                httpAuthenticationUsername: config.flowUsername, 
                                httpAuthenticationPassword: config.flowPassword, 
                                HttpAuthenticationClientCertificate: '', 
                                HttpAuthenticationClientCertificatePassword: '', 
                                configurationValues: [], 
                                id: connector.id, 
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
                                        value: config.tenantId 
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