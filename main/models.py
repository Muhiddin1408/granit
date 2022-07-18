from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    biznes_tahli = models.BooleanField(default=False)
    mahsulot_boshqaruvi = models.BooleanField(default=False)
    savdo_tahli = models.BooleanField(default=False)
    ltv_tahli = models.BooleanField(default=False)
    kassa = models.BooleanField(default=False)
    filial_boshqaruvi = models.BooleanField(default=False)
    kadrlar = models.BooleanField(default=False)
    mijozlar_qardorligi = models.BooleanField(default=False)
    yetkazib_beruvchilar = models.BooleanField(default=False)
    ombor_boshqaruvi = models.BooleanField(default=False)
    faktura_yoqlama = models.BooleanField(default=False)

