# Other word-difficulty signals (freq is not everything)

Candidates, one script each in src/, output a per-lemma table in outputs/:
- Word length (chars, syllables) and morphological complexity (n morphemes, compound yes/no, n components)
- Derivational depth (-llinen, -uus, -minen ...) and inflectional paradigm rarity (existing Noun-Paradigm-* features)
- Inflected-form frequency: rarity of the specific case/form, not just the lemma (e.g. rare plural cases)
- Dispersion / document frequency (appears in many sources vs one) — frequency from one corpus can be skewed
- Domain / register: formal, dialect, slang, archaic (from source/origin metadata)
- Abstractness / concreteness, imageability (translate or use Finnish norms if available)
- Polysemy (n senses in FinnWordNet) and semantic specificity (WordNet depth)
- Cognate / loanword status (borrowed words can be easy for learners, so use as a feature, not only a filter)
- Learner-list level: CEFR-tagged vocab (Kelly-style / Finnish YKI lists), first-seen level in graded readers
- Subword stats: BERT/WordPiece fragmentation count, character n-gram LM perplexity
- Contextual surprisal: LM probability of the word in context
