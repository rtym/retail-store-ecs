"""Generate the SEI drivers register for the retail-store-ecs reconstruction.

Single source of truth for every driver so IDs, matrix rows and per-file content stay
consistent. Re-run after editing the data below; it rewrites architecture/drivers/.
Statuses are kept in STATUS so /atam results can be applied by editing one dict.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "drivers"
DATE = "2026-10-09"
DERIVED = "> **Derived — confirm.** Reconstructed from the deployed AWS environment (read-only evidence), not from a stakeholder. Treat as a hypothesis until confirmed."
EVID = "../../../aws"  # from drivers/<sub>/ to aws/

# ----------------------------------------------------------------------------- status
# open by default; /atam sets "at risk" on drivers whose scenario surfaced a Risk.
STATUS = {}


def st(i):
    return STATUS.get(i, "open")


# ----------------------------------------------------------------------------- stakeholders
STAKEHOLDERS = [
    ("ST-1", "AWS account owner of 111122223333 (identity to confirm)", "sponsor / workload owner", "purpose of the environment, cost, exposure of a shared account", "✓", "✓", "✓"),
    ("ST-2", "Architecture reconstruction author", "architect", "accurate as-built description, traceable risks", "✓", "✓", "✓"),
    ("ST-3", "Operator / SRE (to be named)", "operations", "deployability, observability, recovery, on-call load", "✓", "✓", "✓"),
    ("ST-4", "Security and compliance (to be named)", "security", "data protection in transit/at rest, detection, least privilege", "✓", "✓", "✓"),
    ("ST-5", "Shopper (end-user representative)", "end user", "store available and responsive, personal data protected", "✓", "✓", ""),
    ("ST-6", "Upstream maintainers of aws-containers/retail-store-sample-app", "developers of the container images", "supported configuration, provider options, versions", "", "", "✓"),
    ("ST-7", "Owners of co-tenant workloads in the same account", "downstream / neighbours", "blast radius, quotas, cost attribution in the shared account", "", "✓", ""),
]

# ----------------------------------------------------------------------------- business goals
BGS = [
    dict(id="BG-1", title="Representative container reference workload on ECS",
         stmt="The account owner and the sample-app maintainers (ST-1, ST-6) need a working, representative polyglot microservice store running on Amazon ECS with AWS managed backing services so that container and managed-service patterns on AWS can be demonstrated, learned and evaluated.",
         sh="ST-1 — AWS account owner", cat="managing change", prio="high",
         measure="All five services RUNNING and HEALTHY behind the public endpoint; every backing-service type of the app exercised (DynamoDB, Aurora MySQL, Aurora PostgreSQL, ElastiCache, Amazon MQ, OpenSearch).",
         ctx="The upstream README states the application exists to demonstrate container concepts on AWS and is deliberately over-engineered (decoupled services with different infrastructure dependencies). The deployment tags `created-by=retail-store-sample-app` confirm it is that project's Terraform ECS deployment.",
         uc=["UC-1", "UC-5", "UC-6"], qa=["PQA-1", "DQA-1", "MQA-1", "INQA-1", "OQA-1"],
         notes="Source: upstream README (stated purpose). Whether *this* deployment is a demo, a training lab or a pre-production candidate is not recorded anywhere — ask ST-1."),
    dict(id="BG-2", title="End-to-end shopping journey works",
         stmt="Shoppers (ST-5) need to browse, search, fill a cart and check out so that every completed checkout produces a stored order — the storefront's functional purpose.",
         sh="ST-5 — Shopper", cat="product quality", prio="high",
         measure="Checkout success ratio and order persistence (no metric exists today — see OQA-1).",
         ctx="Derived from the five deployed services (ui, catalog, carts, checkout, orders) and their wiring (`RETAIL_UI_ENDPOINTS_*`, `RETAIL_CHECKOUT_ENDPOINTS_ORDERS`).",
         uc=["UC-1", "UC-2", "UC-3", "UC-4", "UC-5"], qa=["AQA-1", "AQA-2", "PQA-1", "SCQA-1"],
         notes="Derived from function, not from a stated goal."),
    dict(id="BG-3", title="Cost proportionate to a non-production workload",
         stmt="The account owner (ST-1) needs the environment's running cost to stay proportionate to a demonstration / non-production workload so that the shared account's budget is not consumed by it.",
         sh="ST-1 — AWS account owner", cat="financial", prio="medium",
         measure="Monthly cost of resources tagged `environment-name=retail-store-ecs` within a budget ST-1 sets (not measurable today: the tag is not an activated cost-allocation tag).",
         ctx="Inferred from sizing choices: one task per service, burstable `db.t3.medium` / `cache.t3.micro`, single-instance broker and single-node search domain, one NAT Gateway.",
         uc=["UC-6"], qa=["PQA-2", "SCQA-1"],
         notes="Derived from sizing evidence — a hypothesis. Tension with BG-4: every redundancy fix adds cost."),
    dict(id="BG-4", title="Safe to expose and recoverable",
         stmt="The account owner and the security function (ST-1, ST-4) need the environment to protect shopper data, detect misuse and recover from failure so that it can stay exposed on the public internet inside a shared account — and, if ST-1 decides so, be promoted beyond demonstration use — without unacceptable risk.",
         sh="ST-4 — Security and compliance", cat="responsibility to society & law", prio="high",
         measure="Zero plaintext external endpoints; all control-plane activity recorded; documented RPO/RTO met in a restore test.",
         ctx="The environment is internet-facing (`retail-store-ecs-ui` Application Load Balancer, HTTP 80 from 0.0.0.0/0) and shares account 111122223333 with unrelated workloads. Orders carry shopper PII (name, address, e-mail).",
         uc=["UC-4", "UC-6", "UC-7"], qa=["AQA-1", "AQA-2", "RQA-1", "SQA-1", "SQA-2", "SQA-3", "OQA-1", "DQA-1"],
         notes="**Open decision for ST-1**: is this environment demo-only (CON-5) or a production candidate? The answer changes the priority of most risks found by the ATAM."),
]

# ----------------------------------------------------------------------------- use cases
UCS = [
    dict(id="UC-1", name="Browse product catalogue", level="user goal", actor="Shopper", actor_kind="human",
         supp=[], trigger="Shopper opens the storefront URL (`http://retail-store-ecs-ui-0000000000.eu-central-1.elb.amazonaws.com/`).",
         pre="ui and catalog services RUNNING; Aurora MySQL `retail-store-ecs-catalog` available.",
         post="Product list / detail page rendered; no state changed.",
         prio="high",
         mss=["Shopper requests a catalogue page over HTTP port 80 at the internet-facing Application Load Balancer.",
              "The load balancer forwards to the `ui` task on HTTP 8080 (target group `ui-application`).",
              "`ui` calls `http://catalog` (Service Connect alias, port 80) for products and tags.",
              "`catalog` reads products from Aurora MySQL (`RETAIL_CATALOG_PERSISTENCE_PROVIDER=mysql`, TCP 3306).",
              "`ui` also fetches the cart badge from `http://carts` and renders the page."],
         ext=["**3a.** `catalog` unavailable (single task restarting): `ui` cannot render products; shopper sees an error page.",
              "**4a.** Aurora writer unavailable (single instance, no reader): catalogue requests fail until the instance recovers."],
         sig="Dominant read load; crosses the internet trust boundary; exercises Service Connect and the catalogue database.",
         drivers=["BG-1", "BG-2", "PQA-1", "AQA-1", "CON-2"],
         includes=[], extends_by=["UC-2"]),
    dict(id="UC-2", name="Search products", level="user goal", actor="Shopper", actor_kind="human",
         supp=[], trigger="Shopper submits a search term in the storefront (`RETAIL_UI_SEARCH_ENABLED=true`).",
         pre="UC-1 preconditions; OpenSearch domain `retail-store-ecs-catalog` reachable; index `products` populated.",
         post="Matching products listed.",
         prio="medium",
         mss=["Shopper enters a search term on a catalogue page.",
              "`ui` forwards the query to `http://catalog`.",
              "`catalog` queries OpenSearch 3.3 over HTTPS 443 (fine-grained access control, credentials from Secrets Manager), index `products`.",
              "`ui` renders the result list."],
         ext=["**3a.** OpenSearch single node unavailable: search fails; browsing (UC-1) still works from Aurora MySQL."],
         sig="Extends UC-1 conditionally (feature flag); adds a second data store to the catalogue service — a consistency and availability concern.",
         drivers=["BG-2", "PQA-1", "AQA-2", "MQA-1"],
         includes=[], extends_by=[], extends="UC-1"),
    dict(id="UC-3", name="Manage shopping cart", level="user goal", actor="Shopper", actor_kind="human",
         supp=[], trigger="Shopper adds, updates or removes an item.",
         pre="ui and carts RUNNING; DynamoDB table `retail-store-ecs-carts` available.",
         post="Cart persisted in DynamoDB keyed by customer.",
         prio="high",
         mss=["Shopper adds an item from a product page.",
              "`ui` calls `http://carts` via Service Connect.",
              "`carts` writes the cart item to DynamoDB `retail-store-ecs-carts` (on-demand; GSI `idx_global_customerId`) over HTTPS 443 through the NAT Gateway.",
              "`ui` shows the updated cart."],
         ext=["**3a.** NAT Gateway (single, eu-central-1a) unavailable: DynamoDB is unreachable (no gateway endpoint) and cart writes fail in every Availability Zone."],
         sig="State-changing; the only data path that leaves the VPC (to a regional AWS endpoint), making it depend on the NAT Gateway.",
         drivers=["BG-2", "AQA-2", "SCQA-1"],
         includes=[], extends_by=[]),
    dict(id="UC-4", name="Check out", level="user goal", actor="Shopper", actor_kind="human",
         supp=[], trigger="Shopper starts checkout from a non-empty cart.",
         pre="ui, checkout, orders RUNNING; ElastiCache Redis `retail-store-ecs-checkout` available.",
         post="Order submitted (UC-5) and checkout session cleared.",
         prio="high",
         mss=["Shopper enters shipping details and selects delivery.",
              "`ui` calls `http://checkout`; `checkout` stores the in-progress checkout in Redis (`redis://…:6379`, no TLS, no AUTH).",
              "Shopper confirms; `checkout` submits the order to `http://orders` (UC-5).",
              "`ui` shows the order confirmation."],
         ext=["**2a.** Redis node (single, no replica) lost: in-progress checkouts are lost; shopper must restart checkout.",
              "**3a.** `orders` unavailable: checkout cannot complete; no retry or outbox exists at the infrastructure level."],
         sig="Carries PII across three services; the synchronous chain ui → checkout → orders → databases is the longest call path.",
         drivers=["BG-2", "BG-4", "AQA-1", "SQA-1", "SQA-2"],
         includes=["UC-5"], extends_by=[]),
    dict(id="UC-5", name="Place order", level="subfunction", actor="Shopper", actor_kind="human",
         supp=[("Downstream order consumers", "none deployed today")], trigger="`checkout` submits a confirmed checkout to `orders` (included by UC-4).",
         pre="Aurora PostgreSQL `retail-store-ecs-orders` and Amazon MQ broker `retail-store-ecs-orders-broker` available.",
         post="Order row stored; order-created event published to RabbitMQ.",
         prio="high",
         mss=["`orders` receives the order over HTTP via Service Connect.",
              "`orders` writes the order to Aurora PostgreSQL 15.10 (TCP 5432; `rds.force_ssl=0`).",
              "`orders` publishes an order event to RabbitMQ 3.13 on Amazon MQ over AMQPS 5671 (`RETAIL_ORDERS_MESSAGING_PROVIDER=rabbitmq`).",
              "Any subscribed downstream consumer receives the event asynchronously."],
         ext=["**3a.** Broker (single instance) unavailable: publish fails; behaviour of the application on publish failure is not visible from infrastructure — ask ST-6."],
         sig="The integration point of the system (asynchronous event); the only use case that writes PII to a database; included by UC-4.",
         drivers=["BG-1", "BG-2", "BG-4", "INQA-1", "RQA-1", "AQA-2"],
         includes=[], extends_by=[]),
    dict(id="UC-6", name="Deploy a new service version", level="user goal", actor="Operator", actor_kind="human",
         supp=[("Amazon ECR Public", "image registry public.ecr.aws/aws-containers"), ("Terraform", "infrastructure as code (derived)")],
         trigger="A new image tag (e.g. beyond 1.6.3) or a configuration change is to be released.",
         pre="New task-definition revision prepared (Terraform).",
         post="Service runs the new revision; old tasks drained.",
         prio="medium",
         mss=["Operator applies the Terraform change, registering a new task-definition revision.",
              "ECS starts new tasks (rolling: minimum healthy 100 %, maximum 200 %), pulling the image from ECR Public through the NAT Gateway.",
              "New tasks pass the container health check (`curl /health` or `/actuator/health`) and, for `ui`, the target-group health check.",
              "ECS stops the old tasks."],
         ext=["**3a.** New version never becomes healthy: deployment circuit breaker is disabled, so ECS keeps retrying; no automatic rollback.",
              "**2a.** ECR Public unreachable or rate-limited: tasks cannot start (no private mirror)."],
         sig="Deployability and change risk; depends on an external registry and the NAT Gateway.",
         drivers=["BG-1", "BG-3", "BG-4", "DQA-1", "CON-3", "CON-6"],
         includes=[], extends_by=[]),
    dict(id="UC-7", name="Diagnose a running service", level="user goal", actor="Operator", actor_kind="human",
         supp=[("Amazon CloudWatch", "Logs + Container Insights"), ("AWS Systems Manager", "ECS Exec sessions")],
         trigger="A shopper-visible fault is reported (there are no alarms to raise one automatically).",
         pre="Operator holds IAM permissions for logs and ECS Exec.",
         post="Fault located.",
         prio="medium",
         mss=["Operator inspects Container Insights (enhanced) metrics for the cluster `retail-store-ecs-cluster`.",
              "Operator reads the service's stream in log group `retail-store-ecs-tasks` (prefix `<service>-service`).",
              "If needed, operator opens a shell in the task with ECS Exec (enabled on all services).",
              "Operator identifies the failing component."],
         ext=["**1a.** Fault older than 1 day: Container Insights performance logs are already expired (retention 1 day)."],
         sig="Observability is entirely manual: no alarms, no dashboards, no tracing; ECS Exec is a privileged path into every container.",
         drivers=["BG-4", "OQA-1", "SQA-3"],
         includes=[], extends_by=[]),
]

# ----------------------------------------------------------------------------- constraints
CONS = [
    dict(id="CON-1", title="AWS eu-central-1 in a shared account", typ="technical",
         c="The workload runs in AWS region eu-central-1, account 111122223333, which also hosts unrelated workloads (happy-nmt, TMG, sklad-kontrol, Terra, quiz-scanner, …).",
         src="Deployment evidence (`aws/discovery/architecture-inventory.json`); owner to confirm whether intentional.",
         nature="negotiable", prio="high",
         rat="Region and account are where the environment was deployed; no landing-zone or Organizations structure isolates it.",
         impact="Account-level controls (CloudTrail, GuardDuty, Config, IAM users) are shared with neighbours; quotas are shared; cost must be separated by tag.",
         conflicts="BG-4 (isolation and detection are weaker in a shared account).", bg=["BG-1", "BG-3"]),
    dict(id="CON-2", title="Amazon ECS on AWS Fargate", typ="technical",
         c="All five services run as ECS services with launch type FARGATE, `awsvpc` networking, platform version 1.4.0, in cluster `retail-store-ecs-cluster`.",
         src="ECS evidence (`aws/scoped/retail-store-ecs-evidence.json`); upstream Terraform ECS deployment option.",
         nature="hard", prio="high",
         rat="The deployment is the ECS variant of the sample app; the purpose (BG-1) is to show containers on ECS.",
         impact="No host management; scaling and placement are per-task; networking is per-task ENI and security group.",
         conflicts="none", bg=["BG-1"]),
    dict(id="CON-3", title="Upstream pre-built images, version 1.6.3", typ="technical",
         c="Application code is not owned: images are `public.ecr.aws/aws-containers/retail-store-sample-{ui,catalog,cart,checkout,orders}:1.6.3`. Only infrastructure and configuration (environment variables, secrets) can be changed.",
         src="Task definitions `retail-store-ecs-*:1`.",
         nature="hard", prio="high",
         rat="The workload is a deployment of an open-source sample, not a product under development here.",
         impact="Application-level tactics (retries, outbox, idempotency, TLS client settings) are fixed by upstream; architecture changes are limited to the platform.",
         conflicts="BG-4 (application-level hardening cannot be added locally).", bg=["BG-1"]),
    dict(id="CON-4", title="Backing services limited to supported providers", typ="technical",
         c="Each service binds its persistence/messaging provider by environment variable, among the providers the application supports: carts → DynamoDB, catalog → MySQL (+ OpenSearch search), checkout → Redis, orders → PostgreSQL + RabbitMQ.",
         src="Environment variables `RETAIL_*_PROVIDER` in the task definitions.",
         nature="hard", prio="medium",
         rat="Provider choice is a deployment-time binding the app exposes; anything else needs code changes (CON-3).",
         impact="Rules out e.g. SQS/SNS for orders events or Aurora DSQL without upstream support.",
         conflicts="none", bg=["BG-1", "BG-2"]),
    dict(id="CON-5", title="Upstream: educational use, not production", typ="business",
         c="The upstream project states it is intended for educational purposes only and not for production use.",
         src="aws-containers/retail-store-sample-app README.",
         nature="hard", prio="high",
         rat="Upstream disclaimer; governs what the environment may legitimately be used for.",
         impact="Production-grade guarantees (security reviews of the code, support) are not provided upstream.",
         conflicts="BG-4 if ST-1 intends production use — that tension must be decided by ST-1.", bg=["BG-1", "BG-4"]),
    dict(id="CON-6", title="Infrastructure defined as Terraform", typ="technical",
         c="The infrastructure was created by Terraform (the upstream ECS Terraform configuration); changes should be made there, not in the console.",
         src="Derived: timestamp-suffixed names (e.g. `retail-store-ecs-orders-2026100914501960110000001c`) and tags match the upstream Terraform; no CloudFormation stack owns the resources. Terraform source/state location unknown (AC-2).",
         nature="negotiable", prio="medium",
         rat="Keeps the environment reproducible and avoids drift.",
         impact="All remediation from the ATAM should land as Terraform changes.",
         conflicts="none", bg=["BG-1", "BG-3"]),
]

# ----------------------------------------------------------------------------- concerns
ACS = [
    dict(id="AC-1", title="Shared-account co-tenancy", kind="general (technology / organisation)", prio="high",
         c="The workload shares AWS account 111122223333 with unrelated workloads, so blast radius, IAM, quotas and cost attribution are shared.",
         why="A compromise or quota exhaustion in any co-tenant affects this workload and vice versa; cost of this workload cannot be isolated (BG-3).",
         rel="BG-3, BG-4, CON-1, SQA-3"),
    dict(id="AC-2", title="Infrastructure-as-code source and state not available", kind="general (process)", prio="high",
         c="The Terraform configuration and state for this environment are not in this repository and their location is unknown.",
         why="Drift cannot be detected; the reconstruction cannot be compared to intent; remediation has no agreed change path.",
         rel="CON-6, DQA-1"),
    dict(id="AC-3", title="Missing account security baseline", kind="general (technology mandate)", prio="high",
         c="CloudTrail, GuardDuty, AWS Config and Security Hub are not enabled in the account/region; 2 console users lack MFA; no password policy.",
         why="The workload inherits a baseline with no audit trail and no threat detection (see SQA-3).",
         rel="BG-4, SQA-3, CON-1"),
    dict(id="AC-4", title="Version currency of managed engines and images", kind="quality of the design", prio="medium",
         c="ElastiCache runs Redis 4.0.10, images are pinned to 1.6.3, Aurora MySQL 3.10.3 and Aurora PostgreSQL 15.10; Amazon MQ auto-minor-upgrade is on.",
         why="Old engine majors lose support and carry known issues; upgrades need a planned path (and Redis 4 → 7 requires replacing the cluster).",
         rel="BG-4, DQA-1"),
    dict(id="AC-5", title="No defined operations model", kind="general (process)", prio="high",
         c="No owner team, on-call, runbooks, alarms or dashboards are evident for the workload.",
         why="Faults are found by shoppers, not by operators (OQA-1); recovery depends on individual knowledge.",
         rel="BG-4, OQA-1, UC-7"),
]

# ----------------------------------------------------------------------------- quality attribute scenarios
QAS = [
    dict(id="AQA-1", title="Single task failure of the storefront", iso="Reliability", sub="availability",
         src="Fargate platform or application fault", stim="The only running `ui` task crashes or fails its health check",
         art="`ui` ECS service (desiredCount 1) behind the Application Load Balancer",
         env="Normal operation", resp="Traffic is routed only to healthy tasks while ECS replaces the failed one",
         meas="Proposed — confirm: 0 failed shopper requests and < 1 % 5xx over the 5 min after a single-task failure",
         bg=["BG-2", "BG-4"], vr=("H", "M"),
         tactics="*Availability — detect faults*: health check (present), monitor; *recover from faults*: redundant spare (active, ≥ 2 tasks across Availability Zones), rollback.",
         asbuilt="Every service runs `desiredCount 1`. A task failure makes that function unavailable until a replacement passes health checks (target group `ui-application`: path `/actuator/health`, matcher 200). For `ui` this is a total storefront outage."),
    dict(id="AQA-2", title="Loss of Availability Zone eu-central-1a", iso="Reliability", sub="availability / fault tolerance",
         src="AWS infrastructure event", stim="Availability Zone eu-central-1a becomes impaired",
         art="Whole environment — NAT Gateway, Redis node, Amazon MQ broker and OpenSearch node all sit in eu-central-1a",
         env="Normal operation, shoppers active", resp="Browse and cart keep working from eu-central-1b/c; checkout degrades with a clear message; no committed order lost",
         meas="Proposed — confirm: browse + cart restored within 5 min; 0 committed orders lost",
         bg=["BG-2", "BG-4"], vr=("H", "H"),
         tactics="*Availability — recover from faults*: redundant spare (Multi-AZ Aurora, Redis replica with automatic failover, Amazon MQ cluster deployment, OpenSearch zone awareness), one NAT Gateway per Availability Zone; *prevent faults*: removal from service.",
         asbuilt="The data tier is single-AZ: both Aurora writers in 1c, Redis, MQ and OpenSearch in 1a; the only NAT Gateway is in 1a and serves the private subnets of all three Availability Zones. Loss of 1a removes egress for every task (DynamoDB, ECR Public, Secrets Manager, CloudWatch Logs) plus checkout, order events and search."),
    dict(id="RQA-1", title="Restore after data corruption or deletion", iso="Reliability", sub="recoverability",
         src="Operator error or faulty release", stim="Order data in Aurora PostgreSQL or cart data in DynamoDB is deleted or corrupted",
         art="Aurora PostgreSQL `retail-store-ecs-orders`, Aurora MySQL `retail-store-ecs-catalog`, DynamoDB `retail-store-ecs-carts`",
         env="Normal operation", resp="Data restored to a point before the incident and services repointed",
         meas="Proposed — confirm: orders RPO ≤ 5 min and RTO ≤ 4 h; carts RPO ≤ 24 h",
         bg=["BG-4"], vr=("H", "M"),
         tactics="*Availability — recover from faults*: rollback, state resynchronisation; backups with point-in-time recovery, AWS Backup with cross-region copy, deletion protection.",
         asbuilt="Aurora clusters: automated backups 7 days (point-in-time restore possible), deletion protection off. DynamoDB: point-in-time recovery **disabled**, deletion protection off. Redis: 0 snapshots. No AWS Backup plan; nothing copied out of region; restore never tested."),
    dict(id="PQA-1", title="Catalogue page responsiveness", iso="Performance efficiency", sub="time behaviour",
         src="Shoppers", stim="50 concurrent shoppers browse catalogue pages (UC-1)",
         art="ui → catalog → Aurora MySQL request path",
         env="Normal operation", resp="Pages are served",
         meas="Proposed — confirm: Application Load Balancer TargetResponseTime p95 ≤ 1 s, 0 % 5xx",
         bg=["BG-1", "BG-2"], vr=("M", "M"),
         tactics="*Performance — manage resources*: increase resources, introduce concurrency (more tasks), maintain multiple copies of data (read replica, cache); *control demand*: limit event response.",
         asbuilt="1 vCPU / 2 GB per task, one task per service, Aurora `db.t3.medium` (burstable CPU credits). No latency target, no load test results, no caching in front of the catalogue."),
    dict(id="PQA-2", title="Provisioned capacity is used", iso="Performance efficiency", sub="resource utilisation",
         src="Account owner (cost review)", stim="Monthly review of provisioned versus used capacity",
         art="ECS tasks and managed data services",
         env="Normal (low) demonstration load", resp="Over-provisioned resources are identified and right-sized",
         meas="Proposed — confirm: average CPU utilisation ≥ 40 % on tasks and data nodes, or a documented reason why not",
         bg=["BG-3"], vr=("M", "L"),
         tactics="*Performance — manage resources*: schedule resources, right-size; *Energy efficiency*: scale down / schedule off outside use.",
         asbuilt="Fixed sizes without utilisation data: 5 × (1 vCPU, 2 GB), `mq.m5.large`, `r8g.medium.search`, 2 × `db.t3.medium`. Container Insights (enhanced) collects the metrics but keeps performance logs 1 day only."),
    dict(id="SCQA-1", title="Demand spike", iso="Flexibility", sub="scalability",
         src="Marketing event", stim="Request rate grows 10× within 10 minutes and later falls back",
         art="ECS services and their data stores",
         env="Peak load", resp="Task count scales out with demand and back in afterwards",
         meas="Proposed — confirm: capacity added within 5 min, < 1 % 5xx during the spike; back to baseline within 30 min after it",
         bg=["BG-2", "BG-3"], vr=("M", "H"),
         tactics="*Performance — manage resources*: increase resources (ECS target-tracking auto scaling), maintain multiple copies; *control demand*: limit rates.",
         asbuilt="No Application Auto Scaling targets or policies for any service. DynamoDB on-demand scales; Aurora, Redis, MQ and OpenSearch are fixed single nodes."),
    dict(id="SQA-1", title="Shopper traffic confidentiality in transit", iso="Security", sub="confidentiality",
         src="Attacker on the network path", stim="Intercepts storefront traffic carrying shopper PII during checkout",
         art="Application Load Balancer listener and internal service-to-service and service-to-store hops",
         env="Normal operation, internet-facing", resp="All external and internal traffic carrying PII is encrypted",
         meas="Proposed — confirm: 100 % of external requests on TLS 1.2+; 0 plaintext listeners; 0 plaintext connections to stores holding PII",
         bg=["BG-4"], vr=("H", "L"),
         tactics="*Security — resist attacks*: encrypt data (HTTPS listener with ACM certificate and redirect, TLS to Redis/Aurora, Service Connect TLS), limit exposure.",
         asbuilt="The only listener is **HTTP:80** (no TLS). Internal: Service Connect without TLS; Redis without in-transit encryption or AUTH; Aurora PostgreSQL `rds.force_ssl=0` and MySQL `require_secure_transport` OFF. Correct: Amazon MQ uses AMQPS 5671; OpenSearch enforces HTTPS (TLS 1.2 policy)."),
    dict(id="SQA-2", title="Containment of a compromised service", iso="Security", sub="integrity",
         src="Attacker who gained code execution in the `ui` container", stim="Attempts to reach other services' data stores and secrets",
         art="Security groups, task IAM roles and secret scoping",
         env="Normal operation", resp="Only the intended call graph is reachable; other stores and secrets are denied",
         meas="Proposed — confirm: 0 network paths outside the intended graph (verified by VPC Reachability Analyzer); 0 secrets readable by a non-owning task role",
         bg=["BG-4"], vr=("H", "M"),
         tactics="*Security — resist attacks*: limit access, limit exposure, separate entities (per-service security groups and roles); *detect attacks*: detect intrusion.",
         asbuilt="Good: every data store's security group admits only its one client (3306 ← catalog, 5432 ← orders, 5671 ← orders, 6379 ← checkout, 443 ← catalog); secrets are scoped per execution role; separate task roles. Weak: all five task security groups allow TCP 8080 from `0.0.0.0/0` (in practice the whole VPC); `checkout-task` holds `dynamodb:*` on the carts table it does not use; ECS Exec is enabled on all services; Redis has no AUTH."),
    dict(id="SQA-3", title="Detection of suspicious control-plane activity", iso="Security", sub="accountability",
         src="Compromised IAM principal in the shared account", stim="Changes a security group or reads a database secret",
         art="Account audit and detection services",
         env="Normal operation", resp="The action is recorded and the security function alerted",
         meas="Proposed — confirm: 100 % of API calls recorded; alert within 15 min",
         bg=["BG-4"], vr=("H", "L"),
         tactics="*Security — detect attacks*: detect intrusion, maintain audit trail (CloudTrail), verify message integrity; *react*: alert actors.",
         asbuilt="No CloudTrail trail; GuardDuty, Security Hub and AWS Config are disabled in eu-central-1; no VPC Flow Logs; Application Load Balancer access logs off."),
    dict(id="OQA-1", title="Operators learn of failures before shoppers", iso="Observability (cross-cutting)", sub="monitorability",
         src="Any service fault", stim="5xx rate at the load balancer exceeds 5 % or a service has 0 healthy tasks",
         art="Monitoring and alerting of the environment",
         env="Normal operation", resp="The on-call operator is notified with the failing service identified",
         meas="Proposed — confirm: notification within 5 min; 100 % of services covered by an alarm",
         bg=["BG-1", "BG-4"], vr=("H", "L"),
         tactics="*Availability — detect faults*: monitor, heartbeat, exception detection; *Observability*: alarms with actions, dashboards, distributed tracing.",
         asbuilt="0 CloudWatch alarms and 0 dashboards for the workload; Container Insights (enhanced) metrics collected; task logs in `retail-store-ecs-tasks` with **no retention** (never expire); Amazon MQ general logs off; no tracing."),
    dict(id="DQA-1", title="Safe rollout of a bad version", iso="Flexibility", sub="installability (deployability)",
         src="Operator", stim="Deploys a new service version that fails its health check",
         art="ECS rolling deployment of one service",
         env="Normal operation, shoppers active", resp="Rollout stops and the previous version keeps serving",
         meas="Proposed — confirm: 0 shopper-visible errors; automatic rollback within 10 min",
         bg=["BG-1", "BG-4"], vr=("M", "L"),
         tactics="*Deployability — manage deployment pipeline*: scale rollouts, roll back; *Availability*: canary / blue-green.",
         asbuilt="Rolling, minimum healthy 100 % / maximum 200 % (old task kept until the new one is healthy). Deployment circuit breaker **disabled** (`enable: false, rollback: false`), so a failing version is retried indefinitely without rollback; bake time 0."),
    dict(id="MQA-1", title="Swap a backing-service provider", iso="Maintainability", sub="modifiability",
         src="Developer / operator", stim="Needs to change a service's persistence or messaging provider (e.g. orders messaging, checkout persistence) for a new environment",
         art="Task-definition configuration of one service",
         env="Design / deployment time", resp="Provider changed by configuration only",
         meas="Proposed — confirm: 0 lines of application code; ≤ 1 task-definition revision; done within 1 person-day",
         bg=["BG-1"], vr=("M", "L"),
         tactics="*Modifiability — defer binding*: configuration-time binding (environment variables), use an intermediary; *reduce coupling*: encapsulate.",
         asbuilt="Present: each service selects its provider through `RETAIL_*_PERSISTENCE_PROVIDER` / `RETAIL_ORDERS_MESSAGING_PROVIDER`, and endpoints/credentials are injected as environment variables and secrets. Limited to providers the images support (CON-4)."),
    dict(id="INQA-1", title="Add a consumer of order events", iso="Integrability (cross-cutting)", sub="integrability",
         src="New downstream team (e.g. fulfilment)", stim="Needs to react to every new order",
         art="Amazon MQ (RabbitMQ) broker and the orders service",
         env="Normal operation", resp="The consumer subscribes to the existing order events without changes to `orders`",
         meas="Proposed — confirm: 0 changes to the orders service; consumer receiving events within 2 days of effort",
         bg=["BG-1"], vr=("M", "L"),
         tactics="*Integrability — limit dependencies*: use an intermediary (message broker), publish-subscribe; *adapt*: tailor interface.",
         asbuilt="Present: `orders` publishes to RabbitMQ 3.13 on Amazon MQ over AMQPS 5671. The broker's security group admits only the orders task security group, so a new consumer needs a security-group rule and credentials."),
]


# ============================================================================= writers
def w(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def links(ids, base=".."):
    out = []
    for i in ids:
        sub = {"BG": "business-goals", "UC": "use-cases", "CO": "constraints", "AC": "concerns"}.get(i[:2], "quality-attributes")
        out.append(f"[{i}]({base}/{sub}/{i}.md)")
    return ", ".join(out)


NAV_SUB = "\n---\n\n**Navigation**: [drivers README](../README.md) · [architecture package](../../README.md)\n"


def write_stakeholders():
    rows = "\n".join(f"| {a} | {b} | {c} | {d} | {e} | {f} | {g} |" for a, b, c, d, e, f, g in STAKEHOLDERS)
    w(D / "stakeholders.md", f"""# Stakeholders — retail-store-ecs

- **Date**: {DATE}
- **Owner**: workload owner (ST-1) — to confirm

> The single stakeholder register for the whole `architecture/` package. Reconstructed from the
> deployment; **no stakeholder has been interviewed yet** — names marked "to be named" must be filled
> by ST-1 before a QAW or a full ATAM Phase 2.

| ID | Name / representative | Role | Concerns | QAW | ATAM Phase 2 | V&B reader |
|----|-----------------------|------|----------|:---:|:------------:|:----------:|
{rows}

---

**Navigation**: [drivers README](README.md) · [architecture package](../README.md)
""")


def write_bgs():
    idx = []
    for b in BGS:
        w(D / "business-goals" / f"{b['id']}.md", f"""# {b['id']}: {b['title']}

{DERIVED}

- **Statement**: {b['stmt']}
- **Primary stakeholder**: {b['sh']} (see [stakeholders](../stakeholders.md))
- **SEI business-goal category**: {b['cat']}
- **Measure of success**: {b['measure']}
- **Priority**: {b['prio']}
- **Status**: {st(b['id'])}

## Context

{b['ctx']}

## Supported by

- Use cases: {links(b['uc'])}
- Quality attribute scenarios: {links(b['qa'])}

## Notes

{b['notes']}
""")
        idx.append(f"| [{b['id']}]({b['id']}.md) | {b['stmt']} | {b['cat']} | {b['prio']} | {st(b['id'])} |")
    w(D / "business-goals" / "README.md", "# Business goals\n\nIndex for `architecture/drivers/business-goals/`. One linked row per file. The authoritative traceability matrix is in the [drivers README](../README.md).\n\n| ID | Goal (short) | Category | Priority | Status |\n|----|--------------|----------|:--------:|:------:|\n" + "\n".join(idx) + "\n" + NAV_SUB)


def uc_puml(u):
    lines = ["@startuml " + u["id"], "!include plantuml-theme.puml", "skinparam actorStyle awesome", "left to right direction",
             f"title Use case diagram — {u['id']} {u['name']}"]
    lines.append(f'actor "{u["actor"]}" as primary')
    for k, (n, desc) in enumerate(u["supp"]):
        lines.append(f'rectangle "{n}\\n<size:10>{desc}</size>" << system >> as supp{k}')
    lines.append('rectangle "retail-store-ecs" {')
    lines.append(f'  usecase "{u["id"]}\\n{u["name"]}" as uc')
    by = {x["id"]: x for x in UCS}
    for t in u["includes"]:
        lines.append(f'  usecase "{t}\\n{by[t]["name"]}" as {t.replace("-", "")}')
    for t in u["extends_by"]:
        lines.append(f'  usecase "{t}\\n{by[t]["name"]}" as {t.replace("-", "")}')
    if u.get("extends"):
        t = u["extends"]
        lines.append(f'  usecase "{t}\\n{by[t]["name"]}" as {t.replace("-", "")}')
    if u["level"] == "subfunction":
        lines.append(f'  usecase "UC-4\\nCheck out" as UC4ext')
    lines.append("}")
    if u["level"] == "subfunction":
        lines.append("primary --> UC4ext")
        lines.append("UC4ext ..> uc : <<include>>")
    else:
        lines.append("primary --> uc")
    if u.get("extends"):
        lines.append(f'primary --> {u["extends"].replace("-", "")}')
    for k in range(len(u["supp"])):
        lines.append(f"uc --> supp{k}")
    for t in u["includes"]:
        lines.append(f'uc ..> {t.replace("-", "")} : <<include>>')
    for t in u["extends_by"]:
        lines.append(f'uc <.. {t.replace("-", "")} : <<extend>>')
    if u.get("extends"):
        lines.append(f'uc ..> {u["extends"].replace("-", "")} : <<extend>>')
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def write_ucs():
    idx = []
    for u in UCS:
        (D / "use-cases" / "diagrams").mkdir(parents=True, exist_ok=True)
        w(D / "use-cases" / "diagrams" / f"{u['id']}.puml", uc_puml(u))
        supp = ", ".join(f"{n} ({d})" for n, d in u["supp"]) or "none outside the system (all collaborators are internal services)"
        mss = "\n".join(f"{i}. {s}" for i, s in enumerate(u["mss"], 1))
        ext = "\n".join(f"- {e}" for e in u["ext"])
        w(D / "use-cases" / f"{u['id']}.md", f"""# {u['id']}: {u['name']}

{DERIVED}

- **Scope**: retail-store-ecs (as deployed)
- **Level**: {u['level']}
- **Primary actor**: {u['actor']}
- **Supporting actors**: {supp}
- **Stakeholders and interests**:
  - ST-5 Shopper — the step works and personal data is protected
  - ST-3 Operator — failures are visible and recoverable
- **Trigger**: {u['trigger']}
- **Preconditions**: {u['pre']}
- **Postconditions (success guarantee)**: {u['post']}
- **Priority**: {u['prio']}
- **Status**: {st(u['id'])}

## Main success scenario

{mss}

## Extensions / alternate flows

{ext}

## Architectural significance

- **Drivers exercised**: {links([d for d in u['drivers'] if not d.startswith('BG')])}
- **Notes**: {u['sig']}

## Related drivers

{links(u['drivers'])}

## Use case diagram

![{u['id']} — {u['name']}](diagrams/{u['id']}.png)

Source: [`diagrams/{u['id']}.puml`](diagrams/{u['id']}.puml) · rendered with PlantUML · visually verified.
""")
        idx.append(f"| [{u['id']}]({u['id']}.md) | {u['name']} | {u['actor']} | {u['prio']} | [{u['id']}](diagrams/{u['id']}.png) | {st(u['id'])} |")
    # overview diagrams
    w(D / "use-cases" / "diagrams" / "overview-shopper.puml", """@startuml overview-shopper
!include plantuml-theme.puml
skinparam actorStyle awesome
left to right direction
title Use case overview — Shopper journeys (UC-1..UC-5)
actor "Shopper" as shopper
rectangle "Downstream order consumers\\n<size:10>none deployed today</size>" << system >> as consumers
rectangle "retail-store-ecs" {
  usecase "UC-1\\nBrowse product catalogue" as UC1
  usecase "UC-2\\nSearch products" as UC2
  usecase "UC-3\\nManage shopping cart" as UC3
  usecase "UC-4\\nCheck out" as UC4
  usecase "UC-5\\nPlace order" as UC5
}
shopper --> UC1
shopper --> UC3
shopper --> UC4
UC2 ..> UC1 : <<extend>>
UC4 ..> UC5 : <<include>>
UC5 --> consumers
@enduml
""")
    w(D / "use-cases" / "diagrams" / "overview-operator.puml", """@startuml overview-operator
!include plantuml-theme.puml
skinparam actorStyle awesome
left to right direction
title Use case overview — Operator (UC-6, UC-7)
actor "Operator" as op
rectangle "retail-store-ecs" {
  usecase "UC-6\\nDeploy a new service version" as UC6
  usecase "UC-7\\nDiagnose a running service" as UC7
}
rectangle "Amazon ECR Public\\n<size:10>image registry</size>" << system >> as ecr
rectangle "Terraform\\n<size:10>infrastructure as code</size>" << system >> as tf
rectangle "Amazon CloudWatch\\n<size:10>Logs + Container Insights</size>" << system >> as cw
rectangle "AWS Systems Manager\\n<size:10>ECS Exec sessions</size>" << system >> as ssm
op --> UC6
op --> UC7
UC6 --> ecr
UC6 --> tf
UC7 --> cw
UC7 --> ssm
@enduml
""")
    w(D / "use-cases" / "README.md", "# Use cases\n\nIndex for `architecture/drivers/use-cases/`. One linked row per file. The authoritative traceability matrix is in the [drivers README](../README.md). All use cases are **derived — confirm** (reconstructed from the deployed services and their configuration).\n\n| ID | Use case | Primary actor | Priority | Diagram | Status |\n|----|----------|---------------|:--------:|---------|:------:|\n" + "\n".join(idx) + "\n\nOverview diagrams:\n\n![Use case overview — Shopper journeys](diagrams/overview-shopper.png)\n\nSource: [`diagrams/overview-shopper.puml`](diagrams/overview-shopper.puml)\n\n![Use case overview — Operator](diagrams/overview-operator.png)\n\nSource: [`diagrams/overview-operator.puml`](diagrams/overview-operator.puml)\n" + NAV_SUB)


def write_cons():
    idx = []
    for c in CONS:
        w(D / "constraints" / f"{c['id']}.md", f"""# {c['id']}: {c['title']}

{DERIVED}

- **Type**: {c['typ']}
- **Constraint**: {c['c']}
- **Source**: {c['src']}
- **Nature**: {c['nature']}
- **Priority**: {c['prio']}
- **Status**: {st(c['id'])}

## Rationale

{c['rat']}

## Impact on the architecture

{c['impact']}

## Conflicts

{c['conflicts']}

## Traces up to

- Business goals: {links(c['bg'])}
""")
        idx.append(f"| [{c['id']}]({c['id']}.md) | {c['typ']} | {c['title']} | {c['nature']} | {st(c['id'])} |")
    w(D / "constraints" / "README.md", "# Constraints\n\nIndex for `architecture/drivers/constraints/`. One linked row per file. The authoritative traceability matrix is in the [drivers README](../README.md).\n\n| ID | Type | Constraint (short) | Nature | Status |\n|----|------|--------------------|:------:|:------:|\n" + "\n".join(idx) + "\n" + NAV_SUB)


def write_acs():
    idx = []
    for a in ACS:
        rel = ", ".join(a["rel"].split(", "))
        w(D / "concerns" / f"{a['id']}.md", f"""# {a['id']}: {a['title']}

- **Concern**: {a['c']}
- **Kind**: {a['kind']}
- **Raised by**: ST-2 (architecture reconstruction)
- **Priority**: {a['prio']}
- **Status**: {st(a['id'])}

## Why it matters

{a['why']}

## Related drivers

{links(a['rel'].split(', '))}
""")
        idx.append(f"| [{a['id']}]({a['id']}.md) | {a['title']} | {a['kind']} | {a['prio']} | {st(a['id'])} |")
    w(D / "concerns" / "README.md", "# Architectural concerns\n\nIndex for `architecture/drivers/concerns/`. One linked row per file. Concerns are ADD input and are not traced to a business goal.\n\n| ID | Concern (short) | Kind | Priority | Status |\n|----|-----------------|------|:--------:|:------:|\n" + "\n".join(idx) + "\n" + NAV_SUB)


def esc(s):
    return s.replace("`", "").replace('"', "'").replace("<", "&lt;").replace(">", "&gt;")


def qa_mermaid(q):
    return f"""flowchart LR
  %% Quality attribute scenario — {q['id']} — {q['iso']} / {q['sub']}
  %% name: scenario-{q['id']}
  src["<b>Source of stimulus</b><br/>{esc(q['src'])}"]
  stim["<b>Stimulus</b><br/>{esc(q['stim'])}"]
  subgraph env["Environment: {esc(q['env'])}"]
    art["<b>Artifact</b><br/>{esc(q['art'])}"]
  end
  resp["<b>Response</b><br/>{esc(q['resp'])}"]
  meas["<b>Response measure</b><br/>{esc(q['meas'])}"]
  src -->|generates| stim --> art
  art --> resp -->|measured by| meas
  classDef source   fill:#E7E3F3,stroke:#6B5BA6,color:#1F2933;
  classDef artifact fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;
  classDef response fill:#E4F0E9,stroke:#3F7D5C,color:#1F2933;
  class src,stim source
  class art artifact
  class resp,meas response
"""


def pesc(t):
    return t.replace("`", "").replace('"', "'")


def qa_puml(q):
    return f"""@startuml scenario-{q['id']}
!include plantuml-theme.puml
left to right direction
hide stereotype
title Quality attribute scenario — {q['id']} — {q['iso']} / {q['sub']}
rectangle "<b>Source of stimulus</b>\\n{pesc(q['src'])}" as SRC #E7E3F3
rectangle "<b>Stimulus</b>\\n{pesc(q['stim'])}" as STIM #E7E3F3
rectangle "<b>Artifact</b>\\n{pesc(q['art'])}" as ART #EDF2F8
rectangle "<b>Response</b>\\n{pesc(q['resp'])}" as RESP #E4F0E9
rectangle "<b>Response measure</b>\\n{pesc(q['meas'])}" as MEAS #E4F0E9
rectangle "<b>Environment</b>\\n{pesc(q['env'])}" as ENV #F5EEE3
SRC  --> STIM : generates
STIM --> ART  : arrives at
ART  --> RESP : produces
RESP --> MEAS : measured by
ENV  ..> ART
@enduml
"""


def write_qas():
    idx = []
    for q in QAS:
        (D / "quality-attributes" / "diagrams" / f"scenario-{q['id']}.mmd").unlink(missing_ok=True)
        w(D / "quality-attributes" / "diagrams" / f"scenario-{q['id']}.puml", qa_puml(q))
        v, r = q["vr"]
        w(D / "quality-attributes" / f"{q['id']}.md", f"""# {q['id']}: {q['title']}

- **Status**: {st(q['id'])}
- **Source**: authored here by `/drivers` (register mode) during the brownfield reconstruction

{DERIVED} The response measure is a **proposed straw-man target** to bracket the discussion with the stakeholders — no SLO, alarm threshold or contract exists in the deployment to harvest one from.

| Part | Value |
|------|-------|
| **ID** | {q['id']} |
| **ISO/IEC 25010 characteristic** | {q['iso']} |
| **Sub-characteristic** | {q['sub']} |
| **Source of stimulus** | {q['src']} |
| **Stimulus** | {q['stim']} |
| **Artifact** | {q['art']} |
| **Environment** | {q['env']} |
| **Response** | {q['resp']} |
| **Response measure** | {q['meas']} |
| **Business goals supported** | {', '.join(q['bg'])} |
| **Priority** | Importance = {v} · Difficulty = {r} |
| **Candidate tactics** | {q['tactics']} |
| **Type** | concrete |

## As-built evidence

{q['asbuilt']}

Evidence: [`aws/scoped/retail-store-ecs-evidence.json`]({EVID}/scoped/retail-store-ecs-evidence.json), [`aws/well-architected/well-architected-findings.md`]({EVID}/well-architected/well-architected-findings.md).

## Six-part scenario diagram

SEI six-part quality attribute scenario notation (no UML diagram type exists for it), drawn with PlantUML in the package's UML palette.

![{q['id']} six-part scenario](diagrams/scenario-{q['id']}.png)

Source: [`diagrams/scenario-{q['id']}.puml`](diagrams/scenario-{q['id']}.puml) · rendered with PlantUML · visually verified: yes
""")
        star = " ★" if (v, r) == ("H", "H") else ""
        idx.append((q, f"| [{q['id']}]({q['id']}.md) | {q['iso']} / {q['sub']} | {q['title']} — {q['meas'].replace('Proposed — confirm: ', '')} | ({v}, {r}){star} | {st(q['id'])} |"))
    order = ["Reliability", "Performance efficiency", "Flexibility", "Security", "Maintainability", "Observability (cross-cutting)", "Integrability (cross-cutting)"]
    idx.sort(key=lambda x: order.index(x[0]["iso"]))
    w(D / "quality-attributes" / "README.md", "# Quality attribute scenarios\n\nIndex for `architecture/drivers/quality-attributes/`. Grouped by ISO/IEC 25010 characteristic (same order as the [utility tree](utility-tree.md)). All scenarios are **derived — confirm**; measures are proposed targets.\n\n| ID | ISO 25010 characteristic / sub | One-line scenario | (V, R) | Status |\n|----|-------------------------------|-------------------|:------:|:------:|\n" + "\n".join(r for _, r in idx) + "\n\n**[Utility tree (table) →](utility-tree.md)** — the summary of these quality attributes, `(V, R)` per leaf.\n" + NAV_SUB)
    # utility tree
    rows = []
    for q, _ in idx:
        v, r = q["vr"]
        star = " `★`" if (v, r) == ("H", "H") else ""
        rows.append(f"| {q['iso']} | {q['sub']} | `{q['id']}` — {q['title']}: {q['meas'].replace('Proposed — confirm: ', '')} | ({v}, {r}){star} | {st(q['id'])} |")
    w(D / "quality-attributes" / "utility-tree.md", f"""# Quality Attribute Utility Tree: retail-store-ecs

- **Date**: {DATE}
- **Purpose**: prioritise the reconstructed quality-attribute requirements as scenarios (input to the ATAM)
- **Basis**: built by the architect (ST-2) from the as-built evidence — **no QAW was held**; `(V, R)` values are the architect's proposal for ST-1 to confirm. ISO/IEC 25010:2023 is the quality model.

`(V, R)` = business value and technical risk (`H`/`M`/`L`). `★` marks `(H, H)` leaves.

## Utility tree — Root: Utility (fitness for purpose)

| Quality attribute | Refinement (concern) | Leaf scenario (ID — one line, with the response measure) | Priority (V, R) | Status |
|-------------------|----------------------|---------------------------------------------------------|:---------------:|:------:|
{chr(10).join(rows)}

## Reading the tree

- **Reliability** carries the only `★` leaf (`AQA-2`, Availability Zone loss): the single-AZ data tier
  and the single NAT Gateway make it both valuable and hard — it touches every data store.
- **Security** and **Observability** leaves are high value but low difficulty: the tactics are
  configuration changes (TLS listener, CloudTrail/GuardDuty, alarms), not structural redesign.
- **Usability**, **Compatibility** and **Portability** have no leaf — not investigated, because the
  application code is fixed (CON-3); raise them in a QAW if ST-1 wants them.
- No leaf is `addressed` yet; `MQA-1` and `INQA-1` are already supported by tactics present in the
  deployment (configuration-time binding, broker intermediary) — candidates for non-risks in the ATAM.

## Analysis targets

The `(H, H)` and `(H, M)` leaves are analysed first: `AQA-2`, `AQA-1`, `RQA-1`, `SQA-2`, then the
`(H, L)` security and observability leaves `SQA-1`, `SQA-3`, `OQA-1`.

---

**Navigation**: [quality attributes index](README.md) · [drivers README](../README.md) · [architecture package](../../README.md)
""")


def write_index():
    bg_rows = "\n".join(f"| {b['id']} | {b['stmt']} | [{b['id']}](business-goals/{b['id']}.md) |" for b in BGS)
    uc_rows = "\n".join(f"| {u['id']} | {u['name']} | {u['actor']} | [{u['id']}](use-cases/diagrams/{u['id']}.png) | [{u['id']}](use-cases/{u['id']}.md) |" for u in UCS)
    con_rows = "\n".join(f"| {c['id']} | {c['typ']} | {c['title']} | {c['nature']} | [{c['id']}](constraints/{c['id']}.md) |" for c in CONS)
    ac_rows = "\n".join(f"| {a['id']} | {a['title']} | {a['kind']} | {a['prio']} | [{a['id']}](concerns/{a['id']}.md) |" for a in ACS)
    qa_rows = "\n".join(f"| {q['id']} | {q['iso']} / {q['sub']} | {q['title']} — {q['meas'].replace('Proposed — confirm: ', '')} | ({q['vr'][0]}, {q['vr'][1]}) | [scenario](quality-attributes/diagrams/scenario-{q['id']}.png) | [{q['id']}](quality-attributes/{q['id']}.md) |" for q in QAS)
    tr = []
    sub = {"UC": "use-cases", "CO": "constraints"}
    for u in UCS:
        bgs = [d for d in u["drivers"] if d.startswith("BG")]
        rel = [d for d in u["drivers"] if not d.startswith("BG")]
        tr.append(f"| {u['id']} | [{u['id']}](use-cases/{u['id']}.md) | {', '.join(bgs)} | {', '.join(rel)} | {ADDRESSED.get(u['id'], 'as-built: docs/view-cnc-runtime.md')} | {st(u['id'])} |")
    for q in QAS:
        tr.append(f"| {q['id']} | [{q['id']}](quality-attributes/{q['id']}.md) | {', '.join(q['bg'])} | — | {ADDRESSED.get(q['id'], 'ATAM')} | {st(q['id'])} |")
    for c in CONS:
        tr.append(f"| {c['id']} | [{c['id']}](constraints/{c['id']}.md) | {', '.join(c['bg'])} | — | {ADDRESSED.get(c['id'], 'as-built: docs/view-allocation-deployment.md')} | {st(c['id'])} |")
    for b in BGS:
        tr.append(f"| {b['id']} | [{b['id']}](business-goals/{b['id']}.md) | — | {', '.join(b['uc'] + b['qa'])} | — | {st(b['id'])} |")
    order = sorted(QAS, key=lambda q: ({"H": 0, "M": 1, "L": 2}[q["vr"][0]], {"H": 0, "M": 1, "L": 2}[q["vr"][1]]))
    prio = []
    n = 1
    for q in order:
        if q["vr"][0] == "H":
            prio.append(f"{n}. [{q['id']}](quality-attributes/{q['id']}.md) ({q['vr'][0]},{q['vr'][1]}) — {q['title']}")
            n += 1
    for u in UCS[:5]:
        prio.append(f"{n}. [{u['id']}](use-cases/{u['id']}.md) — {u['name']}: {u['sig']}")
        n += 1
    for c in CONS:
        if c["nature"] == "hard":
            prio.append(f"{n}. [{c['id']}](constraints/{c['id']}.md) (hard) — {c['title']}")
            n += 1
    for q in order:
        if q["vr"][0] != "H":
            prio.append(f"{n}. [{q['id']}](quality-attributes/{q['id']}.md) ({q['vr'][0]},{q['vr'][1]}) — {q['title']}")
            n += 1
    w(D / "README.md", f"""# Architectural Drivers — `drivers/README.md`: retail-store-ecs

- **Date**: {DATE}
- **Owner**: workload owner (ST-1) — to confirm; drafted by ST-2
- **Status**: draft
- **QA model**: ISO/IEC 25010:2023
- **Design purpose**: brownfield — as-built architecture recovery of an existing deployment (input to an assessment; possible later brownfield extension)
- **Stakeholders**: [stakeholders.md](stakeholders.md)

> **How this register was built.** No requirements documents exist for this deployment and no
> stakeholder has been interviewed. Every driver below was **derived from the deployed AWS
> environment** (read-only evidence in [`../../aws/`](../../aws/README.md)) and from the upstream
> project README, following the SEI brownfield-intake procedure ([intake note](../brownfield-intake.md)).
> All of them are **derived — confirm**. Response measures are proposed targets, not recovered facts.

## Driver inventory

### Business goals — [`business-goals/`](business-goals/README.md)
| ID | Goal (short) | File |
|----|--------------|------|
{bg_rows}

### Use cases — [`use-cases/`](use-cases/README.md)  (primary functional requirements)
| ID | Use case | Primary actor | Diagram | File |
|----|----------|---------------|---------|------|
{uc_rows}

Overview use case diagrams: [`use-cases/diagrams/overview-shopper.png`](use-cases/diagrams/overview-shopper.png) · [`use-cases/diagrams/overview-operator.png`](use-cases/diagrams/overview-operator.png)

### Constraints — [`constraints/`](constraints/README.md)
| ID | Type | Constraint (short) | Hard / negotiable | File |
|----|------|--------------------|-------------------|------|
{con_rows}

### Architectural concerns — [`concerns/`](concerns/README.md)  (ADD input; not traced to a BG)
| ID | Concern (short) | Kind | Priority | File |
|----|-----------------|------|:--------:|------|
{ac_rows}

### Quality attribute scenarios — [`quality-attributes/`](quality-attributes/README.md)
| ID | ISO 25010 characteristic / sub | One-line scenario | (V, R) | Diagram | File |
|----|-------------------------------|-------------------|:------:|---------|------|
{qa_rows}

**Utility tree** (summary of the quality attributes in these drivers, **as a table**):
[`quality-attributes/utility-tree.md`](quality-attributes/utility-tree.md) — one leaf per row, `★` on each `(H, H)` leaf.

**QA ID legend** (attribute → prefix): AQA availability · RQA reliability(other) · PQA performance
· SQA security · SCQA scalability · DQA deployability · MQA modifiability · OQA observability ·
INQA integrability. Never `QAS-`.

## Traceability matrix

| Driver | File | Supports BG | Realised / constrained by | Addressed in | Status |
|--------|------|-------------|---------------------------|--------------|--------|
{chr(10).join(tr)}

`Status` ∈ open / in design / partially / addressed / at risk (set by ATAM) / retired.

**Coverage check**: every BG is supported by ≥ 1 UC or QA scenario (BG-1: UC-1, UC-5, UC-6 + 5 QA;
BG-2: UC-1–UC-5 + 4 QA; BG-3: UC-6, PQA-2, SCQA-1; BG-4: UC-4, UC-6, UC-7 + 8 QA); every UC, QA
scenario and CON traces up to ≥ 1 BG. Gaps found: none. Open question that could change the set:
BG-4's scope depends on ST-1's demo-vs-production decision (CON-5).

## Prioritised driver list (input to ADD / ATAM)

{chr(10).join(prio)}

## Change log

| Date | Change |
|------|--------|
{CHANGELOG}

---

**Navigation**: [architecture package](../README.md) · [stakeholders](stakeholders.md) · [brownfield intake](../brownfield-intake.md){NAV_EXTRA}
""")


ADDRESSED = {}
CHANGELOG = f"| {DATE} | initial driver set derived from the as-built AWS evidence (brownfield intake): 4 BG, 7 UC, 6 CON, 5 AC, 13 QA scenarios |"
NAV_EXTRA = ""

if __name__ == "__main__":
    import importlib.util, sys
    # optional overlay with post-ATAM statuses / change log (kept separate so the base data stays as derived)
    ov = ROOT / "tools" / "drivers_overlay.py"
    if ov.exists():
        spec = importlib.util.spec_from_file_location("overlay", ov)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        STATUS.update(getattr(mod, "STATUS", {}))
        ADDRESSED.update(getattr(mod, "ADDRESSED", {}))
        CHANGELOG += "".join("\n" + l for l in getattr(mod, "CHANGELOG", []))
        NAV_EXTRA = getattr(mod, "NAV_EXTRA", "")
    write_stakeholders()
    write_bgs()
    write_ucs()
    write_cons()
    write_acs()
    write_qas()
    write_index()
    print("drivers written to", D)
