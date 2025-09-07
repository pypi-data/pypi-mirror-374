"""
FIS MCP Server - Python Implementation
Converted from Node.js MCP server for AWS Fault Injection Simulator
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import boto3
from botocore.config import Config
import mcp.server.stdio
import mcp.types as types
from mcp.server.fastmcp import FastMCP

from validate.validator import ExperimentValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS client configuration with timeout
def _get_aws_config():
    """Get AWS client configuration with timeout settings"""
    return Config(
        read_timeout=300,
        connect_timeout=60,
        retries={'max_attempts': 3}
    )

mcp = FastMCP("failure-invoker-mcp")
validator = ExperimentValidator()


# Initialize AWS client
def _get_aws_client():
    """Get AWS FIS client with proper configuration"""
    region = os.environ.get("AWS_REGION", "us-west-2")
    return boto3.client("fis", region_name=region, config=_get_aws_config())


def _get_account_id():
    """Get current AWS account ID"""
    sts_client = boto3.client("sts", config=_get_aws_config())
    return sts_client.get_caller_identity()["Account"]


client = _get_aws_client()


def _load_config() -> Dict[str, Any]:
    """Load configuration from aws_config.json if it exists"""
    config_path = os.path.join(os.path.dirname(__file__), "aws_config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load config file: {str(e)}")
    return {}


@mcp.tool()
async def db_failure(
    db_identifier: str,
    failure_type: str = "reboot",
    region: Optional[str] = None,
) -> types.CallToolResult:
    """Execute database failure experiment with minimal configuration"""
    try:
        if not region:
            region = os.environ.get("AWS_REGION", "us-west-2")

        account_id = _get_account_id()
        role_arn = f"arn:aws:iam::{account_id}:role/FISExperimentRole"

        # Determine if it's RDS instance or Aurora cluster
        rds_client = boto3.client("rds", region_name=region, config=_get_aws_config())
        is_cluster = False

        try:
            rds_client.describe_db_clusters(DBClusterIdentifier=db_identifier)
            is_cluster = True
        except rds_client.exceptions.DBClusterNotFoundFault:
            try:
                rds_client.describe_db_instances(DBInstanceIdentifier=db_identifier)
                is_cluster = False
            except rds_client.exceptions.DBInstanceNotFoundFault:
                raise Exception(f"Database {db_identifier} not found")

        # Set appropriate values based on resource type
        if is_cluster:
            resource_type = "aws:rds:cluster"
            resource_arn = f"arn:aws:rds:{region}:{account_id}:cluster:{db_identifier}"
            if failure_type == "reboot":
                action_id = "aws:rds:failover-db-cluster"  # Clusters don't support reboot, use failover
            elif failure_type == "failover":
                action_id = "aws:rds:failover-db-cluster"
            elif failure_type == "stop":
                action_id = "aws:rds:stop-db-cluster"
            else:
                action_id = "aws:rds:failover-db-cluster"
        else:
            resource_type = "aws:rds:db"
            resource_arn = f"arn:aws:rds:{region}:{account_id}:db:{db_identifier}"
            if failure_type == "reboot":
                action_id = "aws:rds:reboot-db-instances"
            elif failure_type == "failover":
                action_id = "aws:rds:reboot-db-instances"  # Instances don't support failover, use reboot
            elif failure_type == "stop":
                action_id = "aws:rds:stop-db-instances"
            else:
                action_id = "aws:rds:reboot-db-instances"

        # Create template
        template_config = {
            "description": f"DB {failure_type} experiment for {db_identifier}",
            "roleArn": role_arn,
            "actions": {
                "db_action": {
                    "actionId": action_id,
                    "targets": {
                        "DBInstances" if not is_cluster else "DBClusters": "db_target"
                    },
                }
            },
            "targets": {
                "db_target": {
                    "resourceType": resource_type,
                    "resourceArns": [resource_arn],
                    "selectionMode": "ALL",
                }
            },
            "stopConditions": [{"source": "none"}],
        }

        # Create and start experiment
        template_response = client.create_experiment_template(**template_config)
        template_id = template_response["experimentTemplate"]["id"]

        experiment_response = client.start_experiment(experimentTemplateId=template_id)

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"DB failure experiment started: {experiment_response['experiment']['id']} ({'cluster' if is_cluster else 'instance'})",
                )
            ]
        )

    except Exception as error:
        raise Exception(f"DB failure experiment failed: {str(error)}")


def _convert_duration(duration_str: str) -> str:
    """Convert duration string to ISO 8601 format (PT format)"""
    import re

    # Already in PT format
    if duration_str.startswith("PT"):
        return duration_str

    # Parse common formats like "60s", "10m", "2h"
    match = re.match(r"(\d+)([smh])", duration_str.lower())
    if not match:
        raise ValueError(
            f"Invalid duration format: {duration_str}. Use formats like '60s', '10m', '2h'"
        )

    value, unit = match.groups()
    unit_map = {"s": "S", "m": "M", "h": "H"}

    return f"PT{value}{unit_map[unit]}"


@mcp.tool()
async def az_failure(
    availability_zone: str,
    duration: str = "10m",
    region: Optional[str] = None,
) -> types.CallToolResult:
    """Execute availability zone failure experiment with minimal configuration"""
    try:
        if not region:
            region = os.environ.get("AWS_REGION", "us-west-2")

        account_id = _get_account_id()
        role_arn = f"arn:aws:iam::{account_id}:role/FISExperimentRole"

        # Convert duration to PT format
        pt_duration = _convert_duration(duration)

        # Get all subnets in the specified AZ
        ec2_client = boto3.client("ec2", region_name=region, config=_get_aws_config())
        response = ec2_client.describe_subnets(
            Filters=[{"Name": "availability-zone", "Values": [availability_zone]}]
        )

        subnet_arns = []
        for subnet in response["Subnets"]:
            subnet_id = subnet["SubnetId"]
            subnet_arn = f"arn:aws:ec2:{region}:{account_id}:subnet/{subnet_id}"
            subnet_arns.append(subnet_arn)

        if not subnet_arns:
            raise Exception(
                f"No subnets found in availability zone {availability_zone}"
            )

        # Get all EC2 instances in the specified AZ
        instances_response = ec2_client.describe_instances(
            Filters=[
                {"Name": "availability-zone", "Values": [availability_zone]},
                {"Name": "instance-state-name", "Values": ["running", "stopped"]},
            ]
        )

        instance_arns = []
        for reservation in instances_response["Reservations"]:
            for instance in reservation["Instances"]:
                instance_id = instance["InstanceId"]
                instance_arn = (
                    f"arn:aws:ec2:{region}:{account_id}:instance/{instance_id}"
                )
                instance_arns.append(instance_arn)

        # Get all ASGs in the specified AZ
        asg_client = boto3.client("autoscaling", region_name=region, config=_get_aws_config())
        asg_response = asg_client.describe_auto_scaling_groups()

        asg_arns = []
        for asg in asg_response["AutoScalingGroups"]:
            # Check if ASG has instances in the target AZ
            for az in asg["AvailabilityZones"]:
                if az == availability_zone:
                    asg_arn = asg["AutoScalingGroupARN"]
                    asg_arns.append(asg_arn)
                    break

        # Get all RDS instances in the specified AZ
        rds_client = boto3.client("rds", region_name=region, config=_get_aws_config())
        db_instances_response = rds_client.describe_db_instances()
        db_clusters_response = rds_client.describe_db_clusters()

        db_instance_arns = []
        db_cluster_arns = []

        for db in db_instances_response["DBInstances"]:
            if db["AvailabilityZone"] == availability_zone:
                db_arn = db["DBInstanceArn"]
                db_instance_arns.append(db_arn)

        for cluster in db_clusters_response["DBClusters"]:
            for az in cluster.get("AvailabilityZones", []):
                if az == availability_zone:
                    cluster_arn = cluster["DBClusterArn"]
                    db_cluster_arns.append(cluster_arn)
                    break

        # Create template for AZ failure (only include targets with resources)
        targets = {
            "Subnet": {
                "resourceType": "aws:ec2:subnet",
                "resourceArns": subnet_arns[:5],
                "selectionMode": "ALL",
            }
        }
        actions = {
            "Pause-network-connectivity": {
                "actionId": "aws:network:disrupt-connectivity",
                "parameters": {"duration": pt_duration, "scope": "all"},
                "targets": {"Subnets": "Subnet"},
            }
        }

        if instance_arns:
            targets["EC2-Instances"] = {
                "resourceType": "aws:ec2:instance",
                "resourceArns": instance_arns[:5],
                "selectionMode": "ALL",
            }
            actions["Stop-Instances"] = {
                "actionId": "aws:ec2:stop-instances",
                "parameters": {"startInstancesAfterDuration": pt_duration},
                "targets": {"Instances": "EC2-Instances"},
            }

        if asg_arns:
            targets["ASG"] = {
                "resourceType": "aws:ec2:autoscaling-group",
                "resourceArns": asg_arns[:5],
                "selectionMode": "ALL",
            }
            actions["Pause-ASG"] = {
                "actionId": "aws:ec2:asg-insufficient-instance-capacity-error",
                "parameters": {
                    "availabilityZoneIdentifiers": availability_zone,
                    "duration": pt_duration,
                    "percentage": "100",
                },
                "targets": {"AutoScalingGroups": "ASG"},
            }

        if db_instance_arns:
            targets["DB-Instances"] = {
                "resourceType": "aws:rds:db",
                "resourceArns": db_instance_arns[:5],
                "selectionMode": "ALL",
            }
            actions["Reboot-DB-Instances"] = {
                "actionId": "aws:rds:reboot-db-instances",
                "targets": {"DBInstances": "DB-Instances"},
            }

        if db_cluster_arns:
            targets["DB-Clusters"] = {
                "resourceType": "aws:rds:cluster",
                "resourceArns": db_cluster_arns[:5],
                "selectionMode": "ALL",
            }
            actions["Failover-DB-Clusters"] = {
                "actionId": "aws:rds:failover-db-cluster",
                "targets": {"Clusters": "DB-Clusters"},
            }

        template_config = {
            "description": f"AZ failure experiment for {availability_zone}",
            "roleArn": role_arn,
            "targets": targets,
            "actions": actions,
            "stopConditions": [{"source": "none"}],
            "experimentOptions": {"emptyTargetResolutionMode": "skip"},
        }

        # Create and start experiment
        template_response = client.create_experiment_template(**template_config)
        template_id = template_response["experimentTemplate"]["id"]

        experiment_response = client.start_experiment(experimentTemplateId=template_id)

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"AZ failure experiment started: {experiment_response['experiment']['id']}",
                )
            ]
        )

    except Exception as error:
        raise Exception(f"AZ failure experiment failed: {str(error)}")


@mcp.tool()
async def get_automation_status(
    execution_id: str,
    region: Optional[str] = None,
) -> types.CallToolResult:
    """Get SSM automation execution status"""
    try:
        if not region:
            region = os.environ.get("AWS_REGION", "us-west-2")

        ssm_client = boto3.client("ssm", region_name=region, config=_get_aws_config())

        response = ssm_client.describe_automation_executions(
            Filters=[{"Key": "ExecutionId", "Values": [execution_id]}]
        )

        executions = response.get("AutomationExecutionMetadataList", [])

        if not executions:
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"No automation execution found with ID: {execution_id}",
                    )
                ]
            )

        execution = executions[0]

        # Get step executions for detailed info
        step_response = ssm_client.describe_automation_step_executions(
            AutomationExecutionId=execution_id
        )

        result_text = f"""
Automation Execution Status:
- ID: {execution["AutomationExecutionId"]}
- Status: {execution["AutomationExecutionStatus"]}
- Document: {execution["DocumentName"]}
- Start Time: {execution.get("ExecutionStartTime", "N/A")}
- End Time: {execution.get("ExecutionEndTime", "N/A")}

Step Details:
"""

        for step in step_response["StepExecutions"]:
            result_text += f"""
- Step: {step["StepName"]}
- Status: {step["StepStatus"]}
- Start Time: {step.get("ExecutionStartTime", "N/A")}
- End Time: {step.get("ExecutionEndTime", "N/A")}
"""
            if "FailureMessage" in step:
                result_text += f"- Failure Message: {step['FailureMessage']}\n"
            if "Response" in step:
                result_text += f"- Response: {step['Response']}\n"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to get automation status: {str(error)}")


@mcp.tool()
async def tag_based_failure(
    tag_key: str,
    tag_value: str,
    duration: str = "10m",
    region: Optional[str] = None,
) -> types.CallToolResult:
    """Execute failure experiments on all resources matching the specified tag"""
    try:
        if not region:
            region = os.environ.get("AWS_REGION", "us-west-2")

        account_id = _get_account_id()
        role_arn = f"arn:aws:iam::{account_id}:role/FISExperimentRole"

        # Convert duration to PT format
        pt_duration = _convert_duration(duration)

        # Initialize clients
        ec2_client = boto3.client("ec2", region_name=region, config=_get_aws_config())
        rds_client = boto3.client("rds", region_name=region, config=_get_aws_config())
        ecs_client = boto3.client("ecs", region_name=region, config=_get_aws_config())
        lambda_client = boto3.client("lambda", region_name=region, config=_get_aws_config())
        asg_client = boto3.client("autoscaling", region_name=region, config=_get_aws_config())
        elb_client = boto3.client("elbv2", region_name=region, config=_get_aws_config())
        eks_client = boto3.client("eks", region_name=region, config=_get_aws_config())

        targets = {}
        actions = {}

        # 1. EC2 Instances
        ec2_response = ec2_client.describe_instances(
            Filters=[
                {"Name": f"tag:{tag_key}", "Values": [tag_value]},
                {"Name": "instance-state-name", "Values": ["running"]}
            ]
        )
        
        instance_arns = []
        for reservation in ec2_response["Reservations"]:
            for instance in reservation["Instances"]:
                instance_arn = f"arn:aws:ec2:{region}:{account_id}:instance/{instance['InstanceId']}"
                instance_arns.append(instance_arn)

        if instance_arns:
            targets["EC2Instances"] = {
                "resourceType": "aws:ec2:instance",
                "resourceArns": instance_arns,
                "selectionMode": "ALL"
            }
            actions["StopEC2Instances"] = {
                "actionId": "aws:ec2:stop-instances",
                "parameters": {"startInstancesAfterDuration": pt_duration},
                "targets": {"Instances": "EC2Instances"}
            }

        # 2. RDS Instances
        rds_instances = rds_client.describe_db_instances()["DBInstances"]
        db_instance_arns = []
        for db in rds_instances:
            tags = rds_client.list_tags_for_resource(ResourceName=db["DBInstanceArn"])["TagList"]
            if any(tag["Key"] == tag_key and tag["Value"] == tag_value for tag in tags):
                db_instance_arns.append(db["DBInstanceArn"])

        if db_instance_arns:
            targets["RDSInstances"] = {
                "resourceType": "aws:rds:db",
                "resourceArns": db_instance_arns,
                "selectionMode": "ALL"
            }
            actions["RebootRDSInstances"] = {
                "actionId": "aws:rds:reboot-db-instances",
                "targets": {"DBInstances": "RDSInstances"}
            }

        # 3. RDS Clusters
        rds_clusters = rds_client.describe_db_clusters()["DBClusters"]
        db_cluster_arns = []
        for cluster in rds_clusters:
            tags = rds_client.list_tags_for_resource(ResourceName=cluster["DBClusterArn"])["TagList"]
            if any(tag["Key"] == tag_key and tag["Value"] == tag_value for tag in tags):
                db_cluster_arns.append(cluster["DBClusterArn"])

        if db_cluster_arns:
            targets["RDSClusters"] = {
                "resourceType": "aws:rds:cluster",
                "resourceArns": db_cluster_arns,
                "selectionMode": "ALL"
            }
            actions["FailoverRDSClusters"] = {
                "actionId": "aws:rds:failover-db-cluster",
                "targets": {"Clusters": "RDSClusters"}
            }

        # 4. ECS Services
        ecs_clusters = ecs_client.list_clusters()["clusterArns"]
        ecs_service_arns = []
        for cluster_arn in ecs_clusters:
            services = ecs_client.list_services(cluster=cluster_arn)["serviceArns"]
            for service_arn in services:
                tags = ecs_client.list_tags_for_resource(resourceArn=service_arn)["tags"]
                if any(tag["key"] == tag_key and tag["value"] == tag_value for tag in tags):
                    ecs_service_arns.append(service_arn)

        if ecs_service_arns:
            targets["ECSServices"] = {
                "resourceType": "aws:ecs:service",
                "resourceArns": ecs_service_arns,
                "selectionMode": "ALL"
            }
            actions["StopECSTasks"] = {
                "actionId": "aws:ecs:stop-task",
                "parameters": {"completeAfterDuration": pt_duration},
                "targets": {"Services": "ECSServices"}
            }

        # 5. Lambda Functions
        lambda_functions = lambda_client.list_functions()["Functions"]
        lambda_arns = []
        for func in lambda_functions:
            try:
                tags = lambda_client.list_tags(Resource=func["FunctionArn"])["Tags"]
                if tag_key in tags and tags[tag_key] == tag_value:
                    lambda_arns.append(func["FunctionArn"])
            except:
                continue

        if lambda_arns:
            targets["LambdaFunctions"] = {
                "resourceType": "aws:lambda:function",
                "resourceArns": lambda_arns,
                "selectionMode": "ALL"
            }
            actions["InvokeLambdaError"] = {
                "actionId": "aws:lambda:invocation-error",
                "parameters": {"duration": pt_duration, "errorType": "General"},
                "targets": {"Functions": "LambdaFunctions"}
            }

        # 6. Auto Scaling Groups
        asgs = asg_client.describe_auto_scaling_groups()["AutoScalingGroups"]
        asg_arns = []
        for asg in asgs:
            tags = asg.get("Tags", [])
            if any(tag["Key"] == tag_key and tag["Value"] == tag_value for tag in tags):
                asg_arns.append(asg["AutoScalingGroupARN"])

        if asg_arns:
            targets["AutoScalingGroups"] = {
                "resourceType": "aws:ec2:autoscaling-group",
                "resourceArns": asg_arns,
                "selectionMode": "ALL"
            }
            actions["ASGCapacityError"] = {
                "actionId": "aws:ec2:asg-insufficient-instance-capacity-error",
                "parameters": {"duration": pt_duration, "percentage": "100"},
                "targets": {"AutoScalingGroups": "AutoScalingGroups"}
            }

        # 7. Load Balancers
        elbs = elb_client.describe_load_balancers()["LoadBalancers"]
        elb_arns = []
        for elb in elbs:
            tags = elb_client.describe_tags(ResourceArns=[elb["LoadBalancerArn"]])["TagDescriptions"]
            if tags:
                tag_dict = {tag["Key"]: tag["Value"] for tag in tags[0]["Tags"]}
                if tag_key in tag_dict and tag_dict[tag_key] == tag_value:
                    elb_arns.append(elb["LoadBalancerArn"])

        if elb_arns:
            targets["LoadBalancers"] = {
                "resourceType": "aws:elasticloadbalancing:loadbalancer",
                "resourceArns": elb_arns,
                "selectionMode": "ALL"
            }
            actions["ELBUnavailable"] = {
                "actionId": "aws:elasticloadbalancing:unavailable-load-balancer",
                "parameters": {"duration": pt_duration},
                "targets": {"LoadBalancers": "LoadBalancers"}
            }

        # 8. EKS Node Groups
        eks_clusters = eks_client.list_clusters()["clusters"]
        nodegroup_arns = []
        for cluster_name in eks_clusters:
            nodegroups = eks_client.list_nodegroups(clusterName=cluster_name)["nodegroups"]
            for ng_name in nodegroups:
                ng_info = eks_client.describe_nodegroup(clusterName=cluster_name, nodegroupName=ng_name)["nodegroup"]
                tags = ng_info.get("tags", {})
                if tag_key in tags and tags[tag_key] == tag_value:
                    nodegroup_arns.append(ng_info["nodegroupArn"])

        if nodegroup_arns:
            targets["EKSNodeGroups"] = {
                "resourceType": "aws:eks:nodegroup",
                "resourceArns": nodegroup_arns,
                "selectionMode": "ALL"
            }
            actions["EKSNodeGroupError"] = {
                "actionId": "aws:eks:terminate-nodegroup-instances",
                "parameters": {"instanceTerminationPercentage": 100},
                "targets": {"Nodegroups": "EKSNodeGroups"}
            }

        if not targets:
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"No resources found with tag {tag_key}={tag_value}"
                    )
                ]
            )

        # Create experiment template
        template_config = {
            "description": f"Tag-based failure experiment for {tag_key}={tag_value} (duration: {duration})",
            "roleArn": role_arn,
            "targets": targets,
            "actions": actions,
            "stopConditions": [{"source": "none"}],
            "experimentOptions": {"emptyTargetResolutionMode": "skip"}
        }

        template_response = client.create_experiment_template(**template_config)
        template_id = template_response["experimentTemplate"]["id"]

        experiment_response = client.start_experiment(experimentTemplateId=template_id)

        resource_summary = ", ".join([f"{len(targets[t]['resourceArns'])} {t}" for t in targets])
        
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"Tag-based failure experiment started: {experiment_response['experiment']['id']} (duration: {duration}, affecting: {resource_summary})"
                )
            ]
        )

    except Exception as error:
        raise Exception(f"Tag-based failure experiment failed: {str(error)}")


@mcp.tool()
async def msk_failure(
    cluster_name: str,
    failure_percent: int = 50,
    region: Optional[str] = None,
) -> types.CallToolResult:
    """Execute MSK cluster failure experiment using SSM automation"""
    try:
        if not region:
            region = os.environ.get("AWS_REGION", "us-west-2")

        # Get cluster ARN and broker IDs
        kafka_client = boto3.client("kafka", region_name=region, config=_get_aws_config())
        clusters = kafka_client.list_clusters()["ClusterInfoList"]
        cluster_arn = None
        for cluster in clusters:
            if cluster["ClusterName"] == cluster_name:
                cluster_arn = cluster["ClusterArn"]
                break

        if not cluster_arn:
            raise Exception(f"MSK cluster {cluster_name} not found")

        # Get actual broker node info
        nodes_response = kafka_client.list_nodes(ClusterArn=cluster_arn)

        # Debug: Print all node info to understand the structure
        print(f"DEBUG: Nodes response: {nodes_response}")

        broker_ids = []
        for node in nodes_response["NodeInfoList"]:
            if "BrokerNodeInfo" in node:
                broker_id = int(node["BrokerNodeInfo"]["BrokerId"])  # Ensure integer
                broker_ids.append(broker_id)
                print(f"DEBUG: Found broker ID: {broker_id} (type: {type(broker_id)})")

        if not broker_ids:
            raise Exception(f"No broker nodes found in MSK cluster {cluster_name}")

        print(f"DEBUG: All broker IDs: {broker_ids}")

        # Select percentage of brokers based on failure_percent
        import random

        num_brokers_to_affect = max(1, int(len(broker_ids) * failure_percent / 100))
        # Ensure we don't try to select more brokers than available
        num_brokers_to_affect = min(num_brokers_to_affect, len(broker_ids))
        selected_broker_ids = random.sample(broker_ids, num_brokers_to_affect)

        print(f"DEBUG: Selected broker IDs: {selected_broker_ids}")

        # Create SSM document
        ssm_client = boto3.client("ssm", region_name=region, config=_get_aws_config())
        doc_name = f"MSK-RestartBroker-{cluster_name}"

        ssm_document = {
            "schemaVersion": "0.3",
            "description": f"Restart MSK brokers for {cluster_name}",
            "parameters": {
                "ClusterArn": {"type": "String"},
                "BrokerIds": {"type": "StringList"},
            },
            "mainSteps": [
                {
                    "name": "RestartBroker",
                    "action": "aws:executeAwsApi",
                    "inputs": {
                        "Service": "kafka",
                        "Api": "RebootBroker",
                        "ClusterArn": "{{ ClusterArn }}",
                        "BrokerIds": "{{ BrokerIds }}",
                    },
                }
            ],
        }

        try:
            # Delete existing document if it exists
            try:
                ssm_client.delete_document(Name=doc_name)
            except ssm_client.exceptions.InvalidDocument:
                pass  # Document doesn't exist, which is fine

            ssm_client.create_document(
                Content=json.dumps(ssm_document),
                Name=doc_name,
                DocumentType="Automation",
            )
        except ssm_client.exceptions.DocumentAlreadyExists:
            pass

        # Execute SSM automation directly
        ssm_parameters = {
            "ClusterArn": [cluster_arn],
            "BrokerIds": [
                str(bid) for bid in selected_broker_ids
            ],  # Convert to strings
        }

        print(f"DEBUG: SSM Parameters: {ssm_parameters}")

        automation_response = ssm_client.start_automation_execution(
            DocumentName=doc_name, Parameters=ssm_parameters
        )

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"MSK failure experiment started via SSM automation: {automation_response['AutomationExecutionId']} (affecting brokers: {selected_broker_ids})",
                )
            ]
        )

    except Exception as error:
        raise Exception(f"MSK failure experiment failed: {str(error)}")


def handle_list_tools() -> List[types.Tool]:
    """List available tools"""
    logger.info("Handling list_tools request")

    tools = [
        types.Tool(
            name="db_failure",
            description="Execute database failure experiment with minimal configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "db_identifier": {
                        "type": "string",
                        "description": "Database identifier (RDS instance name or Aurora cluster name)",
                    },
                    "failure_type": {
                        "type": "string",
                        "enum": ["reboot", "failover", "stop"],
                        "description": "Type of failure to simulate (default: reboot)",
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region (uses AWS_REGION env var if not specified)",
                    },
                },
                "required": ["db_identifier"],
            },
        ),
        types.Tool(
            name="az_failure",
            description="Execute availability zone failure experiment with minimal configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "availability_zone": {
                        "type": "string",
                        "description": "Availability zone to target (e.g., us-west-2a)",
                    },
                    "duration": {
                        "type": "string",
                        "description": "Duration of the failure (e.g., '60s', '10m', '2h', default: '10m')",
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region (uses AWS_REGION env var if not specified)",
                    },
                },
                "required": ["availability_zone"],
            },
        ),
        types.Tool(
            name="get_automation_status",
            description="Get SSM automation execution status and details",
            inputSchema={
                "type": "object",
                "properties": {
                    "execution_id": {
                        "type": "string",
                        "description": "SSM automation execution ID",
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region (uses AWS_REGION env var if not specified)",
                    },
                },
                "required": ["execution_id"],
            },
        ),
        types.Tool(
            name="msk_failure",
            description="Execute MSK cluster failure experiment with minimal configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "MSK cluster name to target",
                    },
                    "failure_percent": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": "Percentage of brokers to affect (default: 50)",
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region (uses AWS_REGION env var if not specified)",
                    },
                },
                "required": ["cluster_name"],
            },
        ),
        types.Tool(
            name="tag_based_failure",
            description="Execute failure experiments on all resources matching the specified tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag_key": {
                        "type": "string",
                        "description": "Tag key to search for",
                    },
                    "tag_value": {
                        "type": "string",
                        "description": "Tag value to match",
                    },
                    "duration": {
                        "type": "string",
                        "description": "Duration of the failure (e.g., '60s', '10m', '2h', default: '10m')",
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region (uses AWS_REGION env var if not specified)",
                    },
                },
                "required": ["tag_key", "tag_value"],
            },
        ),
    ]

    for i, tool in enumerate(tools):
        logger.info(f"Tool {i}: {type(tool)} - {getattr(tool, 'name', 'NO_NAME')}")
        if not hasattr(tool, "name"):
            logger.error(f"Tool missing name attribute: {tool}")
            raise ValueError(f"Invalid tool definition: {tool}")

    logger.info(f"Returning {len(tools)} tools")
    return tools


def run_server():
    """Run the MCP server"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
    run_server()
