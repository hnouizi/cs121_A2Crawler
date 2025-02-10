import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from report import Report
BLUE_TEXT = "\033[34m"
GREEN_TEXT = "\033[32m"
RED_TEXT = "\033[31m"
YELLOW_TEXT = "\033[1;33m"
RESET_TEXT = "\033[0m"
found_urls = set()
    
def get_domain(url):
    parsed_url = urlparse(url)

    # check if hostname exists
    if (parsed_url.hostname is None):
        return ""
        
    hostname_list = parsed_url.hostname.split('.')
    domain_list = hostname_list

    # check if hostname has a subdomain
    if (len(hostname_list) == 4):
        domain_list = hostname_list[1:]

    return '.'.join(domain_list)

def get_subdomain(url):
    parsed_url = urlparse(url)

    # check if hostname exists
    if (parsed_url.hostname is None):
        return ""
    
    hostname_list = parsed_url.hostname.split('.')
    domain_list = hostname_list

    if (len(hostname_list) == 4):
        return hostname_list[0]

    return None
    
    
def scraper(url, resp, report):
    # print terminal text
    print(f"URL: {BLUE_TEXT}{url}{RESET_TEXT}, status: ", end="")
    if (resp.status != 200):
        print(f"{RED_TEXT}{resp.status}{RESET_TEXT}")
    else:
        print(f"{GREEN_TEXT}{resp.status}{RESET_TEXT}")

    # return an empty list if page couldn't be reached
    if (resp.status != 200):
        return []

    # check if url is in ics domain
    if (get_domain(url) == "ics.uci.edu") and (get_subdomain(url) is not None):
        print(f"{YELLOW_TEXT} ICS subdomain found!: {get_subdomain(url)}{RESET_TEXT}")
        report.add_ics_subdomain(get_subdomain(url))
        print(f"{report.ics_subdomains})")
        
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # parse the web page
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    # find all links on the current web page
    extracted_links = []
    for link in soup.find_all('a'): 
        # remove fragment from the link
        extracted_link = urldefrag(link.get('href')).url
        
        # add the defragmented link to extracted links list
        extracted_links.append(extracted_link)

    return extracted_links

def path_contains_dates(parsed_url):
    possible_date_1 = []
    possible_date_2 = []

    if (len(parsed_url.path.split('/')) >= 2):
        possible_date_1 = parsed_url.path.split('/')[-1].split('-')
        possible_date_2 = parsed_url.path.split('/')[-2].split('-')

    if (len(possible_date_1) > 0 and possible_date_1[0] != ''):
         if len(possible_date_1) == 3:
             if possible_date_1[0].isdigit() and possible_date_1[1].isdigit() and possible_date_1[2].isdigit():
                 print(f"{YELLOW_TEXT}date: {possible_date_1}{RESET_TEXT}")
                 return True
    elif (len(possible_date_2) > 0 and possible_date_2[0] != ''):
        if len(possible_date_2) == 3:
             if possible_date_2[0].isdigit() and possible_date_2[1].isdigit() and possible_date_2[2].isdigit():
                 print(f"{YELLOW_TEXT}date: {possible_date_2}{RESET_TEXT}")
                 return True

    return False

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # check if the domain is valid
        if (get_domain(url) not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"])):
            return False

        # check if url has already been found
        if (url.split('?')[0] in found_urls):
            return False

        # check for dates to avoid crawler traps
        if (path_contains_dates(parsed)):
            return False
        
        if (re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())):
                return False

        # add url to found list
        found_urls.add(url.split('?')[0])
        
        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise
