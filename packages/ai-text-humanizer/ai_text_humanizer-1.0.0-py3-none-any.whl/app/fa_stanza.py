# Persian Text Humanizer using Stanza

# Humanize Persian text using stanza (advanced version)
import stanza

class PersianStanzaHumanizer:
    def __init__(self):
        stanza.download('fa', processors='tokenize,pos,lemma,pos,depparse', verbose=False)
        self.nlp = stanza.Pipeline('fa', processors='tokenize,pos,lemma,pos,depparse', use_gpu=False, verbose=False)

    def humanize_text(self, text, use_lemma=True, **kwargs):
        doc = self.nlp(text)
        transformed = []
        for sentence in doc.sentences:
            words = []
            for word in sentence.words:
                if use_lemma:
                    words.append(word.lemma)
                else:
                    words.append(word.text)
            # Capitalize first word
            if words:
                words[0] = words[0].capitalize()
            transformed.append(' '.join(words))
        return '\n'.join(transformed)
