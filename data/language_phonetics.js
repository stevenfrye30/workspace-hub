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

// ════════════════════════════════════════════════════════════════════════
//  Explicit per-language phoneme inventories (for Coverage view)
// ════════════════════════════════════════════════════════════════════════
//
// Cons rows: [ipa, place, manner, voice]  — voice 0=voiceless, 1=voiced
// Vowel rows: [ipa, height, backness, rounded]
//   height:   0=close, 1=close-mid, 2=open-mid, 3=open
//   backness: 0=front, 1=central, 2=back
//   rounded:  0|1
// Diphthongs: list of IPA strings (drawn as a separate group).
//
// Manners used across languages: stop, nasal, fricative, affricate,
// approximant, lateral, trill, tap. Aspirated/palatalized variants keep
// the base manner and place; they render as separate cells inside the
// same grid slot.

const LANG_MANNER_ORDER = ["stop","nasal","trill","tap","fricative","affricate","approximant","lateral"];

const LANG_PHONEMES = {
  en: {
    cons: [
      ["p","bilabial","stop",0],["b","bilabial","stop",1],["m","bilabial","nasal",1],["w","bilabial","approximant",1],
      ["f","labiodental","fricative",0],["v","labiodental","fricative",1],
      ["θ","dental","fricative",0],["ð","dental","fricative",1],
      ["t","alveolar","stop",0],["d","alveolar","stop",1],["n","alveolar","nasal",1],["s","alveolar","fricative",0],["z","alveolar","fricative",1],["l","alveolar","lateral",1],["ɹ","alveolar","approximant",1],
      ["ʃ","postalveolar","fricative",0],["ʒ","postalveolar","fricative",1],["tʃ","postalveolar","affricate",0],["dʒ","postalveolar","affricate",1],
      ["j","palatal","approximant",1],
      ["k","velar","stop",0],["g","velar","stop",1],["ŋ","velar","nasal",1],
      ["h","glottal","fricative",0]
    ],
    vowels: [
      ["i",0,0,0],["ɪ",0,0,0],["ɛ",2,0,0],["æ",3,0,0],
      ["ə",1,1,0],["ʌ",2,1,0],["ɝ",1,1,0],
      ["u",0,2,1],["ʊ",0,2,1],["ɔ",2,2,1],["ɑ",3,2,0]
    ],
    diphs: ["eɪ","aɪ","aʊ","oʊ","ɔɪ"]
  },
  es: {
    cons: [
      ["p","bilabial","stop",0],["b","bilabial","stop",1],["m","bilabial","nasal",1],
      ["f","labiodental","fricative",0],
      ["t","dental","stop",0],["d","dental","stop",1],["θ","dental","fricative",0],
      ["s","alveolar","fricative",0],["n","alveolar","nasal",1],["l","alveolar","lateral",1],["ɾ","alveolar","tap",1],["r","alveolar","trill",1],
      ["tʃ","postalveolar","affricate",0],
      ["ɲ","palatal","nasal",1],["ʝ","palatal","fricative",1],["j","palatal","approximant",1],
      ["k","velar","stop",0],["g","velar","stop",1],["x","velar","fricative",0]
    ],
    vowels: [["i",0,0,0],["e",1,0,0],["a",3,1,0],["o",1,2,1],["u",0,2,1]],
    diphs: []
  },
  zh: {
    cons: [
      ["p","bilabial","stop",0],["pʰ","bilabial","stop",0],["m","bilabial","nasal",1],
      ["f","labiodental","fricative",0],
      ["t","alveolar","stop",0],["tʰ","alveolar","stop",0],["n","alveolar","nasal",1],["l","alveolar","lateral",1],["s","alveolar","fricative",0],["ts","alveolar","affricate",0],["tsʰ","alveolar","affricate",0],
      ["tʂ","retroflex","affricate",0],["tʂʰ","retroflex","affricate",0],["ʂ","retroflex","fricative",0],["ɻ","retroflex","approximant",1],
      ["tɕ","palatal","affricate",0],["tɕʰ","palatal","affricate",0],["ɕ","palatal","fricative",0],
      ["k","velar","stop",0],["kʰ","velar","stop",0],["x","velar","fricative",0],["ŋ","velar","nasal",1]
    ],
    vowels: [
      ["i",0,0,0],["y",0,0,1],["e",1,0,0],
      ["ə",1,1,0],["a",3,1,0],
      ["u",0,2,1],["ɤ",1,2,0],["o",1,2,1]
    ],
    diphs: ["ai","ei","au","ou","ia","ua"]
  },
  ja: {
    cons: [
      ["p","bilabial","stop",0],["b","bilabial","stop",1],["m","bilabial","nasal",1],["w","bilabial","approximant",1],
      ["t","alveolar","stop",0],["d","alveolar","stop",1],["n","alveolar","nasal",1],["s","alveolar","fricative",0],["z","alveolar","fricative",1],["ɾ","alveolar","tap",1],
      ["ɕ","postalveolar","fricative",0],["dʑ","postalveolar","affricate",1],["tɕ","postalveolar","affricate",0],
      ["j","palatal","approximant",1],["ç","palatal","fricative",0],
      ["k","velar","stop",0],["g","velar","stop",1],
      ["h","glottal","fricative",0]
    ],
    vowels: [["i",0,0,0],["e",1,0,0],["a",3,1,0],["o",1,2,1],["ɯ",0,2,0]],
    diphs: []
  },
  ar: {
    cons: [
      ["b","bilabial","stop",1],["m","bilabial","nasal",1],["w","bilabial","approximant",1],
      ["f","labiodental","fricative",0],
      ["θ","dental","fricative",0],["ð","dental","fricative",1],["ðˤ","dental","fricative",1],
      ["t","alveolar","stop",0],["tˤ","alveolar","stop",0],["d","alveolar","stop",1],["dˤ","alveolar","stop",1],["s","alveolar","fricative",0],["sˤ","alveolar","fricative",0],["z","alveolar","fricative",1],["n","alveolar","nasal",1],["l","alveolar","lateral",1],["r","alveolar","trill",1],
      ["ʃ","postalveolar","fricative",0],["dʒ","postalveolar","affricate",1],
      ["j","palatal","approximant",1],
      ["k","velar","stop",0],["x","velar","fricative",0],["ɣ","velar","fricative",1],
      ["q","uvular","stop",0],
      ["ħ","pharyngeal","fricative",0],["ʕ","pharyngeal","fricative",1],
      ["ʔ","glottal","stop",0],["h","glottal","fricative",0]
    ],
    vowels: [
      ["i",0,0,0],["iː",0,0,0],
      ["a",3,1,0],["aː",3,1,0],
      ["u",0,2,1],["uː",0,2,1]
    ],
    diphs: ["aj","aw"]
  },
  hi: {
    cons: [
      ["p","bilabial","stop",0],["pʰ","bilabial","stop",0],["b","bilabial","stop",1],["bʱ","bilabial","stop",1],["m","bilabial","nasal",1],
      ["t̪","dental","stop",0],["t̪ʰ","dental","stop",0],["d̪","dental","stop",1],["d̪ʱ","dental","stop",1],["n̪","dental","nasal",1],
      ["s","alveolar","fricative",0],["l","alveolar","lateral",1],["r","alveolar","trill",1],
      ["tʃ","postalveolar","affricate",0],["tʃʰ","postalveolar","affricate",0],["dʒ","postalveolar","affricate",1],["dʒʱ","postalveolar","affricate",1],["ʃ","postalveolar","fricative",0],
      ["ʈ","retroflex","stop",0],["ʈʰ","retroflex","stop",0],["ɖ","retroflex","stop",1],["ɖʱ","retroflex","stop",1],["ɳ","retroflex","nasal",1],["ɽ","retroflex","tap",1],["ɽʱ","retroflex","tap",1],
      ["j","palatal","approximant",1],
      ["k","velar","stop",0],["kʰ","velar","stop",0],["g","velar","stop",1],["gʱ","velar","stop",1],["ŋ","velar","nasal",1],
      ["h","glottal","fricative",1],["ɦ","glottal","fricative",1]
    ],
    vowels: [
      ["i",0,0,0],["ɪ",0,0,0],["e",1,0,0],["ɛ",2,0,0],
      ["ə",1,1,0],["a",3,1,0],
      ["u",0,2,1],["ʊ",0,2,1],["o",1,2,1],["ɔ",2,2,1]
    ],
    diphs: ["ai","au"]
  },
  fr: {
    cons: [
      ["p","bilabial","stop",0],["b","bilabial","stop",1],["m","bilabial","nasal",1],["w","bilabial","approximant",1],
      ["f","labiodental","fricative",0],["v","labiodental","fricative",1],
      ["t","alveolar","stop",0],["d","alveolar","stop",1],["s","alveolar","fricative",0],["z","alveolar","fricative",1],["n","alveolar","nasal",1],["l","alveolar","lateral",1],
      ["ʃ","postalveolar","fricative",0],["ʒ","postalveolar","fricative",1],
      ["ɲ","palatal","nasal",1],["j","palatal","approximant",1],["ɥ","palatal","approximant",1],
      ["k","velar","stop",0],["g","velar","stop",1],["ŋ","velar","nasal",1],
      ["ʁ","uvular","fricative",1]
    ],
    vowels: [
      ["i",0,0,0],["y",0,0,1],["e",1,0,0],["ø",1,0,1],["ɛ",2,0,0],["œ",2,0,1],["ɛ̃",2,0,0],["œ̃",2,0,1],
      ["a",3,1,0],["ɑ̃",3,1,0],
      ["u",0,2,1],["o",1,2,1],["ɔ",2,2,1],["ɑ",3,2,0],["ɔ̃",2,2,1]
    ],
    diphs: []
  },
  de: {
    cons: [
      ["p","bilabial","stop",0],["b","bilabial","stop",1],["m","bilabial","nasal",1],
      ["f","labiodental","fricative",0],["v","labiodental","fricative",1],["pf","labiodental","affricate",0],
      ["t","alveolar","stop",0],["d","alveolar","stop",1],["s","alveolar","fricative",0],["z","alveolar","fricative",1],["n","alveolar","nasal",1],["l","alveolar","lateral",1],["ts","alveolar","affricate",0],
      ["ʃ","postalveolar","fricative",0],["ʒ","postalveolar","fricative",1],["tʃ","postalveolar","affricate",0],
      ["ç","palatal","fricative",0],["j","palatal","approximant",1],
      ["k","velar","stop",0],["g","velar","stop",1],["x","velar","fricative",0],["ŋ","velar","nasal",1],
      ["ʁ","uvular","fricative",1],
      ["h","glottal","fricative",0]
    ],
    vowels: [
      ["i",0,0,0],["iː",0,0,0],["ɪ",0,0,0],["y",0,0,1],["yː",0,0,1],["ʏ",0,0,1],["e",1,0,0],["eː",1,0,0],["ɛ",2,0,0],["ɛː",2,0,0],["ø",1,0,1],["øː",1,0,1],["œ",2,0,1],
      ["ə",1,1,0],["ɐ",3,1,0],["a",3,1,0],["aː",3,1,0],
      ["o",1,2,1],["oː",1,2,1],["ɔ",2,2,1],["u",0,2,1],["uː",0,2,1],["ʊ",0,2,1]
    ],
    diphs: ["aɪ","aʊ","ɔʏ"]
  },
  ru: {
    cons: [
      ["p","bilabial","stop",0],["pʲ","bilabial","stop",0],["b","bilabial","stop",1],["bʲ","bilabial","stop",1],["m","bilabial","nasal",1],["mʲ","bilabial","nasal",1],
      ["f","labiodental","fricative",0],["fʲ","labiodental","fricative",0],["v","labiodental","fricative",1],["vʲ","labiodental","fricative",1],
      ["t","alveolar","stop",0],["tʲ","alveolar","stop",0],["d","alveolar","stop",1],["dʲ","alveolar","stop",1],["s","alveolar","fricative",0],["sʲ","alveolar","fricative",0],["z","alveolar","fricative",1],["zʲ","alveolar","fricative",1],["n","alveolar","nasal",1],["nʲ","alveolar","nasal",1],["l","alveolar","lateral",1],["lʲ","alveolar","lateral",1],["r","alveolar","trill",1],["rʲ","alveolar","trill",1],["ts","alveolar","affricate",0],
      ["ʂ","postalveolar","fricative",0],["ʐ","postalveolar","fricative",1],["tɕ","postalveolar","affricate",0],["ɕː","postalveolar","fricative",0],
      ["j","palatal","approximant",1],
      ["k","velar","stop",0],["kʲ","velar","stop",0],["g","velar","stop",1],["gʲ","velar","stop",1],["x","velar","fricative",0],["xʲ","velar","fricative",0]
    ],
    vowels: [
      ["i",0,0,0],["e",1,0,0],
      ["ɨ",0,1,0],["a",3,1,0],
      ["u",0,2,1],["o",1,2,1]
    ],
    diphs: []
  },
  pt: {
    cons: [
      ["p","bilabial","stop",0],["b","bilabial","stop",1],["m","bilabial","nasal",1],["w","bilabial","approximant",1],
      ["f","labiodental","fricative",0],["v","labiodental","fricative",1],
      ["t","dental","stop",0],["d","dental","stop",1],
      ["s","alveolar","fricative",0],["z","alveolar","fricative",1],["n","alveolar","nasal",1],["l","alveolar","lateral",1],["ɾ","alveolar","tap",1],
      ["ʃ","postalveolar","fricative",0],["ʒ","postalveolar","fricative",1],
      ["ɲ","palatal","nasal",1],["ʎ","palatal","lateral",1],["j","palatal","approximant",1],
      ["k","velar","stop",0],["g","velar","stop",1],
      ["ʁ","uvular","fricative",1]
    ],
    vowels: [
      ["i",0,0,0],["e",1,0,0],["ɛ",2,0,0],["ĩ",0,0,0],["ẽ",1,0,0],
      ["ɨ",0,1,0],["ɐ",3,1,0],["ɐ̃",3,1,0],
      ["u",0,2,1],["o",1,2,1],["ɔ",2,2,1],["ũ",0,2,1],["õ",1,2,1]
    ],
    diphs: ["aj","ej","oj","aw","ew","ow","ɐ̃j","õj","ũj","ɐ̃w"]
  },
  ko: {
    cons: [
      ["p","bilabial","stop",0],["pʰ","bilabial","stop",0],["p͈","bilabial","stop",0],["m","bilabial","nasal",1],
      ["t","alveolar","stop",0],["tʰ","alveolar","stop",0],["t͈","alveolar","stop",0],["s","alveolar","fricative",0],["s͈","alveolar","fricative",0],["n","alveolar","nasal",1],["l","alveolar","lateral",1],
      ["tɕ","palatal","affricate",0],["tɕʰ","palatal","affricate",0],["t͈ɕ","palatal","affricate",0],["j","palatal","approximant",1],
      ["k","velar","stop",0],["kʰ","velar","stop",0],["k͈","velar","stop",0],["ŋ","velar","nasal",1],
      ["h","glottal","fricative",0]
    ],
    vowels: [
      ["i",0,0,0],["e",1,0,0],["ɛ",2,0,0],
      ["a",3,1,0],["ʌ",2,1,0],["ɯ",0,1,0],
      ["o",1,2,1],["u",0,2,1]
    ],
    diphs: ["ja","jʌ","jo","ju","wa","wʌ","we","wi"]
  },
  tr: {
    cons: [
      ["p","bilabial","stop",0],["b","bilabial","stop",1],["m","bilabial","nasal",1],
      ["f","labiodental","fricative",0],["v","labiodental","fricative",1],
      ["t","alveolar","stop",0],["d","alveolar","stop",1],["s","alveolar","fricative",0],["z","alveolar","fricative",1],["n","alveolar","nasal",1],["l","alveolar","lateral",1],["ɾ","alveolar","tap",1],
      ["ʃ","postalveolar","fricative",0],["ʒ","postalveolar","fricative",1],["tʃ","postalveolar","affricate",0],["dʒ","postalveolar","affricate",1],
      ["c","palatal","stop",0],["ɟ","palatal","stop",1],["j","palatal","approximant",1],
      ["k","velar","stop",0],["g","velar","stop",1],
      ["h","glottal","fricative",0]
    ],
    vowels: [
      ["i",0,0,0],["y",0,0,1],["e",1,0,0],["œ",2,0,1],
      ["ɯ",0,1,0],["a",3,1,0],
      ["u",0,2,1],["o",1,2,1]
    ],
    diphs: []
  },
  sw: {
    cons: [
      ["p","bilabial","stop",0],["b","bilabial","stop",1],["ɓ","bilabial","stop",1],["m","bilabial","nasal",1],["w","bilabial","approximant",1],
      ["f","labiodental","fricative",0],["v","labiodental","fricative",1],
      ["θ","dental","fricative",0],["ð","dental","fricative",1],
      ["t","alveolar","stop",0],["d","alveolar","stop",1],["ɗ","alveolar","stop",1],["s","alveolar","fricative",0],["z","alveolar","fricative",1],["n","alveolar","nasal",1],["l","alveolar","lateral",1],["r","alveolar","trill",1],
      ["ʃ","postalveolar","fricative",0],["ʒ","postalveolar","fricative",1],["tʃ","postalveolar","affricate",0],["dʒ","postalveolar","affricate",1],
      ["ɲ","palatal","nasal",1],["ʄ","palatal","stop",1],["j","palatal","approximant",1],
      ["k","velar","stop",0],["g","velar","stop",1],["ɠ","velar","stop",1],["x","velar","fricative",0],["ɣ","velar","fricative",1],["ŋ","velar","nasal",1],
      ["h","glottal","fricative",0]
    ],
    vowels: [["i",0,0,0],["e",1,0,0],["a",3,1,0],["u",0,2,1],["o",1,2,1]],
    diphs: []
  },
  vi: {
    cons: [
      ["p","bilabial","stop",0],["b","bilabial","stop",1],["ɓ","bilabial","stop",1],["m","bilabial","nasal",1],
      ["f","labiodental","fricative",0],["v","labiodental","fricative",1],
      ["t","alveolar","stop",0],["tʰ","alveolar","stop",0],["d","alveolar","stop",1],["ɗ","alveolar","stop",1],["s","alveolar","fricative",0],["z","alveolar","fricative",1],["n","alveolar","nasal",1],["l","alveolar","lateral",1],
      ["ʂ","retroflex","fricative",0],["ʐ","retroflex","fricative",1],
      ["c","palatal","stop",0],["ɲ","palatal","nasal",1],["j","palatal","approximant",1],
      ["k","velar","stop",0],["ŋ","velar","nasal",1],["x","velar","fricative",0],["ɣ","velar","fricative",1],["w","velar","approximant",1],
      ["ʔ","glottal","stop",0],["h","glottal","fricative",0]
    ],
    vowels: [
      ["i",0,0,0],["e",1,0,0],["ɛ",2,0,0],
      ["ɨ",0,1,0],["ə",1,1,0],["ɐ",3,1,0],
      ["u",0,2,1],["o",1,2,1],["ɔ",2,2,1],["ɤ",1,2,0],["a",3,2,0]
    ],
    diphs: ["iə","uə","ɨə","eo","ia","ai"]
  },
  haw: {
    cons: [
      ["p","bilabial","stop",0],["m","bilabial","nasal",1],["w","bilabial","approximant",1],
      ["n","alveolar","nasal",1],["l","alveolar","lateral",1],
      ["k","velar","stop",0],
      ["ʔ","glottal","stop",0],["h","glottal","fricative",0]
    ],
    vowels: [["i",0,0,0],["e",1,0,0],["a",3,1,0],["u",0,2,1],["o",1,2,1]],
    diphs: ["ai","ae","ao","au","ei","eu","oi","ou","iu"]
  }
};

// Regenerate LANG_INVENTORIES counts/vectors from LANG_PHONEMES so the
// aggregate data consumed by Stats stays in sync with the explicit lists.
(() => {
  for (const code in LANG_PHONEMES) {
    const data = LANG_PHONEMES[code];
    const counts = {};
    for (const p of LANG_PLACE_ORDER) counts[p] = 0;
    for (const c of data.cons) counts[c[1]] = (counts[c[1]] || 0) + 1;
    for (const v of data.vowels) {
      const bucket = v[2] === 0 ? "front-vowel" : v[2] === 1 ? "central-vowel" : "back-vowel";
      counts[bucket]++;
    }
    counts["diphthong"] = (data.diphs || []).length;
    if (!LANG_INVENTORIES[code]) continue;
    LANG_INVENTORIES[code].counts = counts;
    let total = 0;
    for (const p of LANG_PLACE_ORDER) total += counts[p];
    LANG_INVENTORIES[code].total = total;
    LANG_INVENTORIES[code].vector = LANG_PLACE_ORDER.map(p => total > 0 ? counts[p]/total : 0);
  }
})();

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
