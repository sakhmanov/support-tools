import subprocess
import sys
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup

now = datetime.now()
rounded_time = now.replace(minute=0, second=0, microsecond=0)
command = "cat /etc/openvpn/server/openvpn-status.log | awk -F',' '$1 == \"CLIENT_LIST\" { print $4 }'"
output_file = "/var/local/signal-strength/signal-strength.csv"

try:
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    ips = result.stdout.decode('utf-8').strip().split("\n")

except Exception as e:
    print(f"Error getting modems IP list: {e}")
    exit(1)

modems = {}

with ThreadPoolExecutor(max_workers=25) as executor:
    futures = {executor.submit(requests.get, f'http://{ip}/cgi-bin/luci', timeout=180): ip for ip in ips}
    
    for future in as_completed(futures):
        ip = futures[future]
        try:
            response = future.result()
            modems[ip] = {
                "status_code": response.status_code,
                "content": response.text if response.status_code == 403 else None
            }        
        except requests.exceptions.RequestException as e:
            modems[ip] = {
                "status_code": None,
                "content": f"Exception: {e}"
            }

with open(output_file, mode='a', encoding="utf-8") as csv_file:
    csv_output = csv.writer(csv_file)
    for ip, modem in modems.items():
        if modem['status_code'] == 403:
            soup = BeautifulSoup(modem['content'], 'lxml')
            table = soup.find('table')
            table_data = []
            for row in table.find_all('tr'):
                row_data = [rounded_time, ip]
                for cell in row.find_all(['td', 'th'])[1::2]:
                    row_data.append(cell.get_text(strip=True).replace(',', '').replace('\"', ''))
                table_data.append(row_data)
            csv_output.writerows(table_data)
        else:
            print(f"{modem['content']}")
