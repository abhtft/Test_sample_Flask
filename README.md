# Server Deployment Practice

This repository contains a simple Python Flask application designed for learning how to deploy applications using Docker, GitHub Actions, and AWS (ECR, EC2, ECS).

## Directory Structure

```text
.
├── app.py                      # Main Python Application code
├── requirements.txt            # Python dependencies
├── .env                        # Local environment variables
├── Dockerfile                  # Docker image instructions
├── .dockerignore               # Patterns to ignore when building the Docker image
├── .github/
│   └── workflows/
│       └── deploy-ecr.yml      # GitHub Actions workflow for building & pushing to ECR
└── docs/                       # Step-by-step deployment tutorials
```

## How to use this project?

Please follow the guides located in the `docs` directory sequentially:

1. [Local Docker Setup](docs/01-docker-setup.md)
2. [Setting up GitHub Actions & Amazon ECR](docs/02-github-actions-ecr.md)
3. [Manual Deployment to Amazon EC2](docs/03-deploy-to-ec2.md)
4. [Deployment to Amazon ECS (Fargate)](docs/04-deploy-to-ecs.md)
5. [Continuous Deployment (CI/CD) to AWS](docs/05-cicd-deployment.md)
