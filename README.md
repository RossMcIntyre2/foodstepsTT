Hi, this is my attempt at the Foodsteps tech test! Thank you for taking the time to have a look and please let me know if you have any questions or issues in testing.

**Notes/Assumptions:**
-
- Backend task:
  - I decided to save these models in a database using Django, since although it added a bit more complexity to the task, it would be much more reusable for any future work, and I think Django's ORM makes it more explicit as to what is being done at each stage.
  - I did as much preprocessing (of searching up the tree to find the parents' impacts etc.) _before_ saving the models to the DB as possible. This would reduce the number of queries and mean that the information enters the DB in as complete a state as possible.
  - Rounded final impacts to 2 decimal places
  - Other assumptions/reasoning should be covered in comments
  - The main points of interest in the code can be found in `backend_task/bin/calculate_recipe_impacts_from_csv.py` and `backend_task/recipes/models.py`
- Frontend task:
  - I queried the full list of users and posts and then processed them in JS/TS. This is fast enough for small data sets but if we want to filter larger datasets if would be beneficial to send filter parameters in the query. Given the small datasets on this task though I favoured reducing the number of queries by filtering the full dataset when the search term changed - rather than fetching the data for a specific user when filtering.
  - Other assumptions/reasoning should be covered in comments
  - The main points of interest in the code can be found in `frontend_task/src/user-list`

**Testing instructions:**
-
- Backend task:

1. After cloning the repo, `cd` into `backend_task`
2. Run `pip3 install -r requirements.txt`
3. `python3 manage.py makemigrations` (Not needed the first time but needed if there are changes later)
4. `python3 manage.py migrate`
5. Run the script from the terminal with `python -m bin.calculate_recipe_impacts_from_csv`. This should display some logging information about the import/calculation process. It will display any errors in identifying food classes, and then print the overall impact of all the recipes for which we have sufficient information.

    Output should look something like
    ```
   admins-MacBook-Pro-2:backend_task rossmcintyre$ python3 -m bin.calculate_recipe_impacts_from_csv

    INFO:root:Reading food classes csv file and saving to database...
    ERROR:root:Could not calculate impact for Oils as there is insufficient data
    ERROR:root:Could not calculate impact for Prepared Meals as there is insufficient data
    ERROR:root:Could not calculate impact for Spices and Seasonings as there is insufficient data
    ERROR:root:Could not calculate impact for Dairy as there is insufficient data
    ERROR:root:Could not calculate impact for Seasonings as there is insufficient data
    INFO:root:Successfully created 71 food classes from csv file in 0.015 seconds. Failed to resolve impact for 5 of these
    
    
    Reading recipes csv file and saving to database...
    INFO:root:Could not find matching ingredient for Xanthum Gum
    INFO:root:Could not find matching ingredient for Milk Powder
    INFO:root:Successfully created 33 recipe ingredients and 4 recipes in 0.004 seconds. Failed to match 2 ingredients
    
    
    Recipe Impacts 
    
    Spaghetti Bolognese: 13.99kg
    Tiramisu: 4.89kg
    Chickpea Salad: 11.19kg
    INFO:root:Could not calculate impact for Salted Caramel Ice Cream as not all ingredients could be identified
    ```
6. We can do some additional queries in the shell to ensure that all the food class and recipes have been saved to the DB as expected.
Run `python3 manage.py shell` in the `backend_task` directory and try some of the following commands (or similar) and hopefully you get similar results unless there was an error:
    
    ```
    Recipe.objects.all()
    <QuerySet [<Recipe: Spaghetti Bolognese>, <Recipe: Tiramisu>, <Recipe: Chickpea Salad>, <Recipe: Salted Caramel Ice Cream>]>
    ```
    ```
    RecipeIngredient.objects.count()
    33
    ```
    ```
    FoodClass.objects.all()
    <QuerySet [<FoodClass: Beef Mince>, <FoodClass: Beef>, <FoodClass: Ruminant Meat>, <FoodClass: Meat>, <FoodClass: Pork Mince>, <FoodClass: Pork>, <FoodClass: Pork & Poultry>, <FoodClass: Carrots>, <FoodClass: Root Vegetables>, <FoodClass: Vegetables>, <FoodClass: Onions>, <FoodClass: Onions and Leeks>, <FoodClass: Bulbs>, <FoodClass: Celery>, <FoodClass: Stem Vegetables>, <FoodClass: Garlic>, <FoodClass: Rosemary>, <FoodClass: Herbs>, <FoodClass: Leaves>, <FoodClass: Olive Oil>, '...(remaining elements truncated)...']>
    ```
    ```
    Recipe.objects.first().ingredients.all().values_list('weight', 'food_class__name', 'food_class__impact_per_kilogram')
    <QuerySet [(0.25, 'Beef Mince', 2.649402237), (0.25, 'Pork Mince', 4.548881992), (0.1, 'Carrots', 9.811717734), (0.25, 'Onions', 9.000471107), (0.1, 'Celery', 0.2183862344), (0.01, 'Garlic', 4.436081072), (0.002, 'Rosemary', 2.102187648), (0.025, 'Olive Oil', 8.084466052), (0.8, 'Tinned Plum Tomatoes', 1.048766001), (0.5, 'Water', 4.992903259), (0.2, 'Red Wine', 7.828728036), (0.5, 'Spaghetti', 7.57055912)]>
    ```

- Frontend task:

1. `cd` into `frontend_task`
2. `npm i`
3. `npm start`
4. Navigate to `http://localhost:3000/`
5. You should see a simple list of user names and their most recent blog posts. You can filter for substrings in the user name using the search bar at the top.