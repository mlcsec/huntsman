import requests
import json
from colorama import Fore, Style
from typing import Dict, List
from huntsman.utils.helpers import print_info, print_section_header

def get_access_token(client_id: str, client_secret: str) -> str:
    params = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    res = requests.post('https://api.snov.io/v1/oauth/access_token', data=params)
    resText = res.text.encode('ascii', 'ignore')
    return json.loads(resText)['access_token']

def fetch_email_count_data(access_token: str, domain) -> Dict:
    url = "https://api.snov.io/v1/get-domain-emails-count"
    params = {
        "access_token": access_token,
        "domain": domain
    }
   
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

def print_to_both(message, file=None):
    print(message)
    if file:
        file.write(message + '\n')

def print_email_count_results(data: Dict, file=None):    
    print_section_header("Email Count Results", file)
    print_to_both(f"{Fore.YELLOW}Domain:{Style.RESET_ALL} {str(data['domain'])}", file)
    print_to_both(f"{Fore.GREEN}Total Emails:{Style.RESET_ALL} {str(data['result'])}", file)
    print_to_both(f"{Fore.MAGENTA}Webmail:{Style.RESET_ALL} {str(data['webmail'])}", file)

def email_count(args, client_id: str, client_secret: str):
    output_file = None
    try:
        access_token = get_access_token(client_id, client_secret)
        data = fetch_email_count_data(access_token, args.domain)
        
        if args.output:
            output_file = open(args.output, 'w')
        
        print_email_count_results(data, output_file)
        
        if output_file:
            output_file.close()
            print_to_both(f"{Fore.GREEN}\nResults have been saved to '{args.output}'{Style.RESET_ALL}", None)
   
    except Exception as e:
        print_to_both(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}", output_file)
    finally:
        if output_file:
            output_file.close()