import requests
from typing import Dict, List
from colorama import init, Fore, Style
from huntsman.utils.helpers import print_section_header, print_info

def fetch_email_finder_data(api_key: str, **kwargs) -> Dict:
    url = "https://api.hunter.io/v2/email-finder"
    params = {
        "api_key": api_key,
        "max_duration": kwargs.get('max_duration', 10)
    }
    
    if kwargs.get('domain'):
        params['domain'] = kwargs['domain']
    if kwargs.get('first_name'):
        params['first_name'] = kwargs['first_name']
    if kwargs.get('last_name'):
        params['last_name'] = kwargs['last_name']
    if kwargs.get('full_name'):
        params['full_name'] = kwargs['full_name']

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"{Fore.RED}API request failed with status code {response.status_code}{Style.RESET_ALL}")

def print_to_both(message, file=None):
    print(message)
    if file:
        file.write(message + '\n')

def print_email_finder_results(data: Dict, file=None):
    result = data['data']
    print_section_header("Email Finder Results", file)
    print_to_both(f"{Fore.GREEN}First Name:{Style.RESET_ALL} {result['first_name']}", file)
    print_to_both(f"{Fore.GREEN}Last Name:{Style.RESET_ALL} {result['last_name']}", file)
    print_to_both(f"{Fore.MAGENTA}Email:{Style.RESET_ALL} {result['email']}", file)
    print_to_both(f"{Fore.YELLOW}Score:{Style.RESET_ALL} {str(result['score'])}", file)
    print_to_both(f"{Fore.CYAN}Domain:{Style.RESET_ALL} {result['domain']}", file)
    print_to_both(f"{Fore.CYAN}Company:{Style.RESET_ALL} {result.get('company', 'N/A')}", file)
    print_to_both(f"{Fore.CYAN}Position:{Style.RESET_ALL} {result.get('position', 'N/A')}", file)
    print_to_both(f"{Fore.CYAN}Twitter:{Style.RESET_ALL} {result.get('twitter', 'N/A')}", file)
    print_to_both(f"{Fore.CYAN}LinkedIn URL:{Style.RESET_ALL} {result.get('linkedin_url', 'N/A')}", file)
    print_to_both(f"{Fore.CYAN}Phone Number:{Style.RESET_ALL} {result.get('phone_number', 'N/A')}", file)
    
    if result.get('sources'):
        print_section_header("Sources", file)
        for source in result['sources']:
            print_to_both(f"{Fore.YELLOW}Domain:{Style.RESET_ALL} {source['domain']}", file)
            print_to_both(f"{Fore.YELLOW}URI:{Style.RESET_ALL} {source['uri']}", file)
            print_to_both(f"{Fore.YELLOW}Extracted On:{Style.RESET_ALL} {source['extracted_on']}", file)
            print_to_both(f"{Fore.YELLOW}Last Seen On:{Style.RESET_ALL} {source['last_seen_on']}", file)
            print_to_both(f"{Fore.YELLOW}Still On Page:{Style.RESET_ALL} {str(source['still_on_page'])}", file)
            print_to_both(f"{Fore.YELLOW}{'-' * 40}{Style.RESET_ALL}", file)

def email_finder(args, api_key):
    output_file = None
    try:
        data = fetch_email_finder_data(
            api_key,
            domain=args.domain,
            first_name=args.first_name,
            last_name=args.last_name,
            full_name=args.full_name,
            max_duration=args.max_duration
        )
        
        if args.output:
            output_file = open(args.output, 'w')
        
        print_email_finder_results(data, output_file)

        # entraid
        if args.entraid:
            from huntsman.utils.user_enum import invoke_userenumerationasoutsider
            result = data['data']
            email = result['email']
            usernames = [email]
            invoke_userenumerationasoutsider(usernames, output_file)

        # usergen
        if args.usergen:
            from huntsman.utils.user_gen import generate_usernames
            print_section_header("Username Generation", output_file)
            result = data['data']
            fn = result['first_name']
            ln = result['last_name']
            first_names = [fn]
            last_names = [ln]
            usernames = generate_usernames(first_names, last_names, output_file)
            for username in usernames:
                print_to_both(username, output_file)

        # confirm
        if args.uri_confirm:
            from huntsman.commands_hunterio.confirm_user import confirm_URI
            print_section_header("Confirming Email URIs", output_file)
            confirm_URI(args.threads, args.timeout, data, output_file) 

        # context
        if args.uri_context:
            from huntsman.commands_hunterio.confirm_context import confirm_context
            print_section_header("Confirming Email URIs with Context", output_file)
            confirm_context(args.threads, args.timeout, data, output_file)
            
        if output_file:
            output_file.close()
            print_to_both(f"{Fore.GREEN}\nResults have been saved to '{args.output}'{Style.RESET_ALL}", None)
    
    except Exception as e:
        print_to_both(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}", output_file)
    finally:
        if output_file:
            output_file.close()