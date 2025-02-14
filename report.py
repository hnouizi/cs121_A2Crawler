import re
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
STOP = set(stopwords.words("english"))

class Report:
    def __init__(self):
        """Initialize variables."""
        self.urls = set()
        self.longest_page = {"url": '', "count": 0}
        self.ics_subdomains = dict()
        self.frequent_words = dict()

    def get_ics_subdomains(self):
        """Returns a dictionary of ICS subdomains and how many times each has appeared."""
        return self.ics_subdomains

    def add_ics_subdomain(self, subdomain):
        """Add an ICS subdomain to the dictionary."""
        # check if the subdomain is new
        if (subdomain not in self.ics_subdomains.keys()):
            self.ics_subdomains[subdomain] = 0

        # increment subdomain count
        self.ics_subdomains[subdomain] += 1

    def get_urls(self):
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
            word = word.lower().strip()
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

    def print_report(self):
        """Prints the number of unique pages, the page with the largest number of words, the 50 most common words and their frequencies, and the number of subdomains in the ics.uci.edu domain to the console.."""
        print("\n== REPORT ==")
        print(f"number of unique pages: {len(self.urls)}")
        print(f"longest page: {self.longest_page["url"]}")
        print(f"top 50 words:")
        top_50_words = self.get_most_common()

        for i in range(len(top_50_words)):
            word = list(top_50_words.keys())[i]
            print(f"  {i+1}: {word}, {top_50_words[word]}")

        print(f"number of ics.uci.edu subdomains: {len(self.ics_subdomains)}")

        for i in range(len(self.ics_subdomains)):
            subdomain = list(self.ics_subdomains.keys())[i]
            print(f"  {i+1}: {subdomain}, {self.ics_subdomains[subdomain]}")

    def write_to_file(self):
        """Writes the number of unique pages, the page with the largest number of words, the 50 most common words and their frequencies, and the number of subdomains in the ics.uci.edu domain to a file."""
        with open('report.txt', 'w') as report_file:
            print(f"1. number of unique pages: {len(self.urls)}", file=report_file)
            print(f"2. longest page: {self.longest_page["url"]}", file=report_file)
            print(f"3. top 50 words:", file=report_file)
            top_50_words = self.get_most_common()

            for i in range(len(top_50_words)):
                word = list(top_50_words.keys())[i]
                print(f"  {i+1}: {word}, {top_50_words[word]}", file=report_file)

            print(f"4. number of ics.uci.edu subdomains: {len(self.ics_subdomains)}", file=report_file)

            sorted_subdomains = {k: v for k, v in sorted(self.ics_subdomains.items(), key=lambda item: item[1], reverse = True)}
            for i in range(len(sorted_subdomains)):
                subdomain = list(sorted_subdomains.keys())[i]
                print(f"  {i+1}: {subdomain}, {sorted_subdomains[subdomain]}", file=report_file)
            