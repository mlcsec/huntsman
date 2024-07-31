import requests
from typing import Dict, List
from colorama import init, Fore, Style
from huntsman.utils.helpers import print_section_header, print_info

def fetch_email_count_data(api_key: str, domain: str = None, email_type: str = None) -> Dict:
    url = "https://api.hunter.io/v2/email-count"
    params = {"api_key": api_key}
    if domain:
        params['domain'] = domain
    if email_type:
        params['type'] = email_type
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"{Fore.RED}API request failed with status code {response.status_code}{Style.RESET_ALL}")

def print_to_both(message, file=None):
    print(message)
    if file:
        file.write(message + '\n')

def print_email_count_results(data: Dict, file=None):
    result = data['data']
    print_section_header("Email Count Results", file)
    print_to_both(f"{Fore.GREEN}Total Emails:{Style.RESET_ALL} {str(result['total'])}", file)
    print_to_both(f"{Fore.MAGENTA}Personal Emails:{Style.RESET_ALL} {str(result['personal_emails'])}", file)
    print_to_both(f"{Fore.YELLOW}Generic Emails:{Style.RESET_ALL} {str(result['generic_emails'])}", file)

    print_section_header("Department Breakdown", file)
    for dept, count in result['department'].items():
        print_to_both(f"{Fore.CYAN}{dept.capitalize()}:{Style.RESET_ALL} {str(count)}", file)
   
    print_section_header("Seniority Breakdown", file)
    for level, count in result['seniority'].items():
        print_to_both(f"{Fore.BLUE}{level.capitalize()}:{Style.RESET_ALL} {str(count)}", file)

def email_count(args, api_key):
    output_file = None
    try:
        data = fetch_email_count_data(api_key, args.domain, args.type)
       
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