# Part 5: Continuous Deployment (CD) to AWS

Now that you have successfully built and pushed your Docker image via GitHub Actions (CI) and manually deployed to EC2 and ECS, it's time to automate the deployment process (CD). 

This guide covers automating deployments to Amazon ECS using GitHub Actions. Whenever a new image is pushed to ECR, the action will automatically update your ECS service to use the new image.

## Prerequisite: Download your Task Definition

To deploy securely via GitHub actions, you need your ECS Task Definition formatted as a JSON file in your repository.

1. Go to AWS Console -> **Elastic Container Service** -> **Task Definitions**.
2. Click on `python-app-task`.
3. In the top right, click **JSON**, copy the contents, and create a file in your repository named `task-definition.json` in the root directory.

## Option 1: Automated ECS Deployment (Recommended)

ECS makes CD very easy. We can use the official AWS Actions to update our task definition with the new image tag and deploy it to the cluster.

### Update your GitHub Actions Workflow

Open `.github/workflows/deploy-ecr.yml` and add the following steps to the bottom of the `build-and-push` job.
i
```yaml
    - name: Fill in the new image ID in the Amazon ECS task definition
      id: task-def
      uses: aws-actions/amazon-ecs-render-task-definition@v1
      with:
        task-definition: task-definition.json
        container-name: python-app-container
        image: ${{ steps.login-ecr.outputs.registry }}/sample-python-app:${{ github.sha }}

    - name: Deploy Amazon ECS task definition
      uses: aws-actions/amazon-ecs-deploy-task-definition@v1
      with:
        task-definition: ${{ steps.task-def.outputs.task-definition }}
        service: python-app-service
        cluster: python-app-cluster
        wait-for-service-stability: true
```

**How this works:**
1. **Render Task Definition**: It takes your base `task-definition.json` file, looks for the container named `python-app-container`, and inserts the exact ECR image tag we just built (`${{ github.sha }}`).
2. **Deploy Task Definition**: This registers the new task definition revision in AWS and updates the `python-app-service` in your `python-app-cluster` to use it. It optionally waits for the deployment to finish successfully (`wait-for-service-stability: true`).

## Option 2: Automated EC2 Deployment (SSH Method)

If you chose to use raw EC2 instead of ECS, automating CD involves SSHing into your server from the GitHub Action to run the pull and restart commands. 

1. **Add Secrets**: In your GitHub Repository -> Settings -> Secrets and variables -> Actions, add:
   - `EC2_HOST`: The Public IP or DNS of your EC2 instance.
   - `EC2_SSH_KEY`: The private key (`.pem` file contents) used for your EC2 instance.

2. **Add Workflow Steps**: Use `appleboy/ssh-action` at the end of your workflow to connect to the server and pull the latest image.

```yaml
    - name: Deploy to EC2
      uses: appleboy/ssh-action@v1.0.3
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: sample-python-app
        IMAGE_TAG: latest
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ec2-user
        key: ${{ secrets.EC2_SSH_KEY }}
        envs: ECR_REGISTRY,ECR_REPOSITORY,IMAGE_TAG
        script: |
          aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin $ECR_REGISTRY
          docker pull $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker stop my-app || true
          docker rm my-app || true
          docker run -d -p 8000:8000 --name my-app $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
```

> **Note:** The EC2 method requires your server IP to be static or you'll have to keep updating `EC2_HOST`. Using ECS (Option 1) is generally more robust inside cloud native architectures.

## Conclusion

By updating your GitHub Actions workflow, you've successfully created a full CI/CD pipeline! Now, every time you commit and push to the `main` branch, your code will automatically build, push to ECR, and deploy to your AWS environment!
