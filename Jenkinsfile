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
          if (!env.GIT_SHA) {
            error("Não consegui obter GIT_SHA (git rev-parse retornou vazio).")
          }
          echo "Commit SHA: ${env.GIT_SHA}"
          sh 'pwd && ls -la && test -f Makefile'
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
            -v infra-jenkins-factory_jenkins_home:/var/jenkins_home \
            -w "${WORKSPACE}" \
            ${env.APP_NAME}-ci:sha-${env.GIT_SHA} \
            bash -lc 'set -eux; ls -la; test -f Makefile; make lint; make test'
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
