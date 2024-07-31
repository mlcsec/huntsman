import os
import requests
from typing import Dict, List
from colorama import init, Fore, Style
from huntsman.utils.helpers import print_info, print_section_header

def print_to_both(message, file=None):
    print(message)
    if file:
        file.write(message + '\n')

def print_account_info_results(data: Dict, file=None):
    try:
        print_section_header("Account Information", file)
        print_to_both(f"{Fore.GREEN}Name:{Style.RESET_ALL} {data.get('name', 'N/A')}", file)
        print_to_both(f"{Fore.GREEN}Email:{Style.RESET_ALL} {data.get('email', 'N/A')}", file)
        print_to_both(f"{Fore.MAGENTA}Package:{Style.RESET_ALL} {data.get('package', 'N/A')}", file)
        print_to_both(f"{Fore.YELLOW}Package Renewal Date:{Style.RESET_ALL} {str(data.get('packageRDate', 'N/A'))}", file)
        
        print_section_header("Credits", file)
        credits = data.get('credit', {}).get('email', {})
        print_to_both(f"{Fore.CYAN}Email Quota:{Style.RESET_ALL} {str(credits.get('quota', 'N/A'))}", file)
        print_to_both(f"{Fore.CYAN}Email Used:{Style.RESET_ALL} {str(credits.get('used', 'N/A'))}", file)
        
        print_section_header("Options", file)
        options = data.get('options', {})
        if options:
            for option, value in options.items():
                print_to_both(f"{Fore.BLUE}{option.replace('_', ' ').title()}:{Style.RESET_ALL} {str(value)}", file)
        else:
            print_to_both(f"{Fore.BLUE}Options:{Style.RESET_ALL} N/A", file)
        
        print_section_header("Lists", file)
        lists = data.get('lists', [])
        if lists:
            for list_info in lists:
                print_to_both(f"{Fore.YELLOW}List {list_info.get('id', 'N/A')}:{Style.RESET_ALL} "
                              f"{list_info.get('name', 'N/A')} (Path: {list_info.get('path', 'N/A')})", file)
        else:
            print_to_both(f"{Fore.YELLOW}Lists:{Style.RESET_ALL} N/A", file)
    except Exception as e:
        print_to_both(f"{Fore.RED}An error occurred while printing account info: {str(e)}{Style.RESET_ALL}", file)

def fetch_account_info(api_key: str) -> Dict:
    url = "https://api.skrapp.io/api/v2/account"
    headers = {
        "X-Access-Key": api_key,
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")

def account_data(args, api_key):
    output_file = None
    try:
        data = fetch_account_info(api_key)
       
        if args.output:
            try:
                output_file = open(args.output, 'w')
            except IOError as e:
                print_to_both(f"{Fore.RED}Error opening output file: {str(e)}{Style.RESET_ALL}", None)
                return
        print_account_info_results(data, output_file)
       
    except Exception as e:
        print_to_both(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}", output_file)
    finally:
        if output_file:
            output_file.close()
            print_to_both(f"{Fore.GREEN}\nResults have been saved to '{args.output}'{Style.RESET_ALL}", None)