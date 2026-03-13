# Backend-PYTHON Application server
## Launch EC2 "t2.micro" Instance and In Sg, Open port "8000" for Python Application 
# Step:1 ==> Install the Required packages
####  Install GIT
```
sudo yum install git -y
``` 

## Install python
```
sudo yum update -y
sudo yum install git -y
sudo yum install python3 -y
sudo yum install python3-pip -y
```
# Step:2 ==> Create one Application User
#### Create Application user to run the Applicatrion
```
sudo groupadd -r jira
sudo useradd -r -g jira -s /sbin/nologin jira
```


# Step:3 ==> Get the Code
### We keep application in one standard location. This is a usual practice that runs in the organization. Lets setup an app directory.

#### Create central Application Directory for Application
```
sudo mkdir -p /app
```

#### our code is in Git Repo 
```
cd /app
sudo git clone https://github.com/digistackops-JIRA-project/Digistack-JIRA-App.git
cd Digistack-JIRA-App
```
Switch branch

```
git checkout V1-Login-Module
```

# Step:4 ==> DB migration
## Setup your Application Database by executing "init.sql" script from Application-server

Step:1 ==> install "MYSQL-Client" for communicate with MYSQL Database
```
sudo yum update -y
sudo wget https://dev.mysql.com/get/mysql80-community-release-el9-1.noarch.rpm
sudo dnf install mysql80-community-release-el9-1.noarch.rpm -y
sudo rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2023
sudo dnf install mysql-community-client -y
```
Step:2 ==> Execute your "init.sql" script for your Application DB setup
Db setup Setup
```
cd database
sudo chown -R $USER:$USER $(pwd)
```
```
mysql -h <DB-Prvate-IP> -udbadmin -pAdmin@123 < initdb.sql
```

## RUN the flyway Migration
#### Export DB Credentials as Environment Variables for DB Connection

Generate JWT_Secret
```
openssl rand -base64 64
```
Setup the Environment variables for Backend
```
sudo vim backend/.env
```
edit the file
```
# Copy this to .env and fill in real values — NEVER commit .env to Git
DB_HOST=<DB_Private_IP>
DB_PORT=3306
DB_USER=dbadmin
DB_PASSWORD=P@55Word
DB_NAME=admindb

SECRET_KEY=<JWT_Token_HERE>
ACCESS_TOKEN_EXPIRE_MINUTES=1440

APP_ENV=development
CORS_ORIGINS=http://<Public-Browser-IP>:5173

```

#### Run the flyway migration command
HERE we pass DB details in .env, flyway doesnt fetch those values from .env by default, so we need to Load the DB details
##### Load .env variables
```
export $(grep -v '^#' .env | xargs)
```
```
flyway -configFiles=flyway.conf migrate
```

# Step:5 ==> Download the Dependencies
#### Go to the Backen directory 
```
cd /app/Digistack-JIRA-App/backend
sudo chown -R ${USER}:${USER} /app/Digistack-JIRA-App
````
#### Install Dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```
#### Install the "gunicorn" for running HA
```
pip install gunicorn
```
#### Run the Test cases
```
pytest tests/ -v
```
#### Run the Test acses with coverage

it will create the folder "htmlcv" inside Report in html format is created 
```
pytest --cov=app --cov-report=html
```

#### To run these Backend Application up and Running we use Linux service
```
which gunicorn
sudo cp -r  ~/.local/bin/gunicorn /usr/local/bin/
```
#### Our application run with JIRA user so give proper permissions
```
sudo chown -R jira:jira /app/Digistack-JIRA-App/backend
```
create the "admin Backend" service
```
sudo vim /etc/systemd/system/adminbackend.service
```
```
[Unit]
Description=Gunicorn Flask App
After=network.target

[Service]
User=jira
Group=jira

# Application directory
WorkingDirectory=/app/Digistack-JIRA-App/backend

# Start Gunicorn
ExecStart=/usr/local/bin/gunicorn \
          --workers 3 \
          --bind 0.0.0.0:8000 \
          --timeout 120 \
          app:app

# Restart policy
Restart=always
RestartSec=5

# Security (recommended)
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```
Enable backend service
```
sudo systemctl daemon-reload
sudo systemctl enable adminbackend
sudo systemctl start adminbackend
sudo systemctl status adminbackend
```
