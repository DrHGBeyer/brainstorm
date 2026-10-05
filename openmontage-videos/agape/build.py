"""Build narration (Piper, German) + Remotion Explainer props for the
learning video "Agápē".

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
PUBLIC = OM / "remotion-composer" / "public" / "agape"
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
    "1jn4_8": verse("I John", 4, 8),
    "rom5_8": verse("Romans", 5, 8),
    "1jn4_19": verse("I John", 4, 19),
    "1co13_4": verse("I Corinthians", 13, 4),
    "1co13_5": verse("I Corinthians", 13, 5),
    "mt5_44": verse("Matthew", 5, 44),
    "jn13_35": verse("John", 13, 35),
    "2ti4_10": verse("II Timothy", 4, 10),
    "1co13_13": verse("I Corinthians", 13, 13),
}


def must_contain(key: str, fragment: str) -> str:
    assert fragment in Q[key], f"{key}: '{fragment}' not in source text"
    return fragment


SCENES = [
    ("intro",
     ["Das Neue Testament wurde auf Griechisch geschrieben.",
      "Für Liebe kannte das Griechische mehrere Wörter.",
      "Eines davon prägt das Neue Testament wie kein anderes: agápē."],
     {"type": "hero_title", "text": "Agápē · ἀγάπη",
      "heroSubtitle": "Die Liebe, von der die Bibel spricht"}),

    ("words",
     ["Érōs, die leidenschaftliche Liebe, kommt im Neuen Testament nicht vor.",
      "Philía steht für Freundschaft und Zuneigung, storgḗ für die Zuneigung in der Familie.",
      "Agápē ist das Wort, das die Schreiber des Neuen Testaments für Gottes Liebe und für das Liebesgebot gebrauchen."],
     {"type": "callout", "callout_type": "info", "title": "Griechische Wörter für Liebe",
      "text": "érōs – leidenschaftliche Liebe (im NT nicht belegt)  ·  philía – Freundschaft, Zuneigung  ·  "
              "storgḗ – familiäre Zuneigung (im NT nur in Zusammensetzungen)  ·  agápē – Gottes Liebe und das Liebesgebot"}),

    ("count",
     ["Das Substantiv agápē und das Verb agapáō kommen im Neuen Testament zusammen über zweihundertfünfzig Mal vor.",
      "Das Substantiv ist vor der griechischen Übersetzung des Alten Testaments, der Septuaginta, kaum belegt."],
     {"type": "stat_card", "stat": "> 250 ×",
      "subtitle": "agápē (Substantiv) und agapáō (Verb) im Neuen Testament"}),

    ("god",
     ["Der wohl bekannteste Satz dazu steht im ersten Johannesbrief:",
      "„" + must_contain("1jn4_8", "Wer nicht liebt, hat Gott nicht erkannt, denn Gott ist Liebe.") + "“"],
     {"type": "callout", "callout_type": "quote", "title": "1. Johannes 4:8",
      "text": "„" + Q["1jn4_8"] + "“"}),

    ("shown",
     ["Diese Liebe zeigt sich im Handeln.",
      "Paulus schreibt: „" + must_contain("rom5_8", "Gott aber erweist seine Liebe gegen uns darin, daß Christus, da wir noch Sünder waren, für uns gestorben ist.") + "“",
      "Und Johannes folgert: „" + must_contain("1jn4_19", "Wir lieben, weil er uns zuerst geliebt hat.") + "“"],
     {"type": "callout", "callout_type": "quote", "title": "Römer 5:8 · 1. Johannes 4:19",
      "text": "„" + Q["rom5_8"] + "“  ·  „" + Q["1jn4_19"] + "“"}),

    ("cor",
     ["Wie Agápē im Alltag aussieht, beschreibt Paulus so:",
      "„" + must_contain("1co13_4", "Die Liebe ist langmütig, ist gütig; die Liebe neidet nicht") + "“,",
      "„" + must_contain("1co13_5", "sie sucht nicht das Ihrige, sie läßt sich nicht erbittern, sie rechnet Böses nicht zu") + "“."],
     {"type": "callout", "callout_type": "quote", "title": "1. Korinther 13:4–5",
      "text": "„" + Q["1co13_4"] + " " + Q["1co13_5"] + " …“"}),

    ("enemies",
     ["Jesus ging noch weiter.",
      "„" + must_contain("mt5_44", "Liebet eure Feinde") + "“, sagte er,",
      "„" + must_contain("mt5_44", "betet für die, die euch beleidigen und verfolgen") + "“.",
      "Agápē hängt also nicht davon ab, ob der andere sie verdient."],
     {"type": "callout", "callout_type": "quote", "title": "Matthäus 5:44",
      "text": "„" + Q["mt5_44"].rstrip(",") + " …“"}),

    ("mark",
     ["Für Jesus war sie das Erkennungszeichen seiner Jünger:",
      "„" + must_contain("jn13_35", "Daran werden alle erkennen, daß ihr meine Jünger seid, wenn ihr Liebe untereinander habt.") + "“"],
     {"type": "callout", "callout_type": "quote", "title": "Johannes 13:35",
      "text": "„" + Q["jn13_35"] + "“"}),

    ("caution",
     ["Eine Vorsicht ist aber angebracht.",
      "Das Wort allein bedeutet nicht automatisch göttliche, selbstlose Liebe.",
      "Von Demas heißt es, er habe den jetzigen Zeitlauf liebgewonnen, und auch dort steht das Verb agapáō.",
      "Ihren besonderen Inhalt bekommt Agápē erst durch den Zusammenhang: durch das Vorbild Gottes und Jesu."],
     {"type": "callout", "callout_type": "warning", "title": "Vorsicht vor Vereinfachungen",
      "text": "Auch in 2. Timotheus 4:10 steht agapáō: Demas hat „" + must_contain("2ti4_10", "den jetzigen Zeitlauf liebgewonnen")
              + "“. Was Agápē bedeutet, ergibt sich aus dem Zusammenhang, nicht aus dem Wort allein."}),

    ("think",
     ["Zum Nachdenken:",
      "Wo kann ich diese Woche jemandem Gutes tun, der es mir nicht zurückgeben kann?",
      "Und welche Eigenschaft aus dem ersten Korintherbrief, Kapitel dreizehn, fällt mir am schwersten?"],
     {"type": "callout", "callout_type": "tip", "title": "Zum Nachdenken",
      "text": "Wem kann ich Gutes tun, der es mir nicht zurückgeben kann? (Matthäus 5:44)  ·  "
              "Welche Eigenschaft aus 1. Korinther 13:4–7 fällt mir am schwersten?"}),

    ("close",
     ["Paulus schließt sein Kapitel über die Liebe so:",
      "„" + must_contain("1co13_13", "Nun aber bleibt Glaube, Hoffnung, Liebe, diese drei; die größte aber von diesen ist die Liebe.") + "“"],
     {"type": "callout", "callout_type": "quote", "title": "1. Korinther 13:13",
      "text": "„" + Q["1co13_13"] + "“"}),

    ("outro",
     [],
     {"type": "hero_title", "text": "Agápē – Liebe, die handelt",
      "heroSubtitle": "Bibeltexte: Unrevidierte Elberfelder Bibel (1905), gemeinfrei"}),
]


def tts_text(s: str) -> str:
    """Pronunciation fixes for Piper; the caption keeps the original spelling."""
    s = s.replace("„", "").replace("“", "")
    # Greek terms: spell phonetically for the German voice (stress on the marked syllable)
    for a, b in [("agápē", "agahpe"), ("Agápē", "Agahpe"), ("agapáō", "agapah-o"), ("philía", "filija"),
                 ("Philía", "Filija"), ("storgḗ", "storgeh"), ("Storgḗ", "Storgeh"), ("érōs", "eros"),
                 ("Érōs", "Eros"), ("Septuaginta", "Septua-ginta")]:
        s = s.replace(a, b)
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
    "audio": {"narration": {"src": "agape/narration.wav", "volume": 1.0}},
}
(ROOT / "props.json").write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")

# Script for review
lines = ["# Skript: Agápē – die Liebe, von der die Bibel spricht", "",
         "Bibeltexte: Unrevidierte Elberfelder Bibel (1905), gemeinfrei.", ""]
for (sid, sentences, cut), c in zip(SCENES, cuts):
    lines.append(f"## {c['in_seconds']:.1f}–{c['out_seconds']:.1f} s · {cut.get('title') or cut.get('text')}")
    lines += [f"- {s}" for s in sentences] or ["- (ohne Sprecher)"]
    lines.append("")
(ROOT / "SKRIPT.md").write_text("\n".join(lines), encoding="utf-8")
print(f"total {t:.1f}s, {len(cuts)} scenes, {len(captions)} caption words")
