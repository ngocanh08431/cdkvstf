from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_rds as rds
)


class RdsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # VPC
        self._create_vpc()
        # RDS
        dbname = self.node.try_get_context("dbname")
        username = self.node.try_get_context("username")
        password = self.node.try_get_context("password")
        self._create_rds(dbname, username, password)
        # 出力
        core.CfnOutput(
            self, "host",
            value=self.rds.db_instance_endpoint_address
        )

    def _create_vpc(self):
        self.vpc = ec2.Vpc(
            self, "cdk-vpc",
            cidr="192.168.60.0/24",
            max_azs=2
        )
        core.Tag.add(self.vpc, "Name", "vpc-test")

    def _create_rds(self, dbname, username, password):
        self.rds = rds.DatabaseInstance(
            self, "cdk-rds",
            master_username=username,
            master_user_password=core.SecretValue.plain_text(password),
            database_name=dbname,
            instance_identifier="rds-identifier-mysql",
            engine_version="5.7.22",
            engine=rds.DatabaseInstanceEngine.MYSQL,
            vpc=self.vpc,
            port=3306,
            vpc_placement=ec2.SubnetType.PRIVATE,
            instance_class=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2,
                ec2.InstanceSize.MICRO,
            ),
            removal_policy=core.RemovalPolicy.DESTROY,
            deletion_protection=False
        )
        core.Tag.add(self.rds, "Name", "rds-identifier-mysql")
