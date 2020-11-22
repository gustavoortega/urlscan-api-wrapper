# urlscan-api-wrapper



<h1>Instructions for containerized usage</h1>

git clone https://github.com/gustavoortega/urlscan-api-wrapper.git

cd urlscan-api-wrapper/

docker build -t local:urlscan .

docker run --rm -it local:urlscan --url "https://www.example.com/" --urlscankey "apikey"  --s3bucketname "bucketName" --visibility "choosefrom:public/private/unlisted"


<h1>Instructions for usage on local machine</h1>

git clone https://github.com/gustavoortega/urlscan-api-wrapper.git

cd urlscan-api-wrapper/

pip install -r ./requirements.txt

python3 ./urlscan-api-wrapper.py --url "https://www.example.com/" --urlscankey "apikey"  --s3bucketname "bucketName" --visibility "choosefrom:public/private/unlisted"
