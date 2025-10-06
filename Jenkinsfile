pipeline {
    agent any

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
                        withEnv([
                            'RDF_INSTALL_ROOT=/opt/Robust-Design-Flow',
                            'PYTHONUNBUFFERED=1',
                            'XDG_RUNTIME_DIR=/tmp/runtime-root'
                        ]) {
                            githubNotify context: 'rdf-regression',
                                         status: 'PENDING',
                                         description: 'Regression started',
                                         repo: 'ieee-ceda-datc/Robust-Design-Flow',
                                         account: 'ieee-ceda-datc',
                                         sha: env.GIT_COMMIT,
                                         credentialsId: 'github-rdf-user-pass'
                            // sh 'git config --global --add safe.directory "$(pwd)"'
                            // sh 'git submodule update --init --recursive'
                            sh 'python3 tests/run_regression.py'
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            githubNotify context: 'rdf-regression',
                         status: 'SUCCESS',
                         description: 'Regression passed',
                         repo: 'ieee-ceda-datc/Robust-Design-Flow',
                         account: 'ieee-ceda-datc',
                         sha: env.GIT_COMMIT,
                         credentialsId: 'github-rdf-user-pass'
        }
        failure {
            githubNotify context: 'rdf-regression',
                         status: 'FAILURE',
                         description: 'Regression failed',
                         repo: 'ieee-ceda-datc/Robust-Design-Flow',
                         account: 'ieee-ceda-datc',
                         sha: env.GIT_COMMIT,
                         credentialsId: 'github-rdf-user-pass'
        }
        always {
            junit allowEmptyResults: true, testResults: 'rdf.test/logs/*.xml'
            archiveArtifacts artifacts: 'rdf.test/**', allowEmptyArchive: true
        }
    }
}
