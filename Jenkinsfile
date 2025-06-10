pipeline {
    agent any

    environment {        
        // PyPI credentials should be stored in Jenkins credentials store
        PYPI_CREDENTIALS = credentials('pypi-credentials')
        VENV_DIR = "venv/freeports-dev"
        LINT_SCORE_THRESHOLD = '3.0'
        COVERAGE_THRESHOLD = '1.0'
        COVERAGE_THRESHOLD_DOCS = '0.0'
        REPORTS_DIR = 'reports'
        DOCS_DIR = 'docs/build/html'
        TREND_DATA_DIR = 'trend_data'
        
    }
    stages {
        stage('Checkout') {
            steps {
                // Verify if this is a tagged build
                script {
                    isTagged = env.TAG_NAME != null
                    if (isTagged) {
                        echo "Building tagged release: ${env.TAG_NAME}"
                    }
                }
            }
        }
        stage('Setup') {
            steps {
                sh """
                    contrib/init.sh
                    mkdir -p ${REPORTS_DIR}
                """
            }
        }
        stage('Lint') {
             steps {
                script {
                    // Run pylint and capture the score
                    lintOutput = sh(
                        script: """
                            . ${VENV_DIR}/bin/activate
                            pylint --exit-zero --output-format=json src > ${REPORTS_DIR}/pylint.json || true
                            pylint --msg-template='{path}:{line}: [{msg_id}, {obj}] {msg} ({symbol})' --exit-zero src | tee ${REPORTS_DIR}/pylint.txt
                        """,
                        returnStdout: true
                    )
                    
                    // Extract the score from the output
                    lintScore = sh(
                        script: """
                            . ${VENV_DIR}/bin/activate
                            python -c \"import re; print(re.search(r'Your code has been rated at (\\d+\\.\\d+)/10', open('${REPORTS_DIR}/pylint.txt').read()).group(1))\"
                        """,
                        returnStdout: true
                    ).trim()
                    
                    // Store the score for the trend graph
                    currentBuild.description = "Lint score: ${lintScore}/10"
                    
                    // Fail if score is below threshold
                    if (Float.parseFloat(lintScore) < Float.parseFloat(env.LINT_SCORE_THRESHOLD)) {
                        error("Lint score ${lintScore} is below threshold of ${env.LINT_SCORE_THRESHOLD}")
                    }
                }
            }
            post {
                always {
                    // Archive lint reports
                    archiveArtifacts "${REPORTS_DIR}/pylint.*"
                    // Record the lint score for trend analysis
                    recordIssues(
                        tools: [pyLint(pattern: "${REPORTS_DIR}/pylint.txt")],
                        healthy: 8, unhealthy: 6, minimumSeverity: 'LOW'
                    )
                }
            }
        }
        
        stage('Test') {
            steps {
                sh """
                    . ${VENV_DIR}/bin/activate
                    pytest tests/ --cov=src --cov-report=xml:${REPORTS_DIR}/coverage.xml --junitxml=${REPORTS_DIR}/test-results.xml  # Adjust test directory
                """
            }
            post {
                always {
                    script {
                        coverageOutput = sh(
                            script: """
                                . ${VENV_DIR}/bin/activate
                                python -c 'import xml.etree.ElementTree as ET; print(ET.parse(\"${REPORTS_DIR}/coverage.xml\").getroot().attrib[\"line-rate\"])' || echo \"0\"
                            """,
                            returnStdout: true
                        ).trim()
                        coveragePercent = (Float.parseFloat(coverageOutput) * 100).round(2)
                        currentBuild.description = "${currentBuild.description} | Test coverage: ${coveragePercent}%"
                        
                        // Fail if coverage is below threshold (only check if tests passed)
                        if (currentBuild.resultIsBetterOrEqualTo('SUCCESS')) {
                            if (coveragePercent < Float.parseFloat(env.COVERAGE_THRESHOLD)) {
                                error("Test coverage ${coveragePercent}% is below threshold of ${env.COVERAGE_THRESHOLD}%")
                            }
                        }
                    }
                    withChecks("Test restults"){
                        junit "${REPORTS_DIR}/test-results.xml"

                    }
                }
            }
        }
        stage('Build Docs') {
            steps {
                script {
                    sh """
                        . ${VENV_DIR}/bin/activate
                        cd docs && make html && make coverage && cd ../
                    """
                    
                    // Check documentation coverage (requires sphinx-coverage)
                    docsCoverage = sh(
                        script: """
                            . ${VENV_DIR}/bin/activate
                            python -c 'import re; \
                            text = open(\"docs/build/coverage/python.txt\").read(); \
                            match = re.search(r\"TOTAL\\s+\\|\\s+(\\d+\\.\\d+)%\", text); \
                            print(match.group(1)) if match else print(\"0\")' || echo \"0\"
                        """,
                        returnStdout: true
                    ).trim().toFloat()
                    
                    currentBuild.description = "${currentBuild.description} | Docs coverage: ${docsCoverage}%"
                    
                    if (docsCoverage < Float.parseFloat(env.COVERAGE_THRESHOLD_DOCS)) {
                        error("Documentation coverage ${docsCoverage}% is below threshold of ${env.COVERAGE_THRESHOLD_DOCS}%")
                    }
                }
            }
            post {
                always {
                    publishHTML(
                        target: [
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: 'docs/build/html',
                            reportFiles: 'index.html',
                            reportName: 'API Documentation'
                        ]
                    )
                    archiveArtifacts 'docs/build/coverage/python.txt'
                }
            }
        }
        
        stage('Build') {
            when {
                expression { return currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                sh """
                    . ${VENV_DIR}/bin/activate
                    python -m build
                """
                archiveArtifacts 'dist/*'
            }
        }
        
        stage('Release to PyPI') {
            when {
                allOf {
                    expression { return isTagged }
                    expression { return currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
                }
            }
            steps {
                script {
                    // Verify the tag follows semantic versioning (optional but recommended)
                    if (!(env.TAG_NAME ==~ /^v?\d+\.\d+\.\d+(-.+)?$/)) {
                        error("Tag ${env.TAG_NAME} doesn't follow semantic versioning pattern")
                    }
                    
                    // Upload to PyPI
                    withCredentials([usernamePassword(credentialsId: 'pypi-credentials', usernameVariable: 'PYPI_USERNAME', passwordVariable: 'PYPI_PASSWORD')]) {
                        sh """
                            . ${VENV_DIR}/bin/activate
                            twine upload --username ${PYPI_USERNAME} --password ${PYPI_PASSWORD} dist/*
                        """
                    }
                }
            }
        }
    //     stage('Deploy docs on GitHub Pages') {
    //         when {
    //             allOf {
    //                 expression { return isTagged }
    //                 expression { return currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
    //             }
    //         }
    //         steps {
    //             script {
    //                 // Verify the tag follows semantic versioning (optional but recommended)
    //                 if (!(env.TAG_NAME ==~ /^v?\d+\.\d+\.\d+(-.+)?$/)) {
    //                     error("Tag ${env.TAG_NAME} doesn't follow semantic versioning pattern")
    //                 }
                    
    //                 // Upload to PyPI
    //                 withCredentials([usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_TOKEN')]) {
    //                     sh """
    //                         # Configure git
    //                         git config --global user.name "Jenkins"
    //                         git config --global user.email "jenkins@freeports.org"
                            
    //                         # Clone gh-pages branch
    //                         git clone -b gh-pages https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/your-org/your-repo.git gh-pages
                            
    //                         # Copy built docs
    //                         rm -rf gh-pages/*
    //                         cp -r docs/build/html/* gh-pages/
                            
    //                         # Commit and push
    //                         cd gh-pages
    //                         git add .
    //                         git commit -m "Deploy docs for ${env.TAG_NAME}"
    //                         git push origin gh-pages
    //                         cd ..
    //                         rm -rf gh-pages
    //                     """
    //                 }
    //             }
    //         }
    //     }
    }
    post {
        always {
            // Clean up virtual environment
            sh 'rm -rf ./*'
            sh 'rm -rf ./.*'

            // Generate lint trend graph (requires Plot plugin)
            script {
                // Create trend data directory if it doesn't exist
                sh "mkdir -p ${TREND_DATA_DIR}"
                
                // Store metrics for trend graphs
                def metrics = [
                    'lint': currentBuild.description?.replaceAll(/.*Lint score: (\d+\.\d+).*/, '$1'),
                    'test': currentBuild.description?.replaceAll(/.*Test coverage: (\d+\.\d+)%.*/, '$1'),
                    'docs': currentBuild.description?.replaceAll(/.*Docs coverage: (\d+\.\d+)%.*/, '$1')
                ]
                
                // Append new data to existing trend files
                metrics.each { name, value ->
                    def scoreFile = "${TREND_DATA_DIR}/${name}_score.csv"
                    def scoreLine = "${value}\n"
                    writeFile file: scoreFile, text: "${name} score\n${scoreLine}", encoding: 'UTF-8'
                    archiveArtifacts artifacts: scoreFile, onlyIfSuccessful: false

                    // if (value?.isNumber()) {
                    //     // Try to get the last successful trend file
                    //     try {
                    //         copyArtifacts(
                    //             projectName: env.JOB_NAME,
                    //             selector: lastSuccessful(),
                    //             filter: scoreFile,
                    //             target: "${TREND_DATA_DIR}/",
                    //             optional: true,
                    //             flatten: true
                    //         )
                    //     } catch (e) {
                    //         echo "No previous trend data found for ${name}, starting fresh"
                    //     }

                    //     // Append to file or create new
                    //     def existing = fileExists(scoreFile) ? readFile(scoreFile) : ""
                    //     writeFile file: scoreFile, text: "${existing}${scoreLine}", encoding: 'UTF-8'

                    //     archiveArtifacts artifacts: scoreFile, onlyIfSuccessful: false
                    // } else {
                    //     echo "Invalid or missing value for ${name}, skipping trend update."
                    // }
                }
            }
             
            plot(
                csvFileName: 'plot-pylintscore.csv',
                title: 'Pylint Score Trend',
                yaxis: 'Score (0-10)',
                group: 'Quality of code', 
                numBuilds: '50',
                description: 'Lint score of codebase generated by `pylint`',
                style: 'line',
                csvSeries: [[file: "${TREND_DATA_DIR}/lint_score.csv"]],
                yaxisMinimum: '0',
                yaxisMaximum: '10'
            )
            
            plot(
                csvFileName: 'plot-testcoverage.csv',
                title: 'Test Coverage Trend',
                yaxis: 'Coverage %',
                group: 'Quality of code', 
                numBuilds: '50',
                description: 'Test coverage of codebase generated by `pytest`',
                csvSeries: [[file: "${TREND_DATA_DIR}/test_score.csv"]],
                style: 'line',
                yaxisMinimum: '0',
                yaxisMaximum: '100'
            )
            
            plot(
                csvFileName: 'plot-docscoverage.csv',
                title: 'Documentation Coverage Trend',
                yaxis: 'Coverage %',
                group: 'Quality of code', 
                numBuilds: '50',
                description: 'Documentation coverage of codebase generated by `sphinx.ext.coverage`',
                csvSeries: [[file: "${TREND_DATA_DIR}/docs_score.csv"]],
                style: 'line',
                yaxisMinimum: '0',
                yaxisMaximum: '100'
            )
        }
    }
}
