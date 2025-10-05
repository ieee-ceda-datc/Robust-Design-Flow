pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        PATH = "${env.PATH}:${env.HOME}/.local/bin"
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
                sh 'git submodule sync --recursive'
                sh 'git submodule update --init --recursive'
            }
        }

        stage('Build OpenROAD') {
            steps {
                sh 'cd tools/OpenROAD-flow-scripts && ./build_openroad.sh --local && source env.sh'
            }
        }

        stage('Prepare Python Environment') {
            steps {
                sh 'python3 -m pip install --user --break-system-packages --quiet unittest-xml-reporting'
            }
        }

        stage('Run Regression') {
            steps {
                sh 'rm -rf rdf.test || true'
                sh 'python3 tests/run_regression.py'
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'rdf.test/logs/*.xml'
            archiveArtifacts artifacts: 'rdf.test/**', allowEmptyArchive: true
            cleanWs()
        }
    }
}
