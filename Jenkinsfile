pipeline {
    agent any

    stages {
        stage('Validate Inputs') {
            steps {
                script {
                    def config = readJSON file: 'config/config.json'
                    
                    env.BOOMI_ACCOUNT_ID = config.boomiAccountId ?: 'mizuhobankltd-ECNYC6'
                    env.ENVIRONMENT_NAME = config.environmentName ?: 'MIZUHO_DEV_MCS'

                    // Build list of package items
                    def packageList = []

                    // Option A: If triggered manually with Jenkins parameters COMPONENT_NAMES & PACKAGE_VERSION
                    if (params.COMPONENT_NAMES?.trim() && params.PACKAGE_VERSION?.trim()) {
                        def names = params.COMPONENT_NAMES.trim().split('\n').collect { it.trim() }.findAll { it }
                        names.each { cName ->
                            packageList << [
                                componentName: cName,
                                packageVersion: params.PACKAGE_VERSION.trim(),
                                packageNote: null
                            ]
                        }
                    }
                    // Option B: Read packages list from config/config.json
                    else if (config.packages instanceof List && !config.packages.isEmpty()) {
                        config.packages.each { item ->
                            if (item.packageVersion) {
                                packageList << [
                                    componentName: item.componentName ? item.componentName.toString().trim() : '',
                                    packageVersion: item.packageVersion.toString().trim(),
                                    packageNote: item.packageNote ? item.packageNote.toString().trim() : null
                                ]
                            }
                        }
                    }
                    // Option C: Fallback to old single packageVersion / componentNames in config/config.json
                    else if (config.packageVersion) {
                        def cNames = (config.componentNames instanceof List) ? config.componentNames.collect { it.toString().trim() }.findAll { it } : []
                        if (cNames.isEmpty()) {
                            packageList << [
                                componentName: '',
                                packageVersion: config.packageVersion.toString().trim(),
                                packageNote: config.packageNote ? config.packageNote.toString().trim() : null
                            ]
                        } else {
                            cNames.each { cName ->
                                packageList << [
                                    componentName: cName,
                                    packageVersion: config.packageVersion.toString().trim(),
                                    packageNote: config.packageNote ? config.packageNote.toString().trim() : null
                                ]
                            }
                        }
                    }

                    if (packageList.isEmpty()) {
                        echo "⚠️ Missing package definitions (packages or packageVersion). Skipping integration deployment pipeline run."
                        env.SKIP_DEPLOYMENT = 'true'
                        return
                    }

                    env.SKIP_DEPLOYMENT = 'false'

                    echo "Authentication: Using Boomi Integration API Key from Jenkins Credentials"

                    echo "============================================"
                    echo "DEPLOYMENT INPUTS (${packageList.size()} package(s) to deploy)"
                    echo "============================================"
                    packageList.eachWithIndex { item, idx ->
                        def label = item.componentName ?: item.packageVersion
                        echo " [${idx + 1}] Component: '${item.componentName}' | Version: '${item.packageVersion}' | Note: '${item.packageNote ?: ''}'"
                    }
                    echo "Target Environment : ${env.ENVIRONMENT_NAME}"
                    echo "============================================"

                    writeJSON file: 'tmp_packages.json', json: packageList
                    env.PACKAGE_ITEMS_JSON = readFile('tmp_packages.json')
                }
            }
        }

        stage('Get Environment ID') {
            when {
                environment name: 'SKIP_DEPLOYMENT', value: 'false'
            }
            steps {
                withCredentials([
                    string(credentialsId: 'boomi-integration-api-key', variable: 'BOOMI_AUTH_SECRET')
                ]) {
                    script {
                        // Assuming the Secret text contains the full "username:password" or "BOOMI_TOKEN.email:token" string
                        def secretStr = BOOMI_AUTH_SECRET.trim()
                        if (!secretStr.contains(':')) {
                            error("The boomi-integration-api-key secret must be in the format 'BOOMI_TOKEN.email:token' or 'username:password'.")
                        }
                        String encoded = java.util.Base64.getEncoder().encodeToString(secretStr.getBytes("UTF-8"))
                        String authHeader = "Basic ${encoded}"

                        def response = httpRequest(
                            url: "https://api.boomi.com/api/rest/v1/${env.BOOMI_ACCOUNT_ID}/Environment/query",
                            httpMode: 'POST',
                            requestBody: '<QueryConfig xmlns="http://api.platform.boomi.com/"/>',
                            customHeaders: [[
                                name: 'Authorization',
                                value: authHeader
                            ],[
                                name: 'Content-Type',
                                value: 'application/xml'
                            ],[
                                name: 'Accept',
                                value: 'application/json'
                            ]]
                        )

                        def json = readJSON text: response.content
                        def environment = json.result.find { it.name == env.ENVIRONMENT_NAME }

                        if (!environment) {
                            error "Environment '${env.ENVIRONMENT_NAME}' not found in Boomi!"
                        }

                        env.ENVIRONMENT_ID = environment.id.toString()
                        echo "Environment '${env.ENVIRONMENT_NAME}' ID: ${env.ENVIRONMENT_ID}"
                    }
                }
            }
        }

        stage('Deploy Components') {
            when {
                environment name: 'SKIP_DEPLOYMENT', value: 'false'
            }
            steps {
                withCredentials([
                    string(credentialsId: 'boomi-integration-api-key', variable: 'BOOMI_AUTH_SECRET')
                ]) {
                    script {
                        // Assuming the Secret text contains the full "username:password" or "BOOMI_TOKEN.email:token" string
                        def secretStr = BOOMI_AUTH_SECRET.trim()
                        if (!secretStr.contains(':')) {
                            error("The boomi-integration-api-key secret must be in the format 'BOOMI_TOKEN.email:token' or 'username:password'.")
                        }
                        String encoded = java.util.Base64.getEncoder().encodeToString(secretStr.getBytes("UTF-8"))
                        String authHeader = "Basic ${encoded}"

                        String environmentId = env.ENVIRONMENT_ID.toString()
                        echo "Using Environment ID: ${environmentId}"

                        def packageItems = readJSON text: env.PACKAGE_ITEMS_JSON
                        def deploymentResults = []

                        packageItems.each { item ->
                            def cName = (item.componentName != null && !(item.componentName instanceof net.sf.json.JSONNull)) ? item.componentName.toString().trim() : ''
                            def pVersion = (item.packageVersion != null && !(item.packageVersion instanceof net.sf.json.JSONNull)) ? item.packageVersion.toString().trim() : ''
                            def pNote = (item.packageNote != null && !(item.packageNote instanceof net.sf.json.JSONNull)) ? item.packageNote.toString().trim() : null

                            // Determine deployment notes message
                            String notesMessage
                            if (pNote) {
                                notesMessage = pNote
                            } else if (cName) {
                                notesMessage = "Deployed via Jenkins - ${cName}"
                            } else {
                                notesMessage = "Deployed via Jenkins"
                            }

                            def displayLabel = cName ?: pVersion

                            echo "============================================"
                            echo "Processing Package: ${displayLabel} (${pVersion})"
                            echo "============================================"

                            try {
                                echo "Step 1: Searching package version ${pVersion}..."

                                String searchBody = '{"QueryFilter":{"expression":{"operator":"EQUALS","property":"packageVersion","argument":["' + pVersion + '"]}}}'

                                def packageResponse = httpRequest(
                                    url: "https://api.boomi.com/api/rest/v1/${env.BOOMI_ACCOUNT_ID}/PackagedComponent/query",
                                    httpMode: 'POST',
                                    requestBody: searchBody,
                                    validResponseCodes: '100:599',
                                    customHeaders: [[
                                        name: 'Authorization',
                                        value: authHeader
                                    ],[
                                        name: 'Content-Type',
                                        value: 'application/json'
                                    ],[
                                        name: 'Accept',
                                        value: 'application/json'
                                    ]]
                                )

                                echo "Package Search Response Code: ${packageResponse.status}"

                                if (packageResponse.status != 200) {
                                    echo "Package search failed!"
                                    deploymentResults << [name: displayLabel, status: 'FAILED', reason: "Package search failed: ${packageResponse.content}"]
                                    return
                                }

                                def packageJson = readJSON text: packageResponse.content

                                if (!packageJson.result || packageJson.result.size() == 0) {
                                    echo "Package version '${pVersion}' NOT FOUND!"
                                    deploymentResults << [name: displayLabel, status: 'FAILED', reason: "Package version not found"]
                                    return
                                }

                                echo "Step 2: Matching process type package..."

                                def matchedPackage = packageJson.result.find { pkg ->
                                    pkg.componentType == 'process' && pkg.deleted == false
                                }

                                if (!matchedPackage) {
                                    echo "No process type package found for version '${pVersion}'!"
                                    deploymentResults << [name: displayLabel, status: 'FAILED', reason: "No process package found"]
                                    return
                                }

                                String packageId = matchedPackage.packageId.toString()
                                String componentId = matchedPackage.componentId.toString()
                                echo "Package found — packageId: ${packageId}"
                                echo "Component ID: ${componentId}"

                                echo "Step 3: Deploying to ${env.ENVIRONMENT_NAME} with notes: '${notesMessage}'..."
                                String deployBody = '{"@type":"DeployedPackage","packageId":"' + packageId + '","environmentId":"' + environmentId + '","notes":"' + notesMessage + '"}'

                                def deployResponse = httpRequest(
                                    url: "https://api.boomi.com/api/rest/v1/${env.BOOMI_ACCOUNT_ID}/DeployedPackage",
                                    httpMode: 'POST',
                                    requestBody: deployBody,
                                    validResponseCodes: '100:599',
                                    customHeaders: [[
                                        name: 'Authorization',
                                        value: authHeader
                                    ],[
                                        name: 'Content-Type',
                                        value: 'application/json'
                                    ],[
                                        name: 'Accept',
                                        value: 'application/json'
                                    ]]
                                )

                                echo "Deploy Response Code: ${deployResponse.status}"
                                echo "Deploy Response: ${deployResponse.content}"

                                if (deployResponse.status == 200 || deployResponse.status == 201) {
                                    def deployJson = readJSON text: deployResponse.content
                                    echo "Successfully deployed '${displayLabel}'!"
                                    echo "Deployment ID: ${deployJson.deploymentId}"
                                    deploymentResults << [name: displayLabel, status: 'SUCCESS', deploymentId: deployJson.deploymentId]
                                } else {
                                    echo "Deployment failed for '${displayLabel}'"
                                    deploymentResults << [name: displayLabel, status: 'FAILED', reason: "Deploy failed: ${deployResponse.content}"]
                                }

                            } catch (Exception e) {
                                echo "Failed to deploy '${displayLabel}': ${e.message}"
                                deploymentResults << [name: displayLabel, status: 'FAILED', reason: e.message]
                            }
                        }

                        echo "============================================"
                        echo "DEPLOYMENT SUMMARY"
                        echo "============================================"
                        deploymentResults.each { result ->
                            if (result.status == 'SUCCESS') {
                                echo "${result.name} — DEPLOYED SUCCESSFULLY (ID: ${result.deploymentId})"
                            } else {
                                echo "${result.name} — FAILED: ${result.reason}"
                            }
                        }
                        echo "============================================"

                        def failures = deploymentResults.findAll { it.status == 'FAILED' }
                        if (failures.size() > 0) {
                            error "${failures.size()} package(s) failed to deploy!"
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            script {
                if (env.SKIP_DEPLOYMENT == 'true') {
                    echo "Integration Deployment skipped due to empty parameters."
                } else {
                    echo "All components deployed successfully to ${env.ENVIRONMENT_NAME}!"
                }
            }
        }
        failure {
            echo "Deployment failed! Check the logs above for details."
        }
    }
}
