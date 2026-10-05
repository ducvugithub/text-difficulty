# 03 merge lemmas
- surface forms kept: 20,615,619 (total count 2,751,341,018) -> 6,459,885 lemmas (03_lemmas.tsv)
- ambiguous forms count in full for every distinct lemma
- total count = the `freq` counts of the rows added up, i.e. how often those forms appear in the corpus (not the number of different forms)

Columns of 03_lemmas.tsv: `lemma` dictionary form; `class` Voikko word class; `stems` stems it is built from (`+`-joined); `n_forms` inflected forms merged into the lemma; `freq` all those forms' counts added up.

| dropped | rows | total count | most frequent examples |
|---|---:|---:|---|
| unrecognised | 15,271,091 | 182,345,417 | the (1486396), of (1313583), mun (924937), and (826939), The (749631), mä (674945), in (668353), to (619958), jne (531981), oon (466089), quote (457654), oo (455008), ku (450596), mut (421618), mulla (420907) |
| name | 206,005 | 51,794,917 | Helsingin (799338), Euroopan (777575), Tampereen (309632), Helsingissä (283975), Jeesus (282515), Jeesuksen (249306), Helsinki (216520), Mikko (201688), Antti (200923), Pekka (197097), Oulun (185410), Timo (180753), Euroopassa (179838), Juha (174440), Windows (171800) |
| abbrev | 4,224 | 11,196,553 | klo (1536702), a (757761), n (751199), Oy (474977), I (436808), A (300005), km (271834), s (267247), cm (238390), x (234685), GMT (177033), mm (157384), ry (149120), t (142132), kg (142120) |

## English check on unrecognised forms
- unrecognised forms found in /usr/share/dict/words (len>=3): 147,160 rows, total count 46,685,723
- English words are already removed by Voikko recognition; recognised English-looking lemmas (sauna, radio...) are real Finnish loanwords and are deliberately kept.
- review 03_unrecognised.tsv (column 3 = 'en' if in the English dictionary) for Finnish words Voikko misses.
