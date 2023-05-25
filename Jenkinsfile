pipeline {
    agent any
    environment {
        BRANCH_NAME = "${env.BRANCH_NAME}"
        CHANGE_ID = "${env.CHANGE_ID}"
        CHANGE_TARGET = "${env.CHANGE_TARGET}"
        CHANGE_BRANCH = "${env.CHANGE_BRANCH}"
        MAIN_BRANCH = 'main'
        LONG_LIVED_PATTERN = "release.*"
        SONAR_QUBE_SCANNER = "${env.JENKINS_HOME}/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarQubeScanner/bin/sonar-scanner"
    }
    options {
        disableConcurrentBuilds()
        buildDiscarder(logRotator(daysToKeepStr: '30', numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        ansiColor('xterm')
    }

    stages{
        stage('Build Test Image'){
            steps{
				ansiColor('xterm'){
					script{
						docker.build(
							"ubuntu:20.04",
							"--pull -f baseimage/Dockerfile ."
						)
					}
				}			
            }
        }

		stage('Run Tests'){
			steps {
				wrap([$class: 'Xvfb', additionalOptions: '', assignedLabels: '', displayNameOffset: 99, installationName: 'XvfbApp', screen: '0', timeout: 0]) {
					ansiColor('xterm') {
						script{
							docker.image("ubuntu:20.04").inside(){
								sh '''#!/usr/bin/env bash
								pip install --user -r requirements.txt
								pip install --user -r test/requirements.txt
								export PYTHONPATH=test:src
								python3 -m pytest --cov-report=xml:coverage.xml --cov=src -vv test'''
							}
						}
					}
				}
			}
		}

        stage('PR SonarQube analysis') {
            when { changeRequest() }
            steps {
                ansiColor('xterm') {
                    script {
                        def scannerHome = tool 'SonarQubeScanner';
                        withSonarQubeEnv('SonarCloud')
                        {
                            sh "git fetch origin ${CHANGE_TARGET}:refs/remotes/origin/${CHANGE_TARGET}"
                            sh '''${SONAR_QUBE_SCANNER} \
                                -Dsonar.pullrequest.key=${CHANGE_ID} \
                                -Dsonar.pullrequest.branch=${CHANGE_BRANCH} \
                                -Dsonar.pullrequest.base=${CHANGE_TARGET} \
                                -Dsonar.python.coverage.reportPaths=coverage.xml'''
                        }
                    }
                }
            }
        }

        stage('Main branch SonarQube analysis') {
            when { allOf { not { changeRequest() }; branch MAIN_BRANCH} }
            steps {
                ansiColor('xterm') {
                    script {
                        def scannerHome = tool 'SonarQubeScanner';
                        withSonarQubeEnv('SonarCloud')
                        {
                            sh '''${SONAR_QUBE_SCANNER} \
                                -Dsonar.branch.name=${BRANCH_NAME} \
                                -Dsonar.python.coverage.reportPaths=coverage.xml'''
                        }
                    }
                }
            }
        }

        stage('Long-lived branch SonarQube analysis') {
            when { allOf { not { changeRequest() }; branch pattern: LONG_LIVED_PATTERN, comparator: "REGEXP" } }
            steps {
                ansiColor('xterm') {
                    script {
                        def scannerHome = tool 'SonarQubeScanner';
                        withSonarQubeEnv('SonarCloud')
                        {
                            sh '''${SONAR_QUBE_SCANNER} \
                                -Dsonar.branch.name=${BRANCH_NAME} \
                                -Dsonar.branch.target=${MAIN_BRANCH} \
                                -Dsonar.python.coverage.reportPaths=coverage.xml'''
                        }
                    }
                }
            }
        }

        stage('Short-lived branch SonarQube analysis') {
            when { allOf { not { changeRequest() }; not { branch pattern: LONG_LIVED_PATTERN, comparator: "REGEXP" }; not { branch MAIN_BRANCH } } }
            steps {
                ansiColor('xterm') {
                    script {
                        def scannerHome = tool 'SonarQubeScanner';
                        withSonarQubeEnv('SonarCloud')
                        {
                            sh '''${SONAR_QUBE_SCANNER} \
                                -Dsonar.branch.name=${BRANCH_NAME} \
                                -Dsonar.branch.target=${BRANCH_NAME} \
                                -Dsonar.python.coverage.reportPaths=coverage.xml'''
                        }
                    }
                }
            }
        }
    }
}
