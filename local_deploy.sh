zip -r test.zip * -x "venv/*" -x "*.zip" -x "local_deploy.sh"
aws s3 cp test.zip s3://joonggonara-serverless-deployment-stage/serverless/alert-api/ --profile stage
aws lambda update-function-code --function-name cloudwatch-alarm-slack-integration-lambda-stg --s3-bucket joonggonara-serverless-deployment-stage --s3-key serverless/alert-api/test.zip --profile stage --region ap-northeast-2 --output table --no-cli-pager
