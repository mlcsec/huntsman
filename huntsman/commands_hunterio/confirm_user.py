import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from colorama import init, Fore, Style
from urllib3.exceptions import NameResolutionError
import concurrent.futures
import re

def print_to_both(message, file=None):
    print(message)
    if file:
        file.write(message + '\n')

def check_uri(uri, headers, timeout_seconds, email, emailname, firstname=None, lastname=None):
    try:
        response = requests.get(uri, headers=headers, timeout=timeout_seconds)
        response.raise_for_status()
        content = response.text.lower()
        found = []
        if email.lower() in content:
            found.append(f"email: {email}")
        if emailname.lower() in content:
            found.append(f"email username: {emailname}")
        if firstname.lower() in content:
            found.append(f"first name: {firstname}")
        if lastname.lower() in content:
            found.append(f"last name: {lastname}")
       
        if found:
            return f"{Fore.GREEN}✓ {uri} : SUCCESS {', '.join(found)} FOUND{Style.RESET_ALL}"
        else:
            return f"{Fore.YELLOW}⚠ {uri} : email, email username, first name, or last name NOT FOUND{Style.RESET_ALL}"
    except Timeout:
        return f"{Fore.YELLOW}⚠ {uri} : TIMEOUT after {timeout_seconds} seconds{Style.RESET_ALL}"
    except ConnectionError as e:
        if isinstance(e.args[0], NameResolutionError):
            return f"{Fore.RED}✗ {uri} : DNS resolution failed{Style.RESET_ALL}"
        else:
            return f"{Fore.RED}✗ {uri} : connection error{Style.RESET_ALL}"
    except RequestException as e:
        return f"{Fore.RED}✗ {uri} : request failed - {str(e)}{Style.RESET_ALL}"

def confirm_URI(threads, timeout_seconds, data, file=None):
    try:
        # domain-search data
        if 'data' in data and 'emails' in data['data']:
            emails = data['data']['emails']
            for email_data in emails:
                email = email_data.get('value')
                if not email or '@' not in email:
                    print_to_both(f"{Fore.RED}Invalid or missing email address{Style.RESET_ALL}", file)
                    continue
                emailname = email.split('@')[0]
                firstname = email_data.get('first_name', "")
                lastname = email_data.get('last_name', "")
                sources = email_data.get('sources', [])
                uris = [source['uri'] for source in sources if 'uri' in source]
                
                if not uris:
                    print_to_both(f"{Fore.RED}No URIs found for {email}{Style.RESET_ALL}", file)
                    continue
                
                print_to_both(f"\n[{Fore.CYAN}*{Style.RESET_ALL}] Checking URIs for {Fore.CYAN}{email}{Style.RESET_ALL}:", file)
                check_uris(threads, timeout_seconds, uris, email, emailname, firstname, lastname, file)
        else:
            # email-finder or email-verifier data
            result = data.get('data', {})
            if not result:
                raise ValueError("No 'data' field found in the input")
            email = result.get('email')
            if not email or '@' not in email:
                raise ValueError("Invalid or missing email address")
            emailname = email.split('@')[0]
            firstname = result.get('first_name', "")
            lastname = result.get('last_name', "")
            uris = [source['uri'] for source in result.get('sources', [])]
            
            if not uris:
                print_to_both(f"{Fore.RED}No URIs found{Style.RESET_ALL}", file)
                return
            
            check_uris(threads, timeout_seconds, uris, email, emailname, firstname, lastname, file)
    
    except KeyError as e:
        print_to_both(f"{Fore.RED}Error: Missing required field - {str(e)}{Style.RESET_ALL}", file)
    except ValueError as e:
        print_to_both(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}", file)
    except Exception as e:
        print_to_both(f"{Fore.RED}An unexpected error occurred: {str(e)}{Style.RESET_ALL}", file)

def check_uris(threads, timeout_seconds, uris, email, emailname, firstname, lastname, file):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_uri = {executor.submit(check_uri, uri, headers, timeout_seconds, email, emailname, firstname, lastname): uri for uri in uris}
        for future in concurrent.futures.as_completed(future_to_uri):
            result = future.result()
            print_to_both(result, file)