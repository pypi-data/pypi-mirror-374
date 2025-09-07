# Relang

Self hosted, simplest possible web interface for text translations using Meta's
NLLB200 model.

## Why did you make this

Degoogling, fun little project, getting some "AI" experience.

## But didn't tools like this already exist?

Sure! Now there is one more.

The best project I could find is
[nllb-serve](https://pypi.org/project/nllb-serve/), which uses
[pytorch](https://pypi.org/project/torch/). This one uses
[ctranslate2](https://pypi.org/project/ctranslate2/) (copy-pasted from the
opennmt forum) and has less of an interface (my own doing).

## What does it look like

![screenshot](screenshot.png)

## Regardless. How do I set this up

Installation is simply `pip install relang` in a virtual environment, or use a
tool like [pipx](https://pypi.org/project/pipx/) or
[uvx](https://pypi.org/project/uvx/). The model needs to be downloaded
separately using the links from this [forum
post](https://forum.opennmt.net/t/nllb-200-with-ctranslate2/5090). You'll need
the SentencePiece model and any of the three NLLB models -- larger is better.

Running it as `relang` or `python -m relang` with the relevant path arguments
pointing at the downloaded (unzipped) models starts the web server at default
port 5000. Adding `--gpu` should move computations to the GPU, but I didn't
test that for reasons of not having one. Use `--host ::` for IPv6.

Obviously don't expose this to the internet.

## Any known issues

The biggest one is that translations cannot be aborted once started. Also
server side errors are not communicated. I may try to fix this in future.

The other thing is that sentences as split simply at punctuation marks with
some very minimal heuristics, regardless of language. There are external
libraries for this task but they seem to be mainly focused on English, and in
the spirit of NLLB I rather degrate all languages the same.

Also NLLB doesn't appear to like certain unicode symbols so these are replaced
by equivalent, better liked characters. But that table is likely incomplete.

## What is NLLB200 anyway

The [No Language Left
Behind](https://ai.meta.com/research/no-language-left-behind/) model was
developed by Meta (nee Facebook) with the aim to provide high quality
translations between 200+ languages. Its code and weights were released in 2022
for non-commercial use.

## Is that the only model of its kind?

The AI arms race being what it is, no. In particular
[MATLAD400](https://github.com/google-research/google-research/tree/master/madlad_400)
by Google seems interesting, if only for its permissive Creative Commons
licence, but I haven't gotten round to trying it yet.

Sadly all models seem to work at the sentence level, which seems suboptimal for
quality and is a pain because splitting sentences is hard. Hopefully one of
these days somebody will develop a model that can translate entire paragraphs
in context.

## Acknowledgements

All translation code as well as model files referenced above are from forum
posts by [Yasmin Moslem](https://github.com/ymoslem), who, unlike me, actually
seems to understand how any of this works.
