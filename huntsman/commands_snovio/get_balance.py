import os
import requests
import json
from typing import Dict
from colorama import init, Fore, Style
from huntsman.utils.helpers import print_info, print_section_header

def get_access_token(client_id: str, client_secret: str) -> str:
    url = 'https://api.snov.io/v1/oauth/access_token'
    params = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    try:
        response = requests.post(url, data=params, timeout=10)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get access token: {str(e)}")

def print_to_both(message, file=None):
    print(message)
    if file:
        file.write(message + '\n')

def print_balance_results(data: Dict, file=None):
    try:
        print_section_header("Balance Information", file)
        print_to_both(f"{Fore.GREEN}Balance:{Style.RESET_ALL} {data.get('balance', 'N/A')} credits", file)
        print_to_both(f"{Fore.MAGENTA}Teamwork:{Style.RESET_ALL} {'Yes' if data.get('teamwork', False) else 'No'}", file)
        print_to_both(f"{Fore.CYAN}Unique Recipients Used:{Style.RESET_ALL} {str(data.get('unique_recipients_used', 'N/A'))}", file)
        print_to_both(f"{Fore.YELLOW}Limit Resets In:{Style.RESET_ALL} {data.get('limit_resets_in', 'N/A')} days", file)
        print_to_both(f"{Fore.BLUE}Expires In:{Style.RESET_ALL} {data.get('expires_in', 'N/A')} days", file)
    except Exception as e:
        print_to_both(f"{Fore.RED}An error occurred while printing balance info: {str(e)}{Style.RESET_ALL}", file)

def fetch_balance_info(access_token: str) -> Dict:
    url = "https://api.snov.io/v1/get-balance"
    headers = {'Authorization': f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()['data']
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")

def get_balance(args, client_id: str, client_secret: str):
    output_file = None
    try:
        access_token = get_access_token(client_id, client_secret)
        data = fetch_balance_info(access_token)
       
        if args.output:
            try:
                output_file = open(args.output, 'w')
            except IOError as e:
                print_to_both(f"{Fore.RED}Error opening output file: {str(e)}{Style.RESET_ALL}", None)
                return
        print_balance_results(data, output_file)
       
    except Exception as e:
        print_to_both(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}", output_file)
    finally:
        if output_file:
            output_file.close()
            print_to_both(f"{Fore.GREEN}\nResults have been saved to '{args.output}'{Style.RESET_ALL}", None)