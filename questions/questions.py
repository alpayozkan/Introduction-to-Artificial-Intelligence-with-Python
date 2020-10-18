import nltk
import sys
import os
import string
import math
from functools import cmp_to_key

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = dict()
    for fileLocalPath in os.listdir(directory):
        filePath = os.path.join(directory, fileLocalPath)
        with open(filePath, 'r') as f:
            data = f.read()
        files[fileLocalPath] = data
    return files

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    words = [word.lower() for word in nltk.word_tokenize(document)]
    words = [x for x in words if (not x in string.punctuation) and (not x in nltk.corpus.stopwords.words('english'))]
    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idfs = dict()
    for doc in documents:
        for word in documents[doc]:
            if word in idfs:
                continue
            tot = len(documents)
            def wordCount(word):
                count = 0
                for document in documents:
                    if word in documents[document]:
                        count += 1
                return count
            count = wordCount(word)
            idfs[word] = math.log(tot/count)
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    res = []
    for f in files:
        tfidf = 0
        for word in query:
            if not word in files[f]:
                continue
            tfidf += files[f].count(word)*idfs[word]
        res.append((tfidf, f))
    res.sort(reverse=True)
    res = [x[1] for x in res]
    return res[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    def compare(item1, item2):
        if item1[1] < item2[1]:
            return -1
        elif item1[1] > item2[1]:
            return 1
        else:
            if item1[2] < item2[2]:
                return -1
            elif item1[2] > item2[2]:
                return 1
            else:
                return 0 
    res = []
    for sent in sentences:
        Sidf = 0
        count = 0
        for word in query:
            if word in sentences[sent]:
                Sidf += idfs[word]
                count += 1
        qtd = count/len(sentences[sent])
        res.append((sent, Sidf, qtd))
    res = sorted(res, key=cmp_to_key(compare), reverse=True)
    res = [x[0] for x in res]
    return res[:n]

if __name__ == "__main__":
    main()
