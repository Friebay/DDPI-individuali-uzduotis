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

### Laikas, pagreitėjimas ir efektyvumas

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

Analizuojant efektyvumo rezultatus galime teigti, kad efektyviausiai programa veikė su vienu procesu. Tačiau jeigu norime spartesnio veikimo, tuomet reikia atsižvelgti į duomenų kiekį, kadangi priklausomai nuo duomenų kiekio priklausys procesų skaičius, pavyzdžiui su 100 000 duomenų eilučių lygiagretumas efektyviausias buvo su 8 procesais, o su 10 000 duomenų eilučių - su 4 procesais.

### MPI profiliavimas

MPI profiliavimo statistikos buvo gautos naudojantis `cProfile` biblioteką. `.stats.` failai iš HPC buvo iškelti į savo virtualią aplinką naudojantis šią komandą: `scp vartotojo_vardas@login.university.lt:~/profile_rank_0.stats .`. Tuomet atsisiųsti iš serverio naudojantis šią komandą: `scp vartotojo_vardas@uosis.mif.vu.lt:~/profile_rank_0.stats .`.

#### 1. Paskirstytojas

| ncalls | tottime | percall | cumtime | percall | filename:lineno(function) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 2 | 1.446 | 0.7231 | 1.446 | 0.7231 | `~:0(<method 'recv' of 'mpi4py.MPI.Comm' objects>)` |
| 4 | 0.001842 | 0.0004605 | 0.001842 | 0.0004605 | `~:0(<built-in method io.open_code>)` |
| 5 | 0.0009316 | 0.0001863 | 0.0009316 | 0.0001863 | `~:0(<built-in method builtins.next>)` |
| 1 | 0.0008502 | 0.0008502 | 0.001136 | 0.001136 | `core.py:311(__init__)` |
| 2 | 0.0007304 | 0.0003652 | 0.003583 | 0.001792 | `pandas_compat.py:783(table_to_dataframe)` |

![test](https://i.imgur.com/hCiBPY1.png "test")

#### 2. Darbuotojas 1

| ncalls | tottime | percall | cumtime | percall | filename:lineno(function) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 2505/501 | 0.1241 | 0.0002477 | 0.6972 | 0.001392 | `util.py:1751(_pipe)` |
| 70 | 0.1082 | 0.001546 | 0.1084 | 0.001548 | `numpy_ops.pyx:91(gemm)` |
| 1 | 0.06223 | 0.06223 | 0.07842 | 0.07842 | `vocab.pyx:538(from_disk)` |
| 8997/3933 | 0.05683 | 0.00001445 | 0.1707 | 0.00004339 | `main.py:1036(validate_model)` |
| 50 | 0.05296 | 0.001059 | 0.05327 | 0.001065 | `numpy_ops.pyx:165(maxout[float3d_t])` |

![test](https://i.imgur.com/Z7q1RbW.png "test")

#### 3. Darbuotojas 2

| ncalls | tottime | percall | cumtime | percall | filename:lineno(function) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 2505/501 | 0.137 | 0.0002734 | 0.7365 | 0.00147 | `util.py:1751(_pipe)` |
| 70 | 0.1137 | 0.001624 | 0.1138 | 0.001626 | `numpy_ops.pyx:91(gemm)` |
| 1 | 0.06195 | 0.06195 | 0.07897 | 0.07897 | `vocab.pyx:538(from_disk)` |
| 8997/3933 | 0.05721 | 0.00001445 | 0.1707 | 0.00004339 | `main.py:1036(validate_model)` |
| 50 | 0.05439 | 0.001088 | 0.05465 | 0.001093 | `numpy_ops.pyx:165(maxout[float3d_t])` |

![test](https://i.imgur.com/iWHwGxA.png "test")

#### 4. Darbuotojas 3

| ncalls | tottime | percall | cumtime | percall | filename:lineno(function) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 0.06234 | 0.06234 | 0.0785 | 0.0785 | `vocab.pyx:538(from_disk)` |
| 8997/3933 | 0.0581 | 0.00001477 | 0.1732 | 0.00004403 | `main.py:1036(validate_model)` |
| 167 | 0.03765 | 0.0002255 | 0.0885 | 0.00053 | `__init__.py:101(get_all)` |
| 23 | 0.02854 | 0.001241 | 0.02981 | 0.001296 | `sre_compile.py:292(_optimize_charset)` |
| 24579/4132 | 0.02011 | 0.000004867 | 0.1579 | 0.00003822 | `fields.py:850(validate)` |

![test](https://i.imgur.com/dB3iHhr.png "test")

## Šaltiniai
1. https://huggingface.co/datasets/Friebay/ccnews-LT
2. https://spacy.io/models/lt/
3. https://mif.vu.lt/itwiki/hpc
4. https://emokymai.vu.lt/mod/assign/view.php?id=111949
5. https://jiffyclub.github.io/snakeviz/
6. https://aistudio.google.com/