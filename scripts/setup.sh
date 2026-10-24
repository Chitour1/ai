#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update
sudo apt-get install -y ffmpeg
python -m pip install --upgrade pip
python -m pip install "gradio>=4,<6" "git+https://github.com/MahmoudAshraf97/ctc-forced-aligner.git"
python - <<'PY'
from transformers import AutoTokenizer, AutoModelForCTC
model = "jonatasgrosman/wav2vec2-large-xlsr-53-arabic"
AutoTokenizer.from_pretrained(model, word_delimiter_token=None)
AutoModelForCTC.from_pretrained(model)
print("Arabic model cached")
PY
