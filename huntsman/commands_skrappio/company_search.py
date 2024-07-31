import sys
import requests
from colorama import Fore, Style
from typing import Dict, List
from huntsman.utils.helpers import print_info, print_section_header

def fetch_skrapp_data(api_key: str, **kwargs) -> Dict:
    url = "https://api.skrapp.io/profile/search/email"
    headers = {
        "X-Access-Key": api_key,
        "Content-Type": "application/json"
    }
    params = {k: v for k, v in kwargs.items() if v is not None}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

def print_company_info(data: Dict, file=None):
    company = data.get('company', {})
    if not company:
        print_to_both(f"{Fore.RED}No company information available.{Style.RESET_ALL}", file)
        return

    print_section_header("Company Information", file)
    
    fields = [
        ('Name', 'name'),
        ('Domain', 'domain'),
        ('Website', 'website'),
        ('Industry', 'industry'),
        ('Type', 'type'),
        ('LinkedIn', 'linkedin_url'),
        ('Revenue', 'revenue'),
        ('Employees', 'employee_count'),
        ('Location', lambda c: f"{c.get('city', 'N/A')}, {c.get('geo_area', 'N/A')}, {c.get('country', 'N/A')}"),
    ]

    for label, key in fields:
        value = company.get(key, 'N/A') if isinstance(key, str) else key(company)
        print_to_both(f"{Fore.GREEN}{label}:{Style.RESET_ALL} {value}", file)

    meta = data.get('meta', {})
    email_count = meta.get('total_all')    
    print_to_both(f"{Fore.GREEN}Total Results:{Style.RESET_ALL} {email_count}", file)

    print_section_header("Specialities", file)
    
    specialities = company.get('specialities', [])
    if specialities:
        for specialty in specialities:
            print_to_both(f"{Fore.YELLOW}•{Style.RESET_ALL} {specialty}", file)
    else:
        print_to_both(f"{Fore.YELLOW}No specialities listed.{Style.RESET_ALL}", file)

def print_results(data: Dict, file=None):
    results = data.get('results', [])
    print_section_header("Profile Results", file)
    for result in results:
        print_to_both(f"{Fore.MAGENTA}Name:{Style.RESET_ALL} {result.get('full_name', 'N/A')}", file)
        print_to_both(f"{Fore.MAGENTA}Location:{Style.RESET_ALL} {result.get('location', 'N/A')}", file)
       
        position = result.get('position', {})
        if position:
            print_to_both(f"{Fore.MAGENTA}Position:{Style.RESET_ALL}", file)
            print_to_both(f"  {Fore.CYAN}Title:{Style.RESET_ALL} {position.get('title', 'N/A')}", file)
            print_to_both(f"  {Fore.CYAN}Location:{Style.RESET_ALL} {position.get('location', 'N/A')}", file)
            start_date = position.get('start_date', {})
            if start_date:
                start_date_str = f"{start_date.get('month', 'N/A')}/{start_date.get('year', 'N/A')}"
                print_to_both(f"  {Fore.CYAN}Start Date:{Style.RESET_ALL} {start_date_str}", file)
        else:
            print_to_both(f"{Fore.MAGENTA}Position:{Style.RESET_ALL} N/A", file)

        print_to_both(f"{Fore.MAGENTA}Email:{Style.RESET_ALL} {result.get('email', 'N/A')}", file)
        
        email_quality = result.get('email_quality', {})
        if email_quality:
            print_to_both(f"{Fore.MAGENTA}Email Quality:{Style.RESET_ALL}", file)
            print_to_both(f"  {Fore.CYAN}Status:{Style.RESET_ALL} {email_quality.get('status', 'N/A')}", file)
            print_to_both(f"  {Fore.CYAN}Message:{Style.RESET_ALL} {email_quality.get('status_message', 'N/A')}", file)
        
        print_to_both(f"{Fore.YELLOW}{'-' * 40}{Style.RESET_ALL}", file)

def print_to_both(message, file=None):
    print(message)
    if file:
        file.write(message + '\n')

def company_search(args, api_key):
    try:
        params = {
            "companyName": args.company,
            "companyWebsite": args.company_url,
            "title": args.title,
            "location": args.location,
            "size": args.size
        }
        
        if hasattr(args, 'next') and args.next:
            params["nextId"] = args.next

        data = fetch_skrapp_data(api_key, **params)
        
        output_file = None
        if hasattr(args, 'output') and args.output:
            output_file = open(args.output, 'w')

        if args.emails_only:
            if 'results' in data:
                for result in data['results']:
                    email = result.get('email', 'N/A')
                    print_to_both(email, output_file)
        else:
            if 'company' in data:
                print_company_info(data, output_file)
            else:
                print_to_both(f"{Fore.RED}No company information available.{Style.RESET_ALL}", output_file)
            
            if 'results' in data:
                print_results(data, output_file)
            else:
                print_to_both(f"{Fore.RED}No profile results available.{Style.RESET_ALL}", output_file)
        
        meta = data.get('meta', {})
        
        next_results_id = meta.get('next_results_id')
        if next_results_id:
            print_to_both(f"{Fore.YELLOW}\nTo get the next {args.size} results append: --next {next_results_id}{Style.RESET_ALL}", output_file)
        
        emails = []
        for result in data['results']:
            email = result.get('email', 'N/A')
            emails.append(email)

        # usergen
        if args.usergen:
            from huntsman.utils.user_gen import generate_usernames
            print_section_header("Username Generation", output_file)
            is_first = True
            for dat in data['results']:
                if 'first_name' in dat and 'last_name' in dat and dat['first_name'] and dat['last_name']:
                    if not is_first:
                        pass
                    else:
                        is_first = False
                    
                    first_names = [dat['first_name']]
                    last_names = [dat['last_name']]
                    generated_usernames = generate_usernames(first_names, last_names, output_file)
                    for username in generated_usernames:
                        print_to_both(username, output_file)
                else:
                    print_to_both(f"Skipping usergen for {dat['value']} - missing first name or last name", output_file)

        # entraid
        if args.entraid:
            from huntsman.utils.user_enum import invoke_userenumerationasoutsider
            invoke_userenumerationasoutsider(emails, output_file)
            
        if output_file:
            output_file.close()
            print(f"{Fore.GREEN}\nResults have been saved to '{args.output}'{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}")