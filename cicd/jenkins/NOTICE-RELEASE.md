# ALB release — static fixture only

Job smoke-notice-release, Pipeline script from SCM, branch */cicd/alb-release-integration, path cicd/jenkins/Jenkinsfile.notice-release. No automatic triggers. Existing SSH key and SMOKE_ANSIBLE_HOST reused. Python runs on Ansible EC2 under ansadmin, using its existing IAM role and kubeconfig. This is a Python control script on the Ansible host, not an Ansible playbook.

## Preflight evidence
2026-11-27 11:48:47–11:49:05 KST, Jenkins release #1 SUCCESS. Blue test-v2 and Green test-v4, each 2 individually tested Pods HTTP 200, matching 2 healthy target IPs per slot, initial Blue 100/Green 0. No previous targets draining. [Evidence](../verification/1127-notice-release-build-1-verify.log).

## Modes
- VERIFY (default, confirmation false): repeats preflight with no mutation. Does not establish ModifyListener permission.
- ROLLBACK_TEST: AWS owner approval, listener-scoped ModifyListener and no concurrent changes required. Changes to Green 100%, verifies three consecutive HTTP 200/version results and target health, deliberately raises a synthetic assertion error, restores original Blue 100% and verifies it. Successful synthetic rollback test is not proof of real outage detection or zero downtime.
- SWITCH: same gates, leaves Green 100% only after validation. Any switch/post-switch failure attempts original listener restoration and fails the job even if restoration succeeds.

The script is intentionally limited to the test-v2/v4 fixtures and initial Blue 100/Green 0. After successful SWITCH do not rerun without reviewing current weights and developing the next release cycle. Before any write the script saves the original full listener default actions in /opt/devops/release-backups (0600 file, 0700 directory), preserving all fields except the two weights. Never publish backups or ARNs. Shared flock prevents concurrent use by the existing CD script on this control host, not external console changes. Coordinate with AWS owner. If rollback is unconfirmed, stop and inspect live state with AWS owner. Host/network loss, SIGKILL and in-flight API request uncertainty can prevent confirmed rollback; no continuous monitoring after pipeline exits. Measured elapsed_s includes API and consecutive response verification; it is not user-visible downtime or production RTO. Separate continuous request measurement required. Do not run actual application or data migration with this fixture script.

AWS documentation: https://docs.aws.amazon.com/cli/latest/reference/elbv2/modify-listener.html ; https://docs.aws.amazon.com/elasticloadbalancing/latest/application/rule-action-types.html .
