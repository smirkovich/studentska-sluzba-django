from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    # Veza na ugrađenog korisnika (koristi Django auth sistem za logovanje)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    ime = models.CharField(max_length=60)
    prezime = models.CharField(max_length=60)
    broj_indeksa = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Studenti"
    
    # Dodatna polja (opciono): npr. program, status studiranja, način finansiranja...
    # program = models.CharField(max_length=100)
    # status_studenta = models.CharField(max_length=10, choices=[("redovan","Redovan"), ("vanredan","Vanredan")])
    def __str__(self):
        return f"{self.ime} {self.prezime} ({self.broj_indeksa})"
    
class Predmet(models.Model):
    sifra = models.CharField(max_length=20, unique=True)
    naziv = models.CharField(max_length=150)
    ects = models.PositiveSmallIntegerField()
    godina_studija = models.PositiveSmallIntegerField()  # npr. 1-6
    semestar = models.PositiveSmallIntegerField(choices=[(1,"Zimski"), (2,"Ljetnji")])

    class Meta:
        verbose_name = "Predmet"
        verbose_name_plural = "Predmeti"
    

    def __str__(self):
        return f"{self.naziv} ({self.sifra})"
    

class AkademskaGodina(models.Model):
    oznaka = models.CharField(max_length=9, unique=True)  # npr. "2023/24"
    
    class Meta:
        verbose_name = "AkademskaGodina"
        verbose_name_plural = "Akademske Godine"
    
    def __str__(self):
        return self.oznaka

class IspitniRok(models.Model):
    oznaka = models.CharField(max_length=10)  # npr. "Jan-Feb", "Sept I"
    ak_godina = models.ForeignKey(AkademskaGodina, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "IspitniRok"
        verbose_name_plural = "Ispitni Rokovi"
    
    def __str__(self):
        return f"{self.oznaka} {self.ak_godina}"
    
class IspitniTermin(models.Model):
    predmet = models.ForeignKey(Predmet, on_delete=models.PROTECT)
    rok = models.ForeignKey(IspitniRok, on_delete=models.PROTECT)
    datum_vrijeme = models.DateTimeField()
    mjesto_izvodjenja = models.CharField(max_length=120, blank=True)
    class Meta:
        indexes = [models.Index(fields=["predmet", "datum_vrijeme"])]
        verbose_name = "IspitniTermin"
        verbose_name_plural = "Ispitni Termini"
    def __str__(self):
        return f"{self.predmet.naziv} - {self.datum_vrijeme.date()} u {self.datum_vrijeme.time()}"
    
class PrijavaIspita(models.Model):
    class Status(models.TextChoices):
        PRIJAVLJEN = "prijavljen", "Prijavljen"
        ODJAVLJEN = "odjavljen", "Odjavljen"
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    termin = models.ForeignKey(IspitniTermin, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRIJAVLJEN)
    kreirano_at = models.DateTimeField(auto_now_add=True)
    odjavljeno_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        unique_together = ("student", "termin")
        verbose_name = "PrijavaIspita"
        verbose_name_plural = "Prijave Ispita"

class Zaduzenje(models.Model):
    TIPOVI = (
        ("skolarina", "Školarina"),
        ("prijava_ispita", "Prijava ispita"),
        ("ostalo", "Ostalo"),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    tip = models.CharField(max_length=20, choices=TIPOVI)
    iznos = models.DecimalField(max_digits=12, decimal_places=2)
    datum = models.DateField(auto_now_add=True)
    povezano_sa_prijavom = models.ForeignKey(PrijavaIspita, null=True, blank=True, on_delete=models.SET_NULL)
    opis = models.CharField(max_length=200, blank=True)
    class Meta:
        verbose_name = "Zaduzenje"
        verbose_name_plural = "Zaduzenja"

class Uplata(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    iznos = models.DecimalField(max_digits=12, decimal_places=2)
    datum = models.DateField()
    svrha = models.CharField(max_length=200, blank=True)
    class Meta:
        verbose_name = "Uplata"
        verbose_name_plural = "Uplate"