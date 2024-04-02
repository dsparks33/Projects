import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000
DIRECTORY = "/Users/dsparks/Downloads/pagerank/corpus0"


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    # corpus = crawl(DIRECTORY)
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def normalize_probabilities(probabilities):
    """
    Return a normalized distribution so that the sum totals to exactly 1
    """
    totalProbability = sum(probabilities.values())
    normalizedProbabilities = {page: prob /
                               totalProbability for page, prob in probabilities.items()}
    return normalizedProbabilities


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    """
    probDistribution = dict()

    # If corpus is empty or the page does not exist, then just return an empty dictionary
    if not corpus or page not in corpus:
        return probDistribution

    # If a page is not linked to anything, then give 100% of the weight to an even distribution
    # across all pages
    pageLinks = corpus[page]
    damping_factor = 0 if not pageLinks else damping_factor

    # With probability 1 - damping_factor, add the probability that a random surfer would choose
    # one of all pages in the corpus with equal probability
    aveDistribution = (1/len(corpus)) * (1 - damping_factor)
    for eachPage in corpus:
        probDistribution[eachPage] = aveDistribution

    # With probability damping_factor, add the probability that a random surfer would choose
    # a link from the page with equal probability. Make sure the page has links.
    if pageLinks:
        aveDistribution = (1/len(pageLinks)) * damping_factor
        for eachPage in pageLinks:
            probDistribution[eachPage] += aveDistribution

    # Normalize the distribution to make sure it sums to 1
    return normalize_probabilities(probDistribution)


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.
    """

    # Initialize a dictionary to save the number of visits to each page
    visits = {page: 0 for page in corpus}
    
    # Determine the starting page, a random selection from the corpus
    randomPage = random.choice(list(corpus.keys()))
    pageLinks = corpus[randomPage]

    for _ in range(0, n):
        pageDistribution = transition_model(corpus, randomPage, damping_factor)
    
        # update the number of visits to each linked page
        for page in pageDistribution:
            visits[page] += pageDistribution[page]

        # Randomly pick the next page based on the current distribution
        keys = list(pageDistribution.keys())
        values = list(pageDistribution.values())
        randomPage = random.choices(keys, weights=values, k=1)[0]
        pageLinks = corpus[randomPage]

    for page in visits:
        visits[page] /= n

    return normalize_probabilities(visits)


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    # Initialize starting rank as an equal distribution across the number of pages in corpus
    rank = {page: 1/len(corpus) for page in corpus}

    # Calculate a new rank for each page based on all of the current rank values
    needAnotherIteration = True
    while needAnotherIteration:
        needAnotherIteration = False
        for page in corpus:
            newRank = 0

            # Get a list of pages that point to this page
            linkedPages = []
            for otherPage in corpus:
                if page in corpus[otherPage]:
                    linkedPages.append(otherPage)
            
            # Sum up the weighted rank of pages that link to this page
            if linkedPages:
                for link in linkedPages:
                    newRank += rank[link]/len(corpus[link])
            else:
                newRank = 1/len(corpus)  # there are no pages linked, assume even probability
            
            # Calculate the new page rank, and iterate until the change in rank gets less than .1%
            newRank = (newRank * damping_factor) + ((1 - damping_factor)/len(corpus))
            if abs(rank[page] - newRank) > .001:
                needAnotherIteration = True
            rank[page] = newRank
    return normalize_probabilities(rank)


if __name__ == "__main__":
    main()
