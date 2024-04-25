# dnd_shop
 

https://habr.com/ru/articles/755036/
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

sudo snap install --classic certbot
	
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo apt install docker-compose
sudo apt install nginx

sudo certbot certonly --nginx
service nginx stop
systemctl stop nginx

docker-compose -f docker-compose.prod.yml up  
docker exec -it DjangoAPI python manage.py createsuperuser