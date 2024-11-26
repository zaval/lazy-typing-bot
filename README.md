# Lazy Typing Bot

Telegram bot transcriber for annoying voice messages

## Overview

Lazy Typing Bot is designed to help users who receive voice messages on Telegram that they would prefer to read instead
of listening to. This bot automatically transcribes voice messages into text and sends the transcribed content back to
the user.

## Features

- **Automated Transcription**: Converts voice messages to text using OpenAI Whisper speech recognition model.
- **Webhook Integration**: Uses webhooks to receive and process messages in real-time.
- **Google Cloud ready**: Can be deployed to Google Cloud.
- **Docker Support**: Can be deployed using Docker for easy setup and scalability.

## How It Works

1. **Voice Message Reception**: The bot receives a voice message via the Telegram API.
2. **Transcription Service**: The voice message is sent to a transcription service.
3. **Sending Text Back**: The transcribed text is sent back to the user in the Telegram chat.

## Telegram bot Setup

1. Create a new bot using [@BotFather](https://t.me/BotFather)
2. Save the bot token into the env variable `TELEGRAM_TOKEN`

## Google Cloud Setup

To get started, clone the repository and follow these steps:

1. Create [project](https://console.cloud.google.com/projectcreate), and activate Cloud Run. 
Save the project name into variable `PROJECT_NAME`, and region name into `REGION`
2. Create two [Cloud Storage](https://console.cloud.google.com/storage/browser) buckets: for audio and for models.
Save bucket names into `AUDIO_BUCKET` and `MODELS_BUCKET`
3. Goto [API Credentials](https://console.cloud.google.com/apis/credentials) and save the Default compute service account into variable `SERVICE_ACCOUNT`
4. Create [Artifact registry](https://console.cloud.google.com/artifacts)
5. Build and deploy Webhook using [this doc](webhook/README.md)
6. Build and deploy Recogniser using [this doc](recogniser/README.md)
7. Download Whisper models and push them into `MODELS_BUCKET` root
8. Create telegram webhook using the Webhook Cloud Run URL
```shell
curl -X POST \
  -d "url=${webhook_url}" \
  https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook
```

## Whisper models

Whisper has several models, I've tested two of them on Cloud Run and they have some memory requirements:

* openai/whisper-small - requries 2GB of memory
* openai/whisper-large-v3 - requires 7GB of memory

Choose any of them, but don't forget to adjust the memory setting for the recogniser Cloud Run service.

However, Whisper has its own package, but it has lots of dependencies and requires CUDA version of PyTorch to be installed which we won't use on Cloud Run.
This creates a docker image of ~5GB, but the current solution creates a docker image of 500MB.

### Download models

1. Use this python code to download the model from [HuggingFace 🤗](https://huggingface.co/)

```python
from transformers import WhisperForConditionalGeneration
model_id = 'openai/whisper-small'  # or 'openai/whisper-large-v3'
model = WhisperForConditionalGeneration.from_pretrained(model_id)
```

2. Goto the huggingface cache directory (usually `~/.cache/huggingface/hub/<model-name>/snapshots/<uuid>`)
3. Copy all files to the temporary models directory (they are symlinks, so better use `cat >`)
```shell
for i in ls ; do cat $i > /path/to/temporary/models/$i ; done
```
4. Upload content of the temporary models dir to the root of `MODELS_BUCKET`


## Local development
1. Install dependencies from webhook and recogniser requirements.txt files
2. Export all environment variables described here and in subfolders readme files  

## Contributions

Contributions to the project are welcome. You can submit issues or pull requests on the GitHub repository.

