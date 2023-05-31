from django.shortcuts import render
from django.shortcuts import redirect

from app.repositories.categoryrepo import getDistinctCategoryLabels, getCategories
from app.repositories.foodrepo import getDistinctIngredientLabels, getIngredients, addIngredient, updateIngredientGet, updateIngredientPost, deleteIngredient
from app.repositories.reciperepo import getCompactRecipes, getCompactRecipes, getRecipeById, insert_recipe
from app.repositories.techniquerepo import getDistinctTechniqueLabels, getTechniques
from app.repositories.food_dbpediarepo import getFood


def recipes(request):
    selectedCategoryList = request.GET.get('selected_categories', '').split(',')
    selectedTechniqueList = request.GET.get('selected_techniques', '').split(',')
    selectedIngredientList = request.GET.get('selected_ingredients', '').split(',')
    selectedCategoryList = list(filter(None, selectedCategoryList))
    selectedTechniqueList = list(filter(None, selectedTechniqueList))
    selectedIngredientList = list(filter(None, selectedIngredientList))
    searchTitle = request.GET.get('searchTitle', None)
    offset = request.GET.get('offset', 0)

    recipes = getCompactRecipes(offset=offset, limit=30, searchTitle=searchTitle, categoryList=selectedCategoryList,
                                techniqueList=selectedTechniqueList, ingredientList=selectedIngredientList)
    categoryList = getDistinctCategoryLabels()
    techniqueList = getDistinctTechniqueLabels()
    ingredientList = getDistinctIngredientLabels()

    context = {
        "recipe_list": recipes,
        "category_list": categoryList,
        "technique_list": techniqueList,
        "ingredient_list": ingredientList,
        "selected_categories": selectedCategoryList,
        "selected_techniques": selectedTechniqueList,
        "selected_ingredients": selectedIngredientList,
        "offset": offset
    }

    return render(request, "recipes.html", context)

def recipe_details(request, recipe_id):
    recipe = getRecipeById(recipe_id=recipe_id)
    context = {"recipe": recipe}
    return render(request, "recipe_details.html", context)

def home(request):
    return render(request, "home.html")

def ingredients(request):
    return render(request, "ingredients.html", getIngredients(request))


def add_ingredient(request):
    if request.method == 'POST':
        addIngredient(request)
        return redirect("/ingredients/")

    return render(request, "add_ingredient.html")

def add_recipe(request):
    selectedCategoryList = request.GET.get('selected_categories', '').split(',')
    selectedTechniqueList = request.GET.get('selected_techniques', '').split(',')
    selectedIngredientList = request.GET.get('selected_ingredients', '').split(',')
    selectedCategoryList = list(filter(None, selectedCategoryList))
    selectedTechniqueList = list(filter(None, selectedTechniqueList))
    selectedIngredientList = list(filter(None, selectedIngredientList))
    recipeTitle = request.GET.get('recipeTitle', None)
  
    categoryList = getDistinctCategoryLabels()
    print(categoryList)
    techniqueList = getDistinctTechniqueLabels()
    ingredientList = getDistinctIngredientLabels()

    context =  {
        "category_list": categoryList,
        "technique_list": techniqueList,
        "ingredient_list": ingredientList, 
        "selected_categories": selectedCategoryList,
        "selected_techniques": selectedTechniqueList,
        "selected_ingredients": selectedIngredientList
    }

    return render(request, "add_recipe.html", context)


def insert_new_recipe(request):
    insert_recipe(request)
    return redirect('/recipes/')

def update_ingredient(request):
    if request.method == 'POST':
        updateIngredientPost(request)
        return redirect('/ingredients/')

    else:
        return render(request, 'update_ingredient.html', updateIngredientGet(request))

def delete_ingredient(request):
    if request.method == 'POST':
        deleteIngredient(request)
        return redirect('/ingredients/')


def categories(request):
    return render(request, "categories.html", getCategories(request))


def techniques(request):
    return render(request, "techniques.html", getTechniques(request))


def dbpedia_food(request):
    return render(request, "dbpedia_food.html", getFood(request))
