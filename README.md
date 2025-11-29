# py-ddns-route53
DDNS updater for AWS route53

## Usage
```
usage: ddns.py [-h] --domain DOMAIN --hosted_zone_id HOSTED_ZONE_ID

DDNS Route53 A Record Update Script

options:
  -h, --help            show this help message and exit
  --domain DOMAIN       The domain you wish to update
  --hosted_zone_id HOSTED_ZONE_ID
                        The AWS route 53 Hosted Zone ID
```

## AWS Credentials
```
AWS Credentials:
    Ensure AWS credentials are configured via:
    - AWS CLI: aws configure
    - Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    - IAM role (if running on EC2)
    - ~/.aws/credentials file example:
        [default]
        aws_access_key_id = AKIAIOSFODNN7EXAMPLE
        aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

## Scheduling
You can add the following to your crontab with `crontab -e` to run the script every 20 min:
```
*/20 * * * * /usr/bin/python3 /path/to/your/ddns.py --domain=DOMAIN --hosted_zone_id=HOSTED_ZONE_ID
```
