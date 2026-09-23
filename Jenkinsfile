pipeline {
    agent any

    stages {

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
                '''
            }
        }

        stage('Validate Application') {
            steps {
                echo 'Checking Order Service...'

                bat '''
                    curl -s http://localhost:3002/health
                '''
            }
        }

        stage('Run JMeter Test') {
            steps {
                echo 'Running JMeter performance test...'

                bat '''
                    if exist scripts\\results.jtl del /q scripts\\results.jtl

                    jmeter -n ^
                      -t scripts\\ai_perf_test.jmx ^
                      -l scripts\\results.jtl

                    echo ===== JMeter Result =====
                    dir scripts\\results.jtl
                '''
            }
        }

        stage('Analyze Performance') {
            steps {
                echo 'Analyzing JMeter results with Python...'

                bat '''
                    cd python-engine

                    "C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" analyzer.py
                '''
            }
        }
		stage('Collect MCP Evidence') {
			steps {
				echo 'Collecting performance evidence through MCP...'

				bat '''
					"C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" mcp-server\\mcp_client.py

					echo ===== MCP Evidence =====
					type ai-engine\\mcp_rca_evidence.json
				'''
				}
			}
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

        stage('Collect Reports') {
            steps {
                echo 'Collecting performance reports...'

                bat '''
                    if not exist "%WORKSPACE%\\results" mkdir "%WORKSPACE%\\results"

                    copy /Y scripts\\results.jtl "%WORKSPACE%\\results\\results.jtl"

                    copy /Y python-engine\\metrics.json "%WORKSPACE%\\results\\metrics.json"
					
					copy /Y ai-engine\\mcp_rca_evidence.json "%WORKSPACE%\\results\\mcp_rca_evidence.json"

                    copy /Y ai-engine\\rca_prompt.txt "%WORKSPACE%\\results\\rca_prompt.txt"

                    copy /Y reports\\ai_rca_report.md "%WORKSPACE%\\results\\ai_rca_report.md"

                    echo ===== Jenkins Artifacts =====
                    dir "%WORKSPACE%\\results"
                '''
            }
        }
    }

    post {
        always {
            echo 'Performance pipeline completed.'

            archiveArtifacts artifacts: 'results/*',
                allowEmptyArchive: false
        }
    }
}