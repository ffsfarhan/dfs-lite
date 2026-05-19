pipeline {
    agent any

    stages {

        stage('Build Backend') {
            steps {
                dir('dfs-lite') {
                    sh 'docker build -t dfs-backend .'
                }
            }
        }

        stage('Build Frontend') {
            steps {
                dir('dfs-frontend') {
                    sh 'docker build -t dfs-frontend .'
                }
            }
        }

        stage('Start Containers') {
            steps {
                sh 'docker-compose up -d'
            }
        }
    }
}
