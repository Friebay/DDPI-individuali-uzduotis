# Organizacijų pavadinimų paieška lietuviškų naujienų straipsnių antraštėse

## Tikslas, problema ir uždaviniai
Tikslas: panaudoti paskirstytų skaičiavimų tinklą ir `mpi4py` sprendžiant įvardytų esybių atpažinimo uždavinį.

Problema: įvardytų esybių atpažinimas užtrunka ilgai, kai naudojame tik vieną procesą ir nenaudojame lygiagretinimo.

Uždaviniai:
1. Susirasti užduoties tikslui tinkamus duomenis;
2. Sukurti Python programą, kuri teisingai apdoroja rastus duomenis naudojant lygiagretinimą;
3. Palyginti programos veikimo laiką, kai naudojamas skirtingas procesų skaičius. 

## Duomenys
Duomenys buvo atsisiųsti iš Hugging Face puslapio, `Friebay/ccnews-LT` repozitorijos, kurioje saugoma 2016 - 2023 m. lietuviškų naujienų straipsnių duomenys. Kadangi bus analizuojamos tik antraštės, todėl atsisiuntus visą `ccnews_LT.parquet` duomenų failą, iš jo buvo paimta tik antraštė, publikavimo data ir naujienų portalo domenas. Taip pat, analizės tikslais, buvo išsaugoti 3 duomenų rinkiniai, kurie turėjo 1 000, 10 000 ir 100 000 duomenų eilučių.


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
pip install pandas pyarrow spacy
```

Atsisiunčiame lietuvišką spaCy modelį

```
python -m spacy download lt_core_news_sm
```

## `submit.sh` failas

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

Norint atsisiųsti programos Python kodą, pasiskirstytų skaičiavimų tinkle paleidžiame šią komandą:
```
wget https://github.com/Friebay/DDPI-individuali-uzduotis/raw/refs/heads/main/ner_extraction.py
```

### Atsisiunčiame norimą duomenų failą

Duomenų failas su 1 000 eilučių:
```
wget https://github.com/Friebay/DDPI-individuali-uzduotis/raw/refs/heads/main/ccnews_LT_subset_1.parquet
```

Duomenų failas su 10 000 eilučių:
```
wget https://github.com/Friebay/DDPI-individuali-uzduotis/raw/refs/heads/main/ccnews_LT_subset_10.parquet
```

Duomenų failas su 100 000 eilučių:
```
wget https://github.com/Friebay/DDPI-individuali-uzduotis/raw/refs/heads/main/ccnews_LT_subset_100.parquet
```

## Rezultatai

Programos veikimo laikas su 1 000 duomenų eilučių

| Procesų skaičius | Laikas (sek.) | Pagreitėjimas | Efektyvumas |
| :---: | :---: | :---: | :---: |
| 1 | 1,37 | 1,00 | 100 % |
| 2 | 1,40 | 0,98 | 49 % |
| 4 | 0,95 | 1,44 | 36 % |
| 8 | 0,99 | 1,38 | 17 % |
| 16 | 1,08 | 1,27 | 8 % |

Programos veikimo laikas su 10 000 duomenų eilučių

| Procesų skaičius | Laikas (sek.) | Pagreitėjimas | Efektyvumas |
| :---: | :---: | :---: | :---: |
| 1 | 9,57 | 1,00 | 100 % |
| 2 | 9,23 | 1,04 | 52 % |
| 4 | 4,03 | 2,37 | 59 % |
| 8 | 2,09 | 4,58 | 57 % |
| 16 | 1,65 | 5,8 | 36 % |

Programos veikimo laikas su 100 000 duomenų eilučių

| Procesų skaičius | Laikas (sek.) | Pagreitėjimas | Efektyvumas |
| :---: | :---: | :---: | :---: |
| 1 | 85,63 | 1,00 | 100 % |
| 2 | 85,03 | 1,01 | 50 % |
| 4 | 31,58 | 2,71 | 68 % |
| 8 | 15,14 | 5,66 | 71 % |
| 16 | 8,67 | 9,88 | 62 % |

Galime pastebėti, kad visais atvejais vieno proceso laikas yra beveik lygus dviejų procesų laikui. Taip gavome, kadangi kuomet yra daugiau negu 1 procesas, tuomet pirmas procesas skirsto darbą, o kitas atlieką tą darbą. Rezultatuose su 1 000 duomenų eilučių matome, kad geriausi rezultatai gauti su 4 procesais ir daugiau procesų darbo nepagreitinto, kadangi su daugiau procesų duomenų dalinimas užtrunka ilgiau ir mūsų vienam procesui skirto rinkinio dydis yra 500, todėl du „darbininkai“ procesai atlieka visą darbą, o kiti negavus darbo yra išjungiami. Iš laiko duomenų su 100 000 eilučių matome, kad lygiagretinimas geriausiai veikia su daug duomenų, kadangi šiame bandyme didinant procesų skaičių dvigubai - programos veikimo laikas sumažėja beveik proporcingai.

## Šaltiniai
1. https://huggingface.co/datasets/Friebay/ccnews-LT
2. https://spacy.io/models/lt/
3. https://mif.vu.lt/itwiki/hpc
4. https://emokymai.vu.lt/mod/assign/view.php?id=111949
4. https://aistudio.google.com/