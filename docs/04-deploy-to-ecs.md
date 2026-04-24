# Part 4: Deploy to Amazon ECS (Fargate)

Deploying a single EC2 instance is great, but manually managing servers doesn't scale well. ECS (Elastic Container Service) with Fargate is a serverless compute engine for containers.

## Step 1: Create an ECS Cluster
A cluster gives your tasks a place to run.

1. Go to AWS Console -> **Elastic Container Service**.
2. Click **Create Cluster**.
3. Cluster name: `python-app-cluster`.
4. Infrastructure: Ensure **AWS Fargate** is selected.
5. Click **Create**.

## Step 2: Create a Task Definition
A task definition tells ECS how to run your Docker container.

1. On the left menu, click **Task Definitions** -> **Create new task definition**.
2. Name it: `python-app-task`.
3. Launch type: **AWS Fargate**.
4. Set OS, CPU, and Memory to the smallest available (0.25 vCPU, .5 GB) to save costs.
5. In the **Container - 1** section:
   - Name: `python-app-container`
   - Image URI: `YOUR_AWS_ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/sample-python-app:latest` *(Get this from ECR)*
   - Container port: `8000`, Protocol: `TCP`
6. Scroll down and click **Create**.

## Step 3: Run the Service
A Service ensures your task stays running and can be exposed to the internet.

1. Go back to your Cluster (`python-app-cluster`).
2. Tab: **Services** -> Click **Create**.
3. Compute options: **Launch type** -> **Fargate**.
4. Deployment configuration:
   - Task definition: `python-app-task` (latest revision).
   - Service name: `python-app-service`.
   - Desired tasks: `1`.
5. Networking:
   - Security group: Ensure you create a new security group or modify an existing one to allow inbound traffic on port `8000` from `0.0.0.0/0`.
   - Public IP: **Turned ON** (Enabled).
6. Click **Create**.

## Step 4: Access the Application!
1. Once the service is created, go to the **Tasks** tab in your cluster.
2. Wait for the task status to say `RUNNING`.
3. Click on the task ID.
4. Look under the **Configuration** section for the **Public IP**.
5. Copy the Public IP and visit `http://YOUR_PUBLIC_IP:8000` in your browser.

🎉 Congratulations! You deployed a Docker container via ECS Fargate.
