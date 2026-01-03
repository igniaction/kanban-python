pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  environment {
    APP_NAME = "kanban-python"
    GIT_SHA = "latest" 
  }

  stages {
    stage("Init") {
      steps {
        script {
          // Captura o SHA curto do commit atual
          env.GIT_SHA = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
          echo "Commit SHA: ${env.GIT_SHA}"
        }
      }
    }

    stage("Build CI Toolchain Image") {
      steps {
        sh "docker build -f ci/jenkins-agent.Dockerfile -t ${env.APP_NAME}-ci:sha-${env.GIT_SHA} ."
      }
    }

    stage("Lint & Test") {
      steps {
        // As aspas simples em volta do bash -c '...' resolvem o erro "No rule to make target"
        sh """
          docker run --rm \
            -v "\$PWD:/workspace" -w /workspace \
            ${env.APP_NAME}-ci:sha-${env.GIT_SHA} \
            bash -c 'make lint && make test'
        """
      }
    }

    stage("Build App Image") {
      steps {
        sh "docker build -t ${env.APP_NAME}:sha-${env.GIT_SHA} ."
      }
    }
  }

  post {
    always {
      echo "Build finalizado para: ${env.APP_NAME}:sha-${env.GIT_SHA}"
    }
  }
}