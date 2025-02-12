import re
import nltk
from nltk.corpus import stopwords

#can we import re?
#can we import ntlk?

nltk.download("stopwords")
STOP = set(stopwords.words("english"))
#up here cause i dont want to keep downloading it?

class Report:
    def __init__(self):
        """Initialize variables."""
        self.urls = set()
        self.longest_page = {"url": '', "count": 0}
        self.ics_subdomains = dict()
        self.frequent_words = dict() #should this be sorted already

    def ics_subdomains(self):
        """Returns a dictionary of ICS subdomains and how many times each has appeared."""
        return self.ics_subdomains

    def add_ics_subdomain(self, subdomain):
        """Add an ICS subdomain to the dictionary."""
        # check if the subdomain is new
        if (subdomain not in self.ics_subdomains.keys()):
            self.ics_subdomains[subdomain] = 0

        # increment subdomain count
        self.ics_subdomains[subdomain] += 1

    def urls(self):
        """Returns a dictionary of all URLs scraped."""
        return self.urls
    
    def add_url(self, url):
        """Adds a url to the set of urls."""
        self.urls.add(url)

    def is_longest_page(self, count):
        """Check if the number of words exceed the number of words of the current longest page."""
        if (count > self.longest_page["count"]):
            return True

        return False

    def set_longest_page(self, url, count):
        """Set the url and word count of the longest page."""
        self.longest_page["url"] = url
        self.longest_page["count"] = count

    def set_frequency(self, text):
        """Add words to the frequent words dict."""
        #things to consider: single characters, duplicates, grammar, uppercase, NUMBERS, STOP WORDS other
        #skips stop words, non alpha, single char tokens
        regex = re.compile("[^a-zA-Z0-9]")
        for word in text:
            if word.isascii() == False:
                continue
            if len(word) <=1:
                continue
            if word in STOP:
                continue
            token = regex.sub('', word.lower())
            if(token in self.frequent_words.keys()):
                self.frequent_words[token] += 1
            else:
                self.frequent_words[token] = 1 

    def get_most_common(self) -> dict:
        return {k: v for k, v in sorted(self.frequent_words.items(), key=lambda item: item[1], reverse = True)[:50]}
