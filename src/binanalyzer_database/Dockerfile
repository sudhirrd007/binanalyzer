# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# copy the content of the local src directory to the working directory
COPY ./binanalyzer_database/main/ ./main/
RUN ls -lt

# copy config files
COPY ./binanalyzer_database/config/ ./config/
RUN ls -lt

# copy the dependencies file to the working directory
COPY ./binanalyzer_database/requirements.txt .
RUN ls -lt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Add entrypoint.sh to the image
COPY ./binanalyzer_database/initialize_db.py .

# Add entrypoint.sh to the image
COPY ./binanalyzer_database/entrypoint.sh .

# Make entrypoint.sh executable
RUN chmod +x entrypoint.sh

# command to run on container start
ENTRYPOINT ["./entrypoint.sh"]