"""Local audio transcription adapter (no cloud API)."""
from pathlib import Path
from faster_whisper import WhisperModel
from .config import settings

_model = None
def transcribe_file(path: str, language: str | None = None) -> dict:
    global _model
    if _model is None:
        _model = WhisperModel(settings.whisper_model, device="cpu", compute_type="int8")
    segments, info = _model.transcribe(Path(path), language=language, vad_filter=True)
    items = [{"start":s.start,"end":s.end,"text":s.text.strip()} for s in segments]
    return {"language":info.language,"language_probability":info.language_probability,"segments":items,
            "text":" ".join(x["text"] for x in items)}
# Speaker diarization is intentionally not faked; integrate a locally licensed model
# (e.g. pyannote with approved weights) and map segment speaker IDs in a later adapter.
