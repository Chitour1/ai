# Arabic speech/text alignment in GitHub Codespaces

This branch adds a self-installing Codespaces environment and an Arabic word-level forced alignment UI.

- Open a Codespace on this branch, and Codespaces automatically runs `scripts/setup.sh`.
- Python dependencies and the model `jonatasgrosman/wav2vec2-large-xlsr-53-arabic` are downloaded automatically.
- The app starts on port 7860 at workspace start. Open the forwarded port to use the UI.
- Upload an audio file and paste its *exact* Arabic transcript.
- Run alignment to get word timestamps, JSON and SRT files.

This uses `ctc-forced-aligner`, **not sherpa-onnx**, because the latter does not directly expose forced alignment in the configuration discussed. The Codespace must be created on this branch; an already-open Codespace for the upstream repository will not see these files.

First setup needs internet access and enough disk/RAM for Torch and model weights. CPU inference may be slow. The model's and code's individual licensing terms govern downstream usage. No successful Codespaces boot or end-to-end alignment run has been verified from this chat.
