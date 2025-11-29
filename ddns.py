#!/usr/bin/env python3

"""
DDNS Route53 A Record Update Script
Updates Route53 A record IP addresse from ipinfo.io.

Requirements:
    sudo apt intall python3-boto3

AWS Credentials:
    Ensure AWS credentials are configured via:
    - AWS CLI: aws configure
    - Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    - IAM role (if running on EC2)
    - ~/.aws/credentials file example:
        [default]
        aws_access_key_id = AKIAIOSFODNN7EXAMPLE
        aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
"""

import logging
import argparse
import requests
import json
import socket
import boto3
from botocore.exceptions import ClientError


# Configure the logger
logging.basicConfig(
    level=logging.INFO,  # Set minimum level to capture
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ddns_update.log"),  # Log to file
        logging.StreamHandler(),  # Also print to console
    ],
)

# Create a logger instance
logger = logging.getLogger(__name__)


def get_ip_address():
    """
    Makes a web request to ipinfo.io/json and returns the IP address.

    Returns:
        str: The IP address if successful, None if there's an error
    """
    try:
        # Make GET request to ipinfo.io/json
        response = requests.get("https://ipinfo.io/json", timeout=5)

        # Check if request was successful
        response.raise_for_status()

        # Parse JSON response
        data = response.json()
        ip = data.get("ip")

        # Extract and return IP address
        logger.info(f"IP address from ipinfo.io is {ip}")
        return ip

    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


def dns_lookup(domain):
    """
    Performs a DNS lookup for a domain name and returns the IP address.

    Args:
        domain (str): The domain name to look up (e.g., 'google.com')

    Returns:
        str: The IP address if successful, None if there's an error

    Example:
        >>> ip = dns_lookup('google.com')
        >>> print(ip)
        142.250.80.46
    """
    try:
        # Remove protocol if present
        domain = domain.replace("https://", "").replace("http://", "")
        # Remove path if present
        domain = domain.split("/")[0]
        # Remove port if present
        domain = domain.split(":")[0]

        # Get the IP address for the domain
        ip_address = socket.gethostbyname(domain)
        logger.info(f"DNS lookup: {domain} resolves to {ip_address}")
        return ip_address
    except socket.gaierror as e:
        logger.error(f"DNS lookup failed for {domain}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


def update_route53_a_record(hosted_zone_id, record_name, new_ip):
    """
    Updates a Route53 A record with a new IP address.

    Args:
        hosted_zone_id (str): The Route53 hosted zone ID (e.g., 'Z1234567890ABC')
        record_name (str): The fully qualified domain name (e.g., 'api.example.com')
        new_ip (str): The new IP address to set

    Returns:
        dict: Response from Route53 with change info, None if error

    Example:
        >>> result = update_route53_a_record(
        ...     'Z1234567890ABC',
        ...     'api.example.com',
        ...     '192.168.1.100'
        ... )
    """
    try:
        # Create Route53 client
        route53 = boto3.client("route53")

        # Ensure record_name ends with a dot
        if not record_name.endswith("."):
            record_name = record_name + "."

        # Prepare the change batch
        change_batch = {
            "Changes": [
                {
                    "Action": "UPSERT",  # UPSERT will create or update
                    "ResourceRecordSet": {
                        "Name": record_name,
                        "Type": "A",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": new_ip}],
                    },
                }
            ]
        }

        # Submit the change
        response = route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id, ChangeBatch=change_batch
        )

        logger.info(f"Successfully initiated update of {record_name} to {new_ip}")
        logger.info(f"Change ID: {response['ChangeInfo']['Id']}")
        logger.info(f"Status: {response['ChangeInfo']['Status']}")

        return response

    except ClientError as e:
        logger.error(f"AWS Client Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="DDNS Route53 A Record Update Script")
    parser.add_argument(
        "--domain", type=str, required=True, help="The domain you wish to update"
    )
    parser.add_argument(
        "--hosted_zone_id",
        type=str,
        required=True,
        help="The AWS route 53 Hosted Zone ID",
    )
    args = parser.parse_args()

    domain = args.domain
    hosted_zone_id = args.hosted_zone_id
    public_ip = get_ip_address()
    dns_ip = dns_lookup(domain)

    if public_ip == dns_ip:
        logger.info(f"No Need to Update: Public IP({public_ip}) = DNS IP({dns_ip})")
    else:
        update_route53_a_record(hosted_zone_id, domain, public_ip)


if __name__ == "__main__":
    main()
