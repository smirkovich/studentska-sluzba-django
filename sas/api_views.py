from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sas.models import IspitniTermin, PrijavaIspita, Uplata, Zaduzenje
from sas.serializers import IspitniTerminSerializer, PrijavaIspitaSerializer, UplataSerializer, ZaduzenjeSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_ispiti_list(request):
    student = request.user.student
    termini = IspitniTermin.objects.all()
    prijavljeni_ids = PrijavaIspita.objects.filter(student=student, status="prijavljen").values_list('termin_id', flat=True)
    dostupni = termini.exclude(id__in=prijavljeni_ids)
    serializer = IspitniTerminSerializer(dostupni, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_prijave_list(request):
    prijave = PrijavaIspita.objects.filter(student=request.user.student, status="prijavljen")
    # Mozemo koristiti isti serializer kao za create ali read_only, ili posebno napraviti
    data = []
    for pr in prijave:
        data.append({
            "id": pr.id,
            "predmet": pr.termin.predmet.naziv,
            "datum_vrijeme": pr.termin.datum_vrijeme,
            "status": pr.status
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_prijava_create(request):
    serializer = PrijavaIspitaSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        prijava = serializer.save()  # ovo poziva custom create
        return Response({"detail": "Prijava uspješna.", "prijava_id": prijava.id}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_finansije(request):
    student = request.user.student
    zaduzenja = Zaduzenje.objects.filter(student=student)
    uplate = Uplata.objects.filter(student=student)
    sz = ZaduzenjeSerializer(zaduzenja, many=True)
    su = UplataSerializer(uplate, many=True)
    saldo = sum(u['iznos'] for u in su.data) - sum(z['iznos'] for z in sz.data)
    return Response({
        "zaduzenja": sz.data,
        "uplate": su.data,
        "saldo": saldo
    })