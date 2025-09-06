# Persian Text Humanizer using Combination of Hazm and Stanza

# Humanize Persian text using combination of hazm, stanza, and transformer paraphrase (if available)
from .fa_hazm import PersianHazmHumanizer
from .fa_stanza import PersianStanzaHumanizer

class PersianComboHumanizer:
    def __init__(self, use_paraphrase=True):
        self.hazm = PersianHazmHumanizer()
        self.stanza = PersianStanzaHumanizer()
        self.use_paraphrase = use_paraphrase
        self.paraphraser = None
        if use_paraphrase:
            try:
                from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
                self.tokenizer = AutoTokenizer.from_pretrained("HooshvareLab/mt5-small-paraphrase-fa")
                self.model = AutoModelForSeq2SeqLM.from_pretrained("HooshvareLab/mt5-small-paraphrase-fa")
                self.paraphraser = True
            except Exception:
                self.paraphraser = None

    def paraphrase(self, text):
        if not self.paraphraser:
            return text
        input_ids = self.tokenizer([text], return_tensors="pt", padding=True)["input_ids"]
        outputs = self.model.generate(input_ids, max_length=256, num_beams=5, num_return_sequences=1)
        paraphrased = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return paraphrased

    def humanize_text(self, text, use_hazm=True, use_stanza=True, use_paraphrase=True, **kwargs):
        result = text
        if use_hazm:
            result = self.hazm.humanize_text(result)
        if use_stanza:
            result = self.stanza.humanize_text(result)
        if use_paraphrase and self.paraphraser:
            result = self.paraphrase(result)
        return result
