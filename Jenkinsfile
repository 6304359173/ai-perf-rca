pipeline {
    agent any

    /*
     * Jenkins runs as Local System on this machine.
     * Therefore explicitly point kubectl to the Docker Desktop
     * Kubernetes configuration used by the Windows user.
     */
    environment {
        KUBECONFIG = 'C:\\Users\\LENOVO\\.kube\\config'
        PYTHON_EXE = 'C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'
    }

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
                    echo ========================================
                    echo JAVA
                    echo ========================================
                    java -version

                    echo ========================================
                    echo GIT
                    echo ========================================
                    git --version

                    echo ========================================
                    echo PYTHON
                    echo ========================================
                    "%PYTHON_EXE%" --version

                    echo ========================================
                    echo JMETER
                    echo ========================================
                    where jmeter
                    jmeter --version

                    echo ========================================
                    echo DOCKER
                    echo ========================================
                    docker --version

                    echo ========================================
                    echo KUBERNETES
                    echo ========================================
                    echo KUBECONFIG=%KUBECONFIG%
                    kubectl version --client
                    kubectl config current-context

                    echo ========================================
                    echo KUBERNETES CLUSTER
                    echo ========================================
                    kubectl get nodes
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
                    echo ========================================
                    echo CHECK PORT 3003
                    echo ========================================

                    netstat -ano | findstr :3003 > nul

                    if %ERRORLEVEL% EQU 0 (
                        echo ERROR: Port 3003 is already in use.
                        echo Please stop the existing process using port 3003.
                        exit /b 1
                    )

                    echo ========================================
                    echo START PORT FORWARD
                    echo ========================================

                    powershell -NoProfile -Command "$p=Start-Process kubectl -ArgumentList 'port-forward','service/ai-perf-order-service','3003:3002' -PassThru -WindowStyle Hidden; $p.Id | Set-Content 'k8s-port-forward.pid'"

                    echo Port-forward process started.

                    echo ========================================
                    echo WAIT FOR PORT 3003
                    echo ========================================

                    powershell -NoProfile -Command "$ok=$false; for($i=0;$i -lt 30;$i++){ try { $r=Invoke-WebRequest -Uri 'http://localhost:3003/health' -UseBasicParsing -TimeoutSec 2; if($r.StatusCode -eq 200){$ok=$true; break} } catch {}; Start-Sleep -Seconds 1 }; if(-not $ok){ Write-Host 'Port-forward health check failed'; exit 1 }"

                    echo ========================================
                    echo PORT FORWARD READY
                    echo ========================================

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
                    echo ========================================
                    echo PODS
                    echo ========================================
                    kubectl get pods -l app=ai-perf-order-service

                    echo ========================================
                    echo SERVICE
                    echo ========================================
                    kubectl get service ai-perf-order-service

                    echo ========================================
                    echo ENDPOINTS
                    echo ========================================
                    kubectl get endpoints ai-perf-order-service

                    echo ========================================
                    echo HEALTH CHECK
                    echo ========================================
                    curl -s http://localhost:3003/health
                    echo.

                    echo ========================================
                    echo PRODUCTS CHECK
                    echo ========================================
                    curl -s http://localhost:3003/products
                    echo.
                '''
            }
        }


        // ============================================================
        // 4. Kubernetes Metrics
        // ============================================================

        stage('Check Kubernetes Metrics') {
            steps {
                echo 'Checking Kubernetes Metrics Server...'

                bat '''
                    echo ========================================
                    echo NODE METRICS
                    echo ========================================
                    kubectl top nodes

                    echo ========================================
                    echo POD METRICS
                    echo ========================================
                    kubectl top pods
                '''
            }
        }


        // ============================================================
        // 5. Run JMeter Performance Test
        // ============================================================

        stage('Run JMeter Test') {
            steps {
                echo 'Running JMeter performance test against Kubernetes application...'

                bat '''
                    echo ========================================
                    echo CLEAN PREVIOUS RESULT
                    echo ========================================

                    if exist scripts\\results.jtl del /q scripts\\results.jtl

                    echo ========================================
                    echo JMeter TEST
                    echo ========================================

                    jmeter -n ^
                      -JTEST_USERS=%TEST_USERS% ^
                      -JRAMP_UP=%RAMP_UP% ^
                      -JDURATION=%DURATION% ^
                      -t scripts\\ai_perf_test.jmx ^
                      -l scripts\\results.jtl

                    if %ERRORLEVEL% NEQ 0 (
                        echo ERROR: JMeter execution failed.
                        exit /b 1
                    )

                    echo ========================================
                    echo JMeter RESULT
                    echo ========================================

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
                    "%PYTHON_EXE%" python-engine\\analyzer.py

                    if %ERRORLEVEL% NEQ 0 (
                        echo ERROR: Performance analyzer failed.
                        exit /b 1
                    )

                    echo ========================================
                    echo PERFORMANCE METRICS
                    echo ========================================

                    type python-engine\\metrics.json
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
                    "%PYTHON_EXE%" mcp-server\\mcp_client.py

                    if %ERRORLEVEL% NEQ 0 (
                        echo ERROR: MCP evidence collection failed.
                        exit /b 1
                    )

                    echo ========================================
                    echo MCP EVIDENCE
                    echo ========================================

                    type ai-engine\\mcp_rca_evidence.json
                '''
            }
        }


        // ============================================================
        // 8. Generate MCP-based AI RCA Prompt
        // ============================================================

        stage('Generate AI RCA Prompt') {
            steps {
                echo 'Generating MCP-based AI RCA prompt...'

                bat '''
                    "%PYTHON_EXE%" ai-engine\\llm_client.py

                    if %ERRORLEVEL% NEQ 0 (
                        echo ERROR: AI RCA prompt generation failed.
                        exit /b 1
                    )

                    echo ========================================
                    echo AI RCA PROMPT
                    echo ========================================

                    if exist ai-engine\\ai_rca_prompt_from_mcp.txt (
                        type ai-engine\\ai_rca_prompt_from_mcp.txt
                    ) else (
                        echo AI RCA prompt file was not generated.
                    )
                '''
            }
        }


        // ============================================================
        // 9. Generate Deterministic RCA Report
        // ============================================================

        stage('Generate RCA Report') {
            steps {
                echo 'Generating deterministic Performance RCA report...'

                bat '''
                    "%PYTHON_EXE%" python-engine\\rca_engine.py

                    if %ERRORLEVEL% NEQ 0 (
                        echo ERROR: RCA engine failed.
                        exit /b 1
                    )

                    "%PYTHON_EXE%" python-engine\\generate_report.py

                    if %ERRORLEVEL% NEQ 0 (
                        echo ERROR: Report generation failed.
                        exit /b 1
                    )

                    echo ========================================
                    echo RCA REPORT
                    echo ========================================

                    if exist reports\\ai_rca_report.md (
                        type reports\\ai_rca_report.md
                    )
                '''
            }
        }


        // ============================================================
        // 10. Generate AI RCA
        // ============================================================

        stage('Generate AI RCA') {
            steps {
                echo 'Generating AI-based performance RCA...'

                bat '''
                    "%PYTHON_EXE%" ai-engine\\mock_ai_rca.py

                    if %ERRORLEVEL% NEQ 0 (
                        echo ERROR: AI RCA generation failed.
                        exit /b 1
                    )

                    echo ========================================
                    echo AI RCA REPORT
                    echo ========================================

                    if exist ai-engine\\ai_rca_report.md (
                        type ai-engine\\ai_rca_report.md
                    )
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
                    echo ========================================
                    echo CREATE RESULTS DIRECTORY
                    echo ========================================

                    if not exist "%WORKSPACE%\\results" mkdir "%WORKSPACE%\\results"

                    echo ========================================
                    echo COPY JMeter RESULTS
                    echo ========================================

                    copy /Y scripts\\results.jtl "%WORKSPACE%\\results\\results.jtl"

                    echo ========================================
                    echo COPY PERFORMANCE METRICS
                    echo ========================================

                    copy /Y python-engine\\metrics.json "%WORKSPACE%\\results\\metrics.json"

                    echo ========================================
                    echo COPY MCP EVIDENCE
                    echo ========================================

                    copy /Y ai-engine\\mcp_rca_evidence.json "%WORKSPACE%\\results\\mcp_rca_evidence.json"

                    echo ========================================
                    echo COPY AI RCA PROMPT
                    echo ========================================

                    if exist ai-engine\\ai_rca_prompt_from_mcp.txt (
                        copy /Y ai-engine\\ai_rca_prompt_from_mcp.txt "%WORKSPACE%\\results\\ai_rca_prompt_from_mcp.txt"
                    )

                    echo ========================================
                    echo COPY RCA PROMPT
                    echo ========================================

                    if exist ai-engine\\rca_prompt.txt (
                        copy /Y ai-engine\\rca_prompt.txt "%WORKSPACE%\\results\\rca_prompt.txt"
                    )

                    echo ========================================
                    echo COPY RCA REPORT
                    echo ========================================

                    if exist reports\\ai_rca_report.md (
                        copy /Y reports\\ai_rca_report.md "%WORKSPACE%\\results\\ai_rca_report.md"
                    )

                    echo ========================================
                    echo JENKINS ARTIFACTS
                    echo ========================================

                    dir "%WORKSPACE%\\results"
                '''
            }
        }
    }


    // ================================================================
    // POST ACTIONS
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

            archiveArtifacts(
                artifacts: 'results/*',
                allowEmptyArchive: true
            )
        }
    }
}