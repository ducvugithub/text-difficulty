# 04 compound stems
- lemmas: 6,459,885; compounds (>=2 stems): 6,126,323
- compounds whose freq changed: 5,775,354; with a stem missing standalone (own freq caps them): 350,873

Columns of `04_lemmas_stem.tsv`:
- `lemma`
- `class`: Voikko word class
- `n_stems`: number of stems (2 or more = compound)
- `n_forms`: inflected forms merged into the lemma
- `freq`: all its forms added up (from step 3)
- `rarest_stem_freq`: the `freq` of the compound's rarest stem (= `freq` for non-compounds)

`04_stems.tsv` (26,211 distinct lowercase stems), columns:
- `stem`
- `freq`: full count = the `freq` of every lemma containing the stem, added up
- `standalone_freq`: the `freq` of the lemma equal to the stem, empty if it never occurs as its own word
- `n_lemmas`: lemmas containing it
- `n_compounds`: compounds containing it

`04_compound_stems.tsv`, one row per compound x stem, to audit the rarest-stem rule, columns:
- `compound`
- `stem`
- `stem_freq`: that stem's standalone `freq`


## Largest changes (freq -> rarest_stem_freq)
| lemma | freq | rarest_stem_freq |
|---|---:|---:|
| voimis-olla | 1 | 19,651,000 |
| parempivoivainen | 1 | 16,197,949 |
| hyvänhyvä | 3 | 16,197,949 |
| olevanhyvä | 7 | 16,197,949 |
| hyvänvointinen | 14 | 16,197,949 |
| hyvänvoiva | 16 | 16,197,949 |
| hyvävointisuus | 18 | 16,197,949 |
| hyvänhyvyys | 24 | 16,197,949 |
| parempivointinen | 106 | 16,197,949 |
| hyvävointinen | 745 | 16,197,949 |
| voivoivoivoivoivoivoivoivoivoi | 1 | 14,290,433 |
| voivoivoivoivoivoivoi | 1 | 14,290,433 |
| voioleva | 1 | 14,290,433 |
| voinhyvä | 1 | 14,290,433 |
| voimaksioleva | 1 | 14,290,433 |
| olemisenvoimainen | 1 | 14,290,433 |
| voivoiva | 2 | 14,290,433 |
| voivoivoivoivoivoi | 3 | 14,290,433 |
| ylivoivoimainen | 3 | 14,290,433 |
| voivoinen | 5 | 14,290,433 |
| voivoivoivoivoi | 8 | 14,290,433 |
| epävoivoinen | 9 | 14,290,433 |
| voivoivoivoi | 64 | 14,290,433 |
| voivoivoi | 338 | 14,290,433 |
| voivoi | 3,258 | 14,290,433 |
| voisaava | 1 | 12,707,829 |
| voisaatava | 4 | 12,707,829 |
| ulossaantiaika | 1 | 12,236,293 |
| nykyajanaika | 1 | 12,236,293 |
| keskiaika-aikainen | 1 | 12,236,293 |
| ajansaatava | 1 | 12,236,293 |
| ajanoltu | 1 | 12,236,293 |
| ajanollut | 1 | 12,236,293 |
| ajanhyvä | 1 | 12,236,293 |
| ajanaikainen | 1 | 12,236,293 |
| ajallisuudenaikainen | 1 | 12,236,293 |
| ajallisolevaisuus | 1 | 12,236,293 |
| aikasaava | 1 | 12,236,293 |
| aikasaama | 1 | 12,236,293 |
| aika-ajattomuus | 1 | 12,236,293 |
