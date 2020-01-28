import sys
import getopt
import argparse
import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')

def error_log(line, exit = False):
    print(line, file = sys.stderr)
    if exit: sys.exit(1)

def execute(params):
    ip_ranges = sorted(find_ip_ranges(params.security_group_id), key = lambda ip_range: ip_range['CidrIp'])
    if params.format == 'nginx': format_nginx(ip_ranges, params.blacklist)
    if params.format == 'plain': format_plain(ip_ranges)

def find_ip_ranges(group_id, ip_ranges = []):
    try:
        for security_group in ec2.describe_security_groups(GroupIds = [group_id])['SecurityGroups']:
            for ip_permission in security_group['IpPermissions']:
                [ips.update({ "SecurityGroupId": group_id }) for ips in ip_permission['IpRanges']]
                ip_ranges = ip_ranges + ip_permission['IpRanges']
                if 'UserIdGroupPairs' in ip_permission:
                    for linked_groups in ip_permission['UserIdGroupPairs']:
                        ip_ranges = find_ip_ranges(linked_groups['GroupId'], ip_ranges)
    except ClientError as client_error:
        error_log("Error obtaining Security Group with ID '{}': \n\t{}".format(group_id, client_error))
    return ip_ranges

def format_plain(ip_ranges):
    for ip_range in ip_ranges:
        print('# from : {: <25} {}'.format(ip_range['SecurityGroupId'], ip_range['Description'] if 'Description' in ip_range else ''))
        print(ip_range['CidrIp'])

def format_nginx(ip_ranges, blacklist):
    for ip_range in ip_ranges:
        print("{} {}; # (from : {}) {}".format('deny' if blacklist else 'allow',
                                ip_range['CidrIp'],
                                ip_range['SecurityGroupId'],
                                ip_range['Description'] if 'Description' in ip_range else ''))
    print("{} all;".format('allow' if blacklist else 'deny'))

if __name__== "__main__":
    parser = argparse.ArgumentParser(description = 'Obtains AWS Security Group IP addresses recursively and outputs them', add_help = True)
    parser.add_argument('-i', '--id', dest = 'security_group_id', help = 'The AWS Security Group used to obtain IP addresses from', required = True)
    parser.add_argument('-b', '--blacklist', dest = 'blacklist', action='store_true', help = 'Will generate and outputs a blacklist (default: generate a whitelist)', default = False)
    parser.add_argument('-f', '--format', dest = 'format', help = 'The formatting mode to output', choices=['plain', 'nginx'], default = 'plain')
    parser.add_argument('-o', '--output', dest = 'output', help = 'File path to direct the contents of the output to (default: stdout)', default = 'stdout')
    params = parser.parse_args()

    if not params.security_group_id.startswith('sg-'): error_log("Security Group ID should start with 'sg-'. Exiting...", exit = True)
    if not params.output == 'stdout': sys.stdout = open(params.output, 'wt')

    execute(params)

