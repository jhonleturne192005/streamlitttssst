import streamlit as st
import requests
import base64
import time
import io
import requests
import json
from pathlib import Path

lambda_url = "https://iv3nd406f1.execute-api.us-east-1.amazonaws.com/default/funciontts" 

# Función para llamar a la Lambda y grabar un audio
def upload_audio_to_lambda(audio_file,extencion):
    # Convierte el archivo de audio en base64
    audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
    
    # URL de tu función Lambda
    
    # Cuerpo de la solicitud que incluye el audio en base64
    payload = {
        "base64": audio_base64,
        "extencion":extencion
    }
    
    # Hacer la solicitud POST a Lambda
    headers = {'Content-Type': 'application/json'}
    response = requests.post(lambda_url, json=payload, headers=headers)
    
    # Verificar si la respuesta es exitosa
    if response.status_code == 200:
        result = response.json()
        print(result)
        return result.get('text', "No se pudo transcribir el audio.")
    else:
        return "Error al procesar el audio."

# Función para convertir texto a audio (usando AWS Polly)
def text_to_audio(text):
    # URL de tu función Lambda para convertir texto a audio
    lambda_url = "https://iv3nd406f1.execute-api.us-east-1.amazonaws.com/default/funciontts" 
    
    # Crear el payload para la solicitud
    payload = {
        "text": text
    }

    headers = {'Content-Type': 'application/json'}
    
    # Enviar la solicitud POST a Lambda
    response = requests.post(lambda_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        # Extraer el audio generado (en base64) y devolverlo
        return result.get('audio_base64', "")
    else:
        return "Error al generar el audio."

# Interfaz de usuario en Streamlit
def main():
    st.title("Aplicación de Audio a Texto y Texto a Voz")

    # Barra lateral para seleccionar una opción
    option = st.sidebar.selectbox("Selecciona una opción", ("Subir un Audio Existente", "Ingresar Texto"))


    if option == "Subir un Audio Existente":
        st.subheader("Sube un archivo de audio y muestra el texto transcrito")

        # Subir archivo de audio existente
        audio_file = st.file_uploader("Selecciona un archivo de audio", type=["mp3", "wav", "ogg", "m4a", "flac"])

        if audio_file is not None:

            file_name = audio_file.name
            file_extension = Path(file_name).suffix.replace(".","")
            st.write(f"Nombre del archivo: {file_name}")
            st.write(f"Extensión del archivo: {file_extension}")

            st.audio(audio_file, format='audio/{file_extension}')  # Reproducir el archivo de audio subido

            if st.button("Convertir a Texto"):
                st.write("Procesando audio...")
                result = upload_audio_to_lambda(audio_file,file_extension)
                print(result)
                st.write("Texto transcrito:")

                response = requests.get(result)

                # Verificar si la solicitud fue exitosa
                
                print("Respuesta en formato JSON:")
                print(response.json())  # Convierte la respuesta JSON a un diccionario de Python

                jsondata=response.json()
                transcription = jsondata['results']['transcripts'][0]['transcript']
                st.text_area("Texto", value=transcription, height=200)

    elif option == "Ingresar Texto":
        st.subheader("Ingresa texto y conviértelo a voz")

        # Caja de texto para ingresar texto
        text_input = st.text_area("Escribe el texto aquí", height=150)

        if st.button("Convertir a Voz"):
            if text_input.strip() != "":
                audio_base64 = text_to_audio(text_input)
                if audio_base64:
                    audio_data = base64.b64decode(audio_base64)
                    st.audio(audio_data, format="audio/mp3")  # Reproducir el audio generado
                else:
                    st.error("Error al convertir el texto a voz.")
            else:
                st.error("Por favor, ingresa un texto para convertirlo a voz.")

    st.sidebar.text("Aplicación usando Streamlit y AWS Lambda")

if __name__ == "__main__":  
    main()
