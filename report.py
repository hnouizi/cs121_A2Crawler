class Report:
    def __init__(self):
        """Initialize variables."""
        self.urls = set()
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

