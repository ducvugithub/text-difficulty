# cognitive-diff — processing-load signals

How hard the text is to hold in mind, beyond words and grammar. One script per signal in src/, outputs in outputs/.
Candidates:
- Discourse: connective density, coreference chain length / distance, referential cohesion (lemma overlap between sentences)
- Information density: propositions per sentence, lexical density (content words / tokens), TTR / MTLD
- Working memory: dependency distance (avg / max), embedding depth, center-embedding count
- Surprisal: LM per-token surprisal (mean / max / variance), sentence-length variance
- Background knowledge: named-entity density, abstract-word ratio, domain-specific terms
- Text-level: length, paragraph structure, genre/source
