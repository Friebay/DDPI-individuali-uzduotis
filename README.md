# Organizacijų pavadinimų paieška lietuviškuose naujienų straipsniuose

## Paskirstytų skaičiavimų tinklo aplinkos paruošimas

Sukuriame virtualią aplinką, kad galėtume atsisiųsti reikiamas bibliotekas

```
python3 -m venv ~/ner_venv
```

Aktyvuojame sukurta aplinką

```
source ~/ner_venv/bin/activate
```

Atsisiunčiame reikalingas bibliotekas

```
pandas pyarrow spacy
```

Atsisiunčiame lietuvišką spaCy modelį

```
python -m spacy download lt_core_news_sm
```

## submit.sh failas

Sukuriame `submit.sh` failą

```
nano submit.sh
```

Ir įklijuojame šį tekstą:

```
#!/bin/bash
#SBATCH -p main
#SBATCH -n 4 # nustatome, kiek procesu norime sukurti

module load py-mpi4py
source ~/ner_venv/bin/activate # aktyvuojame sukurta virtualia aplinka

mpirun python ner_extraction.py
```

## Programos paleidimas paskirstytų skaičiavimų tinkle

### Atsisiunčiame programos kodą

Pasiskirstytų skaičiavimų tinkle paleidžiame šią komandą:
```
wget https://github.com/Friebay/DDPI-individuali-uzduotis/raw/refs/heads/main/ner_extraction.py
```

### Atsisiunčiame norimą duomenų failą

Duomenų failas su 1000 eilučių:
```
wget https://github.com/Friebay/DDPI-individuali-uzduotis/raw/refs/heads/main/ccnews_LT_subset_1.parquet
```

Duomenų failas su 10000 eilučių:
```
wget https://github.com/Friebay/DDPI-individuali-uzduotis/raw/refs/heads/main/ccnews_LT_subset_10.parquet
```

Duomenų failas su 100000 eilučių:
```
wget https://github.com/Friebay/DDPI-individuali-uzduotis/raw/refs/heads/main/ccnews_LT_subset_100.parquet
```

1 procesas, 100 000 duomenų eilučių:

Apdorota per 85.63 sek.

Dažniausiai paminėtos organizacijos:

LRT            3880

Seimo          1013

Seimas          658

NATO            555

Vyriausybė      511

Seime           361

NBA             335

VU              293

Vyriausybės     259

AINA            243


2 procesai, 100 000 duomenų eilučių:

Apdorota per 85.03 sek.

Dažniausiai paminėtos organizacijos:

LRT            3880

Seimo          1013

Seimas          658

NATO            555

Vyriausybė      511

Seime           361

NBA             335

VU              293

Vyriausybės     259

AINA            243

4 procesai, 100 000 duomenų eilučių:
Apdorota per 31.58 sek.
Dažniausiai paminėtos organizacijos:
LRT            3880
Seimo          1013
Seimas          658
NATO            555
Vyriausybė      511
Seime           361
NBA             335
VU              293
Vyriausybės     259
AINA            243

8 procesai, 100 000 duomenų eilučių:
Apdorota per 15.14 sek.
Dažniausiai paminėtos organizacijos:
LRT            3880
Seimo          1013
Seimas          658
NATO            555
Vyriausybė      511
Seime           361
NBA             335
VU              293
Vyriausybės     259
AINA            243
Name: count, dtype: int64

16 procesų, 100 000 duomenų eilučių:
Apdorota per 8.67 sek.
Dažniausiai paminėtos organizacijos:
LRT            3880
Seimo          1013
Seimas          658
NATO            555
Vyriausybė      511
Seime           361
NBA             335
VU              293
Vyriausybės     259
AINA            243
