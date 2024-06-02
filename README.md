# DnD_shop

## Github connection

Generate ssh key pairs on server using Linux commands:  `ssh-keygen -t ed25519`.

For convenience, rename the key files: 
```
mv ~/.ssh/id_ed25519 ~/.ssh/personal_key
mv ~/.ssh/id_ed25519.pub ~/.ssh/personal_key.pub
```

In order for ssh to automatically use the correct keys when working with remote repositories, some settings need to be made. Add the following lines to the `~/.ssh/config` file:

```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/personal_key
    IdentitiesOnly yes
```

In your [GitHub account settings](https://github.com/settings/keys), you need to specify a public ssh key:
1. Click “New SSH key”.
2. In the “Key” field insert the contents of the `personal_key.pub` file 
3. Click “Add SSH key”.

To identify the GitHub SSH client host, add keys to known_hosts (this allows you to verify the legitimacy of the remote host before establishing a secure SSH connection):  
```
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
```

Clone the repository code:
```
git clone git@github.com:Alangard/dnd_shop.git
```
If you don't have access to the [author's account](https://github.com/Alangard/), bend the repository with:
```
git clone https://github.com/Alangard/dnd_shop.git
```

## Accessing dockerhub
For regions where dockerhub has been discontinued, you should:

1. Create a docker settings file `daemon.json` in a directory:
```
/etc/docker/daemon.json
```
2. Configurate a proxy through timeweb resource:
```
{ "registry-mirrors" : [ "https://dockerhub.timeweb.cloud" ] }
```
3. Restart the docker configuration:
```
systemctl reload docker
```

## Installing packages 

To start the project correctly, install the packages using:
```
sudo apt update
sudo snap install --classic certbot
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo apt install docker-compose
sudo apt install nginx
```

## SSL certificate installation 
Using certbot and letsencrypt we install the certificate that will be used by nginx when switching to HTTPS ([certbot official documentation for Nginx on Ubuntu 20](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)):
```
sudo certbot certonly --nginx
```

After issuing the certificates, stop Nginx from running:
```
service nginx stop
systemctl stop nginx
```

## Install enviromental variables and start the project
In the `.env.dev` and `.env.prod` files, change the `ALLOWED_HOSTS`, `EMAIL_HOST_PASSWORD`, `EMAIL_HOST_USER` and `DOMAIN` values according to your project

Start the `prod server` can be started with:
```
docker-compose -f docker-compose.prod.yml up
```

Create superuser:
```
docker exec -it DjangoAPI python manage.py createsuperuser
```

Run the server in `dev mode` using:
```
docker-compose -f docker-compose.dev.yml up
``` 

Run tests:
```
docker exec -it DjangoAPI python manage.py test
```
