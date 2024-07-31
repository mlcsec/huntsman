import os
import requests
import json
from tqdm import tqdm
from typing import Dict, List
from colorama import init, Fore, Style
from huntsman.utils.helpers import print_section_header, print_info
import time

def get_access_token(client_id: str, client_secret: str) -> str:
    url = 'https://api.snov.io/v1/oauth/access_token'
    params = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    try:
        response = requests.post(url, data=params, timeout=10)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get access token: {str(e)}")

def add_emails_for_verification(emails: List[str], access_token: str) -> Dict:
    url = 'https://api.snov.io/v1/add-emails-to-verification'
    params = {
        'access_token': access_token,
        'emails[]': emails
    }
    
    try:
        response = requests.post(url, data=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to add emails for verification: {str(e)}")

def get_email_verifier(emails: List[str], access_token: str) -> Dict:
    url = 'https://api.snov.io/v1/get-emails-verification-status'
    params = {
        'access_token': access_token,
        'emails[]': emails
    }
   
    try:
        response = requests.post(url, data=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get email verification status: {str(e)}")

def print_to_both(message, file=None):
    print(message)
    if file:
        file.write(message + '\n')

def print_email_verifier_results(data: Dict, file=None):
    print_section_header("Email Verification Results", file)
   
    for email, result in data.items():
        if email != 'success':
            print_to_both(f"{Fore.GREEN}Email:{Style.RESET_ALL} {email}", file)
            print_to_both(f"{Fore.MAGENTA}Status:{Style.RESET_ALL} {result['status']['identifier']}", file)
            print_to_both(f"{Fore.YELLOW}Description:{Style.RESET_ALL} {result['status']['description']}", file)
           
            if 'data' in result and result['data']:
                print_to_both(f"{Fore.BLUE}Valid Format:{Style.RESET_ALL} {str(result['data'].get('isValidFormat', 'N/A'))}", file)
                print_to_both(f"{Fore.BLUE}Disposable:{Style.RESET_ALL} {str(result['data'].get('isDisposable', 'N/A'))}", file)
                print_to_both(f"{Fore.BLUE}Webmail:{Style.RESET_ALL} {str(result['data'].get('isWebmail', 'N/A'))}", file)
                print_to_both(f"{Fore.BLUE}Gibberish:{Style.RESET_ALL} {str(result['data'].get('isGibberish', 'N/A'))}", file)
                print_to_both(f"{Fore.CYAN}SMTP Status:{Style.RESET_ALL} {result['data'].get('smtpStatus', 'N/A')}", file)
                print_to_both(f"{Fore.BLUE}Catchall:{Style.RESET_ALL} {str(result['data'].get('isCatchall', 'N/A'))}", file)
                print_to_both(f"{Fore.BLUE}Greylist:{Style.RESET_ALL} {str(result['data'].get('isGreylist', 'N/A'))}", file)
                print_to_both(f"{Fore.BLUE}Banned Error:{Style.RESET_ALL} {str(result['data'].get('isBannedError', 'N/A'))}", file)
                print_to_both(f"{Fore.BLUE}Connection Error:{Style.RESET_ALL} {str(result['data'].get('isConnectionError', 'N/A'))}", file)
           
            print_to_both(f"{Fore.YELLOW}{'-' * 40}{Style.RESET_ALL}", file)

def email_verifier(args, client_id, client_secret):
    output_file = None
    try:
        access_token = get_access_token(client_id, client_secret)
        
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

        # add emails to verification queue
        add_result = add_emails_for_verification(emails, access_token)
        custom_bar = '╢{bar:50}╟'
        for _ in tqdm(range(5), bar_format='{l_bar}'+custom_bar+'{r_bar}', leave=False, colour='yellow'):
            time.sleep(1)
        
        # get verification status
        data = get_email_verifier(emails, access_token)
        
        if args.output:
            output_file = open(args.output, 'w')
       
        print_email_verifier_results(data, output_file)
        
        # entraid
        if args.entraid:
            from huntsman.utils.user_enum import invoke_userenumerationasoutsider
            invoke_userenumerationasoutsider(emails, output_file)    
        
        if output_file:
            output_file.close()
            print_to_both(f"{Fore.GREEN}\nResults have been saved to '{args.output}'{Style.RESET_ALL}", None)
   
    except Exception as e:
        print_to_both(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}", output_file)
    finally:
        if output_file:
            output_file.close()