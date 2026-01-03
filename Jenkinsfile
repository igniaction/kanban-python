pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  environment {
    APP_NAME = "kanban-python"
    // não fixe GIT_SHA aqui; ele será definido no Init
  }

  stages {
    stage("Checkout") {
      steps {
        // Para pipeline multibranch, normalmente já vem feito,
        // mas manter explícito evita rodar fora do workspace.
        checkout scm
      }
    }

    stage("Init") {
      steps {
        script {
          env.GIT_SHA = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
          if (!env.GIT_SHA) {
            error("Não consegui obter GIT_SHA (git rev-parse retornou vazio).")
          }
          echo "Commit SHA: ${env.GIT_SHA}"
          sh "pwd && ls -la && test -f Makefile"
        }
      }
    }

    stage("Build CI Toolchain Image") {
      steps {
        sh """
          docker build \
            -f ci/jenkins-agent.Dockerfile \
            -t ${env.APP_NAME}-ci:sha-${env.GIT_SHA} \
            .
        """
      }
    }

    stage("Lint & Test") {
      steps {
        sh """
          docker run --rm \
            -v "\${WORKSPACE}:/workspace" \
            -w /workspace \
            ${env.APP_NAME}-ci:sha-${env.GIT_SHA} \
            bash -lc "make lint && make test"
        """
      }
    }

    stage("Build App Image") {
      steps {
        sh """
          docker build \
            -t ${env.APP_NAME}:sha-${env.GIT_SHA} \
            .
        """
      }
    }
  }

  post {
    always {
      echo "Build finalizado para: ${env.APP_NAME}:sha-${env.GIT_SHA}"
    }
  }
}
