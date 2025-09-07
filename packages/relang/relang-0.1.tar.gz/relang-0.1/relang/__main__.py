from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from flask import Flask, render_template, request, Response

from .model import Model
from .lang import LANGUAGE_CODES

parser = ArgumentParser(prog="relang", formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "sp_path", help="path to the tokenization model in sentencepiece format"
)
parser.add_argument("tr_path", help="path to the NLLB model in CTranslate2 format")
parser.add_argument(
    "--batchsize",
    metavar="B",
    type=int,
    default=2,
    help="number of batches to process in parallel",
)
parser.add_argument(
    "--threads",
    metavar="T",
    type=int,
    default=12,
    help="number of threads to use per batch",
)
parser.add_argument(
    "--beamsize",
    metavar="B",
    type=int,
    default=4,
    help="number of hypotheses to consider at all times",
)
parser.add_argument(
    "--host", metavar="H", type=str, default="0.0.0.0", help="the interface to bind to"
)
parser.add_argument(
    "--port", metavar="P", type=int, default=5000, help="the port to bind to"
)
parser.add_argument(
    "--gpu",
    dest="device",
    default="cpu",
    action="store_const",
    const="cuda",
    help="use the GPU, requires CUDA",
)
args = parser.parse_args()

model = Model(
    args.sp_path,
    args.tr_path,
    device=args.device,
    intra_threads=args.threads,
)

app = Flask("relang")


@app.route("/")
def route_index():
    return render_template("index.html", languages=LANGUAGE_CODES)


@app.route("/translate", methods=["POST"])
def route_translate():
    post = request.get_json()
    event_stream = model.translate_text(
        src_text=post["src_text"],
        src_lang=post["src_lang"],
        tgt_lang=post["tgt_lang"],
        max_batch_size=args.batchsize,
        beam_size=args.beamsize,
    )
    return Response(event_stream, mimetype="text/event-stream")


app.run(host=args.host, port=args.port)
