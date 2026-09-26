pipeline {
    agent any

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

                    echo ========================================
                    echo KUBERNETES CONTEXT
                    echo ========================================
                    kubectl config current-context

                    echo ========================================
                    echo KUBERNETES NODES
                    echo ========================================
                    kubectl get nodes
                '''
            }
        }


        stage('Start Kubernetes Port Forward') {
            steps {
                echo 'Starting Kubernetes port-forward...'

                bat '''
                    echo ========================================
                    echo KUBERNETES CONTEXT
                    echo ========================================

                    set KUBECONFIG=C:\\Users\\LENOVO\\.kube\\config

                    kubectl config current-context

                    echo ========================================
                    echo CHECK APPLICATION PODS
                    echo ========================================

                    kubectl get pods -l app=ai-perf-order-service

                    echo ========================================
                    echo CLEAN OLD PORT 3003
                    echo ========================================

                    powershell -NoProfile -Command "$c=Get-NetTCPConnection -LocalPort 3003 -State Listen -ErrorAction SilentlyContinue; if($c){$c | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object {Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue}; Start-Sleep -Seconds 2}"

                    echo ========================================
                    echo CLEAN OLD PID FILE
                    echo ========================================

                    if exist k8s-port-forward.pid del /q k8s-port-forward.pid

                    echo ========================================
                    echo CLEAN OLD LOG FILES
                    echo ========================================

                    if exist k8s-port-forward.out.log del /q k8s-port-forward.out.log

                    if exist k8s-port-forward.err.log del /q k8s-port-forward.err.log

                    echo ========================================
                    echo START KUBECTL PORT FORWARD
                    echo ========================================

                    powershell -NoProfile -Command "$env:KUBECONFIG='C:\\Users\\LENOVO\\.kube\\config'; $p=Start-Process kubectl -ArgumentList '--kubeconfig','C:\\Users\\LENOVO\\.kube\\config','port-forward','service/ai-perf-order-service','3003:3002' -RedirectStandardOutput 'k8s-port-forward.out.log' -RedirectStandardError 'k8s-port-forward.err.log' -PassThru -WindowStyle Hidden; if($null -eq $p){Write-Host 'ERROR: kubectl process was not started'; exit 1}; $p.Id | Set-Content 'k8s-port-forward.pid'; Write-Host ('kubectl PID: ' + $p.Id)"

                    if not exist k8s-port-forward.pid (
                        echo ERROR: Port-forward PID file was not created.
                        exit /b 1
                    )

                    echo ========================================
                    echo PORT FORWARD PROCESS
                    echo ========================================

                    type k8s-port-forward.pid

                    echo ========================================
                    echo WAIT FOR APPLICATION
                    echo ========================================

                    powershell -NoProfile -Command "$ok=$false; for($i=0;$i -lt 30;$i++){ try { $r=curl.exe -s -o NUL -w '%{http_code}' http://127.0.0.1:3003/health; if($r -eq '200'){$ok=$true; break} } catch {}; Start-Sleep -Seconds 1 }; if(-not $ok){ Write-Host '========================================'; Write-Host 'PORT-FORWARD FAILED'; Write-Host '========================================'; Write-Host 'STDOUT:'; if(Test-Path 'k8s-port-forward.out.log'){Get-Content 'k8s-port-forward.out.log'}; Write-Host 'STDERR:'; if(Test-Path 'k8s-port-forward.err.log'){Get-Content 'k8s-port-forward.err.log'}; exit 1 }"

                    echo ========================================
                    echo PORT FORWARD READY
                    echo ========================================

                    curl -s http://127.0.0.1:3003/health

                    echo.
                '''
            }
        }


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

                    curl -s http://127.0.0.1:3003/health

                    echo.

                    echo ========================================
                    echo PRODUCTS CHECK
                    echo ========================================

                    curl -s http://127.0.0.1:3003/products

                    echo.
                '''
            }
        }


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


        stage('Run JMeter Test') {
            steps {
                echo 'Running JMeter performance test against Kubernetes application...'

                bat '''
                    echo ========================================
                    echo CLEAN PREVIOUS RESULT
                    echo ========================================

                    if exist scripts\\results.jtl del /q scripts\\results.jtl

                    echo ========================================
                    echo JMETER TEST
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
                    echo JMETER RESULT
                    echo ========================================

                    dir scripts\\results.jtl
                '''
            }
        }


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


        stage('Collect MCP Evidence') {
            steps {
                echo 'Collecting performance and Kubernetes evidence through MCP...'

                bat '''
				
				echo ===== MCP ENVIRONMENT =====
				echo Python:
				"%PYTHON_EXE%" --version

				echo Kubectl:
				where kubectl

				echo Kubectl version:
				kubectl version --client

				echo Kubernetes context:
				kubectl config current-context

				echo Kubernetes nodes:
				kubectl top nodes

				echo Kubernetes pods:
				kubectl top pods

				echo ===== RUN MCP CLIENT =====
				"%PYTHON_EXE%" mcp-server\\mcp_client.py

				if not exist ai-engine\\mcp_rca_evidence.json (
					echo ERROR: MCP evidence file was not generated.
					exit /b 1
				)

				echo ===== MCP EVIDENCE =====
				type ai-engine\\mcp_rca_evidence.json
				'''
                    "%PYTHON_EXE%" mcp-server\mcp_client.py

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
                        echo AI RCA prompt was not generated.
                    )
                '''
            }
        }


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


        stage('Collect Reports') {
            steps {
                echo 'Collecting performance reports...'

                bat '''
                    echo ========================================
                    echo CREATE RESULTS DIRECTORY
                    echo ========================================

                    if not exist "%WORKSPACE%\\results" mkdir "%WORKSPACE%\\results"

                    echo ========================================
                    echo COPY JMETER RESULTS
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
                    echo COPY PORT FORWARD STDOUT
                    echo ========================================

                    if exist k8s-port-forward.out.log (
                        copy /Y k8s-port-forward.out.log "%WORKSPACE%\\results\\k8s-port-forward.out.log"
                    )

                    echo ========================================
                    echo COPY PORT FORWARD STDERR
                    echo ========================================

                    if exist k8s-port-forward.err.log (
                        copy /Y k8s-port-forward.err.log "%WORKSPACE%\\results\\k8s-port-forward.err.log"
                    )

                    echo ========================================
                    echo JENKINS ARTIFACTS
                    echo ========================================

                    dir "%WORKSPACE%\\results"
                '''
            }
        }
    }


    post {

        always {

            echo 'Stopping Kubernetes port-forward...'

            bat '''
                echo ========================================
                echo STOP KUBERNETES PORT FORWARD
                echo ========================================

                if exist k8s-port-forward.pid (
                    for /f %%P in (k8s-port-forward.pid) do (
                        taskkill /PID %%P /T /F > nul 2>&1
                    )

                    del /q k8s-port-forward.pid
                )

                echo ========================================
                echo VERIFY PORT 3003
                echo ========================================

                powershell -NoProfile -Command "$c=Get-NetTCPConnection -LocalPort 3003 -State Listen -ErrorAction SilentlyContinue; if($c){$c | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object {Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue}}"

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