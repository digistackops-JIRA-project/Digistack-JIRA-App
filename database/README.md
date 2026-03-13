# Step:1 ==> Database Setup
Create "t2.micro" EC2 Instance and open port "3306" for DB 

## Install MYSQL DB
```
sudo yum update -y
sudo wget https://dev.mysql.com/get/mysql80-community-release-el9-1.noarch.rpm
sudo dnf install mysql80-community-release-el9-1.noarch.rpm -y
sudo rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2023
sudo dnf install mysql-community-client -y
sudo dnf install mysql-community-server -y
sudo systemctl start mysqld
sudo systemctl enable mysqld
sudo systemctl status mysqld
```

## Setup MYSQL DB

#### Allow any Host connect to DB
```
sudo vi /etc/my.cnf
```
ADD these Under [mysqld]
```
bind-address = 0.0.0.0
```
Restart MYSQL DB
```
sudo systemctl restart mysqld
```
Get your temporary root Password
```
sudo grep 'temporary password' /var/log/mysqld.log
```
Setup your root Password
```
sudo mysql_secure_installation
```
Login to your MYSQL
```
mysql -u root -p
```
Test it is working or Not
```
SELECT VERSION();
```
### Create one Databse Admin User for our DB 
These user can login to DB to do Tasks and used 
```
CREATE USER '<user-name>'@'Host-IP' IDENTIFIED BY 'Password-HERE';
GRANT ALL PRIVILEGES ON <DB-Name>.* TO '<user-name>'@'Host-IP';
FLUSH PRIVILEGES;
```

```
CREATE USER 'dbadmin'@'%' IDENTIFIED BY 'Admin@123';
GRANT ALL PRIVILEGES ON *.* TO 'dbadmin'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```


# Step:2 ==> Database Migration 

## Get the DB Code
```
mkdir /app
git clone https://github.com/digistackops-JIRA-project/Digistack-JIRA-App.git
cd Digistack-JIRA-App
```
### switch to PROD Branch

```
sudo git checkout 02-Local-setup-Prod
```
Go to that DB Directory
```
cd  /app/Digistack-JIRA-App/database
```

### Create the Database 'admindb' using init.sql
Step:1 ==> install "MYSQL-Client" for communicate with MYSQL Database
```
sudo yum update -y
sudo wget https://dev.mysql.com/get/mysql80-community-release-el9-1.noarch.rpm
sudo dnf install mysql80-community-release-el9-1.noarch.rpm -y
sudo rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2023
sudo dnf install mysql-community-client -y
```
Step:2 ==> Execute your "init.sql" script for your Application DB setup

```
mysql -h <DB-Prvate-IP> -udbadmin -pAdmin@123 < initdb.sql
```

## RUN the flyway Migration
Create EC2 Instance for Run the Migrations {These is DB team Task}
#### Install flyway Tool
```
cd /app
```

get latest version
```
LATEST=$(curl -s https://api.github.com/repos/flyway/flyway/releases/latest | grep tag_name | cut -d '"' -f4)
```
Remove the flyway- prefix:
```
VERSION=${LATEST#flyway-}
```
Download the flyway
```
sudo wget https://github.com/flyway/flyway/releases/download/$LATEST/flyway-commandline-$VERSION-linux-x64.tar.gz
```
Extract the flyway
```
sudo tar -xzf flyway-commandline-$VERSION-linux-x64.tar.gz
```
move to /opt
```
sudo mv flyway-$VERSION /opt/flyway
```
Add to path
```
sudo ln -sf /opt/flyway/flyway /usr/local/bin/flyway
```
Check flyway version
```
flyway -v
```
#### Export DB Credentials as Environment Variables for DB Connection

```
export DB_HOST="DB_Private_IP"
export DB_PORT=3306
export DB_NAME="admindb"
export DB_USER="appuser"
export DB_PASSWORD="P@55Word"
```

#### Run the flyway migration command
```
sudo -E flyway -configFiles=flyway.conf migrate
```


# Step:3 ==> Check data saved in DB or Not

Login to your MYSQL
```
mysql -u root -p
```
Show the List of DBs
```
SHOW DATABASES;
```
Switch to your "user" DB
```
USE admindb;
```

See the Tables under "user" DB
```
SHOW TABLES;
```
To see Data stored under "user" DB or Not
```
SELECT * FROM admins;
SELECT * FROM teams;
SELECT * FROM managers;
SELECT * FROM employees;
```
