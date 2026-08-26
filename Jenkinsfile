pipeline {
    agent any

    stages {
        stage('Publish Flows') {
            steps {
                withCredentials([
                    string(credentialsId: 'boomi-flow-api-key', variable: 'FLOW_API_KEY')
                ]) {
                    script {
                        def config = readJSON file: 'config/config.json'
                        def tenantId = config.tenantId as String
                        def flowBaseUrl = config.flowBaseUrl as String
                        def flowIds = params.FLOW_IDS ? params.FLOW_IDS.split('\n').collect { it.trim() }.findAll { it } : config.flowIds

                        if (!flowIds || flowIds.isEmpty()) {
                            echo "⚠️ No Flow IDs provided in build parameters or config/config.flow.publish.json. Skipping flow publish stage."
                            return
                        }

                        def commonHeaders = [
                            [name: 'manywhotenant', value: tenantId],
                            [name: 'x-boomi-flow-api-key', value: FLOW_API_KEY, maskValue: true]
                        ]

                        flowIds.each { flowId ->
                            echo "=== Processing Flow ID: ${flowId} ==="

                            // Step 1: Look up the latest snapshot version for this flow
                            def snapResponse = httpRequest(
                                httpMode: 'GET',
                                url: "${flowBaseUrl}/api/draw/1/flow/snap/${flowId}",
                                customHeaders: commonHeaders,
                                validResponseCodes: '100:599',
                                consoleLogResponseBody: true
                            )

                            if (snapResponse.status >= 300) {
                                error("Failed to list snapshots for Flow ID: ${flowId}. Status: ${snapResponse.status}")
                            }

                            def snapshots = readJSON(text: snapResponse.content)

                            if (!(snapshots instanceof List) || snapshots.isEmpty()) {
                                error("No snapshots found for Flow ID: ${flowId}")
                            }

                            // Sort explicitly by dateCreated
                            def latestSnapshot = snapshots.max { it.dateCreated }
                            def versionId = latestSnapshot.id.versionId

                            if (!versionId) {
                                error("Could not determine version ID for Flow ID: ${flowId}")
                            }

                            echo "Latest version for Flow ID ${flowId}: ${versionId} (created ${latestSnapshot.dateCreated})"

                            // Step 2: Activate that version and make it the default
                            def activateResponse = httpRequest(
                                httpMode: 'POST',
                                url: "${flowBaseUrl}/api/draw/1/flow/activation/${flowId}/${versionId}/true/true",
                                customHeaders: commonHeaders,
                                validResponseCodes: '100:599',
                                consoleLogResponseBody: true
                            )

                            echo "Activation status: ${activateResponse.status}"
                            echo "Activation body: ${activateResponse.content}"

                            if (activateResponse.status >= 300) {
                                error("Publish failed for Flow ID: ${flowId}")
                            } else {
                                echo "✅ Flow ID ${flowId} published successfully (version ${versionId})"
                                echo "${flowBaseUrl}/${tenantId}/play/theme/default/?flow-id=${flowId}"
                            }
                        }
                    }
                }
            }
        }
    }
}
