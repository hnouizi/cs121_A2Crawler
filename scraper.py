import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from report import Report
import simhash as sh

BLUE_TEXT = "\033[34m"
GREEN_TEXT = "\033[32m"
RED_TEXT = "\033[31m"
YELLOW_TEXT = "\033[1;33m"
RESET_TEXT = "\033[0m"

urls_no_query = set()
simhashes = dict()

MAX_WORD_COUNT = 20000
MIN_WORD_COUNT = 100
CHAR_PER_WORD_THRESH = [4, 7]
    
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

    if (len(hostname_list) == 4):
        return hostname_list[0]

    return None 

def path_contains_individual_events(parsed_url):
    path_list = parsed_url.path.split('/')
    path_list = [path for path in path_list if path]

    if "events" in path_list:
        if path_list[-1] == "events":
            return False

        return True

    if "event" in path_list:
        if path_list[-1] == "event":
            return False

        return True

    return False
    
def scraper(url, resp, report:Report):
    # print terminal text
    # print(f"URL: {BLUE_TEXT}{url}{RESET_TEXT}, status: ", end="")
    # if (resp.status >= 300) and (resp.status < 400):
        # print(f"{YELLOW_TEXT}{resp.status}{RESET_TEXT}")
    # elif (resp.status < 200) or (resp.status >= 400):
        # print(f"{RED_TEXT}{resp.status}{RESET_TEXT}")
    # else:
        # print(f"{GREEN_TEXT}{resp.status}{RESET_TEXT}")
        
    # don't scrape if page couldn't be reached
    if (resp.status < 200) or (resp.status >= 300):
        return []

    # don't scrape if there's no content
    if (resp.raw_response.content is None):
        return []

    # add url to set of all unique urls
    # print(f"adding url: {YELLOW_TEXT}{url}{RESET_TEXT}")
    report.add_url(url)

    # don't scrape if the url (without the query string) has already been found
    if (url.split('?')[0] in urls_no_query):
        # print(f"{RED_TEXT}{url.split('?')[0]}{RESET_TEXT}: already crawled")
        return []

    # add url to urls (without query strings)
    urls_no_query.add(url.split('?')[0])

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    
    # get webpage text & ignore non-text elements (credit: bumpkin on StackOverflow)
    for non_text_elements in soup(["script", "style"]):
        non_text_elements.extract()

    text = soup.get_text()
    lines = text.splitlines()

    # create a string of words in the webpage separated by spaces
    text = ' '.join(line for line in lines if line) # remove unecessary whitespace

    # create a list of words in the webpage
    words = re.split("[^a-zA-Z0-9]", text)
    # print(f"num of words: {YELLOW_TEXT}{len(words)}{RESET_TEXT}")
    # print(f"num of chars per word: {YELLOW_TEXT}{len(text) / len(words)}{RESET_TEXT}")

    # don't scrape if the page is too small
    if len(words) < MIN_WORD_COUNT:
        # print(f"{RED_TEXT}too few words: {len(words)}{RESET_TEXT}")
        return []
        
    # don't scrape if the page is too large
    if len(words) >= MAX_WORD_COUNT:
        # print(f"{RED_TEXT}too many words: {len(words)}{RESET_TEXT}")
        return []

    # don't scrape if page has low textual information content
    if (len(text) / len(words) < CHAR_PER_WORD_THRESH[0]) or (len(text) / len(words) > CHAR_PER_WORD_THRESH[1]):
        # print(f"{RED_TEXT}low information content found{RESET_TEXT}")
        return []

    # don't scrape if url contains individual events
    if (path_contains_individual_events(urlparse(url))):
        # print(f"{RED_TEXT}{url}{RESET_TEXT}: contains individual dates/months")
        return []

    # don't scrape if content is similar to other pages using simhash
    cur_hash = sh.simhash(text)
    for (next_url, next_hash) in simhashes.items():
        if (sh.compute_similarity(cur_hash, next_hash) >= sh.THRESH):
            # print(f"{RED_TEXT}similar sites detected: {url} and {next_url}{RESET_TEXT}")
            # print(f"similarity: {sh.compute_similarity(cur_hash, next_hash)}")
            # print(text)
            return []

    # add simhash to dictionary
    simhashes[url] = cur_hash

    #anything that is not alphanumeric is split and frequencies are counted
    report.set_frequency(words)
    # print(f"{YELLOW_TEXT}words: {report.get_most_common()}{RESET_TEXT}")

    # check if url has the most words
    if (report.is_longest_page(len(words))):
        report.set_longest_page(url, len(words))
        # print(f"{YELLOW_TEXT}new longest page found: url: {report.longest_page['url']}, word count: {report.longest_page['count']}{RESET_TEXT}")

    # check if url is in ics domain
    if (get_domain(url) == "ics.uci.edu") and (get_subdomain(url) is not None):
        # print(f"{YELLOW_TEXT}updated ics subdomains: {report.ics_subdomains}){RESET_TEXT}")
        report.add_ics_subdomain(get_subdomain(url))

    # update file
    report.write_to_file()

    # extract links
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
        if (link.get('rel') is not None):
            # don't extract thinks with "nofollow"
            if ("nofollow" in link.get('rel')):
                continue
        # remove fragment from the link
        extracted_link = urldefrag(link.get('href')).url
        
        # add the defragmented link to the extracted links list
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
        if (get_domain(url) not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"])):
            # print(f"{RED_TEXT}{url}{RESET_TEXT}: invalid domain")
            return False
        
        if (re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|war|sql"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())):
                return False

        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise

    except ValueError:
        return False
