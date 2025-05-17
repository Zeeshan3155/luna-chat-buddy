# Use the official Python base image from Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install dependencies (e.g., Java for LanguageTool)
RUN apt-get update && apt-get install -y default-jre

# Install dependencies
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your application will run on
EXPOSE 7860
EXPOSE 8081

# Start LanguageTool server and your app simultaneously
CMD java -cp /app/app/language-tool/languagetool-server.jar org.languagetool.server.HTTPServer --port 8081 & \
    uvicorn app.main:app --host 0.0.0.0 --port 7860