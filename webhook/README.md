# Lazy Typing Bot Webhook

The telegram bot webhook which translates audio messages into the text.

## Prepare

Export environment variables

```dotenv
REGION=us-east1
WEBHOOK_DOCKER_IMAGE=<docker_image>
SERVICE_ACCOUNT=<service_account>
TELEGRAM_TOKEN=<telegram_token>
PROJECT_NAME=<project_name>
MODELS_BUCKET=<models_bucket>
AUDIO_BUCKET=<audio_bucket>
```

## Build and install

```shell
gcloud auth configure-docker \
    ${REGION}-docker.pkg.dev
docker build . --platform=linux/x86_64 -t ${WEBHOOK_DOCKER_IMAGE}
docker push ${WEBHOOK_DOCKER_IMAGE}
```

## Deploy

```shell
gcloud run deploy webhook \
    --image=${WEBHOOK_DOCKER_IMAGE} \
    --allow-unauthenticated \
    --port=8000 \
    --service-account=${SERVICE_ACCOUNT} \
    --set-env-vars=AUTHORIZED_USERS=${AUTHORIZED_USERS},BUCKET_NAME=${AUDIO_BUCKET},TG_TOKEN=${TELEGRAM_TOKEN},TG_SECRET=${TELEGRAM_SECRET} \
    --region=${REGION} \
    --project=${PROJECT_NAME}
```


## Local docker run

```shell
docker run --rm \
  -e AUTHORIZED_USERS=${AUTHORIZED_USERS} \
  -e BUCKET_NAME=${AUDIO_BUCKET} \
  -e TG_TOKEN=${TELEGRAM_TOKEN} \
  -e TG_SECRET=${TELEGRAM_SECRET} \
  -p 8000:8000 \
  -it ${WEBHOOK_DOCKER_IMAGE}
```
