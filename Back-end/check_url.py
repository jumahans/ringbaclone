import whois
import socket
from urllib.parse import urlparse

def get_actual_carrier(url_or_ip):
    try:
        # 1. Clean the URL to get the hostname
        hostname = urlparse(url_or_ip).netloc if "://" in url_or_ip else url_or_ip
        
        # 2. Extract Root Domain (e.g., azurefd.net instead of z03.azurefd.net)
        domain_parts = hostname.split('.')
        root_domain = '.'.join(domain_parts[-2:]) 
        
        # 3. Try WHOIS on the root domain
        try:
            res = whois.whois(root_domain)
            if res.registrar or res.org:
                return res.registrar or res.org
        except:
            pass

        # 4. Fallback: Resolve to IP and check the IP's Carrier
        ip_address = socket.gethostbyname(hostname)
        ip_res = whois.whois(ip_address)
        return ip_res.get('org') or ip_res.get('asn_description')

    except Exception as e:
        return f"error {e}"

# Test with your Azure link
print(get_actual_carrier("https://edulogicpoint-g9hzcwcyewfrc0d8.z03.azurefd.net/Ma0cHelpAsMEr0t0140/index.html"))