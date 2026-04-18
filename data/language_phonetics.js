// Phoneme-inventory place-of-articulation distributions for 15 languages.
// Counts are distinct phonemes per place class for a standard/reference
// variety. Cross-checked against the Wikipedia "<lang> phonology" articles
// and Ladefoged & Maddieson's Sounds of the World's Languages where feasible.
//
// Notes on method:
//   • Aspirated / palatalized / glottalized consonants count as the same
//     place as their plain counterpart (e.g. Hindi pʰ → bilabial).
//   • Long/short vowel pairs each count as one phoneme (e.g. Arabic a, aː).
//   • Nasal vowels are counted at their base frontness (French ɛ̃ → front).
//   • Diphthongs are only listed where they are phonemically contrastive
//     in the reference variety (e.g. English /aɪ/, Hawaiian /ai/). Glides
//     are classed by their consonantal place (English /w/ = bilabial).
//
// These are INVENTORY proportions, not token frequencies in speech —
// a caveat the UI makes explicit to the user.

const LANG_PLACE_ORDER = [
  "bilabial", "labiodental", "dental", "alveolar", "postalveolar",
  "retroflex", "palatal", "velar", "uvular", "pharyngeal", "glottal",
  "front-vowel", "central-vowel", "back-vowel", "diphthong"
];

const LANG_PLACE_LABELS = {
  "bilabial": "bilabial",
  "labiodental": "labiodental",
  "dental": "dental",
  "alveolar": "alveolar",
  "postalveolar": "postalveolar",
  "retroflex": "retroflex",
  "palatal": "palatal",
  "velar": "velar",
  "uvular": "uvular",
  "pharyngeal": "pharyngeal",
  "glottal": "glottal",
  "front-vowel": "front vowel",
  "central-vowel": "central vowel",
  "back-vowel": "back vowel",
  "diphthong": "diphthong"
};

// Each entry: { name, variety, family, region, note?, counts: {place: n} }
const LANG_INVENTORIES = {
  en: {
    name: "English", variety: "General American", family: "Germanic (IE)", region: "North America",
    counts: { bilabial:4, labiodental:2, dental:2, alveolar:7, postalveolar:4,
              retroflex:0, palatal:1, velar:3, uvular:0, pharyngeal:0, glottal:1,
              "front-vowel":5, "central-vowel":3, "back-vowel":5, diphthong:5 }
  },
  es: {
    name: "Spanish", variety: "Castilian", family: "Romance (IE)", region: "Iberia",
    counts: { bilabial:3, labiodental:1, dental:3, alveolar:5, postalveolar:1,
              retroflex:0, palatal:3, velar:3, uvular:0, pharyngeal:0, glottal:0,
              "front-vowel":2, "central-vowel":1, "back-vowel":2, diphthong:0 }
  },
  zh: {
    name: "Mandarin", variety: "Standard (Beijing)", family: "Sinitic", region: "East Asia",
    note: "Tones omitted.",
    counts: { bilabial:3, labiodental:1, dental:0, alveolar:7, postalveolar:0,
              retroflex:4, palatal:3, velar:4, uvular:0, pharyngeal:0, glottal:0,
              "front-vowel":3, "central-vowel":2, "back-vowel":3, diphthong:6 }
  },
  ja: {
    name: "Japanese", variety: "Tokyo", family: "Japonic", region: "East Asia",
    counts: { bilabial:4, labiodental:0, dental:0, alveolar:6, postalveolar:3,
              retroflex:0, palatal:2, velar:2, uvular:0, pharyngeal:0, glottal:1,
              "front-vowel":2, "central-vowel":1, "back-vowel":2, diphthong:0 }
  },
  ar: {
    name: "Arabic", variety: "Modern Standard", family: "Semitic (Afro-Asiatic)", region: "MENA",
    note: "Emphatic (pharyngealized) consonants counted at their primary place.",
    counts: { bilabial:3, labiodental:1, dental:3, alveolar:10, postalveolar:2,
              retroflex:0, palatal:1, velar:3, uvular:1, pharyngeal:2, glottal:2,
              "front-vowel":2, "central-vowel":2, "back-vowel":2, diphthong:2 }
  },
  hi: {
    name: "Hindi", variety: "Standard", family: "Indo-Aryan (IE)", region: "South Asia",
    note: "Aspirated stops counted at their primary place.",
    counts: { bilabial:5, labiodental:0, dental:5, alveolar:3, postalveolar:5,
              retroflex:7, palatal:1, velar:5, uvular:0, pharyngeal:0, glottal:2,
              "front-vowel":4, "central-vowel":2, "back-vowel":4, diphthong:2 }
  },
  fr: {
    name: "French", variety: "Metropolitan", family: "Romance (IE)", region: "W. Europe",
    note: "Nasal vowels counted at their base frontness.",
    counts: { bilabial:4, labiodental:2, dental:0, alveolar:6, postalveolar:2,
              retroflex:0, palatal:3, velar:3, uvular:1, pharyngeal:0, glottal:0,
              "front-vowel":8, "central-vowel":1, "back-vowel":5, diphthong:0 }
  },
  de: {
    name: "German", variety: "Standard", family: "Germanic (IE)", region: "C. Europe",
    counts: { bilabial:3, labiodental:3, dental:0, alveolar:7, postalveolar:3,
              retroflex:0, palatal:2, velar:4, uvular:1, pharyngeal:0, glottal:1,
              "front-vowel":13, "central-vowel":2, "back-vowel":6, diphthong:3 }
  },
  ru: {
    name: "Russian", variety: "Standard", family: "Slavic (IE)", region: "E. Europe / N. Asia",
    note: "Hard and palatalized (soft) consonants counted separately at the same place.",
    counts: { bilabial:6, labiodental:4, dental:0, alveolar:15, postalveolar:4,
              retroflex:0, palatal:1, velar:6, uvular:0, pharyngeal:0, glottal:0,
              "front-vowel":2, "central-vowel":2, "back-vowel":2, diphthong:0 }
  },
  pt: {
    name: "Portuguese", variety: "European", family: "Romance (IE)", region: "Iberia",
    note: "Nasal vowels counted at their base frontness. Nasal diphthongs included.",
    counts: { bilabial:4, labiodental:2, dental:2, alveolar:5, postalveolar:2,
              retroflex:0, palatal:3, velar:2, uvular:1, pharyngeal:0, glottal:0,
              "front-vowel":5, "central-vowel":3, "back-vowel":5, diphthong:10 }
  },
  ko: {
    name: "Korean", variety: "Seoul", family: "Koreanic", region: "East Asia",
    note: "Tense (fortis) stops counted separately from plain and aspirated.",
    counts: { bilabial:4, labiodental:0, dental:0, alveolar:7, postalveolar:0,
              retroflex:0, palatal:4, velar:4, uvular:0, pharyngeal:0, glottal:1,
              "front-vowel":3, "central-vowel":3, "back-vowel":2, diphthong:8 }
  },
  tr: {
    name: "Turkish", variety: "Istanbul", family: "Turkic", region: "Anatolia",
    counts: { bilabial:3, labiodental:2, dental:0, alveolar:7, postalveolar:4,
              retroflex:0, palatal:3, velar:2, uvular:0, pharyngeal:0, glottal:1,
              "front-vowel":4, "central-vowel":2, "back-vowel":2, diphthong:0 }
  },
  sw: {
    name: "Swahili", variety: "Standard (Kiunguja)", family: "Bantu (Niger-Congo)", region: "E. Africa",
    note: "Implosives and prenasalized stops counted at their primary place.",
    counts: { bilabial:5, labiodental:2, dental:2, alveolar:8, postalveolar:4,
              retroflex:0, palatal:3, velar:6, uvular:0, pharyngeal:0, glottal:1,
              "front-vowel":2, "central-vowel":1, "back-vowel":2, diphthong:0 }
  },
  vi: {
    name: "Vietnamese", variety: "Northern (Hanoi)", family: "Austroasiatic", region: "SE Asia",
    note: "Tones omitted.",
    counts: { bilabial:4, labiodental:2, dental:0, alveolar:8, postalveolar:0,
              retroflex:2, palatal:3, velar:5, uvular:0, pharyngeal:0, glottal:2,
              "front-vowel":3, "central-vowel":3, "back-vowel":5, diphthong:6 }
  },
  haw: {
    name: "Hawaiian", variety: "Standard", family: "Polynesian (Austronesian)", region: "Pacific",
    note: "One of the world's smallest consonant inventories.",
    counts: { bilabial:3, labiodental:0, dental:0, alveolar:2, postalveolar:0,
              retroflex:0, palatal:0, velar:1, uvular:0, pharyngeal:0, glottal:2,
              "front-vowel":2, "central-vowel":1, "back-vowel":2, diphthong:9 }
  }
};

// Pre-compute normalized distribution vectors (as proportions, summing to 1)
// for each language in the canonical place order. Kept as a separate map
// so we only pay the division cost once.
const LANG_VECTORS = (() => {
  const out = {};
  for (const code in LANG_INVENTORIES) {
    const counts = LANG_INVENTORIES[code].counts;
    let total = 0;
    for (const place of LANG_PLACE_ORDER) total += (counts[place] || 0);
    const vec = LANG_PLACE_ORDER.map(p => total > 0 ? (counts[p] || 0) / total : 0);
    out[code] = vec;
    LANG_INVENTORIES[code].total = total;
    LANG_INVENTORIES[code].vector = vec;
  }
  return out;
})();

// Cosine similarity on two equal-length vectors.
function langCosineSim(a, b) {
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  const denom = Math.sqrt(na) * Math.sqrt(nb);
  return denom > 0 ? dot / denom : 0;
}

// Convert a flat phoneme list (user's input) into a normalized place-distribution
// vector in LANG_PLACE_ORDER. Phonemes without a SM_FEATS entry are ignored.
function langUserVector(phonemes) {
  const counts = {};
  let total = 0;
  for (const p of phonemes) {
    const feat = (typeof SM_FEATS !== "undefined") ? SM_FEATS[p] : null;
    if (!feat) continue;
    counts[feat.place] = (counts[feat.place] || 0) + 1;
    total++;
  }
  const vec = LANG_PLACE_ORDER.map(p => total > 0 ? (counts[p] || 0) / total : 0);
  return { vector: vec, counts, total };
}
