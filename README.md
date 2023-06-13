# PingOne Integration with Amazon Verified Permissions

### Amazon Verified Permissions
Amazon Verified Permissions is a scalable, fine-grained permissions management and authorization service for custom applications. The service centralizes fine-grained permissions for custom applications and helps developers authorize user actions within applications. Amazon Verified Permissions uses the Cedar policy language to define fine-grained permissions for application users.

![Amazon Verified Permissions](images/Product-Page-Diagram_AVP.png)

### Amazon API Gateway and Lambda Authorizers
Amazon API Gateway is a fully managed AWS service that simplifies the process of creating and managing REST APIs at any scale. An organization using PingOne as their Identity Provider (IdP) can use AWS Lambda Authorizers to implement a standard token-based authorization scheme for REST APIs that are deployed using the Amazon API Gateway.

Lambda Authorizers are a good choice for organizations that use third-party identity providers directly (without federation) to control access to resources in API Gateway, or organizations requiring authorization logic beyond the capabilities offered by “native” authorization mechanisms.


### PingOne as an Identity Provider for Amazon Verified Permissions
PingOne, operating as the Identity Provider (IdP), issues cryptographically signed tokens to users containing information about the user identity and their permissions. In order to use these non-AWS tokens to control access to resources within Amazon API Gateway, you will need to define custom authorization code using a Lambda function to “map” token characteristics to Amazon API Gateway resources and permissions. The PingOne Lambda Authorizer function is available here: [https://github.com/pingone-davinci/pingone-avp-lambda-authorizer]

The diagram below illustrates the process flow of a user authenticating with PingOne:

![PingOne Integration with Amazon Verified Permissions](images/pingone-avp-lambda-authorizer.png)


### PingOne Lambda Authorizer
The PingOne Lambda Authorizer performs the following functions:
* The authorization token is pulled from the request headers and subjected to a verification process
* User information is pulled from the token after the verification process
* The user information along with more information from the request is used to construct an authorization query
* The created query is sent to the Amazon Verified Permissions authorization service
* Depending on the response, the method builds either an allow or a deny IAM policy and returns it as output


## Requirements
* PingOne Tenant
* Amazon API Gateway
* Amazon Verified Permissions
* AWS Lambda Function


## Before you begin
### Create the AWS Lambda Zip Deployment Package
  * Download the **pingone_lambda_authorizer.py**, **verifiedpermissions.json** and **prepare.sh** files from https://github.com/pingone-davinci/pingone-avp-lambda-authorizer
    * Run the **prepare.sh** file to create the zip deployment package


## Steps
### From the PingOne Console:
  * Create a new Application with Application Type: **OIDC Web App**
    * Copy the **JWKS Endpoint** URL as you will need this later
    * Edit the new Application and change the **Token Endpoint Authentication Method** to **Client Secret Post**
    * Under the **Resources** tab, add the **profile** OIDC scope
  * Click **Identities** in the left navigation pane, click **Users**, and then select/create a user that will be used for testing authentication and authorization
    * Under the **API** tab, copy the **ID** of the PingOne user


### From the AWS Console:
#### AWS Lambda
  * In the **AWS Lambda** console, create a new AWS Lambda Function
    * Select **Python 3.9** as the **Runtime**, **x86_64** as the **Architecture**, and then click **Create function**
      * Click **Upload from** and select **.zip file**
        * Click **Upload** and select the .zip file you created earlier in the **Before you begin** section
          * Click **Save**
    * Under the **Configuration** tab, click **Environment Variables** and click **Edit**
      * Create the required **Environment Variables** with the following details:
        | Environment Variable | Value |
        | ----------- | ----------- |
        | **AWS_DATA_PATH** | **./models** |
        | **JWKS_ENDPOINT** | The **JWKS Endpoint** from the PingOne Lambda Authorizer OIDC Application |
        | **POLICY_STORE_ID** | The Amazon Verified Permissions **Policy Store ID** |


#### Amazon Verified Permissions
  * In the **Amazon Verified Permissions** console, create a new Policy Store (if required)
    * Click **Settings** in the left navigation pane and copy the **Policy store ID** as you will need this later
    * Click **Policies** in the left navigation pane, click **Create policy** in the top right, and then choose **Create inline policy**
      * Add the following policy for testing:
        ```
        permit (
            principal == User::"<PingOne User ID>",
            action in [Action::"POST"],
            resource == Resource::"protected-resource"
        );
        ```


#### Amazon API Gateway
  * In the **API Gateway** console, create a new API Gateway (if required)
    * Select **REST API** and click **Import**
      * Select the **REST** option in the **Choose the protocol** section, then select the **Example API** option in the **Create New API** section and **Regional** as the **Endpoint Type**. Then click **Import**
      * Click on **Actions**, under the subsection **API ACTIONS** click **Deploy API**
        * Select **[New Stage]**
          * Provide a **Stage name** then click **Deploy**
    * Click **Authorizers** in the left navigation pane and then click **Create New Authorizer**
      * Populate the necessary values as follows:
        * **Name:** [Choose an authorizer name]
        * **Type:** Lambda
        * **Lambda Function:** [Select the Lambda Function created earlier]
        * **Lambda Event Payload:** Request
        * **Identity Sources > Header:** Authorization
        * Click **Create**
    * Click **Resources** in the left navigation pane and click on the **GET** method under **/{petId}**
      * Click **Method Request**
        * In the **Settings** section, click the pencil button for the **Authorization** configuration to edit
          * Select the **Authorizer** created earlier and confirm the selection by clicking the check-mark button
        * From the Resources **Actions** pull-down on the top of the screen, select the **Deploy API** menu item


### Summary
After the configuration has been completed, PingOne will function as the Identity Provider (IdP) for your Amazon API Gateway.