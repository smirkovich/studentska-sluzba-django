# Studentska služba – Django web aplikacija

Web aplikacija za podršku rada studentske službe. Studentima omogućava:
- prijavu i odjavu ispita (uz poslovna pravila, npr. 48h),
- prikaz dostupnih ispitnih termina (bez termina u prošlosti),
- pregled finansija (uplate, zaduženja, saldo) i validaciju prava na prijavu ispita na osnovu procenta izmirenja školarine,
- administraciju podataka preko Django admin panela.

> Projekat je razvijen u Django framework-u, uz Tailwind CSS za UI. U projektu postoji i REST API sloj (DRF) kao priprema za buduću mobilnu aplikaciju.

---

## Tehnologije
- Python 3.x
- Django
- Django REST Framework (DRF)
- SQLite (dev)
- PostgreSQL (prod)
- Tailwind CSS

---

## Preduslovi
Instalirano na računaru:
- Python (preporuka 3.10+)
- Git
- (ako koristiš Tailwind build) Node.js + npm

---

1) Kloniranje repozitorijuma
```bash
git clone https://github.com/smirkovich/studentska-sluzba-django.git
cd studentska-sluzba-django
```

2) Kreiranje virtualnog okruženja (venv)
Windows (CMD)
```bash
python -m venv venv
venv\Scripts\activate
```
Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

3) Instalacija zavisnosti
```bash
pip install -r requirements.txt
```

4) Migracije baze (kreiranje šeme)
```bash
python manage.py migrate
```

5) Kreiranje admin (superuser) naloga
```bash
python manage.py createsuperuser
```

6) Pokretanje aplikacije
```bash
python manage.py runserver
```

Aplikacija će biti dostupna na:
http://127.0.0.1:8000/

Admin panel:
http://127.0.0.1:8000/admin/

7) Tailwind CSS
```bash
npm install
npm run build
```

8) Unos početnih podataka (preko admin panela)
Preporučeni minimalni setup:
1. Kreiraj korisnika (User) i poveži/kreiraj Student profil (ako model postoji).
2. Kreiraj Predmete.
3. Kreiraj Ispitne termine (IspitniTermin) sa datumom u budućnosti.
4. Dodaj finansijske stavke:
 - Zaduženje školarine (za akademsku godinu),
 - Uplate (da bi testirao validaciju procenta izmirenja školarine).

9) Najčešće rute
Login: /login/
Student ispiti: /student/ispiti/
Admin: /admin/


