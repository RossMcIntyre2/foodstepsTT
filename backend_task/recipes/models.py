from __future__ import annotations

import uuid

from django.db import models


class FoodClass(models.Model):
    id = models.IntegerField(editable=False, primary_key=True)
    # In reality I would use on_delete=models.PROTECT since we don't want to delete any child recipes if a parent is
    # deleted, but for this task it is helpful to CASCADE to make clearing the db easier at the start of the script
    parent_food_class = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)
    name = models.CharField(max_length=255, blank=False)
    impact_per_kilogram = models.FloatField(null=True, blank=False)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    id = models.IntegerField(editable=False, primary_key=True)
    name = models.CharField(max_length=255, blank=False)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    id = models.AutoField(editable=False, primary_key=True)
    recipe = models.ForeignKey(Recipe, null=False, blank=False, on_delete=models.CASCADE, related_name='ingredients')
    food_class = models.ForeignKey(FoodClass, null=True, on_delete=models.CASCADE)
    weight = models.FloatField(null=False, blank=False)
