pipeline {

    agent any

    environment {

        // ============================================================
        // Tools
        // ============================================================

        JMeterHome = 'C:\\apache-jmeter-5.6.3'

        PYTHON_EXE = 'C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'

        // ============================================================
        // Application
        // ============================================================

        APP_PORT = '3003'

        // ============================================================
        // JMeter configuration
        // ============================================================

        TEST_USERS = '10'
        RAMP_UP = '30'
        DURATION = '60'

        // ============================================================
        // Kubernetes
        // ============================================================

        K8S_CONTEXT = 'docker-desktop'

        K8S_NAMESPACE = 'default'

        K8S_SERVICE = 'ai-perf-order-service'

        K8S_SERVICE_PORT = '3002'

        K8S_LOCAL_PORT = '3003'

        // ============================================================
        // Files
        // ============================================================

        JMX_FILE = 'scripts\\ai_perf_test.jmx'

        JTL_FILE = 'scripts\\results.jtl'

        METRICS_FILE = 'python-engine\\metrics.json'

        MCP_EVIDENCE_FILE = 'ai-engine\\mcp_rca_evidence.json'

        RCA_PROMPT_FILE = 'ai-engine\\ai_rca_prompt_from_mcp.txt'

        RCA_REPORT_FILE = 'ai-engine\\ai_rca_report.md'
    }


    stages {


        // ============================================================
        // 1. Checkout
        // ============================================================

        stage('Checkout') {

            steps {

                echo '============================================'
                echo ' CHECKOUT SOURCE CODE'
                echo '============================================'

                checkout scm

                bat '''
                    echo Current directory:
                    cd

                    echo.
                    echo Git branch:
                    git branch --show-current

                    echo.
                    echo Git commit:
                    git rev-parse --short HEAD
                '''
            }
        }


        // ============================================================
        // 2. Validate Environment
        // ============================================================

        stage('Validate Environment') {

            steps {

                echo '============================================'
                echo ' VALIDATE ENVIRONMENT'
                echo '============================================'

                bat '''
                    echo ===== JAVA =====
                    java -version

                    echo.
                    echo ===== PYTHON =====
                    "%PYTHON_EXE%" --version

                    echo.
                    echo ===== NODE =====
                    node --version

                    echo.
                    echo ===== NPM =====
                    npm --version

                    echo.
                    echo ===== GIT =====
                    git --version

                    echo.
                    echo ===== DOCKER =====
                    docker --version

                    echo.
                    echo ===== KUBECTL =====
                    kubectl version --client

                    echo.
                    echo ===== JMETER =====
                    "%JMeterHome%\\bin\\jmeter.bat" --version
                '''
            }
        }


        // ============================================================
        // 3. Validate Project Files
        // ============================================================

        stage('Validate Project Files') {

            steps {

                echo '============================================'
                echo ' VALIDATE PROJECT FILES'
                echo '============================================'

                bat '''
                    echo ===== PROJECT STRUCTURE =====

                    if not exist "%JMX_FILE%" (
                        echo ERROR: JMeter test plan not found.
                        exit /b 1
                    )

                    if not exist "python-engine\\analyzer.py" (
                        echo ERROR: analyzer.py not found.
                        exit /b 1
                    )

                    if not exist "python-engine\\kubernetes_metrics.py" (
                        echo ERROR: kubernetes_metrics.py not found.
                        exit /b 1
                    )

                    if not exist "mcp-server\\performance_mcp.py" (
                        echo ERROR: performance_mcp.py not found.
                        exit /b 1
                    )

                    if not exist "mcp-server\\mcp_client.py" (
                        echo ERROR: mcp_client.py not found.
                        exit /b 1
                    )

                    if not exist "ai-engine\\llm_client.py" (
                        echo ERROR: llm_client.py not found.
                        exit /b 1
                    )

                    echo.
                    echo All required project files exist.
                '''
            }
        }


        // ============================================================
        // 4. Validate Kubernetes
        // ============================================================

        stage('Validate Kubernetes') {

            steps {

                echo '============================================'
                echo ' VALIDATE KUBERNETES'
                echo '============================================'

                bat '''
                    echo ===== KUBERNETES CONTEXT =====

                    kubectl config use-context "%K8S_CONTEXT%"

                    echo.
                    kubectl config current-context

                    echo.
                    echo ===== NODES =====

                    kubectl get nodes -o wide

                    echo.
                    echo ===== ORDER SERVICE PODS =====

                    kubectl get pods -l app=ai-perf-order-service -o wide

                    echo.
                    echo ===== SERVICE =====

                    kubectl get service "%K8S_SERVICE%"

                    echo.
                    echo ===== ENDPOINTS =====

                    kubectl get endpoints "%K8S_SERVICE%"
                '''
            }
        }


        // ============================================================
        // 5. Start Kubernetes Port Forward
        // ============================================================

        stage('Start Kubernetes Port Forward') {

            steps {

                echo '============================================'
                echo ' START KUBERNETES PORT FORWARD'
                echo '============================================'

                bat '''
                    echo ===== CHECK PORT =====

                    netstat -ano | findstr :%K8S_LOCAL_PORT%

                    echo.
                    echo ===== START PORT FORWARD =====

                    powershell -NoProfile -Command "$p = Start-Process kubectl -ArgumentList 'port-forward','service/%K8S_SERVICE%','%K8S_LOCAL_PORT%:%K8S_SERVICE_PORT%','--context=%K8S_CONTEXT%' -RedirectStandardOutput 'k8s-port-forward.out.log' -RedirectStandardError 'k8s-port-forward.err.log' -PassThru; Set-Content -Path 'k8s-port-forward.pid' -Value $p.Id; Write-Host ('Port-forward PID: ' + $p.Id)"

                    echo.
                    echo ===== WAIT FOR PORT FORWARD =====

                    powershell -NoProfile -Command "$ok=$false; for($i=1;$i -le 20;$i++){ try { $r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:%K8S_LOCAL_PORT%/health -TimeoutSec 2; if($r.StatusCode -eq 200){ Write-Host 'PORT FORWARD READY'; $ok=$true; break } } catch { Start-Sleep -Seconds 1 } }; if(-not $ok){ Write-Host 'PORT FORWARD FAILED'; if(Test-Path 'k8s-port-forward.out.log'){Get-Content 'k8s-port-forward.out.log'}; if(Test-Path 'k8s-port-forward.err.log'){Get-Content 'k8s-port-forward.err.log'}; exit 1 }"

                    echo.
                    echo ===== APPLICATION HEALTH =====

                    curl.exe -s http://127.0.0.1:%K8S_LOCAL_PORT%/health

                    echo.
                '''
            }
        }


        // ============================================================
        // 6. Validate Application
        // ============================================================

        stage('Validate Application') {

            steps {

                echo '============================================'
                echo ' VALIDATE APPLICATION'
                echo '============================================'

                bat '''
                    echo ===== HEALTH =====

                    curl.exe -s http://127.0.0.1:%APP_PORT%/health

                    echo.
                    echo.
                    echo ===== PRODUCTS =====

                    curl.exe -s http://127.0.0.1:%APP_PORT%/products

                    echo.
                    echo.
                    echo Application validation completed.
                '''
            }
        }


        // ============================================================
        // 7. Kubernetes Metrics
        // ============================================================

        stage('Collect Kubernetes Metrics') {

            steps {

                echo '============================================'
                echo ' KUBERNETES METRICS'
                echo '============================================'

                bat '''
                    echo ===== NODE METRICS =====

                    kubectl top nodes

                    echo.
                    echo ===== POD METRICS =====

                    kubectl top pods

                    echo.
                    echo ===== APPLICATION POD METRICS =====

                    kubectl top pods -l app=ai-perf-order-service
                '''
            }
        }


        // ============================================================
        // 8. Run JMeter
        // ============================================================

        stage('Run JMeter Performance Test') {

            steps {

                echo '============================================'
                echo ' RUN JMETER PERFORMANCE TEST'
                echo '============================================'

                bat '''
                    if exist "%JTL_FILE%" (
                        del /f /q "%JTL_FILE%"
                    )

                    echo ===== JMETER CONFIGURATION =====

                    echo Users    : %TEST_USERS%
                    echo Ramp-up  : %RAMP_UP% seconds
                    echo Duration : %DURATION% seconds
                    echo Target   : http://localhost:%APP_PORT%

                    echo.
                    echo ===== RUN JMETER =====

                    "%JMeterHome%\\bin\\jmeter.bat" ^
                        -n ^
                        -JTEST_USERS=%TEST_USERS% ^
                        -JRAMP_UP=%RAMP_UP% ^
                        -JDURATION=%DURATION% ^
                        -t "%JMX_FILE%" ^
                        -l "%JTL_FILE%"

                    if %ERRORLEVEL% NEQ 0 (
                        echo ERROR: JMeter execution failed.
                        exit /b 1
                    )

                    echo.
                    echo JMeter execution completed.

                    if not exist "%JTL_FILE%" (
                        echo ERROR: results.jtl was not generated.
                        exit /b 1
                    )

                    echo.
                    echo ===== RESULTS FILE =====

                    dir "%JTL_FILE%"
                '''
            }
        }


        // ============================================================
        // 9. Analyze Performance
        // ============================================================

        stage('Analyze Performance') {

            steps {

                echo '============================================'
                echo ' PYTHON PERFORMANCE ANALYSIS'
                echo '============================================'

                bat '''
                    echo ===== RUN ANALYZER =====

                    "%PYTHON_EXE%" python-engine\\analyzer.py

                    if %ERRORLEVEL% NEQ 0 (
                        echo ERROR: Performance analyzer failed.
                        exit /b 1
                    )

                    echo.
                    echo ===== METRICS FILE =====

                    if not exist "%METRICS_FILE%" (
                        echo ERROR: metrics.json was not generated.
                        exit /b 1
                    )

                    type "%METRICS_FILE%"
                '''
            }
        }


        // ============================================================
        // 10. Collect MCP Evidence
        // ============================================================

        stage('Collect MCP Evidence') {

            steps {

                echo '============================================'
                echo ' COLLECT MCP EVIDENCE'
                echo '============================================'

                bat '''
                    echo ===== MCP ENVIRONMENT =====

                    echo Python:
                    "%PYTHON_EXE%" --version

                    echo.
                    echo Kubectl:
                    where kubectl

                    echo.
                    echo Kubectl version:
                    kubectl version --client

                    echo.
                    echo Kubernetes context:
                    kubectl config current-context

                    echo.
                    echo Kubernetes nodes:
                    kubectl top nodes

                    echo.
                    echo Kubernetes pods:
                    kubectl top pods

                    echo.
                    echo ===== RUN MCP CLIENT =====

                    "%PYTHON_EXE%" mcp-server\\mcp_client.py

                    if %ERRORLEVEL% NEQ 0 (
                        echo ERROR: MCP evidence collection failed.
                        exit /b 1
                    )

                    echo.
                    echo ===== VERIFY MCP EVIDENCE =====

                    if not exist "%MCP_EVIDENCE_FILE%" (
                        echo ERROR: MCP evidence file was not generated.
                        exit /b 1
                    )

                    echo.
                    echo ===== MCP EVIDENCE =====

                    type "%MCP_EVIDENCE_FILE%"
                '''
            }
        }


        // ============================================================
        // 11. Generate AI RCA Prompt
        // ============================================================

        stage('Generate AI RCA') {

            steps {

                echo '============================================'
                echo ' GENERATE AI RCA'
                echo '============================================'

                bat '''
                    echo ===== RUN LLM CLIENT =====

                    "%PYTHON_EXE%" ai-engine\\llm_client.py

                    if %ERRORLEVEL% NEQ 0 (
                        echo WARNING: LLM client returned an error.
                    )

                    echo.
                    echo ===== RCA PROMPT =====

                    if exist "%RCA_PROMPT_FILE%" (
                        type "%RCA_PROMPT_FILE%"
                    ) else (
                        echo RCA prompt file was not generated.
                    )
                '''
            }
        }


        // ============================================================
        // 12. Generate Deterministic RCA Report
        // ============================================================

        stage('Generate RCA Report') {

            steps {

                echo '============================================'
                echo ' GENERATE RCA REPORT'
                echo '============================================'

                bat '''
                    echo ===== GENERATE REPORT =====

                    if exist "ai-engine\\mock_ai_rca.py" (

                        "%PYTHON_EXE%" ai-engine\\mock_ai_rca.py

                        if %ERRORLEVEL% NEQ 0 (
                            echo WARNING: RCA report generation returned an error.
                        )

                    ) else (

                        echo mock_ai_rca.py not found.
                        echo Skipping deterministic RCA report.

                    )

                    echo.
                    echo ===== RCA REPORT =====

                    if exist "%RCA_REPORT_FILE%" (
                        type "%RCA_REPORT_FILE%"
                    ) else (
                        echo RCA report was not generated.
                    )
                '''
            }
        }


        // ============================================================
        // 13. Prepare Artifacts
        // ============================================================

        stage('Prepare Artifacts') {

            steps {

                echo '============================================'
                echo ' PREPARE JENKINS ARTIFACTS'
                echo '============================================'

                bat '''
                    if not exist results (
                        mkdir results
                    )

                    echo ===== COPY PERFORMANCE RESULTS =====

                    if exist "%JTL_FILE%" (
                        copy /Y "%JTL_FILE%" "results\\results.jtl"
                    )

                    if exist "%METRICS_FILE%" (
                        copy /Y "%METRICS_FILE%" "results\\metrics.json"
                    )

                    if exist "%MCP_EVIDENCE_FILE%" (
                        copy /Y "%MCP_EVIDENCE_FILE%" "results\\mcp_rca_evidence.json"
                    )

                    if exist "%RCA_PROMPT_FILE%" (
                        copy /Y "%RCA_PROMPT_FILE%" "results\\ai_rca_prompt_from_mcp.txt"
                    )

                    if exist "%RCA_REPORT_FILE%" (
                        copy /Y "%RCA_REPORT_FILE%" "results\\ai_rca_report.md"
                    )

                    echo.
                    echo ===== ARTIFACTS =====

                    dir results
                '''
            }
        }
    }


    // ================================================================
    // POST ACTIONS
    // ================================================================

    post {

        always {

            echo '============================================'
            echo ' POST BUILD CLEANUP'
            echo '============================================'

            bat '''
                echo ===== PORT FORWARD CLEANUP =====

                if exist k8s-port-forward.pid (

                    set /p K8S_PID=<k8s-port-forward.pid

                    echo Port-forward PID: %K8S_PID%

                    taskkill /PID %K8S_PID% /T /F >nul 2>&1

                    del /f /q k8s-port-forward.pid >nul 2>&1
                )

                echo.
                echo ===== CHECK PORT =====

                netstat -ano | findstr :%K8S_LOCAL_PORT%

                echo.
                echo ===== PORT FORWARD LOGS =====

                if exist k8s-port-forward.out.log (
                    type k8s-port-forward.out.log
                )

                if exist k8s-port-forward.err.log (
                    type k8s-port-forward.err.log
                )
            '''
        }


        success {

            echo '============================================'
            echo ' AI PERFORMANCE PIPELINE SUCCESS'
            echo '============================================'
        }


        failure {

            echo '============================================'
            echo ' AI PERFORMANCE PIPELINE FAILED'
            echo '============================================'
        }
    }
}