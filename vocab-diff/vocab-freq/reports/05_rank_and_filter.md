# 05 rank and filter
- English-looking rule: edit score / longer word length x 100 <= 35 (stems of 3+ characters), or the etymology says `bor:en`; not tagged when the etymology says inherited from Proto-Finnic / Uralic

Stems:

| step | stems |
|---|---:|
| all lowercase stems | 26,211 |
| found in the dictionary (Wiktionary) | 24,337 (1,874 not found: cannot be judged, they stay) |
| with an English translation | 19,145 (the others cannot be judged, they stay) |
| tagged as English-looking | 5,507 (5,415 by edit score, 92 only by etymology `bor:en`) |
| not tagged because the etymology says native | 13 |
| **in the final list** (`05_stem_freq.tsv`) | **20,704** |

Lemmas (a lemma is removed when all of its stems are tagged):

| step | lemmas |
|---|---:|
| before | 6,459,885 |
| removed as English-looking | 176,702 (3.35% of all lemma counts) |
| removed by --min-freq 0 | 0 |
| **in the final list** (`05_lemma_freq.tsv`, sorted by freq) | **6,283,183** |

Columns of `05_lemma_freq.tsv`:
- `rank`: position (1 = most frequent)
- `lemma`
- `class`: Voikko word class
- `n_stems`: number of stems
- `n_forms`: forms merged into the lemma
- `freq`: all forms added up

Columns of `05_stem_freq.tsv`:
- `rank`: position by `freq`
- `stem`
- `freq`: full count (the `freq` of every lemma containing the stem, added up)
- `standalone_freq`: the lemma frequency of the stem as its own word (empty if it never occurs alone)
- `n_lemmas`: lemmas containing it
- `n_compounds`: compounds containing it

Columns of `05_stem_borrowing.tsv` (stems with an English gloss, plus tagged ones; tagged stems first, most frequent first):
- `stem`
- `freq`: full count of the stem
- `english`: closest English translation of the stem's first meaning
- `edit_score`: weighted edit distance
- `norm`: edit score / longer word length x 100
- `borrowed`: 1 = tagged
- `english_from`: `translation` (first meaning) or `etymology` (the English word the stem was borrowed from, for stems tagged only by `bor:en`)
- `reason`: `edit score`; `bor:en` (the etymology says borrowed from English); `native etymology` (a rule fired, but the stem is inherited from Proto-Finnic, so not tagged)
- `etymology`: Wiktionary tags (`bor:sv` borrowed from Swedish, `der:la` derived from Latin, `inh:urj-fin-pro` inherited from Proto-Finnic)

## Calibration: the team sheet pairs (tagged when norm <= 35)
| Finnish | English | sheet edit score | our edit score | sheet norm | our norm | tagged |
|---|---|---:|---:|---:|---:|---|
| banana | banana | 0 | 0.0 | 0 | 0.0 | yes |
| presidentti | president | 0.4 | 0.4 | 3.6 | 3.6 | yes |
| vitamiini | vitamin | 0.4 | 0.4 | 4.4 | 4.4 | yes |
| fysiikka | physics | 0.4 | 0.2 | 5 | 2.5 | yes |
| koreografia | choreography | 0.6 | 0.6 | 5.5 | 5.0 | yes |
| psykologia | psychology | 0.4 | 0.4 | 4 | 4.0 | yes |
| konferenssi | conference | 0.6 | 0.6 | 5.5 | 5.5 | yes |
| meloni | melon | 0.2 | 0.2 | 3.3 | 3.3 | yes |
| tee | tea | 1 | 1.0 | 33.3 | 33.3 | yes |
| bussi | bus | 0.4 | 0.4 | 8 | 8.0 | yes |
| kahvi | coffee | 3.4 | 3.6 | 68 | 60.0 | no |
| matematiikka | mathematics | 0.4 | 0.2 | 3.3 | 1.7 | yes |
| strategia | strategy | 0.2 | 0.2 | 2.2 | 2.2 | yes |
| demokratia | democracy | 1.4 | 1.4 | 14 | 14.0 | yes |
| sohva | sofa | 0.2 | 0.2 | 4 | 4.0 | yes |
| innovaatio | innovation | 1.2 | 1.2 | 12 | 12.0 | yes |
| metalli | metal | 2 | 0.4 | 28.6 | 5.7 | yes |
| linkki | link | 0.4 | 0.4 | 6.7 | 6.7 | yes |
| flunssa | flu | 4 | 4.0 | 57.1 | 57.1 | no |
| flunssa | influenza | 3.2 | 3.2 | 35.6 | 35.6 | no |
| moottori | motor | 0.6 | 0.6 | 7.5 | 7.5 | yes |
| motivoida | motivate | 3.2 | 3.2 | 35.6 | 35.6 | no |
| rekisteröidä | register | 0.4 | 0.4 | 3.3 | 3.3 | yes |
| tsekata | check | 1.6 | 1.6 | 22.9 | 22.9 | yes |
| tatti | bolete | 6 | 4.2 | 120 | 70.0 | no |
| käsi | hand | 4 | 4.0 | 100 | 100.0 | no |
| haluta | want | 5 | 4.0 | 83.3 | 66.7 | no |
| mennä | go | 5 | 5.0 | 100 | 100.0 | no |
| tutkimus | research | 8 | 7.2 | 100 | 90.0 | no |
| jalka | leg | 4 | 4.0 | 80 | 80.0 | no |
| haaste | challenge | 7 | 6.0 | 77.8 | 66.7 | no |
| neuvosto | council | 7 | 6.2 | 87.5 | 77.5 | no |
| siellä | there | 5 | 5.0 | 83.3 | 83.3 | no |
| tieto | data | 3.2 | 4.0 | 64 | 80.0 | no |
| sivu | side | 2 | 2.0 | 50 | 50.0 | no |

## Most frequent removed lemmas

esimerkki (2,982,205), tee (2,298,364), pari (2,297,006), euro (1,634,010), blogi (1,178,205), prosentti (1,091,613), kommentti (1,042,042), minuutti (899,102), merkittävä (865,887), hotelli (844,590), normaali (757,142), musiikki (729,646), merkki (708,442), historia (683,274), idea (667,838), kurssi (649,226), numero (627,994), artikkeli (613,786), media (567,580), projekti (558,147), energia (530,833), poliisi (520,748), aktiivinen (516,997), kulttuuri (513,042), materiaali (504,378), versio (490,419), metri (489,600), video (487,188), netti (486,672), merkitty (477,316), rooli (463,077), tyyli (460,239), linkki (433,447), positiivinen (420,583), internet (414,143), riski (392,924), kokki (381,467), merkitä (360,874), bändi (354,290), sekki (353,835)

## Close to the threshold (norm 25 to 50; check by eye)

| stem | english | norm | tagged |
|---|---|---:|---|
| abnormi | abnormal | 25.0 | yes |
| standardoida | to standardize | 25.0 | yes |
| terapeutti | therapist | 26.0 | yes |
| audiovisuaalinen | audiovisual | 26.2 | yes |
| kurssi | course | 26.7 | yes |
| kompleksi | complex | 26.7 | yes |
| ergonominen | ergonomic | 27.3 | yes |
| kambri | cambrian | 27.5 | yes |
| vermutti | vermouth | 27.5 | yes |
| paali | bale | 28.0 | yes |
| kandelaaberi | candelabrum | 28.3 | yes |
| proletarisoida | to proletarianize | 28.6 | yes |
| hysteerinen | hysterical | 29.1 | yes |
| syntaktinen | syntactic | 29.1 | yes |
| heraldinen | heraldic | 30.0 | yes |
| petrokemia | petrochemistry | 30.0 | yes |
| kanveesi | canvas | 30.0 | yes |
| presidenttiys | presidency | 30.8 | yes |
| totalitaristinen | totalitarian | 31.2 | yes |
| miliisi | militia | 31.4 | yes |
| viktoriaaninen | victorian | 31.4 | yes |
| marginaali | margin | 32.0 | yes |
| antisemitisti | anti-semite | 32.3 | yes |
| optoelektroninen | optoelectric | 32.5 | yes |
| degeneroitua | to degenerate | 33.3 | yes |
| nippa | nipple | 33.3 | yes |
| kuriositeetti | curiosity | 33.8 | yes |
| koaguloida | to coagulate | 34.0 | yes |
| koksata | to coke | 34.3 | yes |
| kvalitatiivinen | qualitative | 34.7 | yes |
| optimaalinen | optimal | 35.0 | yes |
| geodeetti | geodesist | 35.6 | no |
| resonoida | to resonate | 35.6 | no |
| monstrumi | monstrosity | 36.4 | no |
| mallas | malt | 36.7 | no |
| ekspansiivinen | expansive | 37.1 | no |
| graafikko | graphist | 37.8 | no |
| dumdumluoti | dumdum | 38.2 | no |
| eksklusiivinen | exclusive | 38.6 | no |
| haloo | hello | 40.0 | no |
| minolainen | minoan | 40.0 | no |
| rulla | roll | 40.0 | no |
| kaarti | guard | 40.0 | no |
| ekvatoriaalinen | equatorial | 41.3 | no |
| kserokopio | xerocopy | 42.0 | yes |
| skyytti | scythian | 42.5 | no |
| preeria | prairie | 42.9 | no |
| dyyni | dune | 44.0 | no |
| pihka | pitch | 44.0 | no |
| šaahi | shah | 44.0 | no |
| kafkamainen | kafkaesque | 45.5 | no |
| kellata | to yellow | 45.7 | no |
| pussata | to kiss | 45.7 | no |
| bolševistinen | bolshevist | 46.2 | no |
| penikoida | to pup | 46.7 | no |
| viekastella | to weasel | 47.3 | no |
| iisoppi | hyssop | 48.6 | no |
| spagaatti | split | 48.9 | no |
| etabloitua | to establish | 50.0 | no |
| lehtori | lecturer | 50.0 | no |
| pesä | nest | 50.0 | no |
| sitten | then | 50.0 | no |
