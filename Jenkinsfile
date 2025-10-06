pipeline {
    agent {
        docker {
            image 'rdf-openroad-ci'
            args '--user root:root --rm'
        }
    }

    environment {
        PYTHONUNBUFFERED = '1'
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
                sh 'git submodule update --init --recursive'
            }
        }

        stage('Run Regression') {
            steps {
                sh 'python3 tests/run_regression.py'
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
