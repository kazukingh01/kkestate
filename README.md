# kkestate
Collecting real estate data for using it parsonaly

# Server Basic setup

### Vim

```bash
sudo apt-get update
sudo apt-get install -y vim
```

### SSH

Change port no.

```bash
sudo vi /etc/ssh/sshd_config
```

```ssh
Port XXXXX
Protocol 2
PermitRootLogin no
PasswordAuthentication no
ChallengeResponseAuthentication no
PermitEmptyPasswords no
SyslogFacility AUTHPRIV
LogLevel VERBOSE
```

```bash
sudo /etc/init.d/ssh restart
```

### Firewall

if there is no module, install it.

```bash
sudo apt update
sudo apt install -y ufw
```

```bash
sudo ufw enable
sudo ufw logging on
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow XXXXX # set ssh port
sudo ufw allow from 172.128.128.0/24 to any port YYYYY # set db port if you need
sudo ufw reload
sudo ufw status
```

### Time zone

```bash
sudo apt update
sudo apt install -y tzdata
sudo tzselect # select Asis time zone
echo "TZ='Asia/Tokyo'; export TZ" >> ~/.bashrc
source ~/.bashrc
date
```

### Docker ( If you need )

see: https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script

```bash
sudo apt install curl
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Set NO automatic upgrede

```bash
sudo vi /etc/apt/apt.conf.d/20auto-upgrades
```

```
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Unattended-Upgrade "0";
```

### Other

```bash
sudo mkdir /home/share
sudo chown -R ubuntu:ubuntu /home/share/
```

### Reboot

```bash
sudo reboot
```

# Estate programs

### Python

```bash
sudo apt-get update
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev git iputils-ping net-tools cron rsyslog
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
cd ~/.pyenv/plugins/python-build
sudo bash ./install.sh
INSTALL_PYTHON_VERSION="3.11.2"
/usr/local/bin/python-build -v ${INSTALL_PYTHON_VERSION} ~/local/python-${INSTALL_PYTHON_VERSION}
echo 'export PATH="$HOME/local/python-'${INSTALL_PYTHON_VERSION}'/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
cd ~
python -m venv ~/venv
source ~/venv/bin/activate
```

### Git clone

```bash
cd ~
git clone https://github.com/kazukingh01/kkestate.git
cd ~/kkestate/
pip install -e .
```

# Database

### Postgres Container

```bash
cd ~/kkestate
sudo docker image build -t postgres:16.1.jp .
sudo mkdir -p /var/local/postgresql/data
sudo docker run --name psgre \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_INITDB_ARGS="--encoding=UTF8 --locale=ja_JP.utf8" \
    -e TZ=Asia/Tokyo \
    -v /var/local/postgresql/data:/var/lib/postgresql/data \
    -v /home/share:/home/share \
    --shm-size=4g \
    -d postgres:16.1.jp
```

### Recreate Database & Tables

```bash
sudo docker exec --user=postgres psgre /usr/lib/postgresql/16/bin/dropdb estate
sudo docker exec --user=postgres psgre /usr/lib/postgresql/16/bin/createdb --encoding=UTF8 --locale=ja_JP.utf8 --template=template0 --port 5432 estate
cp ~/kkestate/main/database/schema.sql /home/share/
sudo docker exec --user=postgres psgre psql -U postgres -d estate -f /home/share/schema.sql 
```

### Tips

##### Dump Schema

```bash
sudo docker exec --user=postgres psgre pg_dump -U postgres -d estate -s > ./schema.sql
```

##### Backup database

```bash
sudo docker exec --user=postgres psgre pg_dump -U postgres -Fc estate > ./db_`date "+%Y%m%d"`.dump
```

##### Restore database

```bash
sudo docker exec --user=postgres psgre pg_restore -U postgres -a -d estate -Fc /home/share/db_`date "+%Y%m%d"`.dump
```

# Run

### Set config

```bash
vi ~/kkestate/kkestate/config/psgre.py
```

### Cron

```bash
cat ~/kkestate/main/database/crontab | sudo tee -a /etc/crontab
sudo /etc/init.d/cron restart
```

### Test

```bash
cd ~/kkestate/main/database/
bash monitor.sh 1
```