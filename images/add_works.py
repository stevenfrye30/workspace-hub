#!/usr/bin/env python3
"""Append Louvre works to data/*.json, using local image paths under media/."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

NEW_WORKS = {
    "europe": [
        {
            "title": "Mona Lisa (La Joconde)",
            "artist": "Leonardo da Vinci",
            "meta": "c. 1503\u20131519 \u00b7 Oil on poplar \u00b7 Salle des \u00c9tats",
            "desc": "Probably a portrait of Lisa Gherardini, wife of a Florentine merchant. Leonardo carried it with him for years, reworking it endlessly, and it never left his side until his death in France. Her fame owes as much to theft as to genius: when Vincenzo Peruggia stole her in 1911 and kept her in a Paris apartment for two years, the empty wall drew larger crowds than the painting ever had.",
            "image": "media/mona_lisa.jpg",
            "year": 1510,
        },
        {
            "title": "Liberty Leading the People",
            "artist": "Eug\u00e8ne Delacroix",
            "meta": "1830 \u00b7 Oil on canvas \u00b7 Denon Wing",
            "desc": "Painted in the aftermath of the July Revolution that overthrew Charles X. Liberty \u2014 bare-breasted, tricolor raised, bayonet in hand \u2014 strides over the barricades and the dead. The man in the top hat beside her is often read as a self-portrait. The boy with pistols would later inspire Gavroche in Hugo's Les Mis\u00e9rables.",
            "image": "media/liberty.jpg",
            "year": 1830,
        },
        {
            "title": "The Raft of the Medusa",
            "artist": "Th\u00e9odore G\u00e9ricault",
            "meta": "1818\u20131819 \u00b7 Oil on canvas \u00b7 Denon Wing",
            "desc": "A real and recent disaster: the French frigate M\u00e9duse ran aground off Senegal in 1816. The captain and officers took the lifeboats; 147 men were cut loose on a raft. Fifteen survived, after mutiny, thirst, and cannibalism. G\u00e9ricault interviewed survivors, visited morgues to study dead flesh, and built a scale model of the raft in his studio. The scandal reached the throne \u2014 the captain had been appointed through political favor.",
            "image": "media/medusa.jpg",
            "year": 1818,
        },
        {
            "title": "The Coronation of Napoleon",
            "artist": "Jacques-Louis David",
            "meta": "1805\u20131807 \u00b7 Oil on canvas \u00b7 Denon Wing",
            "desc": "Nearly 10 meters wide. Napoleon, having just placed the crown on his own head, is shown about to crown Jos\u00e9phine. The Pope, summoned from Rome, sits behind \u2014 reduced to witness. David inserted Napoleon's mother into the grandstand though she refused to attend. Painters, like emperors, revise history.",
            "image": "media/coronation.jpg",
            "year": 1806,
        },
        {
            "title": "The Wedding at Cana",
            "artist": "Paolo Veronese",
            "meta": "1563 \u00b7 Oil on canvas \u00b7 Salle des \u00c9tats",
            "desc": "The largest painting in the Louvre, at nearly 70 square meters. Commissioned for the refectory of a Benedictine monastery in Venice. Napoleon's troops took it in 1797 and cut it in half to transport it. It hangs directly across from the Mona Lisa \u2014 and is almost entirely ignored by the crowds facing the other way.",
            "image": "media/cana.jpg",
            "year": 1563,
        },
        {
            "title": "The Lacemaker",
            "artist": "Johannes Vermeer",
            "meta": "c. 1669\u20131670 \u00b7 Oil on canvas on panel \u00b7 Richelieu Wing",
            "desc": "One of Vermeer's smallest works \u2014 only about 24 centimeters tall. A young woman bends over her bobbins with the intense near-vision of close handwork. Salvador Dal\u00ed obsessed over it. He was once allowed to set up an easel in the Louvre to copy it, and produced a small canvas covered in rhinoceros horns instead.",
            "image": "media/lacemaker.jpg",
            "year": 1669,
        },
        {
            "title": "La Grande Odalisque",
            "artist": "Jean-Auguste-Dominique Ingres",
            "meta": "1814 \u00b7 Oil on canvas \u00b7 Denon Wing",
            "desc": "Commissioned by Napoleon's sister, Caroline Murat, Queen of Naples. Ingres gave his odalisque two or three extra vertebrae \u2014 anatomically impossible, visually ideal. Critics howled; the distortion is now the point.",
            "image": "media/odalisque.jpg",
            "year": 1814,
        },
        {
            "title": "The Cheat with the Ace of Diamonds",
            "artist": "Georges de La Tour",
            "meta": "c. 1636\u20131638 \u00b7 Oil on canvas \u00b7 Sully Wing",
            "desc": "Four figures, four glances, one con. A na\u00efve young nobleman is about to lose his fortune to the cheat on the left, who has pulled an ace from his belt. The courtesan and her servant are in on it; only the young man isn't looking at anyone.",
            "image": "media/cheat.jpg",
            "year": 1637,
        },
        {
            "title": "Psyche Revived by Cupid's Kiss",
            "artist": "Antonio Canova",
            "meta": "1787\u20131793 \u00b7 Marble \u00b7 Denon Wing",
            "desc": "Cupid bends over Psyche, who has fallen into a death-like sleep. Her arms reach up to draw him in. The composition forms a perfect X \u2014 walk around it and the two bodies rotate through a dance.",
            "image": "media/psyche.jpg",
            "year": 1790,
        },
        {
            "title": "The Dying Slave",
            "artist": "Michelangelo Buonarroti",
            "meta": "c. 1513\u20131515 \u00b7 Marble \u00b7 Denon Wing",
            "desc": "Intended for the tomb of Pope Julius II, a project that consumed Michelangelo for forty years and was never finished as planned. The figure is not dying but \u2014 perhaps \u2014 falling asleep, or surrendering to ecstasy. Michelangelo left the back deliberately rough.",
            "image": "media/dying_slave.jpg",
            "year": 1514,
        },
        {
            "title": "The Marly Horses",
            "artist": "Guillaume Coustou",
            "meta": "1739\u20131745 \u00b7 Marble \u00b7 Cour Marly",
            "desc": "Commissioned for the royal estate of Marly, where Louis XV wanted rearing horses at the entrance to his watering pond. Each is over 3.5 meters tall. They stood outdoors for nearly two centuries before being brought inside in 1984.",
            "image": "media/marly_horses.jpg",
            "year": 1742,
        },
        {
            "title": "Crown of Louis XV",
            "meta": "1722 \u00b7 Silver gilt, originally set with the crown jewels \u00b7 Galerie d'Apollon",
            "desc": "Made for the coronation of the twelve-year-old Louis XV at Reims. The original diamonds \u2014 including the R\u00e9gent, now displayed nearby \u2014 were removed after the ceremony and replaced with paste copies, which are what you see today.",
            "image": "media/crown_louis.jpg",
            "year": 1722,
        },
        {
            "title": "The Napoleon III Apartments",
            "meta": "1861 \u00b7 Richelieu Wing",
            "desc": "Not a single object but an entire suite of state rooms \u2014 crimson silk, gilded stucco, chandeliers heavy enough to frighten the ceiling. These were the ceremonial apartments of the Minister of State under the Second Empire. Walk in and the museum disappears.",
            "image": "media/napoleon_apartments.jpg",
            "year": 1861,
        },
        {
            "title": "The R\u00e9gent Diamond",
            "meta": "140.64 carats \u00b7 Galerie d'Apollon",
            "desc": "Found in India around 1698, smuggled by a slave who hid it in a wound in his leg, sold to Thomas Pitt (grandfather of William Pitt the Elder), and eventually bought by the French crown. Worn by Louis XV, Louis XVI, and set into Napoleon's sword. Still considered the most perfectly cut historical diamond in the world.",
            "image": "media/regent_diamond.jpg",
            "year": 1698,
        },
        {
            "title": "Drawings by Leonardo da Vinci",
            "meta": "c. 1480\u20131510 \u00b7 Chalk, ink, and silverpoint on paper",
            "desc": "The Louvre holds over twenty sheets by Leonardo \u2014 studies of hands, horses, the tilt of a woman's head, the flow of water. A single silverpoint line, set down and never corrected.",
            "image": "media/leonardo_drawing.jpg",
            "year": 1495,
        },
        {
            "title": "Knight, Death and the Devil",
            "artist": "Albrecht D\u00fcrer",
            "meta": "1513 \u00b7 Engraving",
            "desc": "One of D\u00fcrer's three \"Master Engravings.\" A Christian knight rides impassively through a desolate gorge, unmoved by the hourglass-bearing Death beside him or the goat-headed Devil behind. The technical summit of Renaissance printmaking.",
            "image": "media/durer_knight.jpg",
            "year": 1513,
        },
        {
            "title": "Self-Portraits by Rembrandt",
            "meta": "17th century \u00b7 Etching",
            "desc": "Rembrandt made over forty etched self-portraits across his lifetime. The Louvre holds a remarkable set. In ink on paper he is looser and more playful than in his painted selves \u2014 pulling faces, squinting, trying on hats.",
            "image": "media/rembrandt_self.jpg",
            "year": 1650,
        },
    ],
    "egypt-nubia": [
        {
            "title": "The Seated Scribe",
            "meta": "c. 2600\u20132350 BCE \u00b7 Painted limestone, inlaid eyes \u00b7 Sully Wing",
            "desc": "Roughly 4,500 years old. His eyes \u2014 rock crystal set in copper \u2014 are what stop you: unnervingly alive, tracking you as you move. His name and title are lost. He holds a papyrus roll, alert, waiting for dictation to begin.",
            "image": "media/scribe.jpg",
            "year": -2475,
        },
        {
            "title": "Great Sphinx of Tanis",
            "meta": "c. 2600 BCE \u00b7 Pink granite \u00b7 Sully Wing",
            "desc": "Discovered in 1825 in the ruins of the temple of Amun at Tanis. Over 4,500 years old and carved from a single block of granite. The names of at least four pharaohs \u2014 each claiming it for themselves \u2014 are carved on it.",
            "image": "media/sphinx.jpg",
            "year": -2600,
        },
        {
            "title": "Reliefs from the Tomb of Seti I",
            "meta": "c. 1290 BCE \u00b7 Painted limestone \u00b7 Sully Wing",
            "desc": "The goddess Hathor welcomes Seti I into the afterlife. Cut from the walls of KV17 in the Valley of the Kings in the 19th century \u2014 a practice we now consider vandalism, but which saved this relief from the flooding that ravaged the tomb.",
            "image": "media/seti_relief.jpg",
            "year": -1290,
        },
        {
            "title": "Stele of King Djet (The Serpent King)",
            "meta": "c. 3000 BCE \u00b7 Limestone \u00b7 Sully Wing",
            "desc": "Over 5,000 years old \u2014 from the very dawn of writing. A serpent (the king's name) stands above the serekh, the palace fa\u00e7ade, topped by Horus the falcon. This is what Egyptian writing looked like before it became hieroglyphs.",
            "image": "media/stele_djet.jpg",
            "year": -3000,
        },
    ],
    "mediterranean": [
        {
            "title": "Winged Victory of Samothrace",
            "meta": "c. 200\u2013190 BCE \u00b7 Parian marble \u00b7 Daru Staircase",
            "desc": "She stands at the top of the grand Daru staircase, wings flung back, drapery soaked and clinging as if she has just alighted on the prow of a ship. The ship itself is carved too \u2014 she came mounted on a stone warship in a pool of water on the sanctuary of Samothrace. Discovered in 1863 in more than 100 fragments. Her head and arms have never been found.",
            "image": "media/winged_victory.jpg",
            "year": -195,
        },
        {
            "title": "Venus de Milo",
            "meta": "c. 150\u2013125 BCE \u00b7 Parian marble \u00b7 Sully Wing",
            "desc": "Found in 1820 by a peasant on the Aegean island of Milos. France acquired her quickly \u2014 and when Louis XVIII presented her to the Louvre, the fact that her arms were missing was treated as accidental rather than a flaw. She was almost certainly holding an apple, referencing the Judgment of Paris. Her missing arms let every viewer imagine her gesture.",
            "image": "media/venus_milo.jpg",
            "year": -137,
        },
        {
            "title": "Borghese Gladiator",
            "artist": "Agasias of Ephesus",
            "meta": "c. 100 BCE \u00b7 Marble \u00b7 Sully Wing",
            "desc": "Not actually a gladiator \u2014 a warrior fighting a mounted opponent, arm raised with a (lost) shield. A tour de force of anatomical study; every muscle is taut with the effort of the moment before impact.",
            "image": "media/gladiator.jpg",
            "year": -100,
        },
        {
            "title": "Sleeping Hermaphroditus",
            "meta": "Roman copy of a Greek original \u00b7 2nd century CE \u00b7 Sully Wing",
            "desc": "From one angle, a sleeping woman. Walk around to the other side: the body is both. The mattress beneath \u2014 realistic enough that you want to touch it \u2014 was carved by Bernini in 1619 when the statue was restored.",
            "image": "media/hermaphroditus.jpg",
            "year": 150,
        },
        {
            "title": "Sarcophagus of the Spouses",
            "meta": "c. 520 BCE \u00b7 Etruscan terracotta \u00b7 Denon Wing",
            "desc": "A husband and wife recline together on a banquet couch for eternity. Painted terracotta, made in four pieces. The Etruscans, unlike the Greeks and Romans, gave women equal place at the feast \u2014 and in the tomb.",
            "image": "media/spouses.jpg",
            "year": -520,
        },
    ],
    "mesopotamia-persia": [
        {
            "title": "Code of Hammurabi",
            "meta": "c. 1754 BCE \u00b7 Basalt stele \u00b7 Richelieu Wing",
            "desc": "A pillar of black basalt, 2.25 meters tall, covered in cuneiform. At the top: King Hammurabi of Babylon receives the laws from the sun god Shamash. Below: 282 laws \u2014 among the oldest written in the world. \"If a man puts out the eye of another man, his eye shall be put out.\" The logic of lex talionis, set in stone before Moses was born.",
            "image": "media/hammurabi.jpg",
            "year": -1754,
        },
        {
            "title": "Lamassu of Khorsabad",
            "meta": "c. 713\u2013706 BCE \u00b7 Gypsum alabaster \u00b7 Richelieu Wing",
            "desc": "Human-headed winged bulls, each over 4 meters tall. They guarded the gates of Sargon II's palace in what is now northern Iraq. Carved with five legs so that they appear to be standing still when seen from the front, and striding forward when seen from the side.",
            "image": "media/lamassu.jpg",
            "year": -709,
        },
        {
            "title": "Frieze of the Archers of Darius I",
            "meta": "c. 510 BCE \u00b7 Glazed brick \u00b7 Richelieu Wing",
            "desc": "From the palace of Darius the Great at Susa. A procession of the king's elite guard \u2014 the \"Immortals\" \u2014 in brilliantly colored glazed brick. Each carries a spear, bow, and quiver; each face is subtly different from the next.",
            "image": "media/archers.jpg",
            "year": -510,
        },
    ],
    "islamic-world": [
        {
            "title": "Pyxis of al-Mughira",
            "meta": "968 CE \u00b7 Carved ivory \u00b7 Cour Visconti",
            "desc": "A small ivory box made in C\u00f3rdoba for a teenage Umayyad prince. Every surface is carved with figures \u2014 musicians, lions, lovers, a man stealing eggs from an eagle's nest. The inscriptions include barely-veiled warnings about the instability of royal succession. Al-Mughira was executed by strangulation eight years later.",
            "image": "media/pyxis.jpg",
            "year": 968,
        },
        {
            "title": "Baptistery of Saint Louis",
            "meta": "c. 1320\u20131340 \u00b7 Hammered brass inlaid with silver and gold \u00b7 Cour Visconti",
            "desc": "A Mamluk basin made in Egypt or Syria, covered in inlaid scenes of hunters, courtiers, and animals. At some point it entered the French royal treasury, and by tradition \u2014 probably invented \u2014 it was used for the baptism of royal children, including the future Louis XIII.",
            "image": "media/baptistery.jpg",
            "year": 1330,
        },
    ],
}


def main():
    added_total = 0
    for slug, new_works in NEW_WORKS.items():
        path = DATA / f"{slug}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        existing = {w["title"] for w in data["works"]}
        added = 0
        for w in new_works:
            if w["title"] in existing:
                print(f"  skip (already present): {slug} / {w['title']}")
                continue
            data["works"].append(w)
            added += 1
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  {slug}: +{added} (now {len(data['works'])})")
        added_total += added
    print(f"\nAdded {added_total} works.")


if __name__ == "__main__":
    main()
