# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# copy the content of the local src directory to the working directory
COPY ./binanalyzer/main/ ./main/
RUN ls -lt

# copy the dependencies file to the working directory
COPY ./binanalyzer/requirements.txt .
RUN ls -lt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["uvicorn", "main.binanalyzer_service:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]