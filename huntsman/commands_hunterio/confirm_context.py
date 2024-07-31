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

def highlight_contained(container, contained):
    if contained.lower() in container.lower():
        start = container.lower().index(contained.lower())
        end = start + len(contained)
        return (
            container[:start] +
            Fore.CYAN + container[start:end] + Style.RESET_ALL +
            container[end:]
        )
    else:
        return container

def extract_context(content, target, context_size=150):
    index = content.lower().find(target.lower())
    if index != -1:
        start = max(0, index - context_size)
        end = min(len(content), index + len(target) + context_size)
        context = content[start:end]
        highlighted_context = highlight_contained(context, target)
        return f"...{highlighted_context}..."
    return None

def check_uri(uri, headers, timeout_seconds, email, emailname, firstname=None, lastname=None):
    try:
        response = requests.get(uri, headers=headers, timeout=timeout_seconds)
        response.raise_for_status()
        content = response.text
        found = []

        if email.lower() in content.lower():
            context = extract_context(content, email)
            found.append(f"email: {Fore.MAGENTA}{email}{Style.RESET_ALL}\nContext: {context}")

        if emailname.lower() in content.lower():
            context = extract_context(content, emailname)
            found.append(f"email username: {Fore.MAGENTA}{emailname}{Style.RESET_ALL}\nContext: {context}")

        if firstname and firstname.lower() in content.lower():
            context = extract_context(content, firstname)
            found.append(f"first name: {Fore.MAGENTA}{firstname}{Style.RESET_ALL}\nContext: {context}")

        if lastname and lastname.lower() in content.lower():
            context = extract_context(content, lastname)
            found.append(f"last name: {Fore.MAGENTA}{lastname}{Style.RESET_ALL}\nContext: {context}")

        if found:
            return f"{Fore.GREEN}✓ {uri} : SUCCESS{Style.RESET_ALL}\n" + "\n".join(found)
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

def confirm_context(threads, timeout_seconds, data, file=None):
    try:
        if 'data' in data and 'emails' in data['data']:
            # domain-search
            emails = data['data']['emails']
            for email_data in emails:
                process_email_data(threads, timeout_seconds, email_data, file)
        elif 'data' in data and 'email' in data['data']:
            # email-finder or email-verifier data
            process_email_data(threads, timeout_seconds, data['data'], file)
        else:
            raise ValueError("Unexpected data structure")
    
    except KeyError as e:
        print_to_both(f"{Fore.RED}Error: Missing required field - {str(e)}{Style.RESET_ALL}", file)
    except ValueError as e:
        print_to_both(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}", file)
    except Exception as e:
        print_to_both(f"{Fore.RED}An unexpected error occurred: {str(e)}{Style.RESET_ALL}", file)

def process_email_data(threads, timeout_seconds, email_data, file):
    email = email_data.get('value') or email_data.get('email')
    if not email or '@' not in email:
        print_to_both(f"{Fore.RED}Invalid or missing email address{Style.RESET_ALL}", file)
        return
    emailname = email.split('@')[0]
    firstname = email_data.get('first_name')
    lastname = email_data.get('last_name')
    sources = email_data.get('sources', [])
    uris = [source['uri'] for source in sources if 'uri' in source]
    
    if not uris:
        print_to_both(f"{Fore.RED}No URIs found for {email}{Style.RESET_ALL}", file)
        return
    
    print_to_both(f"\n[{Fore.CYAN}*{Style.RESET_ALL}] Checking URIs for {Fore.CYAN}{email}{Style.RESET_ALL}:", file)
    check_uris(threads, timeout_seconds, uris, email, emailname, firstname, lastname, file)

def check_uris(threads, timeout_seconds, uris, email, emailname, firstname, lastname, file):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_uri = {executor.submit(check_uri, uri, headers, timeout_seconds, email, emailname, firstname, lastname): uri for uri in uris}
        for future in concurrent.futures.as_completed(future_to_uri):
            result = future.result()
            print_to_both(result, file)