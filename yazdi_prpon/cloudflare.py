#!/usr/bin/env python3
import os
import time

import requests


class CloudflareAPI:
    """Cloudflare API client for DNS verification"""
    
    def __init__(self, api_token=None, email=None, zone_id=None):
        self.api_token = api_token or os.environ.get('CF_API_TOKEN')
        self.email = email or os.environ.get('CF_EMAIL')
        self.zone_id = zone_id or os.environ.get('CF_ZONE_ID')
        
        if not self.api_token or not self.zone_id:
            raise ValueError("Cloudflare API token and Zone ID are required")
    
    def add_dns_record(self, name, content, type="TXT", ttl=120, proxied=False):
        """Add a DNS record to Cloudflare"""
        url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records"
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "type": type,
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": proxied
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201] and response.json().get('success'):
            return response.json()['result']['id']
        else:
            error_msg = response.json().get('errors', [{'message': 'Unknown error'}])[0].get('message')
            raise Exception(f"Failed to add DNS record: {error_msg}")
    
    def delete_dns_record(self, record_id):
        """Delete a DNS record from Cloudflare"""
        url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records/{record_id}"
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 200 and response.json().get('success'):
            return True
        else:
            error_msg = response.json().get('errors', [{'message': 'Unknown error'}])[0].get('message')
            raise Exception(f"Failed to delete DNS record: {error_msg}")
    
    def wait_for_propagation(self, record_name, expected_content, max_attempts=30, wait_time=10):
        """Wait for DNS record to propagate"""
        print(f"Waiting for DNS record propagation: {record_name}...")
        
        # Simple DNS verification using dig
        import subprocess
        
        for attempt in range(max_attempts):
            try:
                # Try to verify DNS record directly to speed up propagation checks
                result = subprocess.run(
                    ["dig", "+short", record_name, "TXT"], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                
                if expected_content in result.stdout:
                    print(f"DNS record verified after {attempt + 1} attempts")
                    return True
                
                print(f"Attempt {attempt + 1}/{max_attempts}: Record not propagated yet, waiting {wait_time} seconds...")
                time.sleep(wait_time)
            except Exception as e:
                print(f"Error checking DNS propagation: {str(e)}")
                time.sleep(wait_time)
        
        print(f"Failed to verify DNS propagation after {max_attempts} attempts")
        return False