from ctranslate2 import Translator
from sentencepiece import SentencePieceProcessor
import re


class Model:
    def __init__(self, sp_path, tr_path, **tr_args):
        self.sp = SentencePieceProcessor()
        self.sp.load(sp_path)
        self.tr = Translator(tr_path, **tr_args)
        self.charmap = str.maketrans({"“": '"', "”": '"', "–": "-"})
        self.intersent = re.compile(
            r"""(
              (?<=[.?!؟])   # positive lookbehind: punctuation
              \s+           # match: whitespace
              (?![a-zа-џ])  # negative lookahead: lower case
            | \s*\n\s*\n\s* # or match: double newline
            )""",
            re.VERBOSE,
        )

    def translate_text(self, src_text, **kwargs):
        parts = self.intersent.split(src_text.translate(self.charmap))
        sentences = parts[::2]
        spaces = *parts[1::2], ""
        for sentence, space in zip(
            self.translate_sentences(sentences, **kwargs), spaces
        ):
            yield sentence + space

    def translate_sentences(self, src_sents, *, src_lang, tgt_lang, **kwargs):
        for translated_sentence in self.tr.translate_iterable(
            [(src_lang, *s, "</s>") for s in self.sp.encode_as_pieces(src_sents)],
            batch_type="tokens",
            target_prefix=[[tgt_lang]] * len(src_sents),
            **kwargs,
        ):
            h = translated_sentence.hypotheses[0]
            yield self.sp.decode(h[1 if h and h[0] == tgt_lang else 0 :])
