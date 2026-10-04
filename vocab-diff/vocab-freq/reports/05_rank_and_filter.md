# 05 rank and filter
- stems: 26,211 lowercase stems; with a Wiktionary entry: 24,300 (1,911 stems have no Wiktionary entry and stay unjudged); with an English gloss: 19,330
- English-looking rule: edit score / longer word length x 100 <= 35 (stems of 3+ characters), or etymology `bor:en`; not tagged when the etymology says inherited from Proto-Finnic / Uralic
- tagged: 5,791 stems (5,727 by edit score, 64 only by etymology); 45 spared by a native etymology
- `05_stem_freq.tsv`: 20,420 stems ranked by `freq` (full count)
- `05_lemma_freq.tsv` (lemma rule `all`, sorted by freq, min-freq 0): 6,265,299 lemmas ranked, 194,586 removed as English-looking (4.14% of all lemma counts)

Columns of 05_lemma_freq.tsv: `rank` position (1 = most frequent); `lemma`; `class` Voikko word class; `n_stems` number of stems; `n_forms` forms merged into the lemma; `freq` all forms added up; `rarest_stem_freq` `freq` of the rarest stem for compounds (= `freq` otherwise).
Columns of 05_stem_freq.tsv: `rank` position by `freq`; `stem`; `freq` full count (the `freq` of every lemma containing the stem, added up); `standalone_freq` the lemma frequency of the stem as its own word (empty if it never occurs alone); `n_lemmas` lemmas containing it; `n_compounds` compounds containing it.
Columns of 05_stem_borrowing.tsv (only stems with an English gloss; tagged stems first, most frequent first): `stem`; `freq` full count of the stem; `english` closest English gloss; `edit_score` weighted edit distance; `norm` edit score / longer word length x 100; `borrowed` 1 = tagged; `reason` `edit score`, `bor:en`, or `native etymology` (a rule fired but the stem is native, not tagged); `etymology` Wiktionary tags (`bor:sv` borrowed from Swedish, `der:la` derived from Latin, `inh:urj-fin-pro` inherited from Proto-Finnic).

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
| haluta | want | 5 | 3.2 | 83.3 | 53.3 | no |
| mennä | go | 5 | 5.0 | 100 | 100.0 | no |
| tutkimus | research | 8 | 7.2 | 100 | 90.0 | no |
| jalka | leg | 4 | 4.0 | 80 | 80.0 | no |
| haaste | challenge | 7 | 6.0 | 77.8 | 66.7 | no |
| neuvosto | council | 7 | 6.2 | 87.5 | 77.5 | no |
| siellä | there | 5 | 5.0 | 83.3 | 83.3 | no |
| tieto | data | 3.2 | 4.0 | 64 | 80.0 | no |
| sivu | side | 2 | 2.0 | 50 | 50.0 | no |

## Most frequent removed lemmas

mutta (16,836,026), esimerkki (2,982,205), tee (2,298,364), pari (2,297,006), laki (1,712,650), euro (1,634,010), blogi (1,178,205), todeta (1,162,560), prosentti (1,091,613), kommentti (1,042,042), minuutti (899,102), merkittävä (865,887), hotelli (844,590), normaali (757,142), musiikki (729,646), merkki (708,442), historia (683,274), idea (667,838), kurssi (649,226), numero (627,994), artikkeli (613,786), media (567,580), projekti (558,147), energia (530,833), poliisi (520,748), kulttuuri (513,042), materiaali (504,378), versio (490,419), metri (489,600), video (487,188), netti (486,672), merkitty (477,316), lista (471,894), rooli (463,077), tyyli (460,239), linkki (433,447), kissa (415,192), internet (414,143), riski (392,924), kokki (381,467)

## Close to the threshold (norm 25 to 50; check by eye)

| stem | english | norm | tagged |
|---|---|---:|---|
| abnormi | abnormal | 25.0 | yes |
| tina | tin | 25.0 | no |
| idiomaattinen | idiomatic | 26.2 | yes |
| adaptiivinen | adaptive | 26.7 | yes |
| normaalistaa | normalise | 26.7 | yes |
| pasianssi | patience | 26.7 | yes |
| symmetrinen | symmetric | 27.3 | yes |
| seksismi | sexism | 27.5 | yes |
| euroatlanttinen | euro-atlantic | 28.0 | yes |
| analyyttinen | analytical | 28.3 | yes |
| minimi | minimum | 28.6 | yes |
| dogmaatikko | dogmatist | 29.1 | yes |
| stokastinen | stochastic | 29.1 | yes |
| heraldikko | heraldist | 30.0 | yes |
| petrokemia | petrochemistry | 30.0 | yes |
| kanveesi | canvas | 30.0 | yes |
| autenttinen | authentic | 30.9 | yes |
| diileri | dealer | 31.4 | yes |
| muusata | mouse | 31.4 | yes |
| volyymi | volume | 31.4 | yes |
| narsisti | narcissist | 32.0 | yes |
| graviditeetti | gravidity | 32.3 | yes |
| kofeiini | caffeine | 32.5 | yes |
| gaullistinen | gaullist | 33.3 | yes |
| ruoste | rust | 33.3 | no |
| plastiikka | plasticity | 34.0 | yes |
| rakkula | saccule | 34.3 | yes |
| sfinksi | sphinx | 34.3 | yes |
| kristikunta | christianity | 35.0 | yes |
| deponoida | deposit | 35.6 | no |
| moderoida | moderate | 35.6 | no |
| traktaatti | tract | 36.0 | no |
| lammas | lamb | 36.7 | no |
| tapuli | staple | 36.7 | no |
| pasteija | paste | 37.5 | no |
| postpositionaalinen | prepositional | 37.9 | no |
| fysikaalinen | physical | 38.3 | no |
| evolutiivinen | evolutionary | 40.0 | no |
| lape | plane | 40.0 | no |
| pleksilasi | plexiglass | 40.0 | no |
| troolari | trawler | 40.0 | no |
| prokuura | procuration | 40.0 | no |
| bigaaminen | bigamous | 42.0 | no |
| vitaalinen | vital | 42.0 | no |
| jiddiš | yiddish | 42.9 | no |
| byrokraatti | bureaucrat | 43.6 | no |
| kuori | quire | 44.0 | no |
| pääri | peer | 44.0 | no |
| voida | be | 44.0 | no |
| heraldiikka | heraldry | 45.5 | no |
| kanuuna | cannon | 45.7 | no |
| pitko | bitcoin | 45.7 | no |
| tarvike | article | 45.7 | no |
| jonglööri | juggler | 46.7 | no |
| telakoida | dock | 46.7 | no |
| tykky | thick | 48.0 | no |
| kilistä | clink | 48.6 | no |
| suklaa | chocolate | 48.9 | no |
| halki | halved | 50.0 | no |
| markiisi | marquess | 50.0 | no |
| purske | burst | 50.0 | no |
| uurre | furrow | 50.0 | no |
