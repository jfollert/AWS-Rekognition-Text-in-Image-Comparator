#!/usr/bin/python3

import boto3
import sys, getopt
import logging

MIN_CONFIDENCE = 0.97
IGNORED_CHARS = ['!', '.']

# Configuración del logger
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('comparator.log', 'a', 'utf-8')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def getArgs():
    bucket = ''
    control_img = ''
    test_img = ''

    # Recibir como parámetros los nombres del bucket, imagen de control e imagen de prueba
    try:
        opts, _ = getopt.getopt(sys.argv[1:],"hb:c:t:",["bucket=", "controlfile=","testfile="])
    except getopt.GetoptError:
        print('comparator.py -b <bucket> -c <controlfile> -t <testfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('comparator.py -b <bucket> -c <controlfile> -t <testfile>')
            sys.exit()
        elif opt in ("-b", "--bucket"):
            bucket = arg
        elif opt in ("-c", "--controlfile"):
            control_img = arg
        elif opt in ("-t", "--testfile"):
            test_img = arg
    
    # Verificar que se recibieron todos los argumentos
    if bucket == '' or control_img == '' or test_img == '':
        print ('comparator.py -b <bucket> -c <controlfile> -t <testfile>')
        sys.exit()
    
    return bucket, control_img, test_img


def rekognitionTextDetection(client, bucket, image):
    response = client.detect_text(Image = {'S3Object': {'Bucket': bucket,'Name': image}}, 
                                Filters={'WordFilter': {'MinConfidence': MIN_CONFIDENCE}})
    textDetections = response['TextDetections']
    detected = []
    for text in textDetections:
        if "ParentId" in text.keys(): # Filtrar para obtener solo las palabras individualmente
            word = text['DetectedText'].lower() # Transformar toda la palabra a minúscula
            word = ''.join(i for i in word if not i in IGNORED_CHARS) # Filtrar los caracteres a ignorar
            detected.append(word)
    return detected


if __name__ == "__main__":

    # Recibir y verificar los argumentos del programa 
    bucket, control_img, test_img = getArgs()

    # Instanciar cliente de AWS Rekognition
    client = boto3.client('rekognition')

    # Reconocer texto en las imagenes
    control_words = rekognitionTextDetection(client, bucket, control_img)
    test_words = rekognitionTextDetection(client, bucket, test_img)

    # Comparar el texto en las imagenes
    resultado = "true"
    for word in test_words:
        if word not in control_words:
            resultado = "false"
    print(resultado)
    
    #Genera el mensaje de log y actualiza el archivo
    correct_log = '[%s] %s, %s -> %s'
    logger.info(correct_log, bucket, control_img, test_img, resultado)

    sys.exit()
