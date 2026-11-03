# Replicating the architecture reconstruction

This guide explains how to repeat the reconstruction in this repository on another deployment of the
same system. You rebuild the architecture of a running AWS workload from read-only evidence alone,
with no design documents, source code or public documentation. Claude Code does the work through two
plugins:

- **[`aws-well-architected-and-analysis`](https://github.com/rtym/aws-well-architected-and-analysis)** collects read-only evidence from the AWS account: an
  inventory, Well-Architected evidence and the security posture.
- **[`sei-architecture-methodology`](https://github.com/rtym/sei-architecture-methodology)** turns that evidence into an SEI architecture package: a brownfield
  intake, the architectural drivers, and Views and Beyond documentation with UML diagrams.

The [`aws/`](aws/README.md) and [`architecture/`](architecture/README.md) folders in this repository
are the outputs of one such run, in eu-central-1. A replication should produce the same kind of
outputs.

The guide uses these placeholders. Replace them everywhere, including in `CLAUDE.md` and the prompts:

| Placeholder | Meaning | Example |
|-------------|---------|---------|
| `<account-id>` | AWS account that hosts the deployment | `111122223333` |
| `<region>` | Region of the deployment | `us-west-1` |
| `<profile>` | AWS CLI profile used for the analysis | `recon` |
| `<iam-user>` | Read-only IAM user of the analyst | `recon-analyst` |
| `<env-name>` | Terraform environment name of the deployment (also the `environment-name` tag) | `retail-store-ecs` |

| # | Step | Who | Time (approx.) |
|---|------|-----|----------------|
| 0 | Deploy the system and create read-only access | coordinator | — |
| 1 | Console sign-in with MFA, AWS CLI, access key, one profile; test the access | analyst | 30 min |
| 2 | Install Claude Code and sign in | analyst | 10 min |
| 3 | Install the prerequisites and the two plugins | analyst | 20 min |
| 4 | Create the analysis folder and its `CLAUDE.md` | analyst | 5 min |
| 5 | Start a session and run the pre-flight check | analyst | 10 min |
| 6 | Run prompts 1–6 in order. **This is the reconstruction itself.** | analyst | 90 min |

> **Ground rule: read-only.** The analyst can read metadata in `<region>` only, plus global services
> such as IAM. They cannot read secret values, application data (S3 objects, DynamoDB items, queue
> messages, log events) or container images, and cannot change anything. An `AccessDenied` for
> another region or for one of those calls is **expected**. Don't try to work around it.

> **Public sources are out of scope.** Don't use the public repository of the deployed solution
> (`aws-containers/retail-store-sample-app`): its source code, README, issues and Terraform are all off
> limits, as is any other public material about the solution. The reconstruction must come from the
> running deployment only. Don't push or publish raw outputs to a public repository or gist either,
> because they contain account identifiers. Redact them first, as described in
> [README.md](README.md#redaction). The only GitHub access needed is installing the two plugins.

> **Windows:** the simplest route is **WSL 2 with Ubuntu** (`wsl --install -d Ubuntu`, then reboot).
> Inside it, follow the Linux commands everywhere. The plugins' diagram and report scripts are Bash
> scripts and run there unchanged. Native Windows with Git for Windows also works, using the
> PowerShell commands below.

## 0. Coordinator: prepare the deployment and the access

1. Deploy the AWS retail-store sample app on Amazon ECS Fargate in `<region>` with its Terraform
   (`terraform/ecs/default`), using the environment name `<env-name>`. Wait until the five services
   (`ui`, `catalog`, `carts`, `checkout`, `orders`) each have one running task.
2. Create one IAM user per analyst, `<iam-user>`, with a console password (reset required at first
   sign-in) and these permissions attached directly to the user:
   - **Workload read:** `Describe*`, `List*` and `Get*` on metadata for everything the Terraform
     deploys: ECS and Service Connect, Elastic Load Balancing, VPC and security groups, RDS/Aurora
     (including parameter groups), DynamoDB, ElastiCache, OpenSearch, Amazon MQ, SQS, SNS, EventBridge,
     Application Auto Scaling, CloudWatch alarms and metrics, log-group settings, Secrets Manager and SSM
     parameter **names**, KMS key metadata and policies, Cloud Map, X-Ray service graph,
     CloudFormation.
   - **Governance read:** CloudTrail, Config, GuardDuty, Security Hub, Backup, and the global services
     IAM (read), Cost Explorer, Budgets, Organizations, Trusted Advisor, Health, Route 53 (including
     the private zone records) and the S3 bucket list.
   - **Guardrails:** an explicit deny for every region other than `<region>` (global services
     excepted), for secret and parameter values, KMS decrypt, S3 object reads, DynamoDB item reads,
     queue message receipt, log event reads, ECR image downloads, ECS Exec and Session Manager.
   - **Self-service:** manage the user's own password, access keys, and an MFA device whose name
     starts with a prefix you choose.
3. Tag everything you create for the analyst (for example `assigned-to`, `owner`, `purpose`), so it can
   be found and removed at the end.
4. Give the analyst's GitHub account read access to the two private plugin repositories,
   [`rtym/sei-architecture-methodology`](https://github.com/rtym/sei-architecture-methodology) and
   [`rtym/aws-well-architected-and-analysis`](https://github.com/rtym/aws-well-architected-and-analysis).
5. Send the sign-in details and the one-time password through **separate** channels.

The rest of this guide is for the analyst.

## 1. Configure AWS access

### 1.1 Sign in to the console and add MFA

1. Open `https://<account-id>.signin.aws.amazon.com/console`, sign in as `<iam-user>` with the one-time
   password, and set a new password.
2. Install an authenticator app if you don't have one.
3. Account menu (top right) → **Security credentials** → **Multi-factor authentication (MFA)** →
   **Assign MFA device**.
4. Device name: start it with the prefix the coordinator gave you. Any other name fails with
   `AccessDenied`. Type: **Authenticator app** → **Next**.
5. **Show QR code** → scan it → enter two consecutive codes → **Add MFA**.
6. Sign out and back in. From now on the console asks for a 6-digit code.

MFA protects the console. The AWS CLI uses an access key and doesn't ask for MFA codes.

### 1.2 Install AWS CLI v2

```bash
# macOS
brew install awscli

# Windows (PowerShell)
winget install -e --id Amazon.AWSCLI

# Linux (Debian 12/13, Ubuntu 25.10/26.04)
sudo apt update && sudo apt install -y awscli
# Ubuntu 22.04 / 24.04: apt has no v2. Use AWS's installer:
curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip && unzip awscliv2.zip && sudo ./aws/install

aws --version   # must print aws-cli/2.x
```

### 1.3 How the access works

The analysis uses **one credential**, an access key for `<iam-user>`, through **one CLI profile**,
`<profile>`. The read-only permissions are attached directly to the user, so there is no role to
assume, no MFA prompt in the terminal and no session that expires mid-run.

| | Profile `<profile>` |
|---|---|
| Holds | access key ID + secret access key |
| Can do | read-only metadata in `<region>`; global services; manage own password, MFA and keys |
| Cannot do | anything in another region; read secret values or application data; change anything |
| Lifetime | until the key is deleted at the end of the exercise |
| Stored in | `~/.aws/credentials` (key) and `~/.aws/config` (region, output); on Windows under `%USERPROFILE%\.aws\` |

### 1.4 Create the access key

1. Console → your user name → **Security credentials** → **Access keys** → **Create access key**.
2. Use case **Command Line Interface (CLI)**. Acknowledge the IAM Identity Center recommendation →
   **Next**.
3. Optional description: `reconstruction-<laptop name>` → **Create access key**.
4. Copy the access key ID and the secret, or download the `.csv`. **The secret is shown only once.**

> **Treat the key like a password.** The key alone gives read access to the account. Never put it in
> the analysis folder, `CLAUDE.md`, a prompt, a chat or git. Keep it in a password manager, or delete
> the `.csv` after the next step.

### 1.5 Configure the profile

```bash
aws configure --profile <profile>
# AWS Access Key ID:     AKIA...
# AWS Secret Access Key: ...
# Default region name:   <region>
# Default output format: json

chmod 600 ~/.aws/credentials          # macOS / Linux
# Windows: icacls $HOME\.aws\credentials /inheritance:r /grant:r "$($env:USERNAME):(R,W)"

aws sts get-caller-identity --profile <profile>   # "Arn": "arn:aws:iam::<account-id>:user/<iam-user>"
```

In `credentials` the section is `[<profile>]`. In `config` it is `[profile <profile>]`.

### 1.6 Looking after the key

| Situation | What to do |
|-----------|------------|
| Exercise finished | Console → Access keys → **Deactivate**, then **Delete**. Remove the `[<profile>]` section from `credentials`. |
| New laptop, or key older than 90 days | Create a second key → `aws configure --profile <profile>` → test → deactivate and delete the old one. |
| Secret may have leaked | **Deactivate the key immediately** (it takes effect within seconds), tell the coordinator, create a new one. |
| Lost the MFA device | Ask the coordinator to remove it, then assign a new one. |

### 1.7 Test the access

Run these commands and send the results to the coordinator. An empty cluster list still counts as
"allowed" if the store isn't deployed yet.

```bash
aws sts get-caller-identity --profile <profile>                                   # 1 your user ARN
aws ecs list-clusters --profile <profile>                                         # 2 allowed
aws ec2 describe-vpcs --profile <profile> --query "Vpcs[].VpcId"                  # 3 allowed
aws secretsmanager list-secrets --profile <profile> --query "SecretList[].Name"   # 4 allowed (names only)
aws iam get-account-summary --profile <profile> --query "SummaryMap.Users"        # 5 allowed (global)
aws ecs list-clusters --profile <profile> --region <another-region>               # 6 AccessDenied, expected
aws ssm get-parameter --profile <profile> --name /recon/test                      # 7 AccessDenied, expected (values)
```

> **Tip:** if a call fails with "Could not connect to the endpoint URL" (seen with Elastic Load
> Balancing and CloudFormation), set `AWS_USE_DUALSTACK_ENDPOINT=true` and retry.

## 2. Install Claude Code

```bash
# macOS
curl -fsSL https://claude.ai/install.sh | bash        # or: brew install --cask claude-code

# Windows (PowerShell)
winget install -e --id Git.Git                        # Claude Code uses Git Bash on Windows
winget install -e --id Anthropic.ClaudeCode

# Linux (Ubuntu / Debian, including WSL 2): Anthropic's signed apt repository
sudo apt install -y curl gnupg
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl -fsSL https://downloads.claude.ai/keys/claude-code.asc -o /etc/apt/keyrings/claude-code.asc
gpg --show-keys /etc/apt/keyrings/claude-code.asc     # fingerprint 31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE
echo "deb [signed-by=/etc/apt/keyrings/claude-code.asc] https://downloads.claude.ai/claude-code/apt/stable stable main" \
  | sudo tee /etc/apt/sources.list.d/claude-code.list
sudo apt update && sudo apt install -y claude-code

claude --version
```

1. Start `claude` once and sign in with your Claude account in the browser.
2. Run `/model` and choose **Opus** or **Sonnet**. Opus is the strongest for the long,
   judgement-heavy SEI work. Sonnet is faster and also gives good results.
3. Keep the default permission mode (ask before running commands) for the first session. You then see
   every AWS command before it runs.

## 3. Install the prerequisites and the plugins

### 3.1 Prerequisites

| Tool | Why |
|------|-----|
| Python 3.11+ | the AWS plugin's collectors and report builder |
| Java 17+ | PlantUML renderer for the UML diagrams |
| Pango (WeasyPrint) | optional: PDF reports; Markdown and HTML work without it |
| Node.js 18+ | optional: Mermaid renderer |
| git + GitHub CLI (`gh`) | installing the plugins from their GitHub repositories |

```bash
# macOS
brew install python openjdk pango node git gh

# Windows (PowerShell)
winget install -e --id Python.Python.3.12
winget install -e --id EclipseAdoptium.Temurin.21.JDK
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id GitHub.cli
# Pango: MSYS2 + pacman -S mingw-w64-x86_64-pango, or skip PDFs (--formats md,html)

# Linux (Ubuntu / Debian)
sudo apt update
sudo apt install -y python3 python3-venv python3-pip openjdk-17-jre-headless \
  libpango-1.0-0 libpangoft2-1.0-0 git unzip gh
sudo apt install -y nodejs npm   # optional, Mermaid only
```

### 3.2 Give git access to the plugin repositories

The plugins are in two private GitHub repositories. Ask the coordinator for read access:

- [github.com/rtym/sei-architecture-methodology](https://github.com/rtym/sei-architecture-methodology)
- [github.com/rtym/aws-well-architected-and-analysis](https://github.com/rtym/aws-well-architected-and-analysis)

Claude Code clones the plugins with the git credentials already on your machine and **never asks for
a password**, so this must work first:

```bash
gh auth login   # GitHub.com → HTTPS → "Authenticate Git with your GitHub credentials?" Yes → browser

git ls-remote https://github.com/rtym/sei-architecture-methodology.git
git ls-remote https://github.com/rtym/aws-well-architected-and-analysis.git
```

Each `ls-remote` must print a list of refs without prompting. If you get "Repository not found", the
repository access invitation hasn't been accepted yet (see https://github.com/notifications).

### 3.3 Install the plugins (user scope, from any folder)

```bash
claude plugin marketplace add rtym/sei-architecture-methodology
claude plugin install sei-architecture-methodology@sei-architecture-methodology
claude plugin marketplace add rtym/aws-well-architected-and-analysis
claude plugin install aws-analysis@aws-well-architected-and-analysis
```

You can also install them interactively with the same `/plugin marketplace add` and `/plugin install`
commands inside Claude Code. Choose **Install for you (user scope)**. Don't install them inside the
analysis folder with project or local scope.

The reference run used `sei-architecture-methodology` v1.11.1 and `aws-well-architected-and-analysis`
v1.1.0.

### 3.4 Check the plugins

| Where | Command | Expected |
|-------|---------|----------|
| terminal | `claude plugin list` | both plugins, scope `user`, status `enabled` |
| Claude Code | `/sei` | `/sei`, `/drivers`, `/quality-attributes`, `/qaw`, `/add`, `/atam`, `/architecture-docs`, `/sei-diagram` |

If something fails:

- **Failed to clone:** repeat the `git ls-remote` check.
- **SSH key rejected by GitHub:** set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` and reinstall.
- **Plugin listed but its commands are missing:** run `/reload-plugins`, or restart Claude Code.

To update, use `/plugin` → **Marketplaces** → **Update marketplace**, or
`claude plugin update <plugin>@<marketplace>`. These marketplaces don't update automatically.

## 4. Create the analysis folder

Work in a dedicated, empty folder:

```bash
mkdir -p ~/workspace/reconstruction/{aws/{discovery,scoped,well-architected,security},architecture}
cd ~/workspace/reconstruction && git init     # optional, but makes every change reviewable
```

Create `CLAUDE.md` in it. Claude Code reads this file at the start of every session, so the rules
apply to every prompt:

```markdown
# Architecture reconstruction — <region>

## Rules of engagement
- READ-ONLY. Use only Describe*/List*/Get* AWS calls (plus sts get-caller-identity and
  ce get-cost-and-usage). Never create, modify, tag or delete anything in AWS.
- Credentials: AWS_PROFILE=<profile> is set in the environment; use it, no other profile.
  Region: <region>. Do not query other regions except global services.
- Never read secret values (Secrets Manager, SSM SecureString). Redact credential-like
  environment values (PASS|SECRET|TOKEN|KEY|CREDENTIAL) before saving evidence.
- Scope: resources tagged environment-name=<env-name> plus the untagged resources they reference.
  The account is shared — ignore other workloads.
- AccessDenied for other regions, secret values or application data is expected: record it, move on.
- PUBLIC SOURCES ARE PROHIBITED for the deployed solution: do not fetch, search or read its public
  repository (aws-containers/retail-store-sample-app: code, README, issues, Terraform) or any other
  public source about it. Reconstruct from the AWS evidence only.
- Never push or publish output to a public repository or gist.

## Where things go
- Evidence: aws/ (discovery/, scoped/, well-architected/, security/) + aws/README.md
- SEI package: architecture/ (SEI plugin conventions)
- Temporary files: the session scratchpad, not this folder
- Python: if the plugin scripts need libraries, create a virtual environment in the
  session scratchpad, never in this folder.

## Conventions
- Every derived driver is marked "derived — confirm".
- Diagrams: UML in PlantUML, rendered to PNG and visually verified before embedding.
```

## 5. Start a session

Set the profile and region in the terminal you'll start Claude Code from:

```bash
cd ~/workspace/reconstruction
export AWS_PROFILE=<profile> AWS_REGION=<region> AWS_DEFAULT_REGION=<region>
# PowerShell: $env:AWS_PROFILE="<profile>"; $env:AWS_REGION="<region>"; $env:AWS_DEFAULT_REGION="<region>"
```

If you stop and come back later, run `claude --continue`. Completed work is already in the files.

### 5.1 Pre-flight check

Run these checks before the first prompt. Ten minutes here protects the 90-minute run.

```bash
aws sts get-caller-identity --query Arn --output text            # 1 arn:aws:iam::<account-id>:user/<iam-user>
echo $AWS_REGION                                                  # 2 <region>
aws ecs describe-services --cluster <env-name>-cluster \
  --services ui catalog carts checkout orders \
  --query "services[].[serviceName,runningCount]" --output table  # 3 five services, 1 running task each
echo "http://$(aws elbv2 describe-load-balancers --names <env-name>-ui \
  --query 'LoadBalancers[0].DNSName' --output text)"              # 4 store home page opens in a browser
python3 --version                                                 # 5 3.11+
java -version                                                     # 6 17+
```

Then start `claude` and check from inside it:

| # | In Claude Code | Expected |
|---|----------------|----------|
| 7 | `/plugin` | both plugins installed and enabled |
| 8 | prompt 1 (section 6) | the skills and commands of both plugins are listed |
| 9 | *Render a one-box test diagram with the sei-diagrams skill (PlantUML) into the session scratchpad and show it to me.* | a PNG is shown: PlantUML and Java work end to end |
| 10 | *Run aws sts get-caller-identity and aws ecs list-clusters.* | your user, and `<env-name>-cluster` in the list |

### 5.2 While the prompts run

- The AWS plugin runs its own Python collectors (`discover.py`, `collect_evidence.py`,
  `security_scan.py`). They only read, so it's safe to approve them.
- An `AccessDenied` for another region, a secret value, application data or log contents is expected.
  An `AccessDenied` on a describe/list call in `<region>` is **not** expected: report the exact command
  and error to the coordinator.
- After each prompt, do its **Check** before moving on.
- To stay within 90 minutes, approve read-only AWS commands promptly. Accepting **"Yes, and don't ask
  again"** for `aws … describe-*` / `list-*` is safe, because the permissions block every change.

## 6. The prompts, in order

Paste each prompt as is, wait for it to finish and do its check. `CLAUDE.md` and the two plugins supply
the details, so the prompts only state the goal. Keep the evidence reports to Markdown and HTML
(PDF rendering adds time), and finish each step at its **Check** rather than polishing it.

| Prompt | Stage | Time budget |
|--------|-------|-------------|
| 1 | confirm the plugins | 2 min |
| 2 | confirm identity and scope | 5 min |
| 3 | collect the evidence of the whole system | 15 min |
| 4 | review the whole system | 15 min |
| 5 | reconstruct the whole system | 25 min |
| 6 | document the whole system | 28 min |
| | **total** | **90 min** |

### Prompt 1: confirm the plugins (2 min)

```text
Are you using the plugins for SEI and AWS? List the skills and commands you have from
sei-architecture-methodology and aws-well-architected-and-analysis.
```

**Check:** both plugins are listed.

### Prompt 2: confirm identity and scope (5 min)

```text
Read CLAUDE.md. Using the AWS profile <profile>, confirm the caller identity and find the workload
tagged environment-name=<env-name> in <region>: list its ECS cluster(s), services and load balancer.
Write a one-paragraph scope statement.
```

**Check:** your user ARN, the cluster and the five services (`ui`, `catalog`, `carts`, `checkout`,
`orders`).

### Prompt 3: collect the evidence, AWS plugin (15 min)

```text
Using the AWS plugin, collect evidence of the whole system deployed in <region> into aws/.
Keep secret values out of every file.
```

**Check:** evidence files in `aws/`, and no secret values in any of them.

### Prompt 4: review the whole system, AWS plugin (15 min)

```text
Using the AWS plugin, review the whole system against the AWS Well-Architected Framework and for
security, and save the findings in aws/.
```

**Check:** Well-Architected and security findings in `aws/`, with every question answered.

### Prompt 5: reconstruct the whole system, SEI plugin (25 min)

```text
Using the SEI plugin, reconstruct the whole system from the evidence in aws/ only: brownfield intake
and architectural drivers. Do not use public GitHub or any other public source about the deployed
solution.
```

**Check:** `architecture/brownfield-intake.md` and `architecture/drivers/`, with every driver marked
*derived — confirm*.

### Prompt 6: document the whole system, SEI plugin (28 min)

```text
Using the SEI plugin, document the whole system with Views and Beyond. All diagrams in UML.
```

**Check:** `architecture/docs/` with module, C&C and allocation views. Every diagram has a `.puml`
source.

## 7. After the run

1. **Compare** your outputs with the reference run in this repository: [`aws/`](aws/README.md) for
   the evidence and [`architecture/`](architecture/README.md) for the SEI package.
2. **Redact** before sharing: replace the account ID, IAM user names, access key IDs, live endpoint
   hostnames and public IP addresses (see [README.md](README.md#redaction)). Plugin-generated PDFs
   aren't redacted, so leave them out.
3. **Clean up the access:** deactivate and delete the access key and remove the profile. The
   coordinator then removes the IAM user and its policies, using their tags, and tears down the
   deployment.
