import os 
import requests
import json
from colorama import Fore, Style
from typing import Dict, List
from huntsman.utils.helpers import print_info, print_section_header

def get_access_token(client_id: str, client_secret: str) -> str:
    params = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    res = requests.post('https://api.snov.io/v1/oauth/access_token', data=params)
    resText = res.text.encode('ascii', 'ignore')
    return json.loads(resText)['access_token']

def fetch_profile_by_email(access_token: str, email: str) -> Dict:
    url = "https://api.snov.io/v1/get-profile-by-email"
    params = {
        "access_token": access_token,
        "email": email
    }
    
    response = requests.post(url, data=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

def print_to_both(message, file=None):
    print(message)
    if file:
        file.write(message + '\n')

def print_socials(email, profile: Dict, file):
    if not profile or all(value == 'N/A' for value in profile.values()):
        print_to_both("Error: Empty or invalid profile data.", file)
        return

    name = profile.get('name', 'N/A')
    if name != 'N/A':
        print_section_header(f"{name} Socials", file)
    else:
        print_to_both(f"\n{Fore.RED}{profile['result']}: {email}", file)
        return

    if profile.get('social'):
        for social in profile['social']:
            print_to_both(f"{Fore.RESET}{social['link']}{Style.RESET_ALL}", file)

def print_profile_info(email, profile: Dict, file=None):
    if not profile or all(value == 'N/A' for value in profile.values()):
        print_to_both("Error: Empty or invalid profile data.", file)
        return

    name = profile.get('name', 'N/A')
    if name != 'N/A':
        print_section_header(f"Get Profile {name}", file)
    else:
        print_to_both(f"\n{Fore.RED}{profile['result']}: {email}", file)
        return
   
    fields = [
        ('Name', 'name'),
        ('First Name', 'firstName'),
        ('Last Name', 'lastName'),
        ('Industry', 'industry'),
        ('Country', 'country'),
        ('Locality', 'locality'),
        ('Source', 'source'),
        ('Last Update Date', 'lastUpdateDate')
    ]
    for label, key in fields:
        value = profile.get(key, 'N/A')
        if value != 'N/A':
            print_to_both(f"{Fore.GREEN}{label}:{Style.RESET_ALL} {value}", file)
    if profile.get('social'):
        print_to_both(f"{Fore.YELLOW}Social Profiles:{Style.RESET_ALL}", file)
        for social in profile['social']:
            print_to_both(f"  - {Fore.CYAN}{social['type']}:{Style.RESET_ALL} {Fore.RESET}{social['link']}{Style.RESET_ALL}", file)
    if profile.get('currentJobs'):
        print_to_both(f"{Fore.YELLOW}Current Jobs:{Style.RESET_ALL}", file)
        for job in profile['currentJobs']:
            if not any(job.values()):
                continue  # skip empty job entries
            print_to_both(f"  {Fore.CYAN}Company:{Style.RESET_ALL} {job.get('companyName', 'N/A')}", file)
            print_to_both(f"  {Fore.CYAN}Position:{Style.RESET_ALL} {job.get('position', 'N/A')}", file)
            print_to_both(f"  {Fore.GREEN}Start Date:{Style.RESET_ALL} {job.get('startDate', 'N/A')}", file)
            print_to_both(f"  {Fore.RED}End Date:{Style.RESET_ALL} {job.get('endDate', 'N/A')}", file)
            print_to_both(f"  {Fore.CYAN}Company Details:{Style.RESET_ALL}", file)
           
            company_details = [
                ('Social Link', 'socialLink', Fore.RESET),
                ('Website', 'site', Fore.RESET),
                ('Founded', 'founded', Fore.RESET),
                ('Size', 'size', Fore.RESET),
                ('Country', 'country', Fore.RESET),
                ('State', 'state', Fore.RESET),
                ('City', 'city', Fore.RESET),
                ('Street', 'street', Fore.RESET),
                ('Street2', 'street2', Fore.RESET),
                ('Postal', 'postal', Fore.RESET),
                ('Locality', 'locality', Fore.RESET)
            ]
            for label, key, *color in company_details:
                value = job.get(key, 'N/A')
                if value != 'N/A':
                    color_code = color[0] if color else Fore.CYAN
                    print_to_both(f"    {Fore.CYAN}{label}:{Style.RESET_ALL} {color_code}{value}{Style.RESET_ALL}", file)
           
            print_to_both(f"{Fore.YELLOW}  {'-' * 30}{Style.RESET_ALL}", file)

def get_profile(args, client_id: str, client_secret: str):
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
        
        output_file = None
        if args.output:
            output_file = open(args.output, 'w')

        # socials
        if args.socials:
            for email in emails:
                try:
                    profile = fetch_profile_by_email(access_token, email)
                    print_socials(email, profile, output_file)
                except Exception as e:
                    print_to_both(f"{Fore.RED}Error processing email {email}: {str(e)}{Style.RESET_ALL}", output_file)
            return

        for email in emails:
            try:
                profile = fetch_profile_by_email(access_token, email)
                print_profile_info(email, profile, output_file)
            except Exception as e:
                print_to_both(f"{Fore.RED}Error processing email {email}: {str(e)}{Style.RESET_ALL}", output_file)

        # usergen
        if args.usergen:
            print_section_header("Username Generation", output_file)
            from huntsman.utils.user_gen import generate_usernames
            for email in emails:
                profile = fetch_profile_by_email(access_token, email)
                if profile.get('firstName') and profile.get('lastName'):
                    first_names = [profile['firstName']]
                    last_names = [profile['lastName']]
                    generated_usernames = generate_usernames(first_names, last_names, output_file)
                    for username in generated_usernames:
                        print_to_both(username, output_file)

        # entraid
        if args.entraid:
            from huntsman.utils.user_enum import invoke_userenumerationasoutsider
            invoke_userenumerationasoutsider(emails, output_file)

        if output_file:
            output_file.close()
            print_to_both(f"\n{Fore.GREEN}Results have been saved to {args.output}{Style.RESET_ALL}", None)
    
    except Exception as e:
        print_to_both(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}", output_file)