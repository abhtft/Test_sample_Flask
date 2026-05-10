# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Build-time argument for environment variable
ARG MY_CUSTOM_VAR

# Set environment variable from build argument (with default fallback)
ENV MY_CUSTOM_VAR=${MY_CUSTOM_VAR:-Default Variable Value}

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY app.py ./

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "app.py"]
