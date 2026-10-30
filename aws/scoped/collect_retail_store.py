"""Read-only, scoped evidence collector for the retail-store-ecs environment.

Complements the account-wide inventory from aws-architecture-discovery with the
detail an architecture reconstruction needs (task definitions, Service Connect,
listeners/target groups, Amazon MQ, OpenSearch, scaling, logging, IAM).

Only Describe*/List*/Get* calls are made. Secret values are never read:
Secrets Manager is queried for metadata only, and environment variables whose
name looks credential-like are redacted.

Usage: AWS_USE_DUALSTACK_ENDPOINT=true python collect_retail_store.py out.json
"""
import json
import re
import sys
from datetime import datetime

import boto3

ENV = "retail-store-ecs"
CLUSTER = f"{ENV}-cluster"
REGION = "eu-central-1"
SENSITIVE = re.compile(r"PASS|SECRET|TOKEN|KEY|CREDENTIAL", re.I)

s = boto3.Session(region_name=REGION)
out = {"Environment": ENV, "Region": REGION, "CollectedAt": datetime.utcnow().isoformat() + "Z"}


def safe(name, fn):
    try:
        out[name] = fn()
    except Exception as e:  # keep going; record why a section is empty
        out[name] = {"_error": f"{type(e).__name__}: {e}"}


def redact_env(td):
    for c in td.get("containerDefinitions", []):
        for e in c.get("environment", []):
            if SENSITIVE.search(e["name"]):
                e["value"] = "<redacted>"
    return td


ecs = s.client("ecs")
ec2 = s.client("ec2")
elb = s.client("elbv2")


def ecs_section():
    cl = ecs.describe_clusters(clusters=[CLUSTER], include=["SETTINGS", "CONFIGURATIONS", "STATISTICS", "TAGS"])["clusters"]
    arns = ecs.list_services(cluster=CLUSTER, maxResults=100)["serviceArns"]
    svcs = ecs.describe_services(cluster=CLUSTER, services=arns, include=["TAGS"])["services"]
    tds = {}
    for sv in svcs:
        td = ecs.describe_task_definition(taskDefinition=sv["taskDefinition"], include=["TAGS"])["taskDefinition"]
        tds[sv["serviceName"]] = redact_env(td)
    tasks = []
    tarns = ecs.list_tasks(cluster=CLUSTER)["taskArns"]
    if tarns:
        tasks = ecs.describe_tasks(cluster=CLUSTER, tasks=tarns)["tasks"]
    return {"Cluster": cl, "Services": svcs, "TaskDefinitions": tds, "Tasks": tasks}


def network_section():
    vpcs = ec2.describe_vpcs(Filters=[{"Name": "tag:environment-name", "Values": [ENV]}])["Vpcs"]
    vid = [v["VpcId"] for v in vpcs]
    f = [{"Name": "vpc-id", "Values": vid}]
    return {
        "Vpcs": vpcs,
        "Subnets": ec2.describe_subnets(Filters=f)["Subnets"],
        "RouteTables": ec2.describe_route_tables(Filters=f)["RouteTables"],
        "InternetGateways": ec2.describe_internet_gateways(Filters=[{"Name": "attachment.vpc-id", "Values": vid}])["InternetGateways"],
        "NatGateways": ec2.describe_nat_gateways(Filter=f)["NatGateways"],
        "VpcEndpoints": ec2.describe_vpc_endpoints(Filters=f)["VpcEndpoints"],
        "SecurityGroups": ec2.describe_security_groups(Filters=f)["SecurityGroups"],
        "NetworkAcls": ec2.describe_network_acls(Filters=f)["NetworkAcls"],
        "FlowLogs": ec2.describe_flow_logs(Filters=[{"Name": "resource-id", "Values": vid}])["FlowLogs"],
        "NetworkInterfaces": [
            {k: n.get(k) for k in ("NetworkInterfaceId", "SubnetId", "AvailabilityZone", "Description", "InterfaceType", "PrivateIpAddress", "Groups", "RequesterId")}
            for n in ec2.describe_network_interfaces(Filters=f)["NetworkInterfaces"]
        ],
    }


def lb_section():
    lbs = [l for l in elb.describe_load_balancers()["LoadBalancers"] if l["LoadBalancerName"].startswith(ENV)]
    res = []
    for l in lbs:
        arn = l["LoadBalancerArn"]
        tgs = elb.describe_target_groups(LoadBalancerArn=arn)["TargetGroups"]
        res.append({
            "LoadBalancer": l,
            "Attributes": elb.describe_load_balancer_attributes(LoadBalancerArn=arn)["Attributes"],
            "Listeners": [
                {**li, "Rules": elb.describe_rules(ListenerArn=li["ListenerArn"])["Rules"]}
                for li in elb.describe_listeners(LoadBalancerArn=arn)["Listeners"]
            ],
            "TargetGroups": [
                {**t, "Health": elb.describe_target_health(TargetGroupArn=t["TargetGroupArn"])["TargetHealthDescriptions"]}
                for t in tgs
            ],
        })
    return res


def data_section():
    rds = s.client("rds")
    clusters = [c for c in rds.describe_db_clusters()["DBClusters"] if c["DBClusterIdentifier"].startswith(ENV)]
    insts = [i for i in rds.describe_db_instances()["DBInstances"] if i["DBInstanceIdentifier"].startswith(ENV)]
    ddb = s.client("dynamodb")
    t = ddb.describe_table(TableName=f"{ENV}-carts")["Table"]
    ddb_extra = {
        "Backups": ddb.describe_continuous_backups(TableName=t["TableName"])["ContinuousBackupsDescription"],
    }
    ec = s.client("elasticache")
    rg = ec.describe_replication_groups(ReplicationGroupId=f"{ENV}-checkout")["ReplicationGroups"]
    ecc = ec.describe_cache_clusters(ShowCacheNodeInfo=True)["CacheClusters"]
    mq = s.client("mq")
    brokers = [mq.describe_broker(BrokerId=b["BrokerId"]) for b in mq.list_brokers()["BrokerSummaries"] if b["BrokerName"].startswith(ENV)]
    for b in brokers:
        b.pop("ResponseMetadata", None)
    os_ = s.client("opensearch")
    dom = os_.describe_domain(DomainName=f"{ENV}-catalog")["DomainStatus"]
    return {
        "RdsClusters": clusters, "RdsInstances": insts,
        "DynamoDb": {"Table": t, **ddb_extra},
        "ElastiCacheReplicationGroups": rg,
        "ElastiCacheClusters": [c for c in ecc if c["CacheClusterId"].startswith(ENV)],
        "MqBrokers": brokers,
        "OpenSearchDomain": dom,
    }


def platform_section():
    sm = s.client("secretsmanager")
    secrets = [
        {k: x.get(k) for k in ("Name", "ARN", "KmsKeyId", "RotationEnabled", "LastChangedDate", "Description")}
        for x in sm.list_secrets(MaxResults=100)["SecretList"]
        if ENV in x["Name"] or "retail" in x["Name"]
    ]
    ssm = s.client("ssm")
    params = [
        {k: p.get(k) for k in ("Name", "Type", "LastModifiedDate")}
        for p in ssm.describe_parameters(ParameterFilters=[{"Key": "Name", "Option": "Contains", "Values": ["retail"]}])["Parameters"]
    ]
    logs = s.client("logs")
    lgs = logs.describe_log_groups(logGroupNamePrefix=ENV)["logGroups"]
    lgs += [g for g in logs.describe_log_groups()["logGroups"] if "retail" in g["logGroupName"] and g not in lgs]
    cw = s.client("cloudwatch")
    alarms = [a for a in cw.describe_alarms()["MetricAlarms"] if ENV in a["AlarmName"] or any(ENV in str(d.get("Value")) for d in a.get("Dimensions", []))]
    dashboards = [d for d in cw.list_dashboards()["DashboardEntries"] if "retail" in d["DashboardName"]]
    aas = s.client("application-autoscaling")
    targets = [t for t in aas.describe_scalable_targets(ServiceNamespace="ecs")["ScalableTargets"] if CLUSTER in t["ResourceId"]]
    policies = [p for p in aas.describe_scaling_policies(ServiceNamespace="ecs")["ScalingPolicies"] if CLUSTER in p["ResourceId"]]
    sd = s.client("servicediscovery")
    ns = sd.list_namespaces()["Namespaces"]
    sd_services = sd.list_services()["Services"]
    return {
        "Secrets": secrets, "SsmParameters": params, "LogGroups": lgs,
        "Alarms": alarms, "Dashboards": dashboards,
        "ScalableTargets": targets, "ScalingPolicies": policies,
        "CloudMapNamespaces": ns, "CloudMapServices": sd_services,
    }


def iam_section(td_map):
    iam = s.client("iam")
    roles = set()
    for td in td_map.values():
        for k in ("taskRoleArn", "executionRoleArn"):
            if td.get(k):
                roles.add(td[k].split("/")[-1])
    res = {}
    for r in sorted(roles):
        res[r] = {
            "Role": iam.get_role(RoleName=r)["Role"],
            "Attached": iam.list_attached_role_policies(RoleName=r)["AttachedPolicies"],
            "Inline": {
                p: iam.get_role_policy(RoleName=r, PolicyName=p)["PolicyDocument"]
                for p in iam.list_role_policies(RoleName=r)["PolicyNames"]
            },
        }
        for a in res[r]["Attached"]:
            if ":aws:policy/" not in a["PolicyArn"]:
                pol = iam.get_policy(PolicyArn=a["PolicyArn"])["Policy"]
                a["Document"] = iam.get_policy_version(PolicyArn=a["PolicyArn"], VersionId=pol["DefaultVersionId"])["PolicyVersion"]["Document"]
    return res


safe("Ecs", ecs_section)
safe("Network", network_section)
safe("LoadBalancers", lb_section)
safe("DataStores", data_section)
safe("Platform", platform_section)
if isinstance(out.get("Ecs"), dict) and "TaskDefinitions" in out["Ecs"]:
    safe("Iam", lambda: iam_section(out["Ecs"]["TaskDefinitions"]))

json.dump(out, open(sys.argv[1], "w"), indent=2, default=str)
for k, v in out.items():
    if isinstance(v, dict) and "_error" in v:
        print("ERROR", k, v["_error"])
print("written", sys.argv[1])
