# AWS Rekognition Text in Image Comparator
Aplicativo desarrollado en *Python 3.7* que utiliza AWS para verificar que una imagen contenga el mismo texto que una imagen de control.
Para el almacenamiento de las imagenes se utilizará **S3** y para la extracción del texto se utilizará **Rekognition**.

## Consideraciones
- El programa no diferencia entre mayúsculas y minúsculas.
- Se ignoraran los siguientes caracteres para efecto de la comparación -> `!.`

## Instalación
Requiere tener instalado **Python 3.7** o una versión mayor, además de tener instalado [**AWS CLI version 2**](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).

Además, requiere instalar la librería `boto3`, para hacerlo con pip se puede utilizar el siguiente comando:
```bash
pip install boto3
```

## Instrucciones de Uso
Para ejecutar el programa debe utilizar la siguiente estructura:
```bash
python comparator.py -b <bucket> -c <controlfile> -t <testfile>
```