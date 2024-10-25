# Install python version

# pyenv install 3.10.9


# Set your python version

# pyenv global 3.10.9


# Create virual environment

# python -m venv venv


# Activate environment

# source venv/bin/activate


# Install Flask

# pip install flask

# pip install -r requirements.txt to install the file

# must install in backend
# - pip install Flask
# - pip install Flask_cors
# - Ctrl+Shift+P - select ocrrect interpreter

# pip install opentelemetry-api 
# opentelemetry-sdk 
# opentelemetry-exporter-otlp-proto-http 
# opentelemetry-instrumentation-flask 
# opentelemetry-instrumentation-requests

# pip install watchtower


# must install in frontend
# - npm install


# psql -Upostgres --host localhost
# export CONNECTION_URL="postgresql://postgres:password@127.0.0.1:5432/cruddur"
# sau
# export CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"

# postgresql://postgres:password@127.0.0.1:5432/cruddur

# gp env CONNECTION_URL="postgresql://postgres:password@127.0.0.1:5432/cruddur"
# gp env CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"

# export PROD_CONNECTION_URL="postgresql://cruddurroot:Wolverine47@cruddur-db-instance.c3c4wcm6wmvr.eu-north-1.rds.amazonaws.com:5432/cruddur"
# gp env PROD_CONNECTION_URL="postgresql://cruddurroot:Wolverine47@cruddur-db-instance.c3c4wcm6wmvr.eu-north-1.rds.amazonaws.com:5432/cruddur"

# pip install "psycopg[binary]"
# pip install "psycopg[pool]"

# pip install "psycopg2[binary]"

# ip address for gitpod: curl ifconfig.me -must add both as a rule in aws
# set the ip adress: GITPOD_IP=$(curl ifconfig.me)
# export it: export GITPOD_IP=$(curl ifconfig.me)
# return the ip adress: echo $GITPOD_IP