# Part 2: GitHub Actions & Amazon ECR (Elastic Container Registry)

This part focuses on automating the creation of your Docker image and storing it securely in AWS ECR whenever you push code to GitHub.

## Prerequisites
- An AWS Account.
- This repository pushed to your personal GitHub account.

---

## Step 1: Create an IAM User in AWS
GitHub Actions needs permission to upload images to your AWS account.

1. Go to the AWS Console -> **IAM** -> **Users**.
2. Click **Create user** and name it `github-actions-user`. Click Next.
3. Select **Attach policies directly**.
4. Search for and check `AmazonEC2ContainerRegistryFullAccess`.
5. Complete the creation process.
6. Click on the newly created user, go to the **Security credentials** tab.
7. Under "Access keys", click **Create access key**.
8. Choose **Third-party service**, check the confirmation box, and generate the keys.
9. **IMPORTANT**: Keep the `Access key ID` and `Secret access key` handy! You will need them for GitHub.

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 740994137443.dkr.ecr.us-east-1.amazonaws.com

aws ecr create-repository --repository-name sample-python-app --region eu-north-1

aws ecr describe-repositories --repository-names sample-python-app --region eu-north-1

docker tag python-practice-app:latest 740994137443.dkr.ecr.eu-north-1.amazonaws.com/python-practice-app:latest

docker push 740994137443.dkr.ecr.eu-north-1.amazonaws.com/python-practice-app:latest

aws ecr describe-repositories \
    --repository-names sample-python-app \
    --region us-east-1

*(Note: In an enterprise environment, use IAM Roles withl. OIDC instead of long-lived access keys for better security, but access keys are fine for learning).*

---

## Step 2: Create an ECR Repository
This is where AWS will store the Built Docker images.

1. Go to AWS Console -> **Elastic Container Registry**.
2. Click **Create repository**.
3. Set Visibility settings to **Private**.
4. Repository name: `sample-python-app`.
5. Click **Create repository**.

---

## Step 3: Configure GitHub Secrets
We need to give your GitHub repository the AWS keys securely.

1. Go to your repository on GitHub.
2. Click **Settings** -> **Secrets and variables** -> **Actions**.
3. Click **New repository secret**.
4. Create `AWS_ACCESS_KEY_ID` and paste the Access key ID from Step 1.
5. Create `AWS_SECRET_ACCESS_KEY` and paste the Secret access key from Step 1.

---

## Step 4: Review and Push the Action
1. Open the file `.github/workflows/deploy-ecr.yml` in your code editor.
2. Ensure the `AWS_REGION` matches your AWS region (e.g., `us-east-1`).
3. Ensure `ECR_REPOSITORY` matches the name created in Step 2 (`sample-python-app`).
4. Commit and push your code to GitHub.

```bash
git add .
git commit -m "Add GitHub action for ECR"
git push origin main
```

## Step 5: Verify the Deployment
1. Go to your GitHub repository -> **Actions** tab. You should see a workflow running.
2. Once it completes successfully, go back to the AWS Console -> **ECR** -> click your repository `sample-python-app`.
3. You should see a new Image tagged as `latest` and a git commit hash.
