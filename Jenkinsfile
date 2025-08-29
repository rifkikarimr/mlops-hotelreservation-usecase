pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "authentic-host-467010-t5"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }

    stages{
        stage('Cloning Github repo to Jenkins'){
            steps{
                script{
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/rifkikarimr/mlops-hotelreservation-usecase.git']])
                }
            }
        }

        stage('Setting up our Virtual Environment and Installing dependancies'){
            steps{
                script{
                    echo 'Setting up our Virtual Environment and Installing dependancies............'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

        stage('Debug GCP Authentication') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        sh '''
                        echo "--- 1. Verifying Service Account Activation ---"
                        # Activate the service account (corrected command)
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        
                        # Now, verify which account is active
                        echo "Successfully activated account:"
                        gcloud config get-value account
                        
                        echo "--- 2. Verifying IAM Roles for the Account ---"
                        ACCOUNT_EMAIL=$(gcloud config get-value account)
                        echo "Checking roles for account: ${ACCOUNT_EMAIL}"
                        gcloud projects get-iam-policy ${GCP_PROJECT} --format="json" | jq -r --arg USER "serviceAccount:${ACCOUNT_EMAIL}" '.bindings[] | select(.members[] | contains($USER)) | .role'
                        
                        echo "--- 3. Testing Direct Artifact Registry Access ---"
                        gcloud artifacts repositories list --location=asia-southeast2 --project=${GCP_PROJECT}

                        echo "--- 4. Verifying Docker Configuration ---"
                        gcloud auth configure-docker asia-southeast2-docker.pkg.dev --quiet
                        echo "Docker config file contents:"
                        cat ~/.docker/config.json
                        '''
                    }
                }
            }
        }

        stage('Building and Pushing Docker Image to GCR'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Building and Pushing Docker Image to GCR.............'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker --quiet
                        docker build -t asia-southeast2-docker.pkg.dev/${GCP_PROJECT}/ml-images/hotel-reserve:v1.0 .
                        docker push asia-southeast2-docker.pkg.dev/${GCP_PROJECT}/ml-images/hotel-reserve:v1.0
                        '''
                    }
                }
            }
        }


        stage('Deploy to Google Cloud Run'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Deploy to Google Cloud Run.............'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud run deploy ml-project \
                            --image=asia-southeast2-docker.pkg.dev/${GCP_PROJECT}/ml-images/hotel-reserve:v1.0 \
                            --platform=managed \
                            --region=asia-southeast2 \
                            --allow-unauthenticated
                        '''
                    }
                }
            }
        }
    }
}