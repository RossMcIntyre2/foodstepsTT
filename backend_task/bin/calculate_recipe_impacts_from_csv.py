#!/usr/bin/env python3

from __future__ import annotations
import csv
import django
import logging
import os
import time

from django.db import transaction
from django.db.models.functions import Lower

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_task.settings')
django.setup()

from recipes.models import Recipe, FoodClass, RecipeIngredient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

RECIPES_CSV_PATH = os.path.abspath(os.path.dirname('__file__')) + '/data/recipes.csv'
FOOD_CLASSES_CSV_PATH = os.path.abspath(os.path.dirname('__file__')) + '/data/food_classes.csv'


# Remove all data from db - we wouldn't usually want to delete everything for an upload
# (we may want to do a get_or_create), but for this use case this will work
def clean_db():
    Recipe.objects.all().delete()
    FoodClass.objects.all().delete()
    RecipeIngredient.objects.all().delete()


def clean_food_class(ingredient):
    # return a string of lower case words with only letters (and numbers)
    return ''.join([letter.lower() for letter in ingredient if letter.isalnum() or letter == ' '])


def import_food_class_models(csv_path):
    count_failed = 0
    # we need to link the food class instance to its parent after the latter has been created, so here I
    # create a dict to map the IDs so that once the models are created we can link them in one bulk update
    food_class_id_to_parent_id_dict = dict()
    food_class_models = []

    start = time.time()

    with open(csv_path) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        logger.info('Reading food classes csv file and saving to database...')
        for row in csv_reader:
            # create a FoodClass instance but do not save to database so that we can create all
            # entries in one query, so we add them to a list to commit later
            food_class = FoodClass(
                id=row['ID'],
                name=row['Name'],
                impact_per_kilogram=row['Impact / kg'],
            )
            food_class_id_to_parent_id_dict[row['ID']] = row['Parent ID'] if row['Parent ID'] else None
            food_class_models.append(food_class)

        for food_class in food_class_models:
            # if impact is already available we dont need to do anything
            if not food_class.impact_per_kilogram:
                # create a temporary food class to indicate which food class
                # we are looking at during the while loop
                temp_food_class = food_class
                while not food_class.impact_per_kilogram:
                    # if we have no impact for the food class and it has no more parents
                    # then we will not get a value, so break off the while loop and raise an error.
                    # We still create the model though in case it is referenced elsewhere
                    if not food_class_id_to_parent_id_dict[temp_food_class.id]:
                        logger.error(
                            'Could not calculate impact for %s as there is insufficient data',
                            food_class.name,
                        )
                        count_failed += 1
                        food_class.impact_per_kilogram = None
                        break
                    else:
                        # find the parent food class by ID
                        parent = next(
                            filter(
                                lambda x: x.id == food_class_id_to_parent_id_dict[temp_food_class.id],
                                food_class_models),
                            None
                        )
                        if not parent:
                            # if we can't find the parent by ID then we raise an error
                            logger.error(
                                'Could not calculate impact for %s a parent with ID %d does not exist',
                                food_class.name,
                                temp_food_class.parent_food_class_id,
                            )
                            count_failed += 1
                            food_class.impact_per_kilogram = None
                            break
                        if parent.impact_per_kilogram:
                            # if the parent has an impact then we save this value for the original food class
                            food_class.impact_per_kilogram = parent.impact_per_kilogram
                        # if we reach this point we need to move up another level in the tree,
                        # so set the temporary class to be the parent class and "restart" the while loop
                        temp_food_class = parent
            continue

        try:
            # wrap creation in an atomic transaction to ensure we don't have any failing uploads
            with transaction.atomic():
                # Bulk create all the objects from a list to
                # reduce the number of queries from around N to just 1
                food_class_objects = FoodClass.objects.bulk_create(food_class_models)
                for food_class in food_class_objects:
                    food_class.parent_food_class_id = food_class_id_to_parent_id_dict[food_class.id]
                FoodClass.objects.bulk_update(food_class_objects, ['parent_food_class'])
            logger.info(
                f"Successfully created {len(food_class_models)} food classes from csv file "
                f"in {round(time.time() - start, 3)} seconds. Failed to resolve impact for {count_failed} of these"
            )
        except Exception as e:
            print("Failed to create food class models based on CSV file due to error: ", e)


def import_recipe_ingredient_models(csv_path):
    # for ease we can get the lower case name straight from the query to avoid processing nested dictionaries.
    # Just return the id and lower case name so we can match the ingredient name to the food class
    food_class_names = FoodClass.objects.annotate(name_lower=Lower('name')).values('id', 'name_lower')
    failed_ingredient_match_count = 0
    recipe_models = []
    recipe_ingredient_models = []

    start = time.time()

    with open(csv_path) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        print('Reading recipes csv file and saving to database...')
        for row in csv_reader:
            # find the recipe by ID in the list of recipe models, if it's not in the list then we add it in
            recipe = next(
                filter(
                    lambda x: x.id == row['Recipe ID'],
                    recipe_models),
                None
            )
            if not recipe:
                recipe_models.append(
                    Recipe(
                        id=row['Recipe ID'],
                        name=row['Recipe Name'],
                    )
                )
            cleaned_food_class = clean_food_class(row['Ingredient Name'])
            # for each ingredient (row) we try to find the matching food class by
            # checking every word is in the food class name (by checking the length) but not worrying about the order.
            # If there is no match then we return None to make filtering out for errors easier
            ingredient = next(
                filter(
                    lambda x: len(x['name_lower'].split()) == len(cleaned_food_class.split()) and all(
                        [word in x['name_lower'] for word in cleaned_food_class.split()]),
                    food_class_names,
                ), None)
            if not ingredient:
                logger.info('Could not find matching ingredient for %s', row['Ingredient Name'])
                failed_ingredient_match_count += 1
            # now we can link the recipe to the food class through the RecipeIngredient model
            recipe_ingredient = RecipeIngredient(
                recipe_id=row['Recipe ID'],
                weight=row['Ingredient Weight / kg'],
                food_class_id=ingredient['id'] if ingredient else None
            )
            recipe_ingredient_models.append(recipe_ingredient)

        try:
            # wrap creation in an atomic transaction to ensure we don't have any failing uploads
            with transaction.atomic():
                # Bulk create all the objects from a list to
                # reduce the number of queries from around N to just 1
                Recipe.objects.bulk_create(recipe_models)
                RecipeIngredient.objects.bulk_create(recipe_ingredient_models)
        except Exception as e:
            print("Failed to create food class models based on CSV file due to error: ", e)

        logger.info(
            f"Successfully created {len(recipe_ingredient_models)} recipe ingredients and {len(recipe_models)} "
            f"recipes in {round(time.time() - start, 3)} seconds. Failed to match "
            f"{failed_ingredient_match_count} ingredients"
        )


def calculate_recipe_impacts():
    print("Recipe Impacts \n")
    recipes = Recipe.objects.prefetch_related('ingredients__food_class')
    for recipe in recipes:
        # for each recipe return a list of ingredient weights and impact per kg
        ingredients = list(recipe.ingredients.values('weight', 'food_class__impact_per_kilogram'))

        # create a list of impacts (one for each ingredient)
        ingredients_impact_list = [
            ingredient['weight'] * ingredient['food_class__impact_per_kilogram']
            if ingredient['food_class__impact_per_kilogram']
            else None for ingredient in ingredients
        ]
        # if all the ingredients have an impact we can find the sum, else raise an error
        if not all(ingredients_impact_list):
            logger.info("Could not calculate impact for %s as not all ingredients could be identified", recipe.name)
            continue
        print(f"{recipe.name}: {round(sum(ingredients_impact_list), 2)}kg")


if __name__ == "__main__":
    clean_db()
    print('\n')
    import_food_class_models(FOOD_CLASSES_CSV_PATH)
    print('\n')
    import_recipe_ingredient_models(RECIPES_CSV_PATH)
    print('\n')
    calculate_recipe_impacts()
