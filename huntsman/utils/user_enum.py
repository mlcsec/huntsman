import requests
from typing import Dict, List
from colorama import init, Fore, Style
from huntsman.utils.helpers import print_section_header

def invoke_userenumerationasoutsider(usernames: List[str], file=None):
    print_section_header("Entra ID User Enumeration", file)
    for username in usernames:
        exists = None
        try:
            url = "https://login.microsoftonline.com/common/GetCredentialType"
            data = {
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
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                exists = result.get('IfExistsResult', 0) == 0
        except:
            pass
        
        if exists:
            message = f"{Fore.GREEN}[+] {username:<16}{Style.RESET_ALL}"
        else:
            message = f"{Fore.RED}[-] {username:<16}{Style.RESET_ALL}"
        
        print(message)
        if file:
            print(message, file=file)