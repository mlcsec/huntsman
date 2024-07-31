import os 
import sys
import argparse
import configparser
from colorama import init, Fore, Style

init(autoreset=True)

def setup():
    config = configparser.ConfigParser()
       
    config['HUNTERIO'] = {'API_KEY': input("Enter hunter.io API Key: ")}
    config['SNOVIO'] = {
        'USER_ID': input("Enter snov.io User ID: "),
        'SECRET': input("Enter snov.io Secret: ")
    }
    config['SKRAPPIO'] = {'API_KEY': input("Enter skrapp.io API Key: ")}
    
    with open('.huntsman.conf', 'w') as configfile:
        config.write(configfile)
    
    print(f"{Fore.GREEN}Configuration saved to '.huntsman.conf'{Style.RESET_ALL}")

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists('.huntsman.conf'):
        config.read('.huntsman.conf')
        return config
    return None

def main():
    try:
        parser = argparse.ArgumentParser(description="")
        subparsers = parser.add_subparsers(dest='service', metavar='', help='')

        # setup
        setup_parser = subparsers.add_parser('setup', help='API key(s) setup for huntsman')

        # hunterio parser
        hunterio_parser = subparsers.add_parser('hunterio', help='hunter.io commands')
        hunterio_subparsers = hunterio_parser.add_subparsers(dest='command')

        domain_search_parser = hunterio_subparsers.add_parser('domain-search', help='Perform a domain name search')
        domain_search_parser.add_argument("--domain", help="Target domain to search")
        domain_search_parser.add_argument("--emails-only", action="store_true", help="Only returns identified emails")
        domain_search_parser.add_argument("--entraid", action="store_true", help="Invoke user enumeration (AADInternals) with gathered emails")
        domain_search_parser.add_argument("--usergen", action="store_true", help="Generate common username formats from gathered first and last names")
        domain_search_parser.add_argument("--uri-confirm", action="store_true", help="Confirm presence of email or user information within returned URIs")
        domain_search_parser.add_argument("--uri-context", action="store_true", help="Discover surrounding context of email or user information within returned URIs")
        domain_search_parser.add_argument("--threads", type=int, default=10, help="Number of threads for --confirm or --context options (default: 10)")
        domain_search_parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds for --confirm or --context options (default: 10)")
        domain_search_parser.add_argument("--limit", type=int, default=10, help="Max number of email addresses to return (default: 10, max: 100)") 
        domain_search_parser.add_argument("--offset", type=int, default=0, help="Number of email addresses to skip (default: 0) e.g. 100 would print the second 100 emails") 
        domain_search_parser.add_argument("--type", choices=['personal', 'generic'], help="Get only personal or generic email addresses")
        domain_search_parser.add_argument("--seniority", choices=['junior', 'senior', 'executive'], help="Get only email addresses for people with the selected seniority level(s)")
        domain_search_parser.add_argument("--department", choices=['executive', 'it', 'finance', 'management', 'sales', 'legal', 'support', 'hr', 'marketing', 'communication', 'education', 'design', 'health', 'operations'], help="Get only email addresses for people working in the selected department(s)")
        domain_search_parser.add_argument("--required-field", choices=['full_name', 'position', 'phone_number'], help="Get only email addresses that have the selected field(s)")
        domain_search_parser.add_argument("--output", help="Output file name")

        email_finder_parser = hunterio_subparsers.add_parser('email-finder', help='Find email addresses for domain')
        email_finder_parser.add_argument("--domain", help="Domain name of the company (e.g. reddit.com)")
        email_finder_parser.add_argument("--entraid", action="store_true", help="Invoke user enumeration (AADInternals) for emails found")
        email_finder_parser.add_argument("--usergen", action="store_true", help="Generate common username formats from gathered first and last names")
        email_finder_parser.add_argument("--uri-confirm", action="store_true", help="Confirm presence of email or user information within returned URIs")
        email_finder_parser.add_argument("--uri-context", action="store_true", help="Discover surrounding context of email or user information within returned URIs")
        email_finder_parser.add_argument("--threads", type=int, default=10, help="Number of threads for --confirm or --context options (default: 10)")
        email_finder_parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds for --confirm or --context options (default: 10)")
        email_finder_parser.add_argument("--first-name", help="Person's first name")
        email_finder_parser.add_argument("--last-name", help="Person's last name")
        email_finder_parser.add_argument("--full-name", help="Person's full name")
        email_finder_parser.add_argument("--max-duration", type=int, default=10, help="Maximum duration of the request in seconds (3-20, default: 10)")
        email_finder_parser.add_argument("--output", help="Output file name")

        email_verifier_parser = hunterio_subparsers.add_parser('email-verifier', help='Verify email addresses')
        email_verifier_parser.add_argument("--email", help="The email address you want to verify")
        email_verifier_parser.add_argument("--entraid", action="store_true", help="Invoke user enumeration (AADInternals) for supplied emails")
        email_verifier_parser.add_argument("--uri-confirm", action="store_true", help="Confirm presence of email or user information within returned URIs")
        email_verifier_parser.add_argument("--uri-context", action="store_true", help="Discover surrounding context of email or user information within returned URIs")
        email_verifier_parser.add_argument("--threads", type=int, default=10, help="Number of threads for --confirm or --context options (default: 10)")
        email_verifier_parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds for --confirm or --context options (default: 10)")
        email_verifier_parser.add_argument("--output", help="Output file name")

        email_count_parser = hunterio_subparsers.add_parser('email-count', help='Get email count for a domain')
        email_count_parser.add_argument("--domain", help="The domain name for which you want to know the email count")
        email_count_parser.add_argument("--type", choices=['personal', 'generic'], help="Get the count of only personal or generic email addresses")
        email_count_parser.add_argument("--output", help="Output file name")

        account_info_parser = hunterio_subparsers.add_parser('account-info', help='Get information about your hunter.io account')
        account_info_parser.add_argument("--output", help="Output file name")

        # snovio parser 
        snovio_parser = subparsers.add_parser('snovio', help='snov.io commands')
        snovio_subparsers = snovio_parser.add_subparsers(dest='command')

        domain_searchv2_parser = snovio_subparsers.add_parser('domain-search', help='Perform a domain name search')
        domain_searchv2_parser.add_argument("--domain", help="Target domain to search")
        domain_searchv2_parser.add_argument("--emails-only", action="store_true", help="Only returns identified emails")
        domain_searchv2_parser.add_argument("--entraid", action="store_true", help="Invoke user enumeration (AADInternals) for supplied emails")
        domain_searchv2_parser.add_argument("--type", default='all', choices=['all', 'personal', 'generic'], help="Email address type (all, personal, or generic)")
        domain_searchv2_parser.add_argument("--limit", type=int, default=10, help="Max number of email addresses to return (default: 10, max: 100)")
        domain_searchv2_parser.add_argument("--last-id", type=int, default=0, help="Last ID value to skip previously returned data")
        domain_searchv2_parser.add_argument("--output", help="Output file name")

        get_profile_parser = snovio_subparsers.add_parser('get-profile', help='Get profile information for email addresses')
        get_profile_parser.add_argument("--email", help="The email address you want to verify")
        get_profile_parser.add_argument("--entraid", action="store_true", help="Invoke user enumeration (AADInternals) for supplied emails")
        get_profile_parser.add_argument("--usergen", action="store_true", help="Generate common username formats from gathered first and last names")
        get_profile_parser.add_argument("--socials", action="store_true", help="ONLY output associated social media links for emails")
        get_profile_parser.add_argument("--output", help="Output file name")

        snovemail_verifier_parser = snovio_subparsers.add_parser('email-verifier', help='Verify email addresses')
        snovemail_verifier_parser.add_argument("--email", help="The email address you want to verify")
        snovemail_verifier_parser.add_argument("--entraid", action="store_true", help="Invoke user enumeration (AADInternals) for supplied emails")
        snovemail_verifier_parser.add_argument("--output", help="Output file name")

        snovemail_count_parser = snovio_subparsers.add_parser('email-count', help='Get email count for a domain')
        snovemail_count_parser.add_argument("--domain", help="Target domain to search")
        snovemail_count_parser.add_argument("--output", help="Output file name")

        get_balance_parser = snovio_subparsers.add_parser('get-balance', help='Get your snov.io credit balance')
        get_balance_parser.add_argument("--output", help="Output file name")

        # skrappio parser
        skrappio_parser = subparsers.add_parser('skrappio', help='skrapp.io commands')
        skrappio_subparsers = skrappio_parser.add_subparsers(dest='command')

        company_profiles_search_parser = skrappio_subparsers.add_parser('company-search', help='Dump and explore the employment details of company members')
        company_profiles_search_parser.add_argument("--company", help="Company name to search for")
        company_profiles_search_parser.add_argument("--company-url", help="Company website URL")
        company_profiles_search_parser.add_argument("--emails-only", action="store_true", help="Only returns identified emails")
        company_profiles_search_parser.add_argument("--entraid", action="store_true", help="Invoke user enumeration (AADInternals) with gathered emails")
        company_profiles_search_parser.add_argument("--usergen", action="store_true", help="Generate common username formats from gathered first and last names")
        company_profiles_search_parser.add_argument("--size", default=10, help="Number of data to return per query (default: 10, max: 150)")
        company_profiles_search_parser.add_argument("--location", help="Geographic location keyword")
        company_profiles_search_parser.add_argument("--title", help="Job title keyword")
        company_profiles_search_parser.add_argument("--next", help="Pagination ID (next results ID) to get the next set of results")
        company_profiles_search_parser.add_argument("--output", help="Output file name")

        account_data_parser = skrappio_subparsers.add_parser('account-data', help='Get information about your skrapp.io account')
        account_data_parser.add_argument("--output", help="Output file name")

        args = parser.parse_args()

        if args.service == 'setup':
            setup()
            return

        config = load_config()

        # hunterio
        if args.service == 'hunterio':
            api_key = config['HUNTERIO']['API_KEY'] if config else os.environ.get('HUNTERIO_API_KEY')
            if not api_key:
                print(f"{Fore.RED}Error: hunter.io API key not found. Please run 'huntsman setup' or set HUNTERIO_API_KEY environment variable.{Style.RESET_ALL}")
                return

            if args.command == 'domain-search':
                from huntsman.commands_hunterio.domain_search import domain_search
                if not args.domain:
                    domain_search_parser.error(f"{Fore.RED}--domain <company.com> is required{Style.RESET_ALL}")
                domain_search(args, api_key)
            
            elif args.command == 'email-finder':
                from huntsman.commands_hunterio.email_finder import email_finder
                if not args.domain:
                    email_finder_parser.error(f"{Fore.RED}--domain <company.com> is required{Style.RESET_ALL}")
                if not ((args.first_name and args.last_name) or args.full_name):
                    email_finder_parser.error(f"{Fore.RED}--first-name AND --last-name OR --full-name is required{Style.RESET_ALL}")
                email_finder(args, api_key)
            
            elif args.command == 'email-verifier':
                from huntsman.commands_hunterio.email_verifier import email_verifier
                if not args.email:
                    email_verifier_parser.error(f"{Fore.RED}--email is required{Style.RESET_ALL}")
                email_verifier(args, api_key)
            
            elif args.command == 'email-count':
                from huntsman.commands_hunterio.email_count import email_count
                if not args.domain:
                    email_count_parser.error(f"{Fore.RED}--domain <company.com> is required{Style.RESET_ALL}")
                email_count(args, api_key)
            
            elif args.command == 'account-info':
                from huntsman.commands_hunterio.account_info import account_info
                account_info(args, api_key)
            
            else:
                hunterio_parser.print_help()

        # snovio
        elif args.service == 'snovio':
            if config:
                client_id = config['SNOVIO']['USER_ID']
                client_secret = config['SNOVIO']['SECRET']
            else:
                client_id = os.environ.get('SNOVIO_USER_ID')
                client_secret = os.environ.get('SNOVIO_SECRET')
            
            if not client_id or not client_secret:
                print(f"{Fore.RED}Error: snov.io credentials not found. Please run 'huntsman setup' or set SNOVIO_USER_ID and SNOVIO_SECRET environment variables.{Style.RESET_ALL}")
                return

            if args.command == 'domain-search':
                from huntsman.commands_snovio.domain_searchv2 import domain_searchv2
                if not args.domain:
                    domain_searchv2_parser.error(f"{Fore.RED}--domain <company.com> is required{Style.RESET_ALL}")
                domain_searchv2(args, client_id, client_secret)
            
            elif args.command == 'get-profile':
                from huntsman.commands_snovio.get_profile import get_profile
                if not args.email:
                    snovemail_verifier_parser.error(f"{Fore.RED}--email <file or comma-seperated> is required{Style.RESET_ALL}")
                get_profile(args, client_id, client_secret)

            elif args.command == 'email-verifier':
                from huntsman.commands_snovio.email_verifier import email_verifier
                if not args.email:
                    snovemail_verifier_parser.error(f"{Fore.RED}--email <email@domain.com> is required{Style.RESET_ALL}")
                email_verifier(args, client_id, client_secret)

            elif args.command == 'email-count':
                from huntsman.commands_snovio.email_count import email_count
                if not args.domain:
                    snovemail_count_parser.error(f"{Fore.RED}--domain <company.com> is required{Style.RESET_ALL}")
                email_count(args, client_id, client_secret)

            elif args.command == 'get-balance':
                from huntsman.commands_snovio.get_balance import get_balance
                get_balance(args, client_id, client_secret)

            else:
                snovio_parser.print_help()

        # skrappio
        elif args.service == 'skrappio':
            api_key = config['SKRAPPIO']['API_KEY'] if config else os.environ.get('SKRAPPIO_API_KEY')
            if not api_key:
                print(f"{Fore.RED}Error: skrapp.io API key not found. Please run 'huntsman setup' or set SKRAPPIO_API_KEY environment variable.{Style.RESET_ALL}")
                return

            if args.command == 'company-search':
                from huntsman.commands_skrappio.company_search import company_search
                if not args.company or args.company_url:
                    company_profiles_search_parser.error(f"{Fore.RED}--company-url or --company is required{Style.RESET_ALL}")
                company_search(args, api_key)

            elif args.command == 'account-data':
                from huntsman.commands_skrappio.account_data import account_data
                account_data(args, api_key)

            else:
                skrappio_parser.print_help()
        
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Keyboard interrupt detected. Exiting.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()