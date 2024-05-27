# mysql/Dockerfile
FROM mysql:latest

# Set the working directory in the container
# WORKDIR /docker-entrypoint-initdb.d

# COPY ./mysql/mysql_init.sql .
COPY ./mysql/mysql_init.sql /docker-entrypoint-initdb.d/
