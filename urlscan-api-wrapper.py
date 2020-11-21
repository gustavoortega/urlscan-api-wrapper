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



def submitScan(url):
  data = {'url': url, 'visibility': visibility}
  response = requests.post('https://urlscan.io/api/v1/scan/',headers=headers,data=json.dumps(data))
  return (response.json())

def getScanUrl(url):
  time.sleep(10)
  r = requests.get(url)
  if r.status_code == 200:
    return(r.text)
  else:
    retries =30
    timebtwretries = 2
    status = None
    for i in range(1,retries):
      print("Intento numero " + str(i) + " de " + str(retries) + " con intervalos de espera de " + str(timebtwretries) + " segundos entre cada intento.")
      try:
        time.sleep(timebtwretries)
        r = requests.get(url)
        if r.status_code == 200:
          return(r.text)
      except:
        pass
    raise Exception("Se agoto el tiempo de espera")



def uploadToS3(filename, data):
    s3 = boto3.resource('s3', region_name="us-west-1")
    s3.Bucket(s3BucketName).put_object(Body= data, Key= filename)

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

try:
  message = "Submiteando el escaneo al sitio de UrlScan "+ url
  resultScanUrl = submitScan(url)["api"]
except:
  log("error", message)
  raise

try:
  message = "Obteniendo resultado de UrlScan"
  log("ok",message)
  content = getScanUrl(resultScanUrl)
except:
  print( message)
  raise

try:
  message = "Subiendo archivo a S3"
  log("ok",message)
  uploadToS3("resultado.json", content)
except:
  log("error", message)
  raise
 