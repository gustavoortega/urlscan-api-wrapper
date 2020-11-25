import requests
import json
import boto3
import time
import argparse


my_parser = argparse.ArgumentParser(description='Escanear una url con UrlScan y subir el resultado a S3')

my_parser.add_argument('--url',
                       metavar='url',
                       type=str,
                       required=True,
                       help='url a escanear')
my_parser.add_argument('--urlscankey',
                       metavar='urlscankey',
                       type=str,
                       required=True,
                       help='key a utilizar para API de Urlscan')
my_parser.add_argument('--s3bucketname',
                       metavar='s3bucketname',
                       type=str,
                       required=True,
                       help='Nombre del Bucket S3 donde subir el resultado')
my_parser.add_argument('--visibility',
                       metavar='visibility',
                       choices=['public', 'private', 'unlisted'],
                       type=str,
                       required=True,
                       help='Tipo de visibilidad. (private / public / unlisted')

args = my_parser.parse_args()

url = args.url
visibility = args.visibility
key_urlscan = args.urlscankey
headers = dict({'API-Key':key_urlscan, 'Content-Type':'application/json;charset=UTF-8'})
s3BucketName = args.s3bucketname


#Submit de url a escanear, permitiendo especificar el tipo de visibilidad. Es importante utilizar la key para poder consumir la API.
def submitScan(url):
  data = {'url': url, 'visibility': visibility}
  response = requests.post('https://urlscan.io/api/v1/scan/',headers=headers,data=json.dumps(data))
  return (response.json())

#Chequeo de resultado del escaneo. Espero inicialmente 10 segundos, luego 30 intentos cada 2 segundos.
def getScanUrl(url):
  time.sleep(10)
  r = requests.get(url)
  if r.status_code == 200:
    return(r.text)
  else:
    retries =30
    timebtwretries = 2
    for i in range(1,retries):
      log("warn","Intento numero " + str(i) + " de " + str(retries) + " con intervalos de espera de " + str(timebtwretries) + " segundos entre cada intento.")
      try:
        time.sleep(timebtwretries)
        r = requests.get(url)
        if r.status_code == 200:
          return(r.text)
      except:
        pass
    log("error", "Se agoto el tiempo de espera")
    raise Exception("Se agoto el tiempo de espera")


#Upload de archivos con Tag "public=yes" para permitir acceso publico. El tag es requerido unicamente debido al diseño de la bucket policy que realice.
def uploadToS3(filename, data):
    s3 = boto3.resource('s3')
    s3.Bucket(s3BucketName).put_object(Body= data, Key= filename, Tagging= "public=yes")

#Manejo de logs en consola, de modo de contar con diferentes colores segun el mensaje sea de info, error o warning 
def log(type="",msg=""):
  class bcolors:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
   
  if type == "error":
    print(f"{bcolors.FAIL}ERROR: " + msg + f"{bcolors.ENDC}")
  elif type == "ok":
    print(f"{bcolors.OK}OK: " + msg + f"{bcolors.ENDC}")
  else:
    print(f"{bcolors.WARNING}WARN: " + msg + f"{bcolors.ENDC}")


#Start
#Comienzo con una solicitud a Urlscan de la url a escanear. Si todo esta ok, obtengo la URL donde puedo solicitar el resultado.
try:
  message = "Submiteando el escaneo al sitio de UrlScan "+ url
  resultScanUrl = submitScan(url)["api"]
except:
  log("error", message)
  raise

#Voy a intentar obtener el resultado de la url que obtuve al submitear el scan, con reintentos durante un tiempo prudencial segun documentacion de la propia API.
#Como resultado, si todo esta ok, obtengo el contenido del escaneo y lo guardo en una variable
try:
  message = "Obteniendo resultado de UrlScan"
  log("ok",message)
  content = getScanUrl(resultScanUrl)
except:
  log("error", message)
  raise

#Genero un file en S3, con nombre "resultado.json", cuyo contenido se obtuvo como resultado del escaneo.
#Seteo el tag public=yes, de modo de hacer publico el file. Caso contrario, debido a la politica configurada en el bucket, el archivo no sera accedido en forma publica.
try:
  message = "Subiendo archivo a S3"
  log("ok",message)
  uploadToS3("resultado.json", content)
except:
  log("error", message)
  raise