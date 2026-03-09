from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from .models import Predmet, IspitniTermin, PrijavaIspita, Zaduzenje, Uplata
from django.db.models import Sum
from decimal import Decimal

from datetime import date

def akademska_godina_za_datum(d: date):
    start_year = d.year if d.month >= 10 else d.year - 1
    start = date(start_year, 10, 1)
    end = date(start_year + 1, 7, 31)  # do kraja jula
    return start, end

def required_pct_for_date(d: date) -> float:
    # okt..jul = 10 mjeseci
    if d.month >= 10:
        dospjelo = d.month - 10 + 1  # okt=1 ... dec=3
    elif 1 <= d.month <= 7:
        dospjelo = d.month + 3       # jan=4 ... jul=10
    else:
        dospjelo = 10                # avg/sep tretiramo kao 100%
    return dospjelo / 10.0

@login_required
def ispiti_list(request):
    student = request.user.student
    sada = timezone.now()

    # samo budući termini
    svi_termini = IspitniTermin.objects.filter(datum_vrijeme__gte=sada).order_by("datum_vrijeme")

    prijavljeni_qs = PrijavaIspita.objects.filter(
        student=student, status="prijavljen", termin__datum_vrijeme__gte=sada
    )
    prijavljeni_ids = prijavljeni_qs.values_list("termin_id", flat=True)

    dostupni_termini = svi_termini.exclude(id__in=prijavljeni_ids)

    context = {
        "prijavljeni_termini": prijavljeni_qs.select_related("termin", "termin__predmet").order_by("termin__datum_vrijeme"),
        "dostupni_termini": dostupni_termini.select_related("predmet", "rok"),
    }
    return render(request, "sas/exams_list.html", context)

@login_required
def prijava_ispita(request, termin_id):
    student = request.user.student
    termin = get_object_or_404(IspitniTermin, id=termin_id)

    # PROVJERI DA LI POSTOJI BILO KAKVA PRIJAVA ZA TAJ TERMIN
    prijava = PrijavaIspita.objects.filter(student=student, termin=termin).first()

    # Ako već postoji AKTIVNA prijava, ne dozvoljavamo duplo
    if prijava and prijava.status == "prijavljen":
        messages.warning(request, "Već ste prijavili ovaj ispit.")
        return redirect("ispiti_list")

    # Pravilo 48h
    sada = timezone.now()
    if termin.datum_vrijeme - sada < timedelta(hours=48):
        messages.error(request, "Rok za prijavu ovog ispita je istekao (manje od 48h prije termina).")
        return redirect("ispiti_list")

    danas = timezone.localdate()
    ag_start, ag_end = akademska_godina_za_datum(danas)
    required_pct = Decimal(str(required_pct_for_date(danas)))  # npr. januar -> 0.4

    total_skolarina = (
        Zaduzenje.objects
        .filter(student=student, tip="skolarina", datum__gte=ag_start, datum__lte=ag_end)
        .aggregate(s=Sum("iznos"))["s"]
    ) or Decimal("0")

    total_uplaceno = (
        Uplata.objects
        .filter(student=student, datum__gte=ag_start, datum__lte=ag_end)
        .aggregate(s=Sum("iznos"))["s"]
    ) or Decimal("0")

    required_paid = (total_skolarina * required_pct)

    # tolerancija 0.01 zbog decimala
    if total_uplaceno + Decimal("0.01") < required_paid:
        pct_display = int(required_pct * 100)
        messages.error(
            request,
            f"Za prijavu ispita potrebno je uplatiti najmanje {pct_display}% školarine "
            f"za tekuću akademsku godinu."
        )
        return redirect("ispiti_list")

    # SADA: ili reaktiviramo staru prijavu, ili pravimo novu
    if prijava:
        # Postojala je odjavljena prijava za isti termin -> "oživimo" je
        prijava.status = "prijavljen"
        prijava.odjavljeno_at = None
        prijava.kreirano_at = timezone.now()  # opcionalno osvježi "vrijeme prijave"
        prijava.save()
    else:
        # Ne postoji nikakav zapis -> pravimo novi
        prijava = PrijavaIspita.objects.create(student=student, termin=termin)

# Kreiraj novo zaduženje za ovu prijavu
    datum_str = termin.datum_vrijeme.strftime("%d.%m.%Y")
    mjesto_str = f", {termin.mjesto_izvodjenja}" if termin.mjesto_izvodjenja else ""
    Zaduzenje.objects.create(
        student=student,
        tip="prijava_ispita",
        iznos=Decimal("20.00"),
        povezano_sa_prijavom=prijava,
        opis=f"Prijava ispita: {termin.predmet.naziv}, {datum_str}{mjesto_str}",
    )

    messages.success(request, f"Ispit '{termin.predmet.naziv}' je uspješno prijavljen.")
    return redirect("ispiti_list")


@login_required
def odjava_ispita(request, termin_id):
    student = request.user.student
    prijava = get_object_or_404(
        PrijavaIspita,
        student=student,
        termin_id=termin_id,
        status="prijavljen",
    )

    sada = timezone.now()
    if prijava.termin.datum_vrijeme - sada < timedelta(hours=48):
        messages.error(request, "Rok za odjavu ovog ispita je istekao (manje od 48h prije termina).")
        return redirect("ispiti_list")

    prijava.status = "odjavljen"
    prijava.odjavljeno_at = timezone.now()
    prijava.save()

    # storniraj zaduženje
    zaduzenje = Zaduzenje.objects.filter(povezano_sa_prijavom=prijava).first()
    if zaduzenje:
        zaduzenje.delete()

    messages.info(request, f"Ispit '{prijava.termin.predmet.naziv}' je odjavljen.")
    return redirect("ispiti_list")

@login_required
def finansije(request):
    student = request.user.student
    zaduzenja = Zaduzenje.objects.filter(student=student)
    uplate = Uplata.objects.filter(student=student)
    # Izračunaj saldo: suma uplata - suma zaduženja
    ukupno_zaduzeno = sum(z.iznos for z in zaduzenja)
    ukupno_uplaceno = sum(u.iznos for u in uplate)
    saldo = ukupno_uplaceno - ukupno_zaduzeno
    context = {
        "zaduzenja": zaduzenja,
        "uplate": uplate,
        "saldo": saldo
    }
    return render(request, "sas/finances.html", context)


