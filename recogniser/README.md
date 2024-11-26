# Lazy Typing Bot Recogniser

Recogniser task for the telegram bot.
It uses Whisper as a speech-to-text engine and ready to deploy to Google Cloud.

## Prepare

Export environment variables

```dotenv
REGION=us-east1
RECOGNISER_DOCKER_IMAGE=<docker_image>
SERVICE_ACCOUNT=<service_account>
TELEGRAM_TOKEN=<telegram_token>
PROJECT_NAME=<project_name>
MODELS_BUCKET=<models_bucket>
AUDIO_BUCKET=<audio_bucket>
```


## Build

```shell
gcloud auth configure-docker \
    ${REGION}-docker.pkg.dev
docker build . --platform=linux/x86_64 -t ${RECOGNISER_DOCKER_IMAGE}
docker push ${RECOGNISER_DOCKER_IMAGE}
```

## Deploy

```shell
gcloud run deploy recogniser \
    --image=${RECOGNISER_DOCKER_IMAGE} \
    --no-allow-unauthenticated \
    --port=8000 \
    --service-account=${SERVICE_ACCOUNT} \
    --memory=2Gi \
    --set-env-vars=TG_TOKEN=${TELEGRAM_TOKEN} \
    --region=${REGION} \
    --project=${PROJECT_NAME}

gcloud run services update recogniser \
    --add-volume name=models-volume,type=cloud-storage,bucket=${MODELS_BUCKET},readonly=true \
    --add-volume-mount volume=models-volume,mount-path=/mnt/models \
    --region=${REGION} \
    --project=${PROJECT_NAME}

gcloud eventarc triggers create trigger-jrk6s4l3 \
    --location=${REGION} \
    --service-account=${SERVICE_ACCOUNT} \
    --destination-run-service=recogniser \
    --destination-run-region=${REGION} \
    --destination-run-path="/" \
    --event-filters="bucket=${AUDIO_BUCKET}" \
    --event-filters="type=google.cloud.storage.object.v1.finalized"
```

## Local docker run

```shell
docker run --rm \
  -e TG_TOKEN=${TELEGRAM_TOKEN} \
  -v /path/to/downloaded/models:/mnt/models \
  -p 8000:8000 \
  -it ${RECOGNISER_DOCKER_IMAGE}
```