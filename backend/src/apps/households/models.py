from django.db import models


class Household(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Household"
        verbose_name_plural = "Households"
        ordering = ["name", "created_at"]

    def __str__(self) -> str:
        return self.name
