import os 
import requests
from typing import Dict, List
from colorama import init, Fore, Style
from huntsman.utils.helpers import print_section_header, print_info

def fetch_email_verifier_data(email: str, api_key: str) -> Dict:
    url = "https://api.hunter.io/v2/email-verifier"
    params = {
        "email": email,
        "api_key": api_key
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"{Fore.RED}API request failed with status code {response.status_code}{Style.RESET_ALL}")

def print_to_both(message, file=None):
    print(message)
    if file:
        file.write(message + '\n')

def print_email_verifier_results(email, data: Dict, file=None):
    result = data['data']
    print_section_header(f"Email Verification {email}", file)
    print_to_both(f"{Fore.GREEN}Email:{Style.RESET_ALL} {result['email']}", file)
    print_to_both(f"{Fore.MAGENTA}Status:{Style.RESET_ALL} {result['status']}", file)
    print_to_both(f"{Fore.YELLOW}Result:{Style.RESET_ALL} {result['result']}", file)
    print_to_both(f"{Fore.CYAN}Score:{Style.RESET_ALL} {str(result['score'])}", file)
    print_to_both(f"{Fore.CYAN}Regular Expression:{Style.RESET_ALL} {str(result['regexp'])}", file)
    print_to_both(f"{Fore.CYAN}Gibberish:{Style.RESET_ALL} {str(result['gibberish'])}", file)
    print_to_both(f"{Fore.CYAN}Disposable:{Style.RESET_ALL} {str(result['disposable'])}", file)
    print_to_both(f"{Fore.CYAN}Webmail:{Style.RESET_ALL} {str(result['webmail'])}", file)
    print_to_both(f"{Fore.CYAN}MX Records:{Style.RESET_ALL} {str(result['mx_records'])}", file)
    print_to_both(f"{Fore.CYAN}SMTP Server:{Style.RESET_ALL} {str(result['smtp_server'])}", file)
    print_to_both(f"{Fore.CYAN}SMTP Check:{Style.RESET_ALL} {str(result['smtp_check'])}", file)
    print_to_both(f"{Fore.CYAN}Accept All:{Style.RESET_ALL} {str(result['accept_all'])}", file)
    print_to_both(f"{Fore.CYAN}Block:{Style.RESET_ALL} {str(result['block'])}", file)
    
    if result.get('sources'):
        print_to_both(f"{Fore.CYAN}Sources: {Style.RESET_ALL}", file)
        for source in result['sources']:
            print_to_both(f"{Fore.YELLOW}Domain:{Style.RESET_ALL} {source['domain']}", file)
            print_to_both(f"{Fore.YELLOW}URI:{Style.RESET_ALL} {source['uri']}", file)
            print_to_both(f"{Fore.YELLOW}Extracted On:{Style.RESET_ALL} {source['extracted_on']}", file)
            print_to_both(f"{Fore.YELLOW}Last Seen On:{Style.RESET_ALL} {source['last_seen_on']}", file)
            print_to_both(f"{Fore.YELLOW}Still On Page:{Style.RESET_ALL} {str(source['still_on_page'])}", file)
            print_to_both(f"{Fore.YELLOW}{'-' * 40}{Style.RESET_ALL}", file)

def email_verifier(args, api_key):
    output_file = None
    try:
        emails = []
        if os.path.isfile(args.email):
            try:
                with open(args.email, 'r') as file:
                    emails = [line.strip() for line in file if line.strip()]
            except IOError:
                print_to_both(f"{Fore.RED}Error: Unable to read file {args.email}{Style.RESET_ALL}", None)
                return
        else:
            emails = [email.strip() for email in args.email.split(',') if email.strip()]
        
        if args.output:
            output_file = open(args.output, 'w')
        
        for email in emails:
            data = fetch_email_verifier_data([email], api_key)
            print_email_verifier_results(email, data, output_file)
            
            # entraid
            if args.entraid:
                usernames = [email]
                print_to_both(f"{Fore.CYAN}Entra ID User Enumeration: {Style.RESET_ALL}", output_file)
                for username in usernames:
                    exists = None
                    try:
                        url = "https://login.microsoftonline.com/common/GetCredentialType"
                        userdata = {
                            "username": username,
                            "isOtherIdpSupported": True,
                            "checkPhones": False,
                            "isRemoteNGCSupported": True,
                            "isCookieBannerShown": False,
                            "isFidoSupported": True,
                            "originalRequest": "",
                            "country": "US",
                            "forceotclogin": False,
                            "isExternalFederationDisallowed": False,
                            "isRemoteConnectSupported": False,
                            "federationFlags": 0,
                            "isSignup": False,
                            "flowToken": "",
                            "isAccessPassSupported": True
                        }
                        response = requests.post(url, json=userdata)
                        if response.status_code == 200:
                            result = response.json()
                            exists = result.get('IfExistsResult', 0) == 0
                    except:
                        pass
                    
                    if exists:
                        message = f"{Fore.GREEN}[+] {username:<16}{Style.RESET_ALL}"
                    else:
                        message = f"{Fore.RED}[-] {username:<16}{Style.RESET_ALL}"
                    
                    print_to_both(message, output_file)

            # confirm
            if args.uri_confirm:
                from huntsman.commands_hunterio.confirm_user import confirm_URI
                print_to_both(f"{Fore.CYAN}Confirming Email URIs: {Style.RESET_ALL}", output_file)
                confirm_URI(args.threads, args.timeout, data, output_file)
            
            # context
            if args.uri_context:
                from huntsman.commands_hunterio.confirm_context import confirm_context
                print_to_both(f"{Fore.CYAN}Confirming Email URIs with Context: {Style.RESET_ALL}", output_file)
                confirm_context(args.threads, args.timeout, data, output_file)
        
        if output_file:
            output_file.close()
            print_to_both(f"{Fore.GREEN}\nResults have been saved to '{args.output}'{Style.RESET_ALL}", None)
    
    except Exception as e:
        print_to_both(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}", output_file)
    finally:
        if output_file:
            output_file.close()