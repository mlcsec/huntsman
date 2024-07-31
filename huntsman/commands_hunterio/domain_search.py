import requests
from typing import Dict, List
from colorama import init, Fore, Style
from huntsman.utils.helpers import print_section_header, print_info

def print_to_both(message, file=None):
    print(message)
    if file:
        file.write(message + '\n')

def print_company_info(data: Dict, file=None):
    company_info = data['data']
    print_section_header("Company Information", file)
    print_to_both(f"{Fore.GREEN}Domain:{Style.RESET_ALL} {company_info['domain']}", file)
    print_to_both(f"{Fore.GREEN}Organization:{Style.RESET_ALL} {company_info['organization']}", file)
    print_to_both(f"{Fore.GREEN}Description:{Style.RESET_ALL} {company_info['description']}", file)
    print_to_both(f"{Fore.GREEN}Industry:{Style.RESET_ALL} {company_info['industry']}", file)
    print_to_both(f"{Fore.GREEN}Location:{Style.RESET_ALL} {company_info['city']}, {company_info['state']}, {company_info['country']}", file)
    print_to_both(f"{Fore.GREEN}Headcount:{Style.RESET_ALL} {company_info['headcount']}", file)
    print_to_both(f"{Fore.GREEN}Company Type:{Style.RESET_ALL} {company_info['company_type']}", file)
    print_to_both(f"{Fore.GREEN}Total Results:{Style.RESET_ALL} {data['meta']['results']}", file)

    print_section_header("Social Media", file)
    print_to_both(f"{Fore.CYAN}Twitter:{Style.RESET_ALL} {company_info['twitter']}", file)
    print_to_both(f"{Fore.CYAN}Facebook:{Style.RESET_ALL} {company_info['facebook']}", file)
    print_to_both(f"{Fore.CYAN}LinkedIn:{Style.RESET_ALL} {company_info['linkedin']}", file)
    print_to_both(f"{Fore.CYAN}YouTube:{Style.RESET_ALL} {company_info['youtube']}", file)

    print_section_header("Technologies", file)
    for tech in company_info['technologies']:
        print_to_both(f"{Fore.YELLOW}•{Style.RESET_ALL} {tech}", file)

def print_emails(data: Dict, file=None):
    emails = data['data']['emails']
    print_section_header("Identified Emails", file)
    for email in emails:
        print_to_both(f"{Fore.YELLOW}Email:{Style.RESET_ALL} {email['value']}", file)
        print_to_both(f"{Fore.YELLOW}Type:{Style.RESET_ALL} {email['type']}", file)
        print_to_both(f"{Fore.YELLOW}Name:{Style.RESET_ALL} {email['first_name']} {email['last_name']}", file)
        print_to_both(f"{Fore.YELLOW}Position:{Style.RESET_ALL} {email['position'] or 'N/A'}", file)
        print_to_both(f"{Fore.YELLOW}Department:{Style.RESET_ALL} {email['department'] or 'N/A'}", file)
        print_to_both(f"{Fore.YELLOW}LinkedIn:{Style.RESET_ALL} {email['linkedin']}", file)
        print_to_both(f"{Fore.YELLOW}Twitter:{Style.RESET_ALL} {email['twitter']}", file)
        print_to_both(f"{Fore.YELLOW}Phone Number:{Style.RESET_ALL} {email['phone_number']}", file)
        print_to_both(f"{Fore.YELLOW}Confidence:{Style.RESET_ALL} {email['confidence']}%", file)
        if email['sources']:
            print_to_both(f"{Fore.YELLOW}Source:{Style.RESET_ALL}", file)
            for source in email['sources']:
                print_to_both(f"  {Fore.CYAN}URI:{Style.RESET_ALL} {Fore.RESET}{source['uri']}{Style.RESET_ALL}", file)
                print_to_both(f"  {Fore.CYAN}Extracted on:{Style.RESET_ALL} {source['extracted_on']}", file)
                print_to_both(f"  {Fore.CYAN}Last seen on:{Style.RESET_ALL} {source['last_seen_on']}", file)
                print_to_both(f"  {Fore.CYAN}Still on page:{Style.RESET_ALL} {str(source['still_on_page'])}", file)
        print_to_both(f"{Fore.YELLOW}{'-' * 40}{Style.RESET_ALL}", file)

def fetch_domain_data(domain: str, api_key: str, **kwargs) -> Dict:
    url = f"https://api.hunter.io/v2/domain-search"
    params = {
        "domain": domain,
        "api_key": api_key,
        "limit": kwargs.get('limit', 10),
        "offset": kwargs.get('offset', 0),
    }
    
    if kwargs.get('type'):
        params['type'] = kwargs['type']
    if kwargs.get('seniority'):
        params['seniority'] = kwargs['seniority']
    if kwargs.get('department'):
        params['department'] = kwargs['department']
    if kwargs.get('required_field'):
        params['required_field'] = kwargs['required_field']

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"{Fore.RED}API request failed with status code {response.status_code}{Style.RESET_ALL}")

def domain_search(args, api_key):
    output_file = None
    try:
        data = fetch_domain_data(
            args.domain, 
            api_key, 
            limit=args.limit, 
            offset=args.offset, 
            type=args.type, 
            seniority=args.seniority, 
            department=args.department, 
            required_field=args.required_field
        )
        
        if args.output:
            output_file = open(args.output, 'w', encoding='utf-8-sig') 

        if args.emails_only:
            for email in data['data']['emails']:
                print_to_both(email['value'], output_file)
        else:
            print_company_info(data, output_file)
            print_emails(data, output_file)

        # usergen
        if args.usergen:
            from huntsman.utils.user_gen import generate_usernames
            print_section_header("Username Generation", output_file)
            is_first = True
            for email in data['data']['emails']:
                if 'first_name' in email and 'last_name' in email and email['first_name'] and email['last_name']:
                    if not is_first:
                        pass
                    else:
                        is_first = False
                    
                    first_names = [email['first_name']]
                    last_names = [email['last_name']]
                    generated_usernames = generate_usernames(first_names, last_names, output_file)
                    for username in generated_usernames:
                        print_to_both(username, output_file)
                else:
                    print_to_both(f"Skipping usergen for {email['value']} - missing first name or last name", output_file)

        # entraid
        if args.entraid:
            from huntsman.utils.user_enum import invoke_userenumerationasoutsider
            usernames = [email['value'] for email in data['data']['emails']]
            invoke_userenumerationasoutsider(usernames, output_file)

        # confirm
        if args.uri_confirm:
            from huntsman.commands_hunterio.confirm_user import confirm_URI
            print_section_header("Confirming Email URIs", output_file)
            confirm_URI(args.threads, args.timeout, data, output_file) 
        
        # confirm-context
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