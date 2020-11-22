# urlscan-api-wrapper


Instructions for containerized usage:

git clone https://github.com/gustavoortega/urlscan-api-wrapper.git

cd urlscan-api-wrapper/

docker build -t local:urlscan .

docker run --rm -it local:urlscan --url "https://www.example.com/" --urlscankey "apikey"  --s3bucketname "bucketName" --visibility "choosefrom:public/private/unlisted"


Instructions for usage on local machine:

git clone https://github.com/gustavoortega/urlscan-api-wrapper.git

cd urlscan-api-wrapper/

pip install -r requirements.txt

python3 ./urlscan-api-wrapper.py --url "https://www.example.com/" --urlscankey "apikey"  --s3bucketname "bucketName" --visibility "choosefrom:public/private/unlisted"