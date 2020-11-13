# AWS Rekognition Text in Image Comparator
Aplicativo desarrollado en *Python 3.7* que utiliza servicios de AWS para verificar que una imagen contenga el mismo texto que una imagen de control.
Para el almacenamiento de las imagenes se utilizará **S3** y para la extracción del texto se utilizará **Rekognition**.

## Consideraciones
- El programa puede procesar un máximo 50 palabras por imagen.
- El programa no diferencia entre mayúsculas y minúsculas.
- Se ignoraran los siguientes caracteres para efecto de la comparación: `¡!:;,.@/$%-_+*#'`
- El texto debe estar dentro de una orientación de más o menos 90 grados dentro de la imagen
- Se define la **confianza mínima** para la detección de texto como un 97%
- Las extensiones para archivos de imagen permitidos son: `.png, .jpg, .jpeg`

## Instalación
Se Requiere instalar **Python 3.7** o una versión mayor, además de tener instalado [**AWS CLI version 2**](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).

Se requiere instalar el módulo de python `boto3`. Para hacerlo con pip se puede utilizar el siguiente comando:
```bash
pip install boto3
```
Finalmente, es necesario tener actualizado el archivo de `./aws/credentials` con las respectivas credenciales de AWS.

## Instrucciones de Uso
Para ejecutar el programa se debe utilizar el siguiente comando:
```bash
python comparator.py -b <bucket> -c <controlfile> [-t <testfile> | -T <testdir>]
```
#### Opciones:
- `-b <bucket>` :  El nombre del S3 Bucket
- `-c <controlfile>` :  Nombre de la imagen de control. Almacenada en el bucket
- `-t <testfile>` :  Nombre de la imagen a probar. Almacenada en el bucket
- `-T <testdir>` :  Nombre del directorio con las imagenes a probar. Dentro del bucket

**NOTA-1:** Para su ejecución, el programa requiere obligatoriamente recibir argumentos para `<bucket>` y `<controlfile>`

**NOTA-2:** Solamente se recibe un nombre de imagen a probar (`<testfile>`) o un nombre de directorio (`<testdir>`), no ambos. En caso de no recibir ninguno, el programa utilizará el directorio raíz del bucket como `<testdir>`