pipeline {
    agent any

    parameters {
        string(
            name: 'TEST_USERS',
            defaultValue: '10',
            description: 'Number of virtual users for the performance test'
        )

        string(
            name: 'RAMP_UP',
            defaultValue: '30',
            description: 'Ramp-up time in seconds'
        )

        string(
            name: 'DURATION',
            defaultValue: '60',
            description: 'Test duration in seconds'
        )
    }

    stages {

        // ============================================================
        // 1. Environment Check
        // ============================================================

        stage('Environment Check') {
            steps {
                echo 'Checking performance testing environment...'

                bat '''
                    echo ===== JAVA =====
                    java -version

                    echo ===== GIT =====
                    git --version

                    echo ===== PYTHON =====
                    "C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" --version

                    echo ===== JMETER =====
                    where jmeter

                    echo ===== DOCKER =====
                    docker --version

                    echo ===== KUBERNETES =====
                    kubectl version --client
                    kubectl config current-context
                '''
            }
        }


        // ============================================================
        // 2. Start Kubernetes Port Forward
        // ============================================================

        stage('Start Kubernetes Port Forward') {
            steps {
                echo 'Starting Kubernetes port-forward...'

                bat '''
                    echo ===== CHECK PORT 3003 =====

                    netstat -ano | findstr :3003 > nul

                    if %ERRORLEVEL% EQU 0 (
                        echo ERROR: Port 3003 is already in use.
                        echo Please stop the existing process using port 3003.
                        exit /b 1
                    )

                    echo ===== START PORT FORWARD =====

                    powershell -NoProfile -Command "$p=Start-Process kubectl -ArgumentList 'port-forward','service/ai-perf-order-service','3003:3002' -PassThru -WindowStyle Hidden; $p.Id | Set-Content 'k8s-port-forward.pid'"

                    echo Port-forward process started.

                    echo ===== WAIT FOR PORT 3003 =====

                    powershell -NoProfile -Command "$ok=$false; for($i=0;$i -lt 30;$i++){ try { $r=Invoke-WebRequest -Uri 'http://localhost:3003/health' -UseBasicParsing -TimeoutSec 2; if($r.StatusCode -eq 200){$ok=$true; break} } catch {}; Start-Sleep -Seconds 1 }; if(-not $ok){ Write-Host 'Port-forward health check failed'; exit 1 }"

                    echo ===== PORT FORWARD READY =====

                    type k8s-port-forward.pid
                '''
            }
        }


        // ============================================================
        // 3. Validate Kubernetes Application
        // ============================================================

        stage('Validate Kubernetes Application') {
            steps {
                echo 'Checking Kubernetes Order Service...'

                bat '''
                    echo ===== PODS =====
                    kubectl get pods -l app=ai-perf-order-service

                    echo ===== SERVICE =====
                    kubectl get service ai-perf-order-service

                    echo ===== ENDPOINTS =====
                    kubectl get endpoints ai-perf-order-service

                    echo ===== HEALTH CHECK =====
                    curl -s http://localhost:3003/health

                    echo.

                    echo ===== PRODUCTS CHECK =====
                    curl -s http://localhost:3003/products

                    echo.
                '''
            }
        }


        // ============================================================
        // 4. Kubernetes Metrics Check
        // ============================================================

        stage('Check Kubernetes Metrics') {
            steps {
                echo 'Checking Kubernetes Metrics Server...'

                bat '''
                    echo ===== NODE METRICS =====
                    kubectl top nodes

                    echo ===== POD METRICS =====
                    kubectl top pods
                '''
            }
        }


        // ============================================================
        // 5. Run JMeter Test
        // ============================================================

        stage('Run JMeter Test') {
            steps {
                echo 'Running JMeter performance test against Kubernetes application...'

                bat '''
                    if exist scripts\\results.jtl del /q scripts\\results.jtl

                    jmeter -n ^
                      -JTEST_USERS=%TEST_USERS% ^
                      -JRAMP_UP=%RAMP_UP% ^
                      -JDURATION=%DURATION% ^
                      -t scripts/ai_perf_test.jmx ^
                      -l scripts/results.jtl

                    echo ===== JMeter Result =====
                    dir scripts\\results.jtl
                '''
            }
        }


        // ============================================================
        // 6. Analyze Performance
        // ============================================================

        stage('Analyze Performance') {
            steps {
                echo 'Analyzing JMeter results with Python...'

                bat '''
                    cd python-engine

                    "C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" analyzer.py
                '''
            }
        }


        // ============================================================
        // 7. Collect MCP Evidence
        // ============================================================

        stage('Collect MCP Evidence') {
            steps {
                echo 'Collecting performance and Kubernetes evidence through MCP...'

                bat '''
                    "C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" mcp-server\\mcp_client.py

                    echo ===== MCP Evidence =====
                    type ai-engine\\mcp_rca_evidence.json
                '''
            }
        }


        // ============================================================
        // 8. Generate MCP-based AI RCA Prompt
        // ============================================================

        stage('Generate AI RCA Prompt') {
            steps {
                echo 'Generating AI RCA prompt from MCP evidence...'

                bat '''
                    "C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" ai-engine\\llm_client.py

                    echo ===== AI RCA PROMPT =====
                    type ai-engine\\ai_rca_prompt_from_mcp.txt
                '''
            }
        }


        // ============================================================
        // 9. Generate Deterministic RCA Report
        // ============================================================

        stage('Generate RCA Report') {
            steps {
                echo 'Generating Performance RCA report...'

                bat '''
                    cd python-engine

                    "C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" rca_engine.py

                    "C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" generate_report.py
                '''
            }
        }


        // ============================================================
        // 10. Generate Mock AI RCA
        // ============================================================

        stage('Generate AI RCA') {
            steps {
                echo 'Generating AI-based performance RCA...'

                bat '''
                    "C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" ai-engine\\mock_ai_rca.py

                    echo ===== AI RCA REPORT =====
                    type ai-engine\\ai_rca_report.md
                '''
            }
        }


        // ============================================================
        // 11. Collect Reports
        // ============================================================

        stage('Collect Reports') {
            steps {
                echo 'Collecting performance reports...'

                bat '''
                    if not exist "%WORKSPACE%\\results" mkdir "%WORKSPACE%\\results"

                    copy /Y scripts\\results.jtl "%WORKSPACE%\\results\\results.jtl"

                    copy /Y python-engine\\metrics.json "%WORKSPACE%\\results\\metrics.json"

                    copy /Y ai-engine\\mcp_rca_evidence.json "%WORKSPACE%\\results\\mcp_rca_evidence.json"

                    copy /Y ai-engine\\ai_rca_prompt_from_mcp.txt "%WORKSPACE%\\results\\ai_rca_prompt_from_mcp.txt"

                    copy /Y ai-engine\\rca_prompt.txt "%WORKSPACE%\\results\\rca_prompt.txt"

                    copy /Y reports\\ai_rca_report.md "%WORKSPACE%\\results\\ai_rca_report.md"

                    echo ===== Jenkins Artifacts =====
                    dir "%WORKSPACE%\\results"
                '''
            }
        }
    }


    // ================================================================
    // Post Actions
    // ================================================================

    post {

        always {

            echo 'Stopping Kubernetes port-forward...'

            bat '''
                if exist k8s-port-forward.pid (
                    for /f %%P in (k8s-port-forward.pid) do (
                        taskkill /PID %%P /T /F > nul 2>&1
                    )

                    del /q k8s-port-forward.pid
                )

                echo Kubernetes port-forward cleanup completed.
            '''

            echo 'Performance pipeline completed.'

            archiveArtifacts artifacts: 'results/*',
                allowEmptyArchive: false
        }
    }
}