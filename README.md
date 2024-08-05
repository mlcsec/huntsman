# huntsman

<p align="center">
  <img src="./.github/huntsman.png" />
</p>

Email enumerator, username generator, and context validator providing detailed coverage of the hunter.io, snov.io, and skrapp.io APIs with several enhancements to streamline processing for engagements.

## Features

- [x] Confirms email and first/last name context within source URIs to create realistic pretexts for phishing or SE 
- [x] Identifies social media accounts associated with target email addresses
- [x] Generates usernames based on common first and last name combinations for targetting corporate logins, brute forcing web apps, password reset user enum, etc. 
- [x] Automatically validates emails with Entra ID (Azure AD) using python implementation of AADInternal's Invoke-UserEnumerationAsOutsider
- [x] Confirms validity of source URIs and the presence of emails or user related information
- [x] Detailed hunter.io and snov.io API coverage
  - [x] Limited skrapp.io coverage
- [x] Asynchronously resolves source URIs


## Demo

[huntsman.webm](https://github.com/user-attachments/assets/c8293d01-4e4f-4c57-8c59-72c972bc3a70)


## Installation

Install from PyPI with pip:
```
pip install huntsman
```
OR git clone and install:
```
git clone https://github.com/mlcsec/huntsman.git
cd huntsman
pip install .
huntsman -h
```
You can upgrade with:
```
pip install --upgrade huntsman
```

## Setup

Run `huntsman setup` and enter the required API key(s) when prompted or manually update `.huntsman.conf`

## Usage

```
usage: huntsman.py [-h]  ...

positional arguments:

    setup     API key(s) setup for huntsman
    hunterio  hunter.io commands
    snovio    snov.io commands
    skrappio  skrapp.io commands

options:
  -h, --help  show this help message and exit
```
To view available commands for each of the services:
```
huntsman hunterio -h
```
To view available options for each subcommand:
```
huntsman hunterio domain-search -h
```

## Options

The optional arguments include all flags and parameters available from the API documentation. The 'company' option has been removed from hunter.io commands as the documentation states that specifying the domain returns better results.

> _"Note that you'll get better results by supplying the domain name as we won't have to find it. If you send a request with both the domain and the company name, we'll use the domain name. It doesn't need to be in lowercase."_

The following options are the main features of huntsman for gathering actionable data for engagements.

### --uri-confirm

Confirm positive HTTP responses for hunter.io source URIs and the presence of emails and user information. Does NOT provide any context (see `--uri-context`):

![](https://github.com/mlcsec/huntsman/blob/main/.github/confirm-email-uris.png)

### --uri-context

Confirm positive HTTP responses, presence of email address, first name, last name, and the surrounding context for the user information identified in hunter.io source URIs. This aids in confirming the validity of the account information as I have encountered false positives in the past. 

The primary purpose of this functionality is identifying the context the email or user information was used in to create realistic pretexts for phishing or SE. The example below demonstrates this as the `lisa@stripe.com` email should be used for emailing CVs. This provides us with a 'pre-configured' pretext for the user as opposed to blindly creating one based on a list of emails for the target company. 

![](https://github.com/mlcsec/huntsman/blob/main/.github/context-cv-email-pretext.png)

Another example identified a personal GitHub account associated with the email through source URI context validation:

![](https://github.com/mlcsec/huntsman/blob/main/.github/context-github-found.png)

Personal user accounts and usernames for external services such as betalist, hackernews, and nomadlist were discovered in this example:

![](https://github.com/mlcsec/huntsman/blob/main/.github/uri-context-edwin.png)

### --socials

Identify social media accounts associated with supplied user emails (LinkedIn/Twitter primarily):

![](https://github.com/mlcsec/huntsman/blob/main/.github/socials.png)

### --usergen

Generate common usernames from gathered first and last name combinations using the formats specified below. Automates the generation of username lists for targeting corporate logins, brute forcing company web apps, password reset user enumeration, etc. 

```python
{first}.{last}
{first}_{last}
{first}{last}
{first}{last_initial}
{first}_{last_initial}
{first}.{last_initial}
{first_initial}.{last}
{first_initial}_{last}
{first_initial}{last}
{first_three}{last_three}
{last}.{first}
{last}_{first}
{last}{first}
{last}{first_initial}
{last}_{first_initial}
{last}.{first_initial}
{last_initial}.{first}
{last_initial}_{first}
{last_initial}{first}
{last_three}{first_three}
```

![](https://github.com/mlcsec/huntsman/blob/main/.github/username-gen.png)


### --entraid

Automatically confirm gathered emails against Entra ID (Azure AD) using AADInternal's user enumeration as outsider port from [Graphpython](https://github.com/mlcsec/Graphpython/wiki/Demos#invoke-userenumerationasoutsider):

![](https://github.com/mlcsec/huntsman/blob/main/.github/entraid.png)

## Commands

### hunter.io
```
huntsman hunterio [COMMAND] [OPTIONS] [-h] 

    domain-search       Perform a domain name search
    email-finder        Find email addresses for domain
    email-verifier      Verify email addresses
    email-count         Get email count for a domain
    account-info        Get information about your hunter.io account
```
### snov.io
```
huntsman snovio [COMMAND] [OPTIONS] [-h] 

    domain-search       Perform a domain name search
    get-profile         Get profile information for email addresses
    email-verifier      Verify email addresses
    email-count         Get email count for a domain
    get-balance         Get your snov.io credit balance
```
### skrapp.io
```
huntsman skrappio [COMMAND] [OPTIONS] [-h] 

    company-search      Dump and explore the employment details of company members
    account-data        Get information about your skrapp.io account
```

## References

- [hunter.io API documentation](https://hunter.io/api-documentation/v2)
- [snov.io API documentation](https://snov.io/api)
- [skrapp.io API documentation](https://skrapp.io/api)
