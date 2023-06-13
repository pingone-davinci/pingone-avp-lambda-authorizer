# Creating the package folder
mkdir -p package/models/verifiedpermissions/2021-12-01

# Intalling dependencies
pip install python-jose -t package
pip install requests -t package
pip install botocore boto3 -t package

# Copying the source code
cp pingone_lambda_authorizer.py package/index.py
cp ./verifiedpermissions.json package/models/verifiedpermissions/2021-12-01/service-2.json

# Zipping the package
cd package
zip -r ../pingone_lambda_authorizer.zip * -x "*.pyc" "*.DS_Store"
cd ../