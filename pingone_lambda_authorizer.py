import json
from time import time
import os

from jose import jwt

import requests

import boto3

client = boto3.client("verifiedpermissions")


def lambda_handler(event, context):
    print(f"Event: {json.dumps(event)}")

    """---------get authorization token and method arn-------------"""
    authorization_token = event["authorizationToken"].replace("Bearer ", "").strip()
    method_arn = event["methodArn"]

    """---------verify and decode authorization token-------------"""
    verified_token = verify_token(authorization_token)

    """---------prepare authorization query-------------"""
    api_gateway_method = method_arn.split(":")[5].split("/")
    http_method = api_gateway_method[2]
    resource = api_gateway_method[-1]
    principal_id = verified_token["sub"]

    authorization_query = {
        "policyStoreId": os.environ["POLICY_STORE_ID"],
        "principal": {
            "entityType": "User",  # expected to be dynamic, like: verified_token['custom:type']
            "entityId": principal_id,  # expected to use a different value like: verified_token['custom:userId']
        },
        "action": {"actionType": "Action", "actionId": http_method},
        "resource": {"entityType": "Resource", "entityId": resource},
        "context": {"contextMap": {"QueryTime": {"long": int(time() * 1000)}}},
        # "Entities": put your entities here, if you have any
    }

    """---------get authorization decision-------------"""
    authz_result = client.is_authorized(**authorization_query)
    decision = authz_result.get("decision").lower().capitalize()
    print(f"Authorization Decision: {decision}")

    return generate_iam_policy(principal_id, decision, method_arn)


"""-----------------generate IAM policy------------------"""


def generate_iam_policy(principal_id, effect, resource):
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{"Action": "execute-api:Invoke", "Effect": effect, "Resource": resource}],
        },
    }


"""-----------------get public key------------------"""


def get_public_keys(jwks_endpoint):
    response = requests.get(jwks_endpoint)
    jwks = response.json()
    return jwks["keys"]


"""---------------verify and decode JWT token--------------"""


def verify_token(authorization_token):
    public_keys = get_public_keys(os.environ["JWKS_ENDPOINT"])
    token_kid = jwt.get_unverified_header(authorization_token)["kid"]
    signing_key = [key for key in public_keys if key["kid"] == token_kid]
    print(f"Signing Key: {json.dumps(signing_key)}")
    try:
        verified_token = jwt.decode(
            authorization_token,
            signing_key,
            algorithms=["RS256"],
            audience="https://api.pingone.com",  # replace the audience with your PingOne API Audience
        )
        return verified_token

    except Exception as e:
        raise Exception(str(e))
