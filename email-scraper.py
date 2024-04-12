import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
from collections import deque

"""
Simple script to scrape emails from websites.
you have to install BeautifulSoup, re and requests libraries.

The depth is how many links it will search down the website tree,
you can always just leave it big and stop the program once it finds enough emails to your linking.
The program will still show the emails if interrupted.
"""


def get_domain_name(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc.startswith('www.'):
        return parsed_url.netloc[4:]
    return parsed_url.netloc


def is_internal_link(link, domain):
    link_domain = urlparse(link).netloc
    return link_domain == "" or link_domain == domain or link_domain.startswith(f'www.{domain}')


def find_emails(url, domain, depth=500):
    visited = set()
    emails = set()
    urls = deque([url])
    count = 0

    try:
        while urls and count <= depth:
            current_url = urls.popleft()
            if current_url in visited:
                continue
            visited.add(current_url)

            print(f"[{count}] [{len(emails)} emails found] Processing {current_url}")
            count += 1

            # get request
            try:
                response = requests.get(current_url)
                response.raise_for_status()
            except (requests.RequestException, requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # filter emails
            # email_regex = re.compile(rf"[a-zA-Z0-9._%+-]+@{domain}\.com")
            # email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
            email_regex = re.compile(rf"[a-zA-Z0-9._%+-]+@{re.escape(domain)}")
            found_emails = email_regex.findall(response.text)
            emails.update(found_emails)

            # find and queue internal links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if is_internal_link(href, domain):
                    full_url = urljoin(current_url, href)
                    if full_url not in visited:
                        urls.append(full_url)
    except KeyboardInterrupt:
        pass
    return emails


if __name__ == "__main__":
    # url = ""
    url = input("URL: ")
    domain = get_domain_name(url).replace('www.', '')
    emails = find_emails(url, domain)
    print()
    print("------------------------------------")
    print("Emails: ")
    for email in emails:
        print(email)
