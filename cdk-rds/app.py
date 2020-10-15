#!/usr/bin/env python3

from aws_cdk import core

from resource.rds_stack import RdsStack
from resource.lambda_stack import LambdaStack

app = core.App()

RdsStack(app, "rds-stack",
         env=core.Environment(
             account=app.node.try_get_context("account_id"),
             region=app.node.try_get_context("region")
         ))
LambdaStack(
    app, "lambda-stack",
    env=core.Environment(
        account=app.node.try_get_context("account_id"),
        region=app.node.try_get_context("region")
    )
)

app.synth()
