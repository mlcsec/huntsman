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

def fetch_domain_data(access_token: str, **kwargs) -> Dict:
    url = "https://api.snov.io/v2/domain-emails-with-info"
    params = {
        "access_token": access_token,
        **{k: v for k, v in kwargs.items() if v is not None}
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

def print_to_both(message, file=None):
    print(message)
    if file:
        file.write(message + '\n')

def print_domain_info(data: Dict, file=None):
    print_section_header("Domain Information", file)
    print_to_both(f"{Fore.GREEN}Domain:{Style.RESET_ALL} {data['domain']}", file)
    print_to_both(f"{Fore.GREEN}Webmail:{Style.RESET_ALL} {data['webmail']}", file)
    print_to_both(f"{Fore.GREEN}Total Results:{Style.RESET_ALL} {data['result']}", file)

def print_emails(data: Dict, file=None):
    print_section_header("Email Results", file)
    
    for email in data['emails']:
        print_to_both(f"{Fore.MAGENTA}Email:{Style.RESET_ALL} {email['email']}", file)
        #print_to_both(f"{Fore.MAGENTA}Name:{Style.RESET_ALL} {email.get('firstName', 'N/A')} {email.get('lastName', 'N/A')}", file)
        #print_to_both(f"{Fore.MAGENTA}Position:{Style.RESET_ALL} {email.get('position', 'N/A')}", file)
        print_to_both(f"{Fore.MAGENTA}Type:{Style.RESET_ALL} {email['type']}", file)
        print_to_both(f"{Fore.MAGENTA}Status:{Style.RESET_ALL} {email['status']}", file)
        #print_to_both(f"{Fore.MAGENTA}Source:{Style.RESET_ALL} {email.get('sourcePage', 'N/A')}", file)
        print_to_both(f"{Fore.YELLOW}{'-' * 40}{Style.RESET_ALL}", file)

def domain_searchv2(args, client_id: str, client_secret: str):
    try:
        access_token = get_access_token(client_id, client_secret)
        
        data = fetch_domain_data(
            access_token,
            domain=args.domain,
            type=args.type,
            limit=args.limit,
            lastId=args.last_id
        )
        
        output_file = None
        if args.output:
            output_file = open(args.output, 'w')

        if args.emails_only:
            for email in data['emails']:
                print_to_both(email['email'], output_file)
        else:
            print_domain_info(data, output_file)
            print_emails(data, output_file)
        
        print_to_both(f"\n{Fore.GREEN}Last ID: {data['lastId']}{Style.RESET_ALL}", output_file)
        print_to_both(f"{Fore.YELLOW}To get the next set of results, use: --last-id {data['lastId']}{Style.RESET_ALL}", output_file)

        emails = []
        for result in data['emails']:
            email = result.get('email', 'N/A')
            emails.append(email)

        # entraid
        if args.entraid:
            from huntsman.utils.user_enum import invoke_userenumerationasoutsider
            invoke_userenumerationasoutsider(emails, output_file)

        if output_file:
            output_file.close()
            print_to_both(f"\n{Fore.GREEN}Results have been saved to {args.output}{Style.RESET_ALL}", None)
    
    except Exception as e:
        print_to_both(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}", output_file)