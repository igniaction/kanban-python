pipeline {
  agent {
    dockerfile {
      filename 'ci/jenkins-agent.Dockerfile'
      // permite docker build dentro do agente usando o daemon do host/jenkins
      args '-v /var/run/docker.sock:/var/run/docker.sock'
      reuseNode true
    }
  }

  options {
    timestamps()
    disableConcurrentBuilds()
    // evita checkout duplicado quando você NÃO tem stage Checkout manual
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

    stage("Lint") {
      steps { sh "make lint" }
    }

    stage("Test") {
      steps { sh "make test" }
    }

    stage("Build Docker Image") {
      steps {
        sh "docker build -t ${APP_NAME}:sha-${GIT_SHA} ."
        sh "docker image ls ${APP_NAME}:sha-${GIT_SHA}"
      }
    }
  }

  post {
    always {
      echo "Build finalizado: ${APP_NAME}:sha-${env.GIT_SHA}"
    }
  }
}
