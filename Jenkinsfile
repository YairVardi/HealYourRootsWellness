pipeline {
  agent any

  options {
    timestamps()
    timeout(time: 60, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }

  parameters {
    booleanParam(
      name: 'USE_LOCAL_WORKSPACE',
      defaultValue: false,
      description: 'Use PROJECT_DIR instead of Jenkins SCM checkout.'
    )
    string(
      name: 'PROJECT_DIR',
      defaultValue: '/Users/yairvardi/Documents/Automation/HealYourRootsWellness',
      description: 'Absolute project path when USE_LOCAL_WORKSPACE is true.'
    )
    string(
      name: 'TEST_SUITE',
      defaultValue: '',
      description: 'Optional TestNG class, for example SanityTest.ClientFlowTest. Empty runs all tests.'
    )
    choice(
      name: 'PLATFORM_NAME',
      choices: ['WEB', 'api', 'Mobile', 'electron', 'desktop'],
      description: 'Runtime platform mapped to Configuration/DataConfig.xml.'
    )
    choice(
      name: 'BROWSER_NAME',
      choices: ['chrome', 'firefox'],
      description: 'Browser for Java Selenium web runs.'
    )
    booleanParam(
      name: 'HEADLESS',
      defaultValue: true,
      description: 'Run browser without a visible UI.'
    )
    string(
      name: 'BASE_URL',
      defaultValue: 'https://healyourrootswellness.com',
      description: 'Target environment base URL.'
    )
  }

  environment {
    CI = 'true'
    PROJECT_NAME = 'HealYourRootsWellness'
    FRAMEWORK_NAME = 'Java Selenium'
    LANGUAGE_NAME = 'Java'
    PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:${env.PATH}"
  }

  stages {
    stage('Checkout') {
      when {
        expression { !params.USE_LOCAL_WORKSPACE }
      }
      steps {
        checkout scm
      }
    }

    stage('Select Workspace') {
      steps {
        script {
          env.PROJECT_ROOT = params.USE_LOCAL_WORKSPACE ? params.PROJECT_DIR : env.WORKSPACE
        }
      }
    }

    stage('Clean Reports') {
      steps {
        dir(env.PROJECT_ROOT) {
          sh 'rm -rf allure-results allure-report target/surefire-reports target/site/allure-maven-plugin'
        }
      }
    }

    stage('Tool Versions') {
      steps {
        dir(env.PROJECT_ROOT) {
          sh '''
            chmod +x ./mvnw
            java -version
            ./mvnw --version
          '''
        }
      }
    }

    stage('Compile') {
      steps {
        dir(env.PROJECT_ROOT) {
          sh './mvnw -DskipTests test'
        }
      }
    }

    stage('Prepare Allure Metadata') {
      steps {
        dir(env.PROJECT_ROOT) {
          sh 'mkdir -p allure-results'
          writeFile file: 'allure-results/environment.properties', text: """Project=${env.PROJECT_NAME}
BaseURL=${params.BASE_URL}
Framework=${env.FRAMEWORK_NAME}
Language=${env.LANGUAGE_NAME}
BuildTool=Maven
TestRunner=TestNG
"""
        }
      }
    }

    stage('Run Java Selenium Tests') {
      steps {
        dir(env.PROJECT_ROOT) {
          sh '''
            rm -rf target/surefire-reports target/site/allure-maven-plugin

            TEST_ARGS=""
            if [ -n "${TEST_SUITE}" ]; then
              TEST_ARGS="-Dtest=${TEST_SUITE}"
            fi

            ./mvnw test ${TEST_ARGS} \
              -DPlatformName="${PLATFORM_NAME}" \
              -DBrowserName="${BROWSER_NAME}" \
              -DHeadless="${HEADLESS}" \
              -Durl="${BASE_URL}" \
              -Dbase.url="${BASE_URL}" \
              -Dproject.name="${PROJECT_NAME}" \
              -Dframework.name="${FRAMEWORK_NAME}" \
              -Dlanguage.name="${LANGUAGE_NAME}"
          '''
        }
      }
    }
  }

  post {
    always {
      dir(env.PROJECT_ROOT ?: env.WORKSPACE) {
        junit allowEmptyResults: true, testResults: 'target/surefire-reports/TEST-*.xml'

        script {
          if (fileExists('allure-results')) {
            catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
              allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
            }
          } else {
            echo 'No Allure results were generated.'
          }
        }

        archiveArtifacts(
          artifacts: 'target/surefire-reports/**,allure-results/**',
          allowEmptyArchive: true,
          fingerprint: true
        )
      }
    }
  }
}
