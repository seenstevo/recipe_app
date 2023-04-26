# Create a Weekly Shopping List From My Favourite Recipes

## Description

This app aims to take the hassle out of the weekly shop. A user can upload, edit or delete recipes and simply based on the number of recipes desired, a shopping list is automatically created containing the ingredients for recipes that the user likes!
This is a **Python Flask App** that uses a **MySQL** database managed with the **SQLAlchemy** library.

## Installation

This can be installed by cloning this repository, installing the requirements and launching the Flask app. Note this currently comes pre-loaded with recipes which can be deleted.
The aim is to create a docker image of this app.

## Use

1. Upon launching, the home (`/`) endpoint shows the current recipes stored in the DB. 
2. For every current recipe there are two end points which can affect them: to edit (`/edit_recipe/<int:id>`) or delete (`/delete_recipe/<int:id>`). 
3. To add a new recipe (`/add_recipe`) we are taken to a blank form to fill in. 
4. The main thrust of the app is the `/shopping_list` endpoint where we pass a number of recipes we want to create a shopping list for. This randomly selects this number of recipes and generates both a shopping list with the combined ingredients and a separated recipe card for each of the recipes selected. 

## Usage Notes

- It is assumed that each recipe is for 4 portions although this would not affect the performance if some were not.
- The recipes are split into 2 levels of categories with the first containing "meat", "fish", "legume" or "veggie" and the second containing "pasta", "rice", "potato" or "bread". The app will attempt to not select too many dishes from the same categories so giving a variety for the weekly meals. **Note** that this is currently not aimed at a veggie or vegan diet but could be modified to split categories beyond "veggie" or "legume" to help generate this variety.

## Status and Future Plans

The app currently works to create a shopping list based on the number of requested recipes. I would like to add the following features in order of priority:
1. Ability to tick off ingredients from shopping list that you already have (such as cupboard staples, spices etc).
2. Automatic or easy exportation of HTML for mobile use.
3. Ability to tick off during shopping but offline from app. This could be rolled into 1.
4. Endpoint to clear or purge database.
5. Storage of links to actual recipe + instructions such as websites or photos from recipe book etc.
6. Automatically create shopping basket with online supermarket.

