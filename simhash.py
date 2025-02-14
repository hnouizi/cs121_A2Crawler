import hashlib
import re
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
STOP = set(stopwords.words("english"))
BITS = 64
THRESH = 0.9

def create_64_bit_hash(string:str):
    """Converts a string into a 64 bit binary hash."""
    hex = str(hashlib.sha256(string.encode('utf-8')).hexdigest()[:16]) # credit: Arty on StackOverflow
    HEX_TO_BIN = {
        "0": "0000", 
        "1": "0001",
        "2": "0010",
        "3": "0011",
        "4": "0100",
        "5": "0101",
        "6": "0110",
        "7": "0111",
        "8": "1000",
        "9": "1001",
        "A": "1010",
        "B": "1011",
        "C": "1100",
        "D": "1101",
        "E": "1110",
        "F": "1111"
    }

    binary = ""

    for digit in hex:
        # convert letters to uppercase
        if (not digit.isdigit()):
            digit = digit.upper()
        
        binary += HEX_TO_BIN[digit]

    return binary

def find_tokens(text:str):
    """Splits text into tokens."""
    tokens = list()
    text = re.split("[^a-zA-Z0-9]", text)
    regex = re.compile("[^a-zA-Z0-9]")
    for word in text:
        if word.isascii() == False:
            continue
        if len(word) <=1:
            continue
        if word in STOP:
            continue
        token = regex.sub('', word.lower())
        tokens.append(token)

    return tokens

def update_frequencies(token, frequencies):
    """Increment the count for the given token in the frequencies dictionary."""
    if (token in frequencies.keys()):
        frequencies[token] += 1
    else:
        frequencies[token] = 1

def update_hashes(token, hashes):
    """Create and store the hash for the given token in the hashes dictionary."""
    if (token not in hashes.keys()):
        hashes[token] = create_64_bit_hash(token)

def find_frequencies_and_hashes(tokens:list):
    """Create and populate the frequencies and hashes dictionaries."""
    frequencies = dict()
    hashes = dict()

    for token in tokens:
        update_frequencies(token, frequencies)
        update_hashes(token, hashes)

    return frequencies, hashes

def create_vector(frequencies:dict, hashes:dict):
    """Create a simhash vector using the frequencies and hashes of each token."""
    vector = [0] * BITS
    for (token, hash) in hashes.items():
        for i in range(BITS):
            num = 1
            if hash[i] == "0":
                num = -1

            vector[i] += (num * frequencies[token])

    return vector
 
def simhash(text:str):
    """Compute the simhash of a string of text."""
    tokens = find_tokens(text)
    frequencies, hashes = find_frequencies_and_hashes(tokens)
    vector = create_vector(frequencies, hashes)

    # create the fingerprint
    fingerprint = list()
    for num in vector:
        if num >= 0:
            fingerprint.append(1)
        else:
            fingerprint.append(0)

    return fingerprint  

def compute_similarity(simhash1, simhash2):
    """Calculate the similarity between two simhash fingerprints."""
    similarity = 0
    for i in range(BITS):
        if (simhash1[i] == simhash2[i]):
            similarity += 1

    return similarity / BITS
