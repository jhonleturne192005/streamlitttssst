import json
import boto3
import time
import base64
import uuid
from io import BytesIO
from datetime import datetime
import http.client

# Inicializar clientes de AWS
transcribe_client = boto3.client('transcribe')
polly_client = boto3.client('polly')
s3 = boto3.client("s3")

def lambda_handler(event, context):
    try:
        body = event['body']
        band=True
        caracter = "text"
        text=""

        if caracter in body:
            band=False
            #base64_audio = body.get('audio_base64')
            body = json.loads(event['body'])
            text = body.get('text')
        

        if band:    
            body = json.loads(event['body'])
            base64dato=body["base64"]
            extencion=body["extencion"]
            
            # Generar un nombre único para el archivo en S3
            #job_uri = 'data:audio/{};base64,{}'.format(audio_format, body)
            transcription_job_name = f"transcription-job-{int(time.time())}"

            # Especificar el nombre del bucket en S3 donde se almacenarán los resultados
            s3_bucket_name = 'mubucketpersonasrec'  # Aquí debes poner tu bucket de S3

            audio_id = f"audio-{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}.{extencion}"
            bucket_name="mubucketpersonasrec"

            audio_data = base64.b64decode(base64dato)

     
            s3.put_object( Bucket= bucket_name, Key=audio_id,
                Body=audio_data,  ContentType="audio/mpeg")

            # Crear la URL del archivo en S3
            media_file_uri = f"s3://{s3_bucket_name}/{audio_id}"


            # Iniciar el trabajo de transcripción usando un bucket de S3 para almacenar los resultados
            response = transcribe_client.start_transcription_job(
                TranscriptionJobName=transcription_job_name,
                LanguageCode='es-ES',  # Cambia el código del idioma si es necesario
                Media={'MediaFileUri': media_file_uri},  # Usamos el URI Base64 como media source
                MediaFormat=extencion,  # Asegúrate de que el formato esté correcto
                OutputBucketName=s3_bucket_name  # Usa el bucket S3 para la salida
            )
            
            # Esperar a que la transcripción termine
            while True:
                response = transcribe_client.get_transcription_job(TranscriptionJobName=transcription_job_name)
                status = response['TranscriptionJob']['TranscriptionJobStatus']
                if status in ['COMPLETED', 'FAILED']:
                    break
                time.sleep(5)
            
            if status == 'FAILED':
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "status": status,
                    })
                }
            
            # Obtener el texto transcrito
            transcript_text = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
       

            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Transcripción completada",
                    "text": transcript_text
                })
            }

        # Si es un proceso de texto a audio
        polly_response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Lucia'
        )
        
        # Convertir el audio en Base64
        audio_stream = polly_response['AudioStream'].read()
        audio_base64 = base64.b64encode(audio_stream).decode('utf-8')
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Texto convertido a audio con éxito",
                "audio_base64": audio_base64
            })
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
