# Environment Variables in ECS: Two Methods

There are two main ways to pass environment variables to your ECS containers. Both are valid and have different use cases.

---

## Method 1: Docker Build Method (ARG → ENV)

### How It Works
Environment variables are embedded into the Docker image during the build process.

### Dockerfile Changes
```dockerfile
FROM python:3.9-slim

# Build-time argument
ARG MY_CUSTOM_VAR

# Runtime environment variable (with default fallback)
ENV MY_CUSTOM_VAR=${MY_CUSTOM_VAR:-Default Variable Value}

WORKDIR /app
# ... rest of Dockerfile
```

### GitHub Actions Changes
```yaml
- name: Build, tag, and push image to Amazon ECR
  env:
    MY_CUSTOM_VAR: ${{ secrets.MY_CUSTOM_VAR }}
  run: |
    docker build --build-arg MY_CUSTOM_VAR=$MY_CUSTOM_VAR -t app .
```

### Pros
- ✅ Environment variables are baked into the image
- ✅ No changes needed to task definition
- ✅ Works the same everywhere (local, ECS, other platforms)
- ✅ Good for configuration that doesn't change per environment

### Cons
- ❌ Requires rebuilding image to change variables
- ❌ Variables are visible in image layers (security concern for secrets)
- ❌ Same image can't be used across environments with different configs
- ❌ Not ideal for secrets (they're in the image)

### When to Use
- Configuration that's the same across deployments
- Non-sensitive environment variables
- When you want the same config in all environments

---

## Method 2: Task Definition Method

### How It Works
Environment variables are defined in the ECS task definition and injected at runtime.

### Task Definition Changes
```json
{
  "containerDefinitions": [
    {
      "name": "python-app-container-fargate",
      "environment": [
        {
          "name": "MY_CUSTOM_VAR",
          "value": "Default Variable Value"
        }
      ]
    }
  ]
}
```

### GitHub Actions Changes (Dynamic Update)
```yaml
- name: Update task definition with environment variables
  run: |
    sed -i "s/Default Variable Value/${{ secrets.MY_CUSTOM_VAR }}/g" console-task-definition.json

- name: Deploy to ECS
  uses: aws-actions/amazon-ecs-deploy-task-definition@v1
  with:
    task-definition: console-task-definition.json
    # ...
```

### Pros
- ✅ Same image can be used across different environments
- ✅ No image rebuild needed to change variables
- ✅ Variables are not in the image (better for secrets)
- ✅ Environment-specific configuration is easy
- ✅ Can use AWS Secrets Manager for sensitive data

### Cons
- ❌ Requires task definition changes
- ❌ Different behavior in local vs ECS (unless you replicate env vars)
- ❌ More complex deployment process

### When to Use
- Environment-specific configuration
- Secrets and sensitive data
- When you need different configs per deployment
- When you want to use AWS Secrets Manager

---

## Comparison Summary

| Aspect | Docker Build Method | Task Definition Method |
|--------|-------------------|----------------------|
| Image rebuild needed | Yes | No |
| Variables in image | Yes | No |
| Cross-environment use | Difficult | Easy |
| Secret handling | Poor | Good |
| Local testing | Same as production | Different setup |
| Complexity | Simple | More complex |

---

## Current Implementation

Your setup now has **both methods implemented**:

### Method 1: Docker Build
- **File**: `.github/workflows/deploy-ecr.yml`
- **Dockerfile**: Updated with ARG and ENV
- **Workflow**: Passes `MY_CUSTOM_VAR` as build argument

### Method 2: Task Definition
- **File**: `.github/workflows/deploy-ecr-taskdef-method.yml`
- **Task Definition**: Has environment variable section
- **Workflow**: Updates task definition before deployment

---

## Which Method Should You Use?

**For your learning project**: Task Definition Method is better because:
- You can change variables without rebuilding
- It's more realistic for production scenarios
- Better for handling secrets

**For production**: Usually use a combination:
- Build-time: Non-sensitive config (debug flags, feature toggles)
- Runtime: Environment-specific config (API URLs, secrets)

---

## Testing Both Methods

To test Method 1 (Docker Build):
1. Push code to trigger `.github/workflows/deploy-ecr.yml`
2. The variable will be baked into the image
3. Check your app to see the value

To test Method 2 (Task Definition):
1. Rename `deploy-ecr-taskdef-method.yml` to `deploy-ecr.yml`
2. Push code
3. The variable will be injected at runtime
4. Check your app to see the value

Both will work, but they achieve the same result through different approaches!
