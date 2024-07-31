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
    result = data['data']
    print_section_header("Account Information", file)
    print_to_both(f"{Fore.GREEN}Name:{Style.RESET_ALL} {result['first_name']} {result['last_name']}", file)
    print_to_both(f"{Fore.GREEN}Email:{Style.RESET_ALL} {result['email']}", file)
    print_to_both(f"{Fore.MAGENTA}Plan Name:{Style.RESET_ALL} {result['plan_name']}", file)
    print_to_both(f"{Fore.MAGENTA}Plan Level:{Style.RESET_ALL} {str(result['plan_level'])}", file)
    print_to_both(f"{Fore.YELLOW}Reset Date:{Style.RESET_ALL} {result['reset_date']}", file)
    print_to_both(f"{Fore.YELLOW}Team ID:{Style.RESET_ALL} {str(result['team_id'])}", file)

    print_section_header("Requests", file)
    print_to_both(f"{Fore.CYAN}Searches Used:{Style.RESET_ALL} {str(result['requests']['searches']['used'])}", file)
    print_to_both(f"{Fore.CYAN}Searches Available:{Style.RESET_ALL} {str(result['requests']['searches']['available'])}", file)
    print_to_both(f"{Fore.BLUE}Verifications Used:{Style.RESET_ALL} {str(result['requests']['verifications']['used'])}", file)
    print_to_both(f"{Fore.BLUE}Verifications Available:{Style.RESET_ALL} {str(result['requests']['verifications']['available'])}", file)

    print_section_header("Calls (Deprecated)", file)
    print_to_both(f"{Fore.RED}Used:{Style.RESET_ALL} {str(result['calls']['used'])}", file)
    print_to_both(f"{Fore.RED}Available:{Style.RESET_ALL} {str(result['calls']['available'])}", file)
    print_to_both(f"{Fore.RED}Deprecation Notice:{Style.RESET_ALL} {result['calls']['_deprecation_notice']}", file)

def fetch_account_info(api_key: str) -> Dict:
    url = "https://api.hunter.io/v2/account"
    params = {
        "api_key": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"{Fore.RED}API request failed with status code {response.status_code}{Style.RESET_ALL}")

def account_info(args, api_key):
    output_file = None
    try:
        data = fetch_account_info(api_key)
       
        if args.output:
            output_file = open(args.output, 'w')
       
        print_account_info_results(data, output_file)
       
        if output_file:
            output_file.close()
            print_to_both(f"{Fore.GREEN}\nResults have been saved to '{args.output}'{Style.RESET_ALL}", None)
   
    except Exception as e:
        print_to_both(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}", output_file)
    finally:
        if output_file:
            output_file.close()