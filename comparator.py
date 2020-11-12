#!/usr/bin/python3

import boto3
import sys, getopt
import logging

MIN_CONFIDENCE = 0.97
IGNORED_CHARS = ['¡', '!', ':', ';', ',', '.', '@', '/', '$', '%', '-', '_', '+', '*', '#', "'"]
AUTHORIZED_EXTS = ["jpg", "jpeg", "png"]

def compareText(test_words, control_words):
    print(test_words)
    for word in test_words:
        if word not in control_words:
            print(word)
            return "false"
    return "true"

def isImageExtension(filename):
    extension = filename.split('.')[-1]
    if extension in AUTHORIZED_EXTS:
        return True
    return False

def listBucketImages(s3, bucket, dir, control_img):
    all_objects = s3.list_objects_v2(Bucket = bucket, Prefix = dir)
    test_img = []
    for obj in all_objects['Contents']:
        key = obj['Key']
        path = key.split("/")
        #Verificar que en caso de que no se haya especificado un directorio solo se considere la raíz del backet
        if len(path) != 1 and dir == '':
            continue
        filename = path[-1]
        # Verificar que el nombre (key) tenga una extensión válida
        if isImageExtension(filename):
            # Verificar no considerar la imagen de control para test.
            if key != control_img:
                test_img.append(key)
    print(test_img)
    return test_img

def getArgs():
    bucket = ''
    control_img = ''
    test_img = ''
    test_dir = ''

    # Recibir como parámetros los nombres del bucket, imagen de control e imagen de prueba
    try:
        opts, _ = getopt.getopt(sys.argv[1:],"hb:c:t:T:")
    except getopt.GetoptError:
        print("USAGE")
        print('comparator.py -b <bucket> -c <controlfile> [-t <testfile> | -T <testdir>]') 
        print("for help use -h option")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("=> USAGE")
            print('comparator.py -b <bucket> -c <controlfile> [-t <testfile> | -T <testdir>]')
            print("=> HELP")
            print("-b <bucket> :  S3 Bucket Name")
            print("-c <controlfile> :  Name of the control image in the Bucket")
            print("-t <testfile> :  Name of the test image in the Bucket")
            print("-T <testdir> :  Name of the dir with the test images in the Bucket")
            print("NOTE-1: Arguments are required for <bucket> and <controlfile>")
            print("NOTE-2: Only one filename or one directory can be received for testing, not both")
            sys.exit()
        elif opt in ("-b", "--bucket"):
            bucket = arg
        elif opt in ("-c"):
            control_img = arg
        elif opt in ("-t"):
            test_img = arg
        elif opt in ("-T"):
            test_dir = arg
    
    # Verificar que se recibieron todos los argumentos obligatorios
    if bucket == '' or control_img == '':
        print("Arguments are required for <bucket> and <controlfile>")
        print("=> USAGE")
        print ('comparator.py -b <bucket> -c <controlfile> [-t <testfile> | -T <testdir>]')
        print("for help use -h option")
        sys.exit(2)

    # Verificar la extension de la imagen de control
    if not isImageExtension(control_img):
        print("The control image file must have a .jpg .jpeg or .png extension")
        print("for help use -h option")
        sys.exit(2)
    
    # Verificar que no se recibieron simultaneamente nombre de imagen y directorio para pruebas.
    if test_img != '' and test_dir != '':
        print("Only one filename or one directory can be received for testing, not both")
        print("=> USAGE")
        print ('comparator.py -b <bucket> -c <controlfile> [-t <testfile> | -T <testdir>]')
        print("for help use -h option")
        sys.exit(2)
    
    return bucket, control_img, test_img, test_dir

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
    # Configuración del logger
    logger = logging.getLogger('root')
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler('comparator.log', 'a', 'utf-8')
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Recibir y verificar los argumentos del programa 
    bucket, control_img, test_img, test_dir = getArgs()

    # Instanciar cliente de S3
    s3 = boto3.client("s3")

    # En caso de no recibir un nombre de imagen, obtenemos la lista de imagenes en el directorio del bucket
    if test_img == '':
        test_list = listBucketImages(s3, bucket, test_dir, control_img)
    # En caso contrario encapsulamos el nombre de la imagen en una lista para iterarlo
    else:
        test_list = list(test_img)

    # Instanciar cliente de AWS Rekognition
    client = boto3.client('rekognition')

    # Reconocer texto en la imagen de control
    control_words = rekognitionTextDetection(client, bucket, control_img)
    
    #Iterar
    for image in test_list:
        #Reconocer el texto de la imagen a probar
        test_words = rekognitionTextDetection(client, bucket, image)

        # Comparar el texto en las imagenes
        resultado = compareText(test_words, control_words)
        print(resultado)
    
        #Genera el mensaje de log y actualiza el archivo
        correct_log = '[%s] %s, %s -> %s'
        logger.info(correct_log, bucket, control_img, image, resultado)

    sys.exit()
