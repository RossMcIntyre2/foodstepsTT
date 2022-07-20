# Foodsteps Take-Home Test
There are two tasks to complete: one backend-oriented data processing task and one frontend-oriented task.

### Data Processing Task
A naïve calculation of the impact of a recipe involves multiplying the weight of each ingredient by the impact per kilogram of that ingredient.

However, we don't necessarily have direct impacts for every ingredient. For instance, there might be scarce academic literature on the impact of Jerusalem artichokes. However, since Jerusalem artichokes are root vegetables, and we have impact data for other root vegetables, we can produce a best estimate for the impact of a generic root vegetable and use that value as a proxy for the impact of Jerusalem artichokes.

To model this, we have created what we call a "food class hierarchy", which is just an n-ary tree. When we want to retrieve the impact for a given ingredient, we first look at its corresponding food class. If that food class has an impact, we use it. Otherwise, we move to its parent food class and repeat the process. We continue this recursion up the tree until we reach a food class without a parent, in which case we've reached a root node. If this node has no impact, then we can't recurse and we've failed to retrieve an impact and should throw an error.

The other issue is ingredient names are entered by users and must be matched to food classes. In some cases, we're lucky and the ingredient name entered by the user matches exactly with the name of a food class. But often this is not the case. As such, when matching names, we ignore case, punctuation and word order. For example, the ingredient `tomatoes, plum (Chopped)` would match with the food class `Chopped Plum Tomatoes`.

##### Inputs

You are provided with two CSV files: `food_classes.csv` and `recipes.csv`.

`food_classes.csv` contains data with the following schema:
- ID
- Name
- Impact / kg
- Parent ID

_Impact values are randomly generated._

`recipes.csv` contains data with the following schema:
- Recipe ID
- Recipe Name
- Ingredient Name
- Ingredient Weight / kg

##### Goal

You are required to write a script to calculate the impact of all the recipes in `recipes.csv`. If there is an ingredient in a recipe that cannot be matched to a food class, you should not give an impact for that recipe.

You may use whatever language and libraries you'd like.

### Frontend Task

This task uses the API provided by <https://jsonplaceholder.typicode.com>.

Create a single page application using JavaScript or TypeScript that fetches data from the API, and displays a list of users along with their latest post. You should include a search bar which allows filtering the results by users' names using a simple substring match.

Assuming post ID corresponds to date created (lower ID means created earlier), for each user, show:

- Their name
- The title and body of their latest post

Feel free to use a framework (e.g. Create React App, React) or to do it in plain JavaScript using `<script>` tags, or anything inbetween – whatever’s easiest for you.

Styling is unimportant. Layout is important only insofar as the required information is presented in a sensible manner.
