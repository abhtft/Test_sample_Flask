# Part 3: Deploy to Amazon EC2 Manually

This guide explains how to spin up a basic EC2 server and pull your Docker image from ECR to run it manually.

## Step 1: Give your EC2 instance access to ECR
Servers need permission to download images from your private registry.

1. Go to AWS Console -> **IAM** -> **Roles**.
2. Click **Create Role**.
3. Select **AWS service** and choose **EC2** as the use case. Click Next.
4. Search for and attach the policy: `AmazonEC2ContainerRegistryReadOnly`. Click Next.
5. Name the role `EC2-ECR-Read-Role` and create it.

## Step 2: Launch an EC2 Instance
1. Go to AWS Console -> **EC2** -> **Launch Instances**.
2. Name it `docker-test-server`.
3. Choose **Amazon Linux 2023 AMI** (or Ubuntu).
4. Instance type: `t2.micro` (free tier eligible).
5. Key pair: Create a new key pair or select an existing one to SSH into the box.
6. Network settings: Ensure **Allow HTTP traffic from the internet** is checked (this opens port 80, but our app runs on 8000, so we will fix that).
7. Advanced Details -> **IAM instance profile**: Select `EC2-ECR-Read-Role` (from Step 1).
8. Click **Launch Instance**.

## Step 3: Open Port 8000
1. Once the instance is running, click on its *Security Group* in the EC2 dashboard.
2. Edit Inbound Rules -> Add Rule.
3. Type: Custom TCP, Port Range: `8000`, Source: `0.0.0.0/0`.
4. Save rules.

## Step 4: SSH into EC2 and Install Docker
1. Connect to your EC2 instance using SSH (or EC2 Instance Connect).
2. Update the OS and install docker:
```bash
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
```
3. Exit your SSH session and reconnect so the group changes take effect.

## Step 5: Pull Image and Run
Since we attached the IAM role, we can login to ECR without credentials!

1. Login to ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```
*(Replace your region and AWS Account ID appropriately)*

2. Pull the image:
```bash
docker pull YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/sample-python-app:latest
```

3. Run the container:
```bash
docker run -d -p 8000:8000 --name my-app YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/sample-python-app:latest
```

## Step 6: Verify
Find your EC2 instance's **Public IPv4 address** in the AWS console.
Go to `http://YOUR_EC2_IP:8000` in your web browser. You should see the application running!
