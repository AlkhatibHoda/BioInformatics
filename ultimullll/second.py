import re
import math
from collections import Counter
from dataclasses import dataclass
from typing import List, Dict, Tuple


WORD_RE = re.compile(r"[A-Za-zĂÂÎȘȚăâîșț]+(?:-[A-Za-zĂÂÎȘȚăâîșț]+)?", re.UNICODE)

def tokenize(text: str) -> List[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


@dataclass
class BigramModel:
    bigram: Counter
    context: Counter
    vocab: set
    k: float

    @classmethod
    def train(cls, tokens: List[str], k: float = 1.0) -> "BigramModel":
        # boundaries help stability for short windows
        seq = ["<s>"] + tokens + ["</s>"]
        bigram = Counter(zip(seq[:-1], seq[1:]))
        context = Counter(seq[:-1])
        vocab = set(seq)
        return cls(bigram=bigram, context=context, vocab=vocab, k=k)

    def prob(self, w1: str, w2: str, V: int) -> float:
        # Add-k smoothing (V = union vocab size)
        return (self.bigram[(w1, w2)] + self.k) / (self.context[w1] + self.k * V)


@dataclass
class LLRScorer:
    model_A: BigramModel  # Eminescu
    model_B: BigramModel  # Stanescu
    vocab_union: List[str]
    eps_neither: float = 0.25  # band around 0 => neither

    def score_window(self, tokens: List[str]) -> float:
        seq = ["<s>"] + tokens + ["</s>"]
        V = len(self.vocab_union)
        s = 0.0
        for w1, w2 in zip(seq[:-1], seq[1:]):
            pA = self.model_A.prob(w1, w2, V)
            pB = self.model_B.prob(w1, w2, V)
            s += math.log(pA / pB, 2)
        return s

    def label(self, score: float) -> str:
        if score > self.eps_neither:
            return "EMINESCU"
        if score < -self.eps_neither:
            return "STANESCU"
        return "NEITHER"


def sliding_window_scores(tokens: List[str], scorer: LLRScorer, window: int, step: int) -> List[Dict]:
    n = len(tokens)
    if n < 2:
        return []

    # Auto-fix window size so we ALWAYS produce windows
    window = max(2, min(window, n))

    rows = []
    for i in range(0, n - window + 1, step):
        w = tokens[i:i + window]
        sc = scorer.score_window(w)
        rows.append({
            "start": i,
            "end": i + window,
            "score": sc,
            "label": scorer.label(sc),
            "snippet": " ".join(w)
        })
    return rows

def word_level_labels(tokens: List[str], windows: List[Dict], scorer: LLRScorer) -> List[str]:
    n = len(tokens)
    if n == 0:
        return []

    sums = [0.0] * n
    cnts = [0] * n

    for r in windows:
        for i in range(r["start"], r["end"]):
            sums[i] += r["score"]
            cnts[i] += 1

    labels = []
    for i in range(n):
        avg = (sums[i] / cnts[i]) if cnts[i] else 0.0
        labels.append(scorer.label(avg))
    return labels

def segments(tokens: List[str], labels: List[str]) -> List[Tuple[str, int, int, str]]:
    if not tokens:
        return []
    segs = []
    cur = labels[0]
    start = 0
    for i in range(1, len(tokens)):
        if labels[i] != cur:
            segs.append((cur, start, i, " ".join(tokens[start:i])))
            cur = labels[i]
            start = i
    segs.append((cur, start, len(tokens), " ".join(tokens[start:])))
    return segs


def print_windows(rows: List[Dict], limit: int = 25):
    print("\n--- Sliding window report (first lines) ---")
    if not rows:
        print("(No windows produced: accused text is too short.)")
        return
    for r in rows[:limit]:
        print(f"[{r['start']:4d}:{r['end']:4d}]  score={r['score']:7.3f}  {r['label']:9s} | {r['snippet']}")
    if len(rows) > limit:
        print(f"... ({len(rows)-limit} more windows)")

def print_word_labels(tokens: List[str], labels: List[str], per_line: int = 12):
    print("\n--- Word-level labels ---")
    if not tokens:
        print("(No tokens.)")
        return
    short = {"EMINESCU": "E", "STANESCU": "S", "NEITHER": "N"}
    for i in range(0, len(tokens), per_line):
        chunk = []
        for w, lab in zip(tokens[i:i+per_line], labels[i:i+per_line]):
            chunk.append(f"{w}({short[lab]})")
        print("  ".join(chunk))

def print_segments(segs: List[Tuple[str,int,int,str]]):
    print("\n--- Detected segments ---")
    if not segs:
        print("(No segments.)")
        return
    for lab, a, b, txt in segs:
        print(f"{lab:9s} words[{a}:{b}]  -> {txt}")


def run_analysis(eminescu_text: str, stanescu_text: str, accused_text: str,
                 window: int = 20, step: int = 1, k: float = 1.0, eps_neither: float = 0.25):

    tokE = tokenize(eminescu_text)
    tokS = tokenize(stanescu_text)
    tokA = tokenize(accused_text)

    # Train even if short (no exception)
    modelE = BigramModel.train(tokE, k=k)
    modelS = BigramModel.train(tokS, k=k)

    vocab_union = sorted(modelE.vocab | modelS.vocab)
    scorer = LLRScorer(model_A=modelE, model_B=modelS, vocab_union=vocab_union, eps_neither=eps_neither)

    # Auto-fix window if accused is short
    effective_window = max(2, min(window, len(tokA))) if tokA else window

    rows = sliding_window_scores(tokA, scorer, window=effective_window, step=step)
    wlabs = word_level_labels(tokA, rows, scorer)
    segs = segments(tokA, wlabs)

    # Print results
    print(f"\nTokens: Eminescu={len(tokE)}  Stanescu={len(tokS)}  Accused={len(tokA)}")
    print(f"Params: window={effective_window} step={step} smoothing_k={k} eps_neither={eps_neither}")

    print_windows(rows, limit=30)
    print_word_labels(tokA, wlabs, per_line=12)
    print_segments(segs)

    # Summary
    from collections import Counter
    win_counts = Counter(r["label"] for r in rows)
    word_counts = Counter(wlabs)

    print("\n--- Summary ---")
    print("Window label counts:", dict(win_counts))
    print("Word label counts:  ", dict(word_counts))


if __name__ == "__main__":
    EMINESCU = """
    Somnoroase pasarele pe la cuiburi se aduna
    se ascund in ramurele noapte buna
    Doar izvoarele suspina pe cand codrul negru tace
    """

    STANESCU = """
    A venit toamna acopera-mi inima cu ceva
    cu umbra unui copac sau mai bine cu umbra ta
    ma tem sa nu te pierd
    """

    ACCUSED = """
    Noaptea isi sprijina fruntea de fereastra si luna arde in aer
    in iarba pasii mei sunt propozitii scurte iar vantul le rescrie
    timpul isi muta greutatea dintr-un sens in altul si nu intreaba
    """

    run_analysis(EMINESCU, STANESCU, ACCUSED, window=20, step=1, k=1.0, eps_neither=0.25)
