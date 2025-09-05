import numpy as np
import pandas as pd
import refseq

# taken from https://www.geeksforgeeks.org/trie-insert-and-search/ with my adaptation
class TrieNode:
    # Trie node class
    def __init__(self, L):
        self.children = [None] * L
        # isEndOfWord is True if node represent the end of the word
        self.isEndOfWord = False
        self.leafID = -1


class Trie:
    # Trie data structure class
    def __init__(self, vocab):
        self.vocab = vocab
        self.vocabSize = len(self.vocab)
        self.root = self.getNode()
        self.firstChar = min(self.vocab)
        self.nLeaves = 0

    def getNode(self):
        # Returns new trie node (initialized to NULLs)
        return TrieNode(self.vocabSize)

    def _charToIndex(self, ch):
        # private helper function
        # Converts key current character into index
        # use only 'a' through 'z' and lower case
        return int(ch - self.firstChar)

    def insert(self, key):

        # If not present, inserts key into trie
        # If the key is prefix of trie node,
        # just marks leaf node
        pCrawl = self.root
        length = len(key)
        for level in range(length):
            index = self._charToIndex(key[level])

            # if current character is not present
            if not pCrawl.children[index]:
                pCrawl.children[index] = self.getNode()
            pCrawl = pCrawl.children[index]

        # mark last node as leaf
        pCrawl.isEndOfWord = True
        self.nLeaves += 1
        pCrawl.leafID = self.nLeaves
        return pCrawl.leafID

    def search(self, key):

        # Search key in the trie
        # Returns true if key presents
        # in trie, else false
        pCrawl = self.root
        length = len(key)
        for level in range(length):
            index = self._charToIndex(key[level])
            if not pCrawl.children[index]:
                return -999
            pCrawl = pCrawl.children[index]

        # if arrive to the end without early break
        return pCrawl.leafID


def build_trie(X, vocab=[-1, 0, 1]):
    t = Trie(vocab)
    for i, row in enumerate(X):
        # new row found, insert it to the trie
        if not t.search(row):
            t.insert(row)
    return t


def get_unique_rows(X, vocab=[np.nan, 0, 1], weights=None):
    t = Trie(vocab)
    uPatterns = []
    counts = {}
    if weights is None:
        weights = np.ones(X.shape[0], dtype=int)

    for i, row in enumerate(X):
        leafID = t.search(row)
        # new row found, insert it to the trie
        if leafID == -999:
            newID = t.insert(row)
            uPatterns.append(row)
            counts[newID] = weights[i]
        else:
            counts[leafID] += weights[i]
    return np.array(uPatterns), counts


def get_sample_bootstrap(arr, weights):
    m = arr.shape[0]
    idx = np.random.choice(range(m), size=(weights.sum(), 1), replace=True, p=weights / weights.sum())
    out = arr[idx].swapaxes(0, 1)[0]
    return out


def get_sample_bootstrap_weight(weights):
    positions = np.random.choice(np.arange(len(weights)), size=np.sum(weights), replace=True, p=weights / np.sum(weights))
    return np.bincount(positions, minlength=len(weights))
