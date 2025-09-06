# Persian Text Humanizer using Hazm

# Humanize Persian text using hazm (advanced version)
from hazm import Normalizer, word_tokenize, sent_tokenize, Lemmatizer, Stemmer, stopwords_list
import re

class PersianHazmHumanizer:
    def __init__(self):
        self.normalizer = Normalizer()
        self.lemmatizer = Lemmatizer()
        self.stemmer = Stemmer()
        self.stopwords = set(stopwords_list())

    def humanize_text(self, text, remove_stopwords=True, use_lemmatize=True, use_stem=True, **kwargs):
        # Normalize
        text = self.normalizer.normalize(text)
        # Remove extra spaces and non-persian chars
        text = re.sub(r'[\u200c\u200f]', '', text)
        sentences = sent_tokenize(text)
        transformed = []
        for sent in sentences:
            words = word_tokenize(sent)
            # Remove stopwords
            if remove_stopwords:
                words = [w for w in words if w not in self.stopwords and len(w) > 1]
            # Lemmatize
            if use_lemmatize:
                words = [self.lemmatizer.lemmatize(w) for w in words]
            # Stem
            if use_stem:
                words = [self.stemmer.stem(w) for w in words]
            # Capitalize first word
            if words:
                words[0] = words[0].capitalize()
            transformed.append(' '.join(words))
        # Join sentences with proper punctuation
        return '\n'.join(transformed)
