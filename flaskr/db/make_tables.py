from sqlalchemy import create_engine
import sys
sys.path.append('../')

from db_models import Recipe, Item, RecipeItem

# Create an engine to connect to the database
engine = create_engine('sqlite:///recipes.db')

# Drop the tables if they exist
Recipe.__table__.drop(bind=engine, checkfirst=True)
Item.__table__.drop(bind=engine, checkfirst=True)
RecipeItem.__table__.drop(bind=engine, checkfirst=True)

# Create the tables in the database
Recipe.metadata.create_all(bind=engine)
Item.metadata.create_all(bind=engine)
RecipeItem.metadata.create_all(bind=engine)
