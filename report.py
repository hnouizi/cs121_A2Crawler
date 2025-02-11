class Report:
    def __init__(self):
        """Initialize variables."""
        self.urls = set()
        self.longest_page = {"url": '', "count": 0}
        self.ics_subdomains = dict()

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