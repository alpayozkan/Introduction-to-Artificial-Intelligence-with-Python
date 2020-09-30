import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
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


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pages = list(corpus.keys())
    links = corpus[page]
    transition = dict()

    # if no links => links empty set
    if links==set():
        for p in pages:
            transition[p] = 1/len(pages)
    #at least 1 link exists => apply damping
    else: 
        for p in pages:
            transition[p] = (1/len(pages))*(1-damping_factor)
        for p in links:
            transition[p] += (1/len(links))*damping_factor

    return transition


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    random.seed()
    
    pages = list(corpus.keys())
    count = dict()

    #build count dictionary : each initial count is zero
    for p in pages:
        count[p] = 0
    # choose initial state randomly
    state = random.choice(pages)
    count[state] += 1

    for i in range(0, n-1):
        transition = transition_model(corpus, state, damping_factor)
        varList = list(transition.keys())
        varDist = list(transition.values())
        state = random.choices(varList, varDist)[0]
        count[state] += 1
    
    for s in count:
        count[s] = count[s]/n 

    return count

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    pages = list(corpus.keys())
    count = dict()

    N = len(pages)
    #build count dictionary : each initial count is zero
    for p in pages:
        count[p] = 1/N

    flag = True
    while flag:
        flag = False
        for p in pages:
            tmp = (1-damping_factor)/N
            for i in pages:
                links = corpus[i]
                # no links: assume link to everyone including itself
                if links==set():
                    tmp += damping_factor*(count[i]/N)
                else: 
                    if p in links:
                        tmp += damping_factor*(count[i]/len(links))
            # if significant change : update and continue updating the system
            if abs(tmp-count[p])>0.001:
                count[p] = tmp
                flag = True
    return count

if __name__ == "__main__":
    main()
