# Intalling dependencies
pip install python-jose -t package
pip install requests -t package   

# Copying the source code
cp pingone_lambda_authorizer.py package/index.py

# Zipping the package
cd package
zip -r ../pingone_lambda_authorizer.zip * -x "*.pyc" "*.DS_Store"
cd ../
