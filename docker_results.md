Welcome to Ubuntu 24.04.4 LTS (GNU/Linux 6.6.87.2-microsoft-standard-WSL2 x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Wed Apr 22 16:48:15 UTC 2026

  System load:  1.28                Processes:             60
  Usage of /:   0.6% of 1006.85GB   Users logged in:       0
  Memory usage: 3%                  IPv4 address for eth0: 192.168.226.160
  Swap usage:   0%

 * Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
   just raised the bar for easy, resilient and secure K8s cluster deployment.

   https://ubuntu.com/engage/secure-kubernetes-at-the-edge

This message is shown once a day. To disable it please create the
/home/abhishek/.hushlogin file.
abhishek@Abhishek:~$
  [Restored 23-04-2026 11:16:19]
abhishek@Abhishek:~$ ssh -i "Tast1.pem" ubuntu@ec2-56-228-7-153.eu-north-1.compute.amazonaws.com
The authenticity of host 'ec2-56-228-7-153.eu-north-1.compute.amazonaws.com (56.228.7.153)' can't be established.
ED25519 key fingerprint is SHA256:QPKANHnm3LDt9ZqY8Ujj1ZgAAaG04ekdwlglk5CF+CI.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'ec2-56-228-7-153.eu-north-1.compute.amazonaws.com' (ED25519) to the list of known hosts.
Welcome to Ubuntu 24.04.4 LTS (GNU/Linux 6.17.0-1007-aws x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Fri Apr 24 16:09:46 UTC 2026

  System load:  0.0               Temperature:           -273.1 C
  Usage of /:   36.5% of 6.71GB   Processes:             111
  Memory usage: 32%               Users logged in:       0
  Swap usage:   0%                IPv4 address for ens5: 172.31.29.177

 * Ubuntu Pro delivers the most comprehensive open source security and
   compliance features.

   https://ubuntu.com/aws/pro

Expanded Security Maintenance for Applications is not enabled.

22 updates can be applied immediately.
To see these additional updates run: apt list --upgradable

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


*** System restart required ***

The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.

ubuntu@ip-172-31-29-177:~$ ss -tulpn | grep 8000
ubuntu@ip-172-31-29-177:~$ sudo yum update -y
sudo: yum: command not found
ubuntu@ip-172-31-29-177:~$ sudo apt update -y
Hit:1 http://eu-north-1.ec2.archive.ubuntu.com/ubuntu noble InRelease
Get:2 http://eu-north-1.ec2.archive.ubuntu.com/ubuntu noble-updates InRelease [126 kB]
Hit:3 http://eu-north-1.ec2.archive.ubuntu.com/ubuntu noble-backports InRelease
Hit:4 http://security.ubuntu.com/ubuntu noble-security InRelease
Get:5 http://eu-north-1.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages [1919 kB]
Get:6 http://eu-north-1.ec2.archive.ubuntu.com/ubuntu noble-updates/universe amd64 Packages [1685 kB]
Fetched 3730 kB in 1s (3840 kB/s)
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
24 packages can be upgraded. Run 'apt list --upgradable' to see them.
ubuntu@ip-172-31-29-177:~$ sudo apt install docker -y
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
Package docker is not available, but is referred to by another package.
This may mean that the package is missing, has been obsoleted, or
is only available from another source
However the following packages replace it:
  wmdocker

E: Package 'docker' has no installation candidate
ubuntu@ip-172-31-29-177:~$ docker --version
Command 'docker' not found, but can be installed with:
sudo snap install docker         # version 28.4.0, or
sudo apt  install docker.io      # version 29.1.3-0ubuntu3~24.04.1
sudo apt  install podman-docker  # version 4.9.3+ds1-1ubuntu0.2
See 'snap info docker' for additional versions.
ubuntu@ip-172-31-29-177:~$
Broadcast message from root@ip-172-31-29-177 (Fri 2026-04-24 16:16:00 UTC):

The system will power off now!

Connection to ec2-56-228-7-153.eu-north-1.compute.amazonaws.com closed by remote host.
Connection to ec2-56-228-7-153.eu-north-1.compute.amazonaws.com closed.
abhishek@Abhishek:~$ ssh -i "Tast1.pem" ubuntu@ec2-51-20-81-60.eu-north-1.compute.amazonaws.com
The authenticity of host 'ec2-51-20-81-60.eu-north-1.compute.amazonaws.com (51.20.81.60)' can't be established.
ED25519 key fingerprint is SHA256:wnJvya/jOvCzMTcD2fZzFDYiVX7SyyDWPJSfKrdfBY4.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'ec2-51-20-81-60.eu-north-1.compute.amazonaws.com' (ED25519) to the list of known hosts.
Welcome to Ubuntu 24.04.4 LTS (GNU/Linux 6.17.0-1012-aws x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Fri Apr 24 16:17:16 UTC 2026

  System load:  0.1               Temperature:           -273.1 C
  Usage of /:   45.0% of 6.71GB   Processes:             117
  Memory usage: 27%               Users logged in:       0
  Swap usage:   0%                IPv4 address for ens5: 172.31.20.63

 * Ubuntu Pro delivers the most comprehensive open source security and
   compliance features.

   https://ubuntu.com/aws/pro

Expanded Security Maintenance for Applications is not enabled.

32 updates can be applied immediately.
10 of these updates are standard security updates.
To see these additional updates run: apt list --upgradable

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


Last login: Fri Apr 17 16:43:02 2026 from 49.205.251.74
ubuntu@ip-172-31-20-63:~$ docker --version
Command 'docker' not found, but can be installed with:
sudo snap install docker         # version 28.4.0, or
sudo apt  install docker.io      # version 29.1.3-0ubuntu3~24.04.1
sudo apt  install podman-docker  # version 4.9.3+ds1-1ubuntu0.2
See 'snap info docker' for additional versions.
ubuntu@ip-172-31-20-63:~$ git --version
git version 2.43.0

ubuntu@ip-172-31-20-63:~$
ubuntu@ip-172-31-20-63:~$ sudo snap install docker
docker 28.4.0 from Canonical✓ installed
ubuntu@ip-172-31-20-63:~$ docker --version
Docker version 28.4.0, build d8eb465
ubuntu@ip-172-31-20-63:~$ git --version
git version 2.43.0
ubuntu@ip-172-31-20-63:~$ aws ecr get-login-password --region us-north-1 | docker login --username AWS --password-stdin 740994137443.dkr.ecr.us-north-1.amazonaws.com

aws: [ERROR]: Could not connect to the endpoint URL: "https://api.ecr.us-north-1.amazonaws.com/"
Error: Cannot perform an interactive login from a non TTY device
ubuntu@ip-172-31-20-63:~$ aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 740994137443.dkr.ecr.eu-north-1.amazonaws.com

aws: [ERROR]: An error occurred (AccessDeniedException) when calling the GetAuthorizationToken operation: User: arn:aws:sts::740994137443:assumed-role/systemmanagerrole/i-07adba9ba71bac750 is not authorized to perform: ecr:GetAuthorizationToken on resource: * because no identity-based policy allows the ecr:GetAuthorizationToken action
Error: Cannot perform an interactive login from a non TTY device
ubuntu@ip-172-31-20-63:~$ aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 740994137443.dkr.ecr.eu-north-1.amazonaws.comaws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 740994137443.dkr.ecr.eu-north-1.amazonaws.comaws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 740994137443.dkr.ecr.eu-north-1.amazonaws.com
unknown flag: --region

Usage:  docker login [OPTIONS] [SERVER]

Run 'docker login --help' for more information
unknown flag: --region

Usage:  docker login [OPTIONS] [SERVER]

Run 'docker login --help' for more information
Error: Cannot perform an interactive login from a non TTY device
ubuntu@ip-172-31-20-63:~$ aws ecr get-login-password --region eu-north-1
eyJwYXlsb2FkIjoiR0d0QXdlRTFPMy81c1FqRzZXNkU4LzJDdEpTdk1UNE9oblhFUElQelMxa2dXczRFQ2NUTUZicFRNZVJrTXlGdCtXYS8xQjlZZ2dQcjJXTSs4V2ROcmxuN2tZMkpYc0VtblJRbjdwa2VhaFNqQmhCbEZKWjBrOE9HYlVhWldCM3Z2anl0RVFsaW1NVEdta2o4WC9JVzdibE8yRzhod3lXNzlKVHVGYXNHbjZHTUNiT2NXVkFyZ0xzbmxlYktUcWFUVTJxVnR6VjFGaFg4aGpYMjBhWXNYalVCMmZDcHJibVRrL0J3V29UUjdST0JPY0l2WjY1RFczb2xhczVTNW9oTWVRdTRjUSs2V1ZxZURSNkxJOHpmMStmQiswQlVRN0ZFZVZwWmo2NjZFcXllOGFFQ2ZrT2p3ZUVmMGYzd2RPakZxd3hRTHl4YUZMUk0xYzU5REFNMFdlZ3BwNEZtMTBkajhkQ0RJNUp5aFkzTXQ5Q2JwbFpGV29VaUNrcjlZWDJ4cUV2cEpyQlNXQ0NwNXRNdDc0b0VMa1R3RmxySzhZTWI5cytIV1BxZjNXRm9VSW1pYjlPTUp6WFFETGMvRzc2RE5EdVJsM05pMzFxZU84UzByMjRVWjQ5UWQ1Tm5aV1NLWGhvQW0yeXd0SXFzMzg0REdTSzVPaVZmY1ZRUUN0TUQrbVM5R0lnMkE5Q01KSjNrZWp5YmxKb05jWmNDT0pmMm95cEYrbmpBZG9NUDNUUjhSWjU1UWRkMWxaZ0VZUlNrM3JKSmpMa0R2cnZSUWVOcjhHczduUFBpOVFMQm1MKzVTT2ZTS0pNTU5ETFo1cVBib05ZZjQ5d3RhVnFTUCtQQzhuZEwrS21xMjRBckRYci9nNlI3YlBnajBHb3h3NlhubHRYREt6MVN3MjhweG4zV3lTbEh3T2FTb3RUaDhuZ3VIaFgrWnQ4RXJ5NFEvZzhoLzRReHN1MGpsSS9LUytGajBWaE50TWcxdkhDTFNLOFVFRVVQRWVwRDUxUE9mSm4wYnowNlhoSnBUeGlHZDFxZ2FGNUtFaE1MQ3Z6dm41aXMvS2JHdFcxOFhjVHNSdzhocEpKMzB1L3RtRTBmYXh4cFQzZGxkVzNXY1htSW1zdi9FWUlRTUdyTDRhUHJSeWtQNFBjME1lRXh4QnNxR0kwUWI2UmZITWJDaE9ZMlJSaWFZSGIwRzdiblpxVDdpNFIrSkVUZHg3VER5RERzNHRiWS9UQUdRZVBXb21xcitJMTAwYWVQc0NwK21HMndYN1A0SDlzRnMyN28rUlNtMjl5WU1YWnRiK2lqck9wRVRMRkRsdFA1L2ZFaG80QW0wQ0VwRUgyNlFiRmVTeTRFcjYwZkt1bVVFekZZSWZOVTl4eXMzRE9qQU9GME5xdTdlTG5uaVppajlKajJjZFFMSDFLZUFJOHFjcVF2N29BcmNpRlJhdkh2VGx1QlMzRlVOSllFZVh5aHZKYUd2RkVoMjdrSGhLV3NENGxhclAyUVFBY0MxbWgxTTNiemdTU09KYlNFZzg2VStxWHg0QkdkdmdYa3VYZUpOSHhmbkw3cHh5ZDd2Tms2ZC8wZ3VpMmx6c2dwcU85U1hBUmVVNW1pNHBPTXhQWHVHWWlIcVRWV2VuMnlZa0htOVJOWVlCT2g1WXkyRGtEZzFzaWJJazBtcGlwYllhMkxTWEptRksxc2F0UFdRR2wrNFZwWGpqWkc3cUhSM0dIOWEzZldCaXJTaXljQmxaMHJ2V0lMR0tVdjlybWgrT0RqdHdkWkY1eEx6RzBJNTdTblhMMnYybWJjeHk2OEl3V0QrdCtXdjhvVTNZamVaNnRXb3RGVHRuT3BTZHhLVDdja292alZEcFRnZWdVNW5KMlN4TFBFTHR2SllqSGpNVGFwbVlIdm1NU1FHNDJheE5idTBxbkZiaXhOMHZJeUFYZFQ5bDFzUll3Qzg3elAvYnBQcEJkYVhMUklTYTRQbW9SeGRnUjRoOXJlc1l2YnBtYVFUdnZsTVpHUFI0bjZFMVhpQ0VwS2hxOEZmZlpQSnR0ZnRrQ1hiZFRvaFJNdnJWUGhJaHpnM0lnQ0hxdlZyM283MjNDZ0drbGVDbExwM2JyQmk4dFkzb3pnV2k0Y2lWV2lZMHdJL3UzaWp1WCtveUgwYXJDMm1qZVdNekZBaDgzbjl1SUl0WnVBditqQmRXenZib1ErNHNUSEVhZkQzK1hGb0lWc0RMZW1iRmpadTMwY21wL3oyL1p6a0dFQlZwdkUzUXhPQUF4MGtGejUyUWJwNDlWSnA4VlphellYczc5Z1lXcW9mL0I2NHZyY1NTb1l3K052RlJoWEpWMHBQNTVGQUhidlUveTlBMlZtdzN3Y3huUlZkNjJiUzJUUC9DT1NTL1YxVFlXNE9ad0kxQ3RnRmVBd0F4Z0RvODJmMFhvVzZ4MG5GSUVVTFBnWEFiaGVxMWtJSGF6RXR3ZUhNMXJFRGREaHZNKys1RnRJSm95OHdPbFUrZXREL3pxU0NZZEhUL2NRS3FtcTVCbGJ3QWU1NVA5SzArNmkiLCJkYXRha2V5IjoiQVFJQkFIaGZyRlEyYUlJd0Y1VmM3OVJIRVBHbmNVV3VyMi9Kek04dC9aem9FdFJyQWdHbDZpZVZZSjhwTFd3bUhxTnE2L1I3QUFBQWZqQjhCZ2txaGtpRzl3MEJCd2FnYnpCdEFnRUFNR2dHQ1NxR1NJYjNEUUVIQVRBZUJnbGdoa2dCWlFNRUFTNHdFUVFNMkdBSkxZWUlwa1huNzVXSUFnRVFnRHRnZnVBQ2tWbFhQanh1ZzRMYmZBcVkyNERkSGovdzBocTY5REg1cS84SUx4eHBoZFlKZ0QxbWVmV1lXWnBuNWtyczRyVS9hd05oMHJMT1Z3PT0iLCJ2ZXJzaW9uIjoiMiIsInR5cGUiOiJEQVRBX0tFWSIsImV4cGlyYXRpb24iOjE3NzcwOTMxOTR9
ubuntu@ip-172-31-20-63:~$ aws ecr get-login-password --region eu-north-1 \
| docker login --username AWS --password-stdin 740994137443.dkr.ecr.eu-north-1.amazonaws.com

WARNING! Your credentials are stored unencrypted in '/home/ubuntu/snap/docker/3377/.docker/config.json'.
Configure a credential helper to remove this warning. See
https://docs.docker.com/go/credential-store/

Login Succeeded
ubuntu@ip-172-31-20-63:~$ docker pull 740994137443.dkr.ecr.eu-north-1.amazonaws.com/sample-python-app:latest
permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Post "http://%2Fvar%2Frun%2Fdocker.sock/v1.51/images/create?fromImage=740994137443.dkr.ecr.eu-north-1.amazonaws.com%2Fsample-python-app&tag=latest": dial unix /var/run/docker.sock: connect: permission denied
ubuntu@ip-172-31-20-63:~$ sudo docker pull 740994137443.dkr.ecr.eu-north-1.amazonaws.com/sample-python-app:latest
Error response from daemon: Head "https://740994137443.dkr.ecr.eu-north-1.amazonaws.com/v2/sample-python-app/manifests/latest": no basic auth credentials
ubuntu@ip-172-31-20-63:~$ aws ecr get-login-password --region eu-north-1 \
| sudo docker login --username AWS --password-stdin 740994137443.dkr.ecr.eu-north-1.amazonaws.com

WARNING! Your credentials are stored unencrypted in '/root/snap/docker/3377/.docker/config.json'.
Configure a credential helper to remove this warning. See
https://docs.docker.com/go/credential-store/

Login Succeeded
ubuntu@ip-172-31-20-63:~$ sudo docker pull 740994137443.dkr.ecr.eu-north-1.amazonaws.com/sample-python-app:latest
latest: Pulling from sample-python-app
38513bd72563: Pull complete
b3ec39b36ae8: Pull complete
fc7443084902: Pull complete
ea56f685404a: Pull complete
44a4001d019d: Pull complete
4dae033a58cc: Pull complete
385b7174d8e7: Pull complete
975e7e7ef71a: Pull complete
Digest: sha256:a06e1f100bed0c78d1a47b37d9cd94aaea8a26c076cbdec8c1130e3c1d7947a0
Status: Downloaded newer image for 740994137443.dkr.ecr.eu-north-1.amazonaws.com/sample-python-app:latest
740994137443.dkr.ecr.eu-north-1.amazonaws.com/sample-python-app:latest
ubuntu@ip-172-31-20-63:~$ docker run -d -p 8000:8000 --name my-app 740994137443.dkr.ecr.eu-north-1.amazonaws.com/sample-python-app:latest
docker: permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Head "http://%2Fvar%2Frun%2Fdocker.sock/_ping": dial unix /var/run/docker.sock: connect: permission denied

Run 'docker run --help' for more information
ubuntu@ip-172-31-20-63:~$ sudo docker run -d -p 8000:8000 --name my-app 740994137443.dkr.ecr.eu-north-1.amazonaws.com/sample-python-app:latest
99b8ee79095a9855d543079a67fdbf10b173371056cbe4419a04afc2ab0dc4e9
ubuntu@ip-172-31-20-63:~$ curl http://127.0.0.1:8000

    <h1>Hello from Python inside Docker! 🚀</h1>
    <p>This is a small application deployed via AWS ECS / EC2.</p>
    <p><strong>Environment Variable (MY_CUSTOM_VAR):</strong> Default Variable Value</p>
    ubuntu@ip-172-31-20-63:~$