from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_iam as iam,
)


class LambdaStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Policyを生成
        self._create_lambda_policy()

        # Lambda用の VPC, Subnet, SecurityGroup をセットアップ
        self._setup_existing_network_for_lambda()

        # IAM Roleの生成
        self.service_principal = iam.ServicePrincipal("lambda.amazonaws.com")
        self._create_lambda_role()

        # Lambda
        context = scope.node.try_get_context("lambda")
        timeout = context["timeout"]
        memory_size = context["memory_size"]
        self._create_vpc_lambda(timeout, memory_size)

    # 管理ポリシー
    def _create_lambda_policy(self):
        self.lambda_inline_policy = iam.Policy(
            self, "LambdaPolicy",
            policy_name="lambda-policy",
            statements=[]
        )

        self.lambda_managed_policy = \
            iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name="service-role/AWSLambdaVPCAccessExecutionRole"
            )

    # Lambdaのロール

    def _create_lambda_role(self):
        self.lambda_role = iam.Role(
            self, "LambdaRole",
            assumed_by=self.service_principal,
            role_name="cdk-lambda-role",
            managed_policies=[self.lambda_managed_policy],
        )
        self.lambda_role.attach_inline_policy(
            self.lambda_inline_policy)

    # Lambdaで使用する VPC, Subnet, SecurityGroup を既存リソースから取得する
    def _setup_existing_network_for_lambda(self):
        lambda_context = self.node.try_get_context("lambda")

        # VPC
        self.lambda_vpc = ec2.Vpc.from_lookup(
            self, "LambdaVpc",
            vpc_id=lambda_context["vpc_id"]
        )

        # Subnet (Lambdaに設定する場合はSubnetSelection型に変換)
        subnet_list = []
        for i, subnet in enumerate(lambda_context["subnets"]):
            subnet_list.append(
                ec2.Subnet.from_subnet_attributes(
                    self, f"LambdaSubnet{i}",
                    availability_zone=subnet["az"],
                    subnet_id=subnet["subnet_id"]
                )
            )
        self.lambda_subnets = ec2.SubnetSelection(
            subnets=subnet_list
        )
        # Security Group
        self.lambda_security_group = ec2.SecurityGroup.from_security_group_id(
            self, "LambdaSg",
            security_group_id=lambda_context["sg_id"]
        )

    # VPC用のLambda
    def _create_vpc_lambda(self, timeout, memory_size):
        self.vpc_function = _lambda.Function(
            self, "VPCLambda",
            function_name="cdk-vpc-lambda",
            runtime=_lambda.Runtime.PYTHON_3_8,
            timeout=core.Duration.seconds(timeout),
            handler="handler.main",
            memory_size=memory_size,
            vpc=self.lambda_vpc,
            vpc_subnets=self.lambda_subnets,
            security_group=self.lambda_security_group,
            role=self.lambda_role,
            code=_lambda.Code.from_asset("resource/lambda/vpc/handler.zip"),
            environment={
                "host": self.node.try_get_context("host"),
                "username": self.node.try_get_context("username"),
                "password": self.node.try_get_context("password")
            }
        )
