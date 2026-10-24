import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import gradio as gr

MODEL = "jonatasgrosman/wav2vec2-large-xlsr-53-arabic"


def to_srt_timestamp(seconds):
    ms = max(0, round(float(seconds) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def align(audio, transcript):
    if not audio or not transcript or not transcript.strip():
        raise gr.Error("أضف الملف الصوتي والنص العربي أولاً.")
    job = Path(tempfile.mkdtemp(prefix="arabic-alignment-"))
    source = Path(audio)
    audio_path = job / "audio.wav"
    text_path = job / "text.txt"
    shutil.copyfile(source, job / ("input" + source.suffix))
    subprocess.run(
        ["ffmpeg", "-nostdin", "-y", "-i", str(job / ("input" + source.suffix)),
         "-ac", "1", "-ar", "16000", str(audio_path)],
        check=True, capture_output=True, text=True,
    )
    text_path.write_text(transcript.strip(), encoding="utf-8")
    cmd = [
        "ctc-forced-aligner",
        "--audio_path", str(audio_path),
        "--text_path", str(text_path),
        "--language", "ara",
        "--alignment_model", MODEL,
        "--device", "cpu",
        "--batch_size", "1",
        "--split_size", "word",
    ]
    run = subprocess.run(cmd, capture_output=True, text=True)
    if run.returncode != 0:
        raise gr.Error("تعذرت المطابقة: " + (run.stderr or run.stdout)[-1500:])
    result_path = job / "audio.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    segments = result.get("segments", [])
    if not segments:
        raise gr.Error("لم ينتج النموذج أي توقيت للكلمات.")
    srt_lines = []
    for n, segment in enumerate(segments, 1):
        srt_lines += [
            str(n),
            f"{to_srt_timestamp(segment['start'])} --> {to_srt_timestamp(segment['end'])}",
            str(segment["text"]),
            "",
        ]
    srt_path = job / "words.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    return [
        [str(s.get("text", "")), round(float(s["start"]), 3),
         round(float(s["end"]), 3)] for s in segments
    ], str(result_path), str(srt_path)


with gr.Blocks(title="محاذاة النص العربي مع الصوت") as demo:
    gr.Markdown("# مطابقة النص العربي مع الصوت\nارفع التسجيل وألصق نصه الصحيح لاستخراج توقيت الكلمات. التشغيل سحابي داخل Codespaces، وقد يستغرق على المعالج العادي.")
    with gr.Row():
        audio = gr.File(label="التسجيل الصوتي", type="filepath", file_types=["audio", ".wav", ".mp3", ".m4a", ".ogg", ".flac"])
        transcript = gr.Textbox(label="النص العربي المطابق للتسجيل", lines=10)
    run_button = gr.Button("مطابقة النص بالصوت", variant="primary")
    table = gr.Dataframe(headers=["الكلمة", "البداية بالثواني", "النهاية بالثواني"], datatype=["str", "number", "number"], label="التوقيت")
    with gr.Row():
        json_file = gr.File(label="النتيجة JSON")
        srt_file = gr.File(label="ترجمة الكلمات SRT")
    run_button.click(align, inputs=[audio, transcript], outputs=[table, json_file, srt_file])

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, share=False)
