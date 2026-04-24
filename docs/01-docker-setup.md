# Part 1: Local Docker Setup & Testing

Before deploying to the cloud, it's best practice to build and run the Docker image locally to ensure it works correctly.

## Prerequisites
- Docker Desktop installed on your machine.
- A terminal configured to run docker commands.

## Step-by-Step Instructions

### 1. Build the Docker Image
Open your terminal, navigate to the `deploy` folder containing the `Dockerfile`, and run:
```bash
docker build -t python-practice-app .
```
This tells Docker to read the `Dockerfile` and package the Python app into an image named `python-practice-app`.

### 2. Run the Docker Container
Once the build is complete, you can start the application:
```bash
docker run -d -p 8000:8000 --name running-practice-app --env-file .env python-practice-app
```
**Explanation:**
- `-d`: Run in detached mode (background).
- `-p 8000:8000`: Map port 8000 of your local machine to port 8000 in the container.
- `--name running-practice-app`: Give the running container a friendly name.
- `--env-file .env`: Pass the environment variables from your local `.env` file into the container.

### 3. Verify it works
Open a web browser and go to:
[http://localhost:8000](http://localhost:8000)

You should see a message saying "Hello from Python inside Docker!" along with your custom environment variable loaded from the `.env` file.

### 4. Cleanup
To stop and remove the container:
```bash
docker stop running-practice-app
docker rm running-practice-app
```
