Diplomska naloga

Repozitorij vsebuje programsko kodo, uporabljeno pri izdelavi diplomske naloge:

Razvoj algoritma za prepoznavanje vzponov in spustov na podlagi kolesarskih podatkov

Opis

Program omogoča obdelavo podatkov iz GPX datotek ter klasifikacijo posameznih odsekov poti glede na naklon.

Glavni koraki obdelave so:
- branje GPX datotek,
- preverjanje veljavnosti aktivnosti,
- izračun razdalje med zaporednimi GPS-točkami,
- izračun naklona,
- klasifikacija odsekov na vzpon, spust in ravnino,
- združevanje podatkov v 100-metrske intervale,
- glajenje nadmorske višine, srčnega utripa in kadence,
- grafični prikaz rezultatov.

Datoteke

- `Main.py` – glavna obdelava podatkov, klasifikacija in grafični prikaz rezultatov
- `gpx_loader.py` – branje podatkov iz GPX datotek
- `riderx_filter.py` – preverjanje veljavnosti GPX aktivnosti
- `generate_valid_trainings.txt.py` – izdelava seznamov veljavnih aktivnosti

Zahteve

Program uporablja Python ter naslednje knjižnice:

- gpxpy
- pandas
- numpy
- matplotlib

Podatki

GPX datoteke niso vključene v repozitorij.
