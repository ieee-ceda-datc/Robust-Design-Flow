pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        XDG_RUNTIME_DIR = '/tmp/runtime-root'
    }

    stages {
        stage('Workspace Cleanup') {
            steps {
                cleanWs()
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run Regression (Docker)') {
            steps {
                script {
                    docker.image('rdf-openroad-ci').inside('--user root:root --rm') {
                        sh 'git config --global --add safe.directory "$(pwd)"'
                        sh 'git submodule update --init --recursive'
                        sh 'python3 tests/run_regression.py'
                    }
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'rdf.test/logs/*.xml'
            archiveArtifacts artifacts: 'rdf.test/**', allowEmptyArchive: true
        }
    }
}
