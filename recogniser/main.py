from __future__ import annotations

import logging
import os

import torch
from google.cloud import storage
from pydantic import BaseModel

from fastapi import FastAPI
from telegram import Bot
from transformers import WhisperForConditionalGeneration, WhisperProcessor, pipeline

logger = logging.getLogger(__name__)

class CustomerEncryption(BaseModel):
    encryptionAlgorithm: str
    keySha256: str

class StorageObjectData(BaseModel):
    name: str
    bucket: str
    generation: int | None = None
    metageneration: int | None = None
    contentType: str | None = None
    timeCreated: str | None = None
    updated: str | None = None
    storageClass: str | None = None
    size: int | None = None
    md5Hash: str | None = None
    mediaLink: str | None = None
    crc32c: str | None = None
    etag: str | None = None
    # customerEncryption: CustomerEncryption

app = FastAPI()

def delete_blob(bucket_name: str, source_blob_name: str) -> None:

    bucket = storage.Client().bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.delete()

def download_blob(bucket_name: str, source_blob_name: str, destination_file_name: str) -> bool:

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    try:
        blob.download_to_filename(destination_file_name)
    except Exception as e:
        logger.info(e)
        return False

    return True

@app.post("/")
async def root(request: StorageObjectData):

    try:
        chat_id = request.name.split("inputs/")[1].split("/")[0]
    except:
        return {"message": "Error"}

    tmp_file = f"/tmp/{os.path.basename(request.name)}"

    if not download_blob(request.bucket, request.name, tmp_file):
        return {"message": "NO file"}

    device = torch.device('cpu')
    torch_dtype = torch.float32
    if os.path.exists("../models"):
        model_id = "../models"
    else:
        model_id = "/mnt/models"
    model = WhisperForConditionalGeneration.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True
    )
    model.to(device)
    processor = WhisperProcessor.from_pretrained(model_id)
    forced_decoder_ids = processor.get_decoder_prompt_ids(language="uk", task="transcribe")

    model.config.forced_decoder_ids = forced_decoder_ids

    whisper = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
    )
    transcription = whisper(tmp_file)
    os.remove(tmp_file)
    try:
        delete_blob(request.bucket, request.name)
    except Exception as e:
        logger.exception(e)

    async with Bot(os.getenv("TG_TOKEN")) as bot:
        await bot.send_message(chat_id=chat_id, text=transcription['text'])

    return {"message": transcription['text']}
