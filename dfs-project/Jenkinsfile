pipeline {
    agent any

    stages {

        stage('Build Backend') {
            steps {
                dir('dfs-project/dfs-lite') {
                    sh 'docker build -t dfs-backend .'
                }
            }
        }

        stage('Build Frontend') {
            steps {
                dir('dfs-project/dfs-frontend') {
                    sh 'docker build -t dfs-frontend .'
                }
            }
        }

        stage('Start Containers') {
            steps {
                dir('dfs-project') {
                    sh 'docker compose up -d'
                }
            }
        }
    }
}
