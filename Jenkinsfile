@Library('promebuilder')_

pipeline {
  agent any
  parameters {
    booleanParam(
      name: 'skip_tests',
      defaultValue: false,
      description: 'Skip all tests'
    )
  }
  environment {
    CONDAENV = "${env.JOB_NAME}_${env.BUILD_NUMBER}".replace('%2F','_').replace('/', '_')
  }
  stages {
    stage('Bootstrap') {
      steps {
        writeFile file: 'buildnum', text: "${env.BUILD_NUMBER}"
        writeFile file: 'commit', text: "${env.GIT_COMMIT}"
        // env.GIT_BRANCH is wrong when the included library is the same project is builded!
        // writeFile file: 'branch', text: "${env.GIT_BRANCH}"
        writeFile file: 'branch', text: bat(script: "git rev-parse --abbrev-ref HEAD", returnStdout: true).split(" ")[-1].trim()
        stash(name: "source", useDefaultExcludes: true)
      }
    }
    stage("MultiBuild") {
      parallel {
        stage("Build on Linux") {
          steps {
            doubleArchictecture('linux')
          }
        }
        stage("Build on Windows") {
          steps {
            doubleArchictecture('windows', 'base', true)
          }
        }
      }
    }
  }
  post {
    success {
      deleteDir()
    }
    failure {
      mail to: 'pytho_support@prometeia.com ',
        subject: "PROMEBUILDER: Failed Pipeline ${currentBuild.fullDisplayName}",
        body: "Loot at ${env.BUILD_URL}"
    }
  }
}
