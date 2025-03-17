# Use the official Python base image from Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your application will run on
EXPOSE 7860

# Specify the command to run your app (replace with your actual command)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]