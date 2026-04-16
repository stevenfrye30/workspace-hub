// Shared phonetic library used by Sound Map and Flow Lab.
// All functions here are pure (no DOM access); keep it that way.
// Depends on the global `D` from data/cmudict.js.

const SM_PHONEMES = [
  "tʃ","dʒ","eɪ","aɪ","aʊ","oʊ","ɔɪ","ɑr","ɪr","ɛr","ɔr","ʊr",
  "p","b","t","d","k","g","m","n","ŋ","f","v","θ","ð","s","z","ʃ","ʒ","h",
  "w","j","l","r","ɹ",
  "i","ɪ","e","ɛ","æ","ə","ɜ","ʌ","ɑ","ɔ","ɒ","o","ʊ","u","ɝ","ɚ"
].sort((a,b)=>b.length-a.length);

const SM_FEATS = {
  "p":{type:"C",place:"bilabial",manner:"stop",voice:0},
  "b":{type:"C",place:"bilabial",manner:"stop",voice:1},
  "t":{type:"C",place:"alveolar",manner:"stop",voice:0},
  "d":{type:"C",place:"alveolar",manner:"stop",voice:1},
  "k":{type:"C",place:"velar",manner:"stop",voice:0},
  "g":{type:"C",place:"velar",manner:"stop",voice:1},
  "m":{type:"C",place:"bilabial",manner:"nasal",voice:1},
  "n":{type:"C",place:"alveolar",manner:"nasal",voice:1},
  "ŋ":{type:"C",place:"velar",manner:"nasal",voice:1},
  "f":{type:"C",place:"labiodental",manner:"fricative",voice:0},
  "v":{type:"C",place:"labiodental",manner:"fricative",voice:1},
  "θ":{type:"C",place:"dental",manner:"fricative",voice:0},
  "ð":{type:"C",place:"dental",manner:"fricative",voice:1},
  "s":{type:"C",place:"alveolar",manner:"fricative",voice:0},
  "z":{type:"C",place:"alveolar",manner:"fricative",voice:1},
  "ʃ":{type:"C",place:"postalveolar",manner:"fricative",voice:0},
  "ʒ":{type:"C",place:"postalveolar",manner:"fricative",voice:1},
  "h":{type:"C",place:"glottal",manner:"fricative",voice:0},
  "tʃ":{type:"C",place:"postalveolar",manner:"affricate",voice:0},
  "dʒ":{type:"C",place:"postalveolar",manner:"affricate",voice:1},
  "w":{type:"C",place:"bilabial",manner:"approximant",voice:1},
  "j":{type:"C",place:"palatal",manner:"approximant",voice:1},
  "l":{type:"C",place:"alveolar",manner:"approximant",voice:1},
  "r":{type:"C",place:"alveolar",manner:"approximant",voice:1},
  "ɹ":{type:"C",place:"alveolar",manner:"approximant",voice:1},
  "i":{type:"V",place:"front-vowel",voice:1},
  "ɪ":{type:"V",place:"front-vowel",voice:1},
  "e":{type:"V",place:"front-vowel",voice:1},
  "ɛ":{type:"V",place:"front-vowel",voice:1},
  "æ":{type:"V",place:"front-vowel",voice:1},
  "ə":{type:"V",place:"central-vowel",voice:1},
  "ɜ":{type:"V",place:"central-vowel",voice:1},
  "ʌ":{type:"V",place:"central-vowel",voice:1},
  "ɝ":{type:"V",place:"central-vowel",voice:1},
  "ɚ":{type:"V",place:"central-vowel",voice:1},
  "ɑ":{type:"V",place:"back-vowel",voice:1},
  "ɔ":{type:"V",place:"back-vowel",voice:1},
  "ɒ":{type:"V",place:"back-vowel",voice:1},
  "o":{type:"V",place:"back-vowel",voice:1},
  "ʊ":{type:"V",place:"back-vowel",voice:1},
  "u":{type:"V",place:"back-vowel",voice:1},
  "eɪ":{type:"V",place:"diphthong",voice:1},
  "aɪ":{type:"V",place:"diphthong",voice:1},
  "aʊ":{type:"V",place:"diphthong",voice:1},
  "oʊ":{type:"V",place:"diphthong",voice:1},
  "ɔɪ":{type:"V",place:"diphthong",voice:1},
  "ɑr":{type:"V",place:"diphthong",voice:1},
  "ɪr":{type:"V",place:"diphthong",voice:1},
  "ɛr":{type:"V",place:"diphthong",voice:1},
  "ɔr":{type:"V",place:"diphthong",voice:1},
  "ʊr":{type:"V",place:"diphthong",voice:1}
};

function smParsePhonemes(ipa) {
  ipa = ipa.replace(/[ˈˌ.]/g, "");
  const out = [];
  let i = 0;
  while (i < ipa.length) {
    let matched = false;
    for (const p of SM_PHONEMES) {
      if (ipa.startsWith(p, i)) { out.push(p); i += p.length; matched = true; break; }
    }
    if (!matched) { out.push(ipa[i]); i++; }
  }
  return out;
}

// Parse IPA string into syllables. Each syllable = {phonemes:[], stress:0|1|2}.
// Stress: 0 = unstressed, 1 = primary (ˈ), 2 = secondary (ˌ).

function smSyllabify(ipa) {
  // 1) Tokenize, tracking stress marks that apply to the upcoming syllable.
  const tokens = [];
  let pending = 0;
  let i = 0;
  while (i < ipa.length) {
    const c = ipa[i];
    if (c === "ˈ") { pending = 1; i++; continue; }
    if (c === "ˌ") { pending = pending || 2; i++; continue; }
    if (c === "." || c === " ") { i++; continue; }
    let matched = null;
    for (const p of SM_PHONEMES) {
      if (ipa.startsWith(p, i)) { matched = p; break; }
    }
    if (!matched) { matched = ipa[i]; }
    tokens.push({ p: matched, stressMark: pending });
    pending = 0;
    i += matched.length;
  }

  // 2) Group into syllables by vowel nucleus, with onset-maximal-ish split.
  const syls = [];
  let cur = { phonemes: [], stress: 0, hasVowel: false };
  let nextStress = 0;

  for (const tok of tokens) {
    if (tok.stressMark) nextStress = Math.max(nextStress, tok.stressMark);
    const feat = SM_FEATS[tok.p];
    const isVowel = feat && feat.type === "V";

    if (isVowel && cur.hasVowel) {
      // New syllable begins. Split intervocalic consonants.
      let lastV = -1;
      for (let k = cur.phonemes.length - 1; k >= 0; k--) {
        const ff = SM_FEATS[cur.phonemes[k]];
        if (ff && ff.type === "V") { lastV = k; break; }
      }
      const between = cur.phonemes.slice(lastV + 1);
      // 0 → nothing moves. 1 → move to new onset. 2+ → first stays as coda, rest move.
      const keep = between.length <= 1 ? 0 : 1;
      const kept = between.slice(0, keep);
      const moved = between.slice(keep);
      cur.phonemes = cur.phonemes.slice(0, lastV + 1).concat(kept);
      syls.push({ phonemes: cur.phonemes, stress: cur.stress });
      cur = { phonemes: moved.concat([tok.p]), stress: nextStress, hasVowel: true };
      nextStress = 0;
    } else if (isVowel) {
      cur.phonemes.push(tok.p);
      cur.stress = Math.max(cur.stress, nextStress);
      cur.hasVowel = true;
      nextStress = 0;
    } else {
      cur.phonemes.push(tok.p);
    }
  }
  if (cur.phonemes.length) syls.push({ phonemes: cur.phonemes, stress: cur.stress });
  if (!syls.length) syls.push({ phonemes: [], stress: 0 });
  return syls;
}

function smDescribe(p, feat) {
  if (!feat) return `/${p}/ — unknown`;
  if (feat.type === "V") {
    return `/${p}/ · vowel · ${feat.place.replace("-vowel","")} · voiced`;
  }
  return `/${p}/ · ${feat.manner} · ${feat.place} · ${feat.voice?"voiced":"voiceless"}`;
}

const SM_GROUP_COLORS = [
  "#ff6b6b","#f39c12","#f1c40f","#6ad86a",
  "#16a085","#4aa3e0","#b47cd6","#e84393"
];

// Example words used when the user clicks a phoneme — they hear a short
// word that prominently features the sound.

const SM_PHON_EXAMPLE = {
  "p":"pat","b":"bat","t":"tap","d":"dad","k":"cat","g":"go",
  "m":"man","n":"no","ŋ":"sing",
  "f":"fan","v":"van","θ":"thin","ð":"this","s":"sun","z":"zoo",
  "ʃ":"ship","ʒ":"measure","h":"hat",
  "tʃ":"chip","dʒ":"jam",
  "w":"we","j":"yes","l":"let","r":"run","ɹ":"run",
  "i":"see","ɪ":"sit","e":"bay","ɛ":"bed","æ":"cat",
  "ə":"sofa","ɜ":"bird","ʌ":"cup","ɝ":"bird","ɚ":"butter",
  "ɑ":"father","ɔ":"thought","ɒ":"hot","o":"go","ʊ":"book","u":"food",
  "eɪ":"day","aɪ":"my","aʊ":"how","oʊ":"go","ɔɪ":"boy",
  "ɑr":"car","ɪr":"ear","ɛr":"air","ɔr":"or","ʊr":"tour"
};

function smSpeak(text, rate) {
  if (!("speechSynthesis" in window)) return false;
  const u = new SpeechSynthesisUtterance(text);
  u.rate = rate || 1;
  u.pitch = 1;
  u.lang = "en-US";
  speechSynthesis.cancel();
  speechSynthesis.speak(u);
  return true;
}

const SM_AUDIO = "speechSynthesis" in window;

function smSylNucleus(syl) {
  for (const p of syl.phonemes) {
    const f = SM_FEATS[p];
    if (f && f.type === "V") return p;
  }
  return "";
}

function smSylOnset(syl) {
  const out = [];
  for (const p of syl.phonemes) {
    const f = SM_FEATS[p];
    if (f && f.type === "V") break;
    out.push(p);
  }
  return out.join("");
}

function smSylCoda(syl) {
  const out = [];
  let seenV = false;
  for (const p of syl.phonemes) {
    const f = SM_FEATS[p];
    if (f && f.type === "V") { seenV = true; out.length = 0; continue; }
    if (seenV) out.push(p);
  }
  return out.join("");
}

function smSylRhymeKey(syl) {
  const n = smSylNucleus(syl);
  return n ? n + smSylCoda(syl) : "";
}

// ── Phonetic distance ──────────────────────────────────────────────────
// Returns 0.0 (identical / deep rhyme) to 1.0 (unrelated).

function smWordProximity(wA, wB) {
  if (!wA || !wB) return 1.0;
  if (wA === wB) return 0.0;
  const a = D[wA], b = D[wB];
  if (!a || !b) return 1.0;
  const rksA = a[1], rksB = b[1];
  const maxDepth = Math.min(rksA.length, rksB.length);
  for (let depth = maxDepth; depth >= 1; depth--) {
    if (rksA[depth-1] === rksB[depth-1]) {
      // depth 4 -> 0.05 (essentially exact), depth 1 -> 0.45
      return Math.max(0.05, 0.55 - depth * 0.13);
    }
  }
  // No exact rhyme. Compare last vowel nucleus for assonance / family match.
  const lastA = smLastVowelOf(a[0]);
  const lastB = smLastVowelOf(b[0]);
  if (lastA && lastB) {
    if (lastA === lastB) return 0.60;                    // same nucleus (assonance)
    const fA = SM_FEATS[lastA], fB = SM_FEATS[lastB];
    if (fA && fB && fA.place === fB.place) return 0.78;  // same vowel family
  }
  return 1.0;
}

function smLastVowelOf(ipa) {
  const phs = smParsePhonemes(ipa);
  for (let i = phs.length - 1; i >= 0; i--) {
    const f = SM_FEATS[phs[i]];
    if (f && f.type === "V") return phs[i];
  }
  return null;
}

function smProximityBucket(d) {
  if (d <= 0.05) return "identical";
  if (d <= 0.22) return "exact";    // deep rhyme (2+ syl)
  if (d <= 0.40) return "rhyme";    // single-syl rhyme
  if (d <= 0.65) return "slant";    // same nucleus, different coda
  if (d <= 0.85) return "family";   // same vowel family
  return "far";
}

const SM_FOOT_NAMES = {
  "iambic":"iambic","trochaic":"trochaic","anapestic":"anapestic",
  "dactylic":"dactylic","spondaic":"spondaic"
};

const SM_METER_NAMES = {
  1:"monometer",2:"dimeter",3:"trimeter",4:"tetrameter",
  5:"pentameter",6:"hexameter",7:"heptameter",8:"octameter"
};

function smAnalyzeMeter(stresses) {
  if (stresses.length < 4) return null;
  const binary = stresses.map(s => s > 0 ? 1 : 0);
  const patterns = [
    { name:"iambic",    foot:[0,1] },
    { name:"trochaic",  foot:[1,0] },
    { name:"anapestic", foot:[0,0,1] },
    { name:"dactylic",  foot:[1,0,0] },
    { name:"spondaic",  foot:[1,1] }
  ];
  let best = null;
  for (const pat of patterns) {
    let matches = 0;
    for (let i = 0; i < binary.length; i++) {
      if (binary[i] === pat.foot[i % pat.foot.length]) matches++;
    }
    const score = matches / binary.length;
    if (!best || score > best.score) best = { ...pat, score };
  }
  const feet = Math.floor(binary.length / best.foot.length);
  return {
    binary,
    pattern: best.name,
    feet,
    meter: SM_METER_NAMES[feet] || `${feet}-foot`,
    confidence: best.score
  };
}

function smFindMultiRhymes(flatSyls, maxLen, minLen) {
  maxLen = maxLen || 4;
  minLen = minLen || 2;
  const used = new Set();
  const chains = [];
  for (let N = maxLen; N >= minLen; N--) {
    const buckets = new Map();
    for (let i = 0; i + N <= flatSyls.length; i++) {
      const keys = [];
      let ok = true;
      for (let k = 0; k < N; k++) {
        const key = flatSyls[i + k].key;
        if (!key) { ok = false; break; }
        keys.push(key);
      }
      if (!ok) continue;
      const sig = keys.join("|");
      if (!buckets.has(sig)) buckets.set(sig, []);
      buckets.get(sig).push(i);
    }
    for (const [, positions] of buckets) {
      const filtered = positions.filter(p => {
        for (let k = 0; k < N; k++) if (used.has(p + k)) return false;
        return true;
      });
      const accepted = [];
      let lastEnd = -1;
      for (const p of filtered) {
        if (p > lastEnd) {
          accepted.push(p);
          lastEnd = p + N - 1;
        }
      }
      if (accepted.length >= 2) {
        for (const p of accepted) {
          for (let k = 0; k < N; k++) used.add(p + k);
        }
        chains.push({ length: N, positions: accepted });
      }
    }
  }
  // Order chains: longer first, then by earliest start
  chains.sort((a, b) => b.length - a.length || a.positions[0] - b.positions[0]);
  return chains;
}

function smComputeGroups(processed, byLine, mode) {
  if (mode === "none") return () => null;

  if (mode === "multirhyme") {
    const flat = [];
    for (let w = 0; w < processed.length; w++) {
      const wp = processed[w];
      if (!wp.known) continue;
      wp.syllables.forEach((sy, s) => {
        flat.push({ w, s, key: smSylRhymeKey(sy) });
      });
    }
    const chains = smFindMultiRhymes(flat, 4, 2).slice(0, SM_GROUP_COLORS.length);
    const byPos = new Map();
    chains.forEach((ch, i) => {
      const color = SM_GROUP_COLORS[i];
      for (const p of ch.positions) {
        for (let k = 0; k < ch.length; k++) {
          const entry = flat[p + k];
          byPos.set(entry.w + ":" + entry.s, color);
        }
      }
    });
    return (w, s) => byPos.get(w + ":" + s) || null;
  }

  const entries = [];
  if (mode === "endrhyme") {
    for (const lineWords of byLine) {
      for (let k = lineWords.length - 1; k >= 0; k--) {
        const wp = processed[lineWords[k]];
        if (!wp.known || !wp.syllables.length) continue;
        const s = wp.syllables.length - 1;
        const key = smSylRhymeKey(wp.syllables[s]);
        if (key) entries.push({ w: lineWords[k], s, key });
        break;
      }
    }
  } else if (mode === "alliteration") {
    for (let w = 0; w < processed.length; w++) {
      const wp = processed[w];
      if (!wp.known || !wp.syllables.length) continue;
      const key = smSylOnset(wp.syllables[0]);
      if (key) entries.push({ w, s: 0, key });
    }
  } else {
    for (let w = 0; w < processed.length; w++) {
      const wp = processed[w];
      if (!wp.known) continue;
      wp.syllables.forEach((sy, s) => {
        let key = "";
        if (mode === "rhyme") key = smSylRhymeKey(sy);
        else if (mode === "assonance") key = smSylNucleus(sy);
        else if (mode === "consonance") key = smSylCoda(sy);
        if (key) entries.push({ w, s, key });
      });
    }
  }
  const groups = new Map();
  for (const e of entries) {
    if (!groups.has(e.key)) groups.set(e.key, []);
    groups.get(e.key).push(e);
  }
  const top = [...groups.entries()]
    .filter(([, v]) => v.length >= 2)
    .sort((a, b) => b[1].length - a[1].length)
    .slice(0, SM_GROUP_COLORS.length);
  const byPos = new Map();
  top.forEach(([, occ], i) => {
    const color = SM_GROUP_COLORS[i];
    for (const o of occ) byPos.set(o.w + ":" + o.s, color);
  });
  return (w, s) => byPos.get(w + ":" + s) || null;
}

function smLevenshtein(a, b) {
  const n = a.length, m = b.length;
  if (!n) return m;
  if (!m) return n;
  let prev = new Array(m + 1);
  let curr = new Array(m + 1);
  for (let j = 0; j <= m; j++) prev[j] = j;
  for (let i = 1; i <= n; i++) {
    curr[0] = i;
    for (let j = 1; j <= m; j++) {
      const cost = a[i-1] === b[j-1] ? 0 : 1;
      curr[j] = Math.min(prev[j] + 1, curr[j-1] + 1, prev[j-1] + cost);
    }
    [prev, curr] = [curr, prev];
  }
  return prev[m];
}

async function smLoadCorpus() {
  if (SM_CORPUS) return SM_CORPUS;
  try {
    const r = await fetch("corpus.json");
    if (!r.ok) throw new Error("HTTP " + r.status);
    SM_CORPUS = await r.json();
    return SM_CORPUS;
  } catch (err) {
    SM_CORPUS = [];
    return SM_CORPUS;
  }
}
