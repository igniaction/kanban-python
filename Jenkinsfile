pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  environment {
    APP_NAME = "kanban-python"
    // Definimos uma fallback caso o git falhe no init
    GIT_SHA = "latest" 
  }

  stages {
    stage("Init") {
      steps {
        script {
          // O checkout SCM automático acontece antes deste estágio. 
          // Se o checkout falhar, o pipeline nem chegará aqui.
          try {
            env.GIT_SHA = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
          } catch (e) {
            error "Falha ao obter o SHA do Git. Verifique se o binário 'git' está instalado no container Jenkins."
          }
          echo "Commit SHA: ${env.GIT_SHA}"
        }
      }
    }

    stage("Build CI Toolchain Image") {
      steps {
        // Usamos env.APP_NAME e env.GIT_SHA para garantir a interpolação correta
        sh """
          docker build -f ci/jenkins-agent.Dockerfile -t ${env.APP_NAME}-ci:sha-${env.GIT_SHA} .
        """
      }
    }

    stage("Lint & Test") {
      steps {
        sh """
          docker run --rm \
            -v "\$PWD:/workspace" -w /workspace \
            ${env.APP_NAME}-ci:sha-${env.GIT_SHA} \
            bash -c "make lint && make test"
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
      // Garantindo o acesso às variáveis de ambiente
      echo "Build finalizado: ${env.APP_NAME}:sha-${env.GIT_SHA}"
    }
    success {
      echo "Deploy liberado para a imagem: ${env.APP_NAME}:sha-${env.GIT_SHA}"
    }
  }
}