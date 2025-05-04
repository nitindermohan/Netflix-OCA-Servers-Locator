#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compatibility script for Python 2.7 on Ubuntu 14.04.
Replaces requests with urllib2, removes pandas dependency,
and retains PrettyTable for output formatting.
"""
import urllib2
import json
import subprocess
import socket
import re
from prettytable import PrettyTable
from urlparse import urlparse

def fetch_public_ip():
    try:
        response = urllib2.urlopen('https://api.ipify.org?format=json')
        data = json.loads(response.read())
        return data.get('ip')
    except Exception as e:
        print("Error fetching public IP: {}".format(e))
        return None

def get_host_isp_info(ip_address):
    try:
        cmd = 'whois -h whois.cymru.com " -v {}"'.format(ip_address)
        output = subprocess.check_output(cmd, shell=True)
        lines = output.strip().split('\n')
        columns = [col.strip() for col in lines[0].split('|')]
        data = [line.split('|') for line in lines[1:]]
        return columns, data
    except subprocess.CalledProcessError as e:
        print("Error fetching ISP info: {}".format(e))
        return [], []

def get_netflix_token():
    fast_js_url = 'https://fast.com/app-ed402d.js'
    try:
        response = urllib2.urlopen(fast_js_url)
        content = response.read()
        match = re.search(r'token:"([^"]+)"', content)
        if match:
            return match.group(1)
    except Exception as e:
        print("Error fetching Netflix token: {}".format(e))
    return None

def fetch_oca_candidates(token):
    url = 'https://api.fast.com/netflix/speedtest?https=true&token={}'.format(token)
    try:
        response = urllib2.urlopen(url)
        oca_list = json.loads(response.read())
        results = []
        for item in oca_list:
            domain = urlparse(item.get('url')).netloc
            try:
                ip_addr = socket.gethostbyname(domain)
            except socket.gaierror:
                ip_addr = None
            results.append((domain, ip_addr))
        return results
    except Exception as e:
        print("Error fetching OCA candidates: {}".format(e))
        return []

def print_table(field_names, rows):
    table = PrettyTable()
    table.field_names = field_names
    for row in rows:
        table.add_row(row)
    print(table)

def main():
    print("=" * 60)
    print("Fetching public IP address...")
    ip = fetch_public_ip()
    if ip:
        print("Your public IP address is: {}".format(ip))
    else:
        print("Could not fetch public IP.")
    print("=" * 60)

    columns, data = get_host_isp_info(ip)
    if columns and data:
        print("Host IP Information:")
        print_table(columns, data)
    else:
        print("Could not retrieve ISP information.")
    print("=" * 60)

    token = get_netflix_token()
    if token:
        rows = fetch_oca_candidates(token)
        if rows:
            print("Allocated OCAs for this user:")
            print_table(['Domain', 'IP Address'], rows)
        else:
            print("No OCA candidates found.")
    else:
        print("Failed to fetch Netflix token.")
    print("=" * 60)

if __name__ == "__main__":
    main()
