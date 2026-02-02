from django.contrib import admin

from django.contrib import admin
from .models import (
    Student, Predmet, AkademskaGodina, IspitniRok,
    IspitniTermin, PrijavaIspita, Zaduzenje, Uplata
)

admin.site.register(Student)
admin.site.register(Predmet)
admin.site.register(AkademskaGodina)
admin.site.register(IspitniRok)
admin.site.register(IspitniTermin)
admin.site.register(PrijavaIspita)
admin.site.register(Zaduzenje)
admin.site.register(Uplata)