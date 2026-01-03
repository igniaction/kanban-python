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
    stage("Init") {
      steps {
        script {
          env.GIT_SHA = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
          echo "Commit SHA: ${env.GIT_SHA}"
        }
      }
    }

    stage("Build CI Toolchain Image") {
      steps {
        sh """
          docker build -f ci/jenkins-agent.Dockerfile -t ${APP_NAME}-ci:sha-${GIT_SHA} .
          docker image ls ${APP_NAME}-ci:sha-${GIT_SHA}
        """
      }
    }

    stage("Lint") {
      steps {
        sh """
          docker run --rm \
            -v "\$PWD:/workspace" -w /workspace \
            ${APP_NAME}-ci:sha-${GIT_SHA} \
            make lint
        """
      }
    }

    stage("Test") {
      steps {
        sh """
          docker run --rm \
            -v "\$PWD:/workspace" -w /workspace \
            ${APP_NAME}-ci:sha-${GIT_SHA} \
            make test
        """
      }
    }

    stage("Build Docker Image") {
      steps {
        sh """
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
