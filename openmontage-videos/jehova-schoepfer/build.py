"""Build narration (Piper, German) + Remotion Explainer props for the
learning video "Jehova - der Schöpfer und Gott aller Menschen".

Bible quotations: unrevidierte Elberfelder Bibel 1905 (public domain),
taken verbatim from scrollmapper/bible_databases GerElb1905.json.
"""
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OM = ROOT.parents[1]
PUBLIC = OM / "remotion-composer" / "public" / "jehova"
PUBLIC.mkdir(parents=True, exist_ok=True)
VOICE = Path(sys.argv[1])           # path to de-thorsten-low.onnx
BIBLE = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
PY = OM / ".venv" / "bin" / "python"

BOOKS = {b["name"]: b for b in BIBLE["books"]}


def verse(book: str, ch: int, v: int) -> str:
    for x in BOOKS[book]["chapters"][ch - 1]["verses"]:
        if x["verse"] == v:
            return x["text"]
    raise KeyError((book, ch, v))


# Every quoted passage is checked against the source text below.
Q = {
    "gen1_1": verse("Genesis", 1, 1),
    "ps83_18": verse("Psalms", 83, 18),
    "isa42_5": verse("Isaiah", 42, 5),
    "rom1_20": verse("Romans", 1, 20),
    "acts17_26": verse("Acts", 17, 26),
    "mal2_10": verse("Malachi", 2, 10),
    "acts17_27": verse("Acts", 17, 27),
    "rev4_11": verse("Revelation of John", 4, 11),
}


def must_contain(key: str, fragment: str) -> str:
    assert fragment in Q[key], f"{key}: '{fragment}' not in source text"
    return fragment


# ---------------------------------------------------------------------------
# Scenes: (id, narration sentences, visual cut without timing)
# Narration text: shown as captions. "say" variants fix pronunciation only.
# ---------------------------------------------------------------------------
SCENES = [
    ("intro",
     ["Wer hat das Universum erschaffen?",
      "Und wem verdanken wir unser Leben?",
      "Die Bibel gibt darauf eine klare Antwort."],
     {"type": "hero_title", "text": "Jehova",
      "heroSubtitle": "Der Schöpfer und Gott aller Menschen"}),

    ("gen",
     ["Schon ihr erster Satz lautet:",
      must_contain("gen1_1", "Im Anfang schuf Gott die Himmel und die Erde.")],
     {"type": "callout", "callout_type": "quote", "title": "1. Mose 1:1",
      "text": "„" + Q["gen1_1"] + "“"}),

    ("name",
     ["Dieser Gott hat einen persönlichen Namen.",
      "Im hebräischen Text des Alten Testaments steht er als vier Buchstaben, J H W H, rund sechstausendachthundert Mal.",
      "Die ursprüngliche Aussprache ist nicht sicher überliefert.",
      "Im Deutschen wird der Name traditionell mit Jehova wiedergegeben."],
     {"type": "stat_card", "title": "Der Name Gottes", "stat": "≈ 6800 ×",
      "subtitle": "steht der Gottesname JHWH (יהוה) im hebräischen Alten Testament"}),

    ("ps83",
     ["In Psalm 83 heißt es:",
      "„" + must_contain("ps83_18", "daß du allein, dessen Name Jehova ist, der Höchste bist über die ganze Erde") + "“."],
     {"type": "callout", "callout_type": "quote", "title": "Psalm 83:18",
      "text": "„… " + Q["ps83_18"].split("erkennen, ", 1)[1] + "“"}),

    ("isa",
     ["Jehova stellt sich selbst als Schöpfer vor.",
      "Durch den Propheten Jesaja sagt er:",
      "„" + must_contain("isa42_5", "So spricht Gott, Jehova, der die Himmel schuf und sie ausspannte, der die Erde ausbreitete mit ihren Gewächsen, dem Volke auf ihr den Odem gab") + "“."],
     {"type": "callout", "callout_type": "quote", "title": "Jesaja 42:5",
      "text": "„" + Q["isa42_5"].rstrip(":") + " …“"}),

    ("rom",
     ["Seine Eigenschaften lassen sich an dem erkennen, was er gemacht hat.",
      "Paulus schreibt sinngemäß: Seine ewige Kraft und Göttlichkeit werden an dem erkannt, was er gemacht hat."],
     {"type": "callout", "callout_type": "quote", "title": "Römer 1:20",
      "text": "„" + must_contain("rom1_20", "das Unsichtbare von ihm, sowohl seine ewige Kraft als auch seine Göttlichkeit, die von Erschaffung der Welt an in dem Gemachten wahrgenommen werden, wird geschaut") + " …“"}),

    ("all",
     ["Jehova ist nicht nur der Gott eines einzelnen Volkes.",
      "In Athen sagte der Apostel Paulus:",
      "„" + must_contain("acts17_26", "Und er hat aus einem Blute jede Nation der Menschen gemacht") + "“."],
     {"type": "callout", "callout_type": "quote", "title": "Apostelgeschichte 17:26",
      "text": "„" + must_contain("acts17_26", "Und er hat aus einem Blute jede Nation der Menschen gemacht, um auf dem ganzen Erdboden zu wohnen") + " …“"}),

    ("mal",
     ["Schon der Prophet Maleachi fragte:",
      "„" + must_contain("mal2_10", "Haben wir nicht alle einen Vater? Hat nicht ein Gott uns geschaffen?") + "“"],
     {"type": "callout", "callout_type": "quote", "title": "Maleachi 2:10",
      "text": "„" + must_contain("mal2_10", "Haben wir nicht alle einen Vater? Hat nicht ein Gott uns geschaffen?") + "“"}),

    ("near",
     ["Und dieser Gott ist erreichbar.",
      "Paulus sagte, die Menschen sollten Gott suchen,",
      "„" + must_contain("acts17_27", "obgleich er nicht fern ist von einem jeden von uns") + "“."],
     {"type": "callout", "callout_type": "quote", "title": "Apostelgeschichte 17:27",
      "text": "„" + Q["acts17_27"] + "“"}),

    ("think",
     ["Zum Nachdenken:",
      "Woran erkennst du in der Natur die Handschrift des Schöpfers?",
      "Und was bedeutet es für dich, dass alle Menschen von demselben Gott geschaffen wurden?"],
     {"type": "callout", "callout_type": "tip", "title": "Zum Nachdenken",
      "text": "Woran erkennst du in der Natur die Handschrift des Schöpfers? (Römer 1:20)  ·  "
              "Was bedeutet es, dass alle Menschen von demselben Gott stammen? (Apg 17:26; Maleachi 2:10)"}),

    ("rev",
     ["Die Offenbarung fasst es so zusammen:",
      "„" + must_contain("rev4_11", "Du bist würdig, o unser Herr und unser Gott, zu nehmen die Herrlichkeit und die Ehre und die Macht; denn du hast alle Dinge erschaffen") + "“."],
     {"type": "callout", "callout_type": "quote", "title": "Offenbarung 4:11",
      "text": "„" + must_contain("rev4_11", "Du bist würdig, o unser Herr und unser Gott, zu nehmen die Herrlichkeit und die Ehre und die Macht; denn du hast alle Dinge erschaffen") + " …“"}),

    ("outro",
     [],
     {"type": "hero_title", "text": "Jehova – Schöpfer aller Dinge",
      "heroSubtitle": "Bibeltexte: Unrevidierte Elberfelder Bibel (1905), gemeinfrei"}),
]


def tts_text(s: str) -> str:
    """Pronunciation fixes for Piper; the caption keeps the original spelling."""
    s = s.replace("„", "").replace("“", "")
    s = re.sub(r"\bJehova(s?)\b", r"Jehowa\1", s)   # German [v], not [f]
    s = s.replace("daß", "dass")
    s = s.replace("J H W H", "Jott, He, Weh, He")
    return s


def synth(text: str, out: Path) -> float:
    subprocess.run([str(PY), "-m", "piper", "-m", str(VOICE), "-c", str(VOICE) + ".json",
                    "-f", str(out), "--length-scale", "1.08", "--sentence-silence", "0.25"],
                   input=text.encode("utf-8"), check=True, capture_output=True)
    with wave.open(str(out)) as w:
        return w.getnframes() / w.getframerate()


GAP = 0.35          # pause between sentences
SCENE_PAD = 0.9     # breathing room at scene end
OUTRO = 4.5

sentence_wavs = []
captions = []
cuts = []
t = 0.0
for sid, sentences, cut in SCENES:
    start = t
    for i, s in enumerate(sentences):
        wav = PUBLIC / f"{sid}_{i}.wav"
        dur = synth(tts_text(s), wav)
        sentence_wavs.append((t, wav))
        # word captions: proportional to word length within the sentence
        words = s.split()
        weights = [max(len(re.sub(r"\W", "", w)), 2) for w in words]
        total = sum(weights)
        cur = t
        for j, (w, wt) in enumerate(zip(words, weights)):
            d = dur * wt / total
            captions.append({"word": w, "startMs": round(cur * 1000), "endMs": round((cur + d) * 1000),
                             **({"pageBreakAfter": True} if j == len(words) - 1 else {})})
            cur += d
        t += dur + GAP
    end = t + SCENE_PAD if sentences else t + OUTRO
    cuts.append({"id": sid, "source": "", "in_seconds": round(start, 3),
                 "out_seconds": round(end, 3), **cut})
    t = end

# Mix all sentence wavs onto one timeline with ffmpeg (adelay per clip).
narration = PUBLIC / "narration.wav"
inputs, filters = [], []
for k, (offset, wav) in enumerate(sentence_wavs):
    inputs += ["-i", str(wav)]
    ms = int(offset * 1000)
    filters.append(f"[{k}:a]adelay={ms}|{ms}[a{k}]")
mix = "".join(f"[a{k}]" for k in range(len(sentence_wavs)))
filters.append(f"{mix}amix=inputs={len(sentence_wavs)}:normalize=0,apad=whole_dur={t:.2f}[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filters),
                "-map", "[out]", "-ar", "44100", str(narration)], check=True)

props = {
    "themeConfig": {
        "primaryColor": "#C8A15A",
        "accentColor": "#E3C27A",
        "backgroundColor": "#14110F",
        "surfaceColor": "#221C17",
        "textColor": "#F5EFE6",
        "mutedTextColor": "#B8AC9C",
        "headingFont": "Space Grotesk",
        "bodyFont": "Space Grotesk",
        "monoFont": "Fira Code",
        "chartColors": ["#C8A15A", "#7FA7C9", "#9CC59A"],
        "springConfig": {"damping": 20, "stiffness": 90, "mass": 1},
        "transitionDuration": 0.5,
        "captionHighlightColor": "#E3C27A",
        "captionBackgroundColor": "rgba(20, 17, 15, 0.8)",
    },
    "cuts": cuts,
    "overlays": [],
    "captions": captions,
    "audio": {"narration": {"src": "jehova/narration.wav", "volume": 1.0}},
}
(ROOT / "props.json").write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")

# Script for review
lines = ["# Skript: Jehova – der Schöpfer und Gott aller Menschen", "",
         "Bibeltexte: Unrevidierte Elberfelder Bibel (1905), gemeinfrei.", ""]
for (sid, sentences, cut), c in zip(SCENES, cuts):
    lines.append(f"## {c['in_seconds']:.1f}–{c['out_seconds']:.1f} s · {cut.get('title') or cut.get('text')}")
    lines += [f"- {s}" for s in sentences] or ["- (ohne Sprecher)"]
    lines.append("")
(ROOT / "SKRIPT.md").write_text("\n".join(lines), encoding="utf-8")
print(f"total {t:.1f}s, {len(cuts)} scenes, {len(captions)} caption words")
