from datetime import timedelta, timezone
from rest_framework import serializers
from .models import Predmet, IspitniTermin, PrijavaIspita, Zaduzenje, Uplata

class IspitniTerminSerializer(serializers.ModelSerializer):
    predmet_naziv = serializers.CharField(source='predmet.naziv', read_only=True)
    class Meta:
        model = IspitniTermin
        fields = ['id', 'predmet_naziv', 'datum_vrijeme']

class PrijavaIspitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrijavaIspita
        fields = ['id', 'student', 'termin', 'status', 'kreirano_at']
        read_only_fields = ['id', 'status', 'kreirano_at', 'student']
    def create(self, validated_data):
        # custom create: postavka student iz request context, provjera 48h i finansija
        student = self.context['request'].user.student
        termin = validated_data['termin']
        # (Ponoviti iste provjere kao u view funkciji prijava_ispita)
        if PrijavaIspita.objects.filter(student=student, termin=termin, status="prijavljen").exists():
            raise serializers.ValidationError("Već ste prijavili ovaj ispit.")
        if termin.datum_vrijeme - timezone.now() < timedelta(hours=48):
            raise serializers.ValidationError("Prekasno za prijavu - manje od 48h.")
        # Finansijska provjera...
        prijava = PrijavaIspita.objects.create(student=student, termin=termin)
        Zaduzenje.objects.create(student=student, tip="prijava_ispita", iznos=0, povezano_sa_prijavom=prijava)
        return prijava
    

class ZaduzenjeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zaduzenje
        fields = ['id', 'tip', 'iznos', 'datum', 'opis']

class UplataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Uplata
        fields = ['id', 'iznos', 'datum', 'svrha']