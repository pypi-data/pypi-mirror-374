from django.db import models

from .constants import COUNTRIES


class Region(models.Model):
    name = models.CharField("Région", max_length=255, unique=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField("Département", max_length=255)
    number = models.CharField("Numéro du département", max_length=3, unique=True)
    region = models.ForeignKey(
        Region, verbose_name="Région", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.number}) - {self.region}"


class School(models.Model):
    uai = models.CharField(max_length=10, unique=True)
    name = models.CharField("Nom", max_length=255)
    city = models.CharField("Ville", max_length=40)
    zip_code = models.CharField("Code postal", max_length=5)
    country = models.CharField(
        max_length=2, choices=COUNTRIES, default="FR", blank=True, verbose_name="pays"
    )
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        verbose_name="Département",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "École"
        verbose_name_plural = "Écoles"
