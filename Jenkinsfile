pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  environment {
    APP_NAME = "kanban-python"
  }

  stages {
    stage("Checkout") {
      steps {
        checkout scm
      }
    }

    stage("Init") {
      steps {
        script {
          env.GIT_SHA = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
          echo "Commit SHA: ${env.GIT_SHA}"
        }
      }
    }

    stage("Lint") {
      steps {
        sh "make lint"
      }
    }

    stage("Test") {
      steps {
        sh "make test"
      }
    }

    stage("Build Docker Image") {
      steps {
        sh """
          set -eux
          docker version
          docker build -t ${APP_NAME}:sha-${GIT_SHA} .
          docker image ls ${APP_NAME}:sha-${GIT_SHA}
        """
      }
    }
  }

  post {
    always {
      echo "Build finalizado: ${APP_NAME}:sha-${env.GIT_SHA}"
    }
  }
}
