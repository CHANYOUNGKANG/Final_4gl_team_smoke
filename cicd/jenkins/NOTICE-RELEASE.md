# ALB release preflight (read-only, execution pending)

Create smoke-notice-release Pipeline script from SCM, branch */cicd/alb-release-integration, path cicd/jenkins/Jenkinsfile.notice-release. No triggers. Existing SSH key and SMOKE_ANSIBLE_HOST reused. Python runs on Ansible EC2 under ansadmin, using its existing IAM role and kubeconfig. No listener write calls.

The preflight checks initial Blue 100/Green 0, default HTTP listener only, expected fixture digests, two ready pods per slot, HTTP and version of every individual pod, exact matching healthy target IPs, no draining and three baseline ALB HTTP responses. It does not verify ModifyListener permission or zero downtime. Actual switch/rollback implementation follows the preflight and AWS owner approval; do not force deregistration. No sensitive ARNs/IPs printed. No actual app deployment.
