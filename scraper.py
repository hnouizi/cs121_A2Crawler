import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
BLUE_TEXT = "\033[34m"
GREEN_TEXT = "\033[32m"
RED_TEXT = "\033[31m"
RESET_TEXT = "\033[0m"

def scraper(url, resp):
    # print terminal text
    print(f"URL: {BLUE_TEXT}{url}{RESET_TEXT}, status: ", end="")
    if (resp.status != 200):
        print(f"{RED_TEXT}{resp.status}{RESET_TEXT}")
    else:
        print(f"{GREEN_TEXT}{resp.status}{RESET_TEXT}")

    # return an empty list if page couldn't be reached
    if (resp.status != 200):
        return []
        
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

        if (link.get('href') != extracted_link):
            print(f"{RED_TEXT}full url: {link.get('href')}{RESET_TEXT}")
            print(f"{RED_TEXT}defragmented url: {extracted_link}{RESET_TEXT}")
        
        # add the defragmented link to extracted links list
        extracted_links.append(extracted_link)

    return extracted_links


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # check if the domain is valid
        domain1 = ".".join(parsed.hostname.split('.'))
        domain2 = ".".join(parsed.hostname.split('.')[1:])
        
        if (domain1 not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"])) and (domain2 not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"])):
            # print(f"invalid domain detected: {RED_TEXT}{url}{RESET_TEXT}")
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
