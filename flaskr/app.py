from flask import Flask, jsonify, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from werkzeug.datastructures import MultiDict
import numpy as np
import pandas as pd

from db_models import db, Recipe, Item, RecipeItem

# Get the directory where the current Python script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Set the current working directory to the script directory
os.chdir(script_dir)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/sean/Documentos/python_projects/recipe_app/flaskr/db/recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)



@app.route('/')
def home():
    with app.app_context():
        recipes = Recipe.query.all()
        return render_template('home.html', recipes=recipes)
    
    


# endpoint for adding a recipe
@app.route('/add_recipe', methods = ['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        name = request.form['name']
        category1_name = request.form['category1']
        category2_name = request.form['category2']
        form_dict = {key: request.form.getlist(key) for key in request.form.keys() if key.endswith('[]')}
        ingredients = form_dict.get('ingredient[]')
        quantities = form_dict.get('quantity[]')
        units = form_dict.get('units[]')
        sections = form_dict.get('shop_section[]')
        
        # Create recipe object
        recipe = Recipe(name = name, category1 = category1_name, category2 = category2_name)
        
        db.session.add(recipe)

        # Create ingredient objects and recipe/ingredient link objects
        for i in range(len(ingredients)):
            ingredient_name = ingredients[i]
            quantity = quantities[i]
            unit = units[i]
            section = sections[i]

            ingredient = Item.query.filter_by(name=ingredient_name, unit=unit).first()

            if not ingredient:
                ingredient = Item(name=ingredient_name, unit=unit, shop_section=section)
                db.session.add(ingredient)

            recipe_ingredient = RecipeItem(recipe=recipe, item=ingredient, quantity=quantity)
            db.session.add(recipe_ingredient)

        db.session.commit()
    
        return redirect(url_for('home'))
    
    return render_template('add_recipe.html')


# endpoint for deleting a recipe
@app.route('/delete_recipe/<int:id>', methods=['POST'])
def delete_recipe(id):
    if request.method == 'POST':
        # Retrieve the recipe from the database
        recipe = Recipe.query.get_or_404(id)

        # Delete the recipe from the RecipeItem table
        RecipeItem.query.filter_by(recipe_id=id).delete()

        # Delete the recipe from the Recipe table
        db.session.delete(recipe)
        db.session.commit()

        # Redirect to the home page
        return redirect(url_for('home'))



# endpoint for editing a recipe
@app.route('/edit_recipe/<int:id>', methods=['GET', 'POST'])
def edit_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    
    # first save all rows from RecipeItems and Items tables for the recipe
    previous_ingredients = db.session.query(Item.name, RecipeItem.quantity, Item.unit, Item.shop_section, Item.id)\
        .join(RecipeItem, Item.id == RecipeItem.item_id)\
        .filter(RecipeItem.recipe_id == id)\
        .all()
        
    if request.method == 'POST':
        name = request.form['name']
        category1_name = request.form['category1']
        category2_name = request.form['category2']
        form_dict = {key: request.form.getlist(key) for key in request.form.keys() if key.endswith('[]')}
        ingredients = form_dict.get('ingredients[]')
        quantities = form_dict.get('quantities[]')
        units = form_dict.get('units[]')
        sections = form_dict.get('shop_section[]')
        
        # then delete these from tables
        RecipeItem.query.filter_by(recipe_id = id).delete()
        item_id_index = 4
        item_ids = [item[item_id_index] for item in previous_ingredients]
        Item.query.filter(Item.id.in_(item_ids)).delete()
        db.session.commit()

        # add back in the row in the Recipe table with recipe name and category
        # Find the recipe to update
        recipe = Recipe.query.filter_by(id=id).first()
        # Update the recipe name and category
        recipe.name = name
        recipe.category1 = category1_name
        recipe.category2 = category2_name
        # Commit the changes to the database
        db.session.commit()

        
        # now loop through the ingredients and add the rows back to the RecipeItems and Items tables
        for i in range(len(ingredients)):
            ingredient_name = ingredients[i]
            quantity = quantities[i]
            unit = units[i]
            section = sections[i]
            
            # Check if the ingredient already exists in the database
            ingredient = Item.query.filter_by(name = ingredient_name, unit = unit, shop_section = section).first()
            if ingredient is None:
                # If the ingredient doesn't exist, create a new row
                ingredient = Item(name=ingredient_name, unit=unit, shop_section=section)
                db.session.add(ingredient)

            #ingredient = Item(name = ingredient_name, unit = unit, shop_section = section)
            #db.session.add(ingredient)

            recipe_ingredient = RecipeItem(recipe_id = recipe.id, item_id = ingredient.id, quantity = quantity)
            db.session.add(recipe_ingredient)

            db.session.commit()
    
        return redirect(url_for('home'))

    return render_template('edit_recipe.html', ingredients = previous_ingredients, recipe = recipe.name, 
                           category1 = recipe.category1, category2 = recipe.category2)


# endpoint for generating a shopping list
@app.route('/shopping_list', methods=['GET'])
def generate_shopping_list():
    # load in the total number of recipes to select
    number = int(request.args.get('number'))
    
    # create a session
    recipes = Recipe.query.all()
    while True:
        choices = np.random.choice(recipes, number, replace = False)
        recipe_category1 = [choice.category1 for choice in choices]
        recipe_category2 = [choice.category2 for choice in choices]
        recipe_names = [choice.name for choice in choices]
        recipe_ids = [choice.id for choice in choices]
        # need to fix the logic for ensuring a balanced selection of recipes
        # here we ensure that we have chosen from at least 3 categories or if selected recipes is less than 3
        if (len(set(recipe_category1)) > 2) or (len(set(recipe_category2)) > 2) or (number < 3):
            break
    
    all_ingredients = db.session.query(Item.name, RecipeItem.quantity, Item.unit, Item.shop_section)\
        .join(RecipeItem, Item.id == RecipeItem.item_id)\
        .filter(RecipeItem.recipe_id.in_(recipe_ids))\
        .all()
    print(all_ingredients)
    all_ingredients = pd.DataFrame(all_ingredients)
    
    full_recipes = {}
    for i, recipe_id in enumerate(recipe_ids):
        full_recipe = db.session.query(Item.name, RecipeItem.quantity, Item.unit)\
            .join(RecipeItem, Item.id == RecipeItem.item_id)\
            .filter(RecipeItem.recipe_id == recipe_id)\
            .all()
        full_recipes[recipe_names[i]] = pd.DataFrame(full_recipe)
    
    shopping_list = (all_ingredients.groupby(['name', 'unit', 'shop_section'], as_index = False)['quantity']
                     .sum())
    shopping_list = (shopping_list.sort_values(by = 'shop_section')
                     [['name', 'quantity', 'unit']])

    return render_template('shopping_list.html', shopping_list = shopping_list, full_recipes = full_recipes)

if __name__ == '__main__':
    app.run(debug=True)


