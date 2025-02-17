import uvicorn
from fastapi import FastAPI
from sqlalchemy import Column, Integer, String, ForeignKey,Table, and_, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship,joinedload

#Database configurations
SQLALCHEMY_DATABASE_URL = "sqlite:///./recipes.db" 
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})  #Create db and allow multi-thread
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #Create session to interact with the database   #commit() to save
Base = declarative_base()

#Association table
recipe_ingredient = Table(
    "recipe_ingredient",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True),
)

#Recipe Model
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)

    ingredients = relationship("Ingredient", secondary="recipe_ingredient", back_populates="recipes")

#Ingredient Model
class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
       
    recipes = relationship("Recipe", secondary="recipe_ingredient", back_populates="ingredients")

Base.metadata.create_all(bind=engine)

app = FastAPI()

#Create Ingredient
@app.post("/ingredient/")
async def create_ingredient(ingredient_name: str):
    db = SessionLocal()

    #Check if the ingredient already exists
    existing_ingredient = db.query(Ingredient).filter(Ingredient.name == ingredient_name).first()
    if existing_ingredient:
        return {"message": f"Ingredient {ingredient_name} already exists."}

    #Create a new ingredient
    db_ingredient = Ingredient(name=ingredient_name)
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return {"message": f"Ingredient {db_ingredient.name} successfully created."}


#Search Ingredient by Id
@app.get("/ingredient/{ingredient_id}")
async def read_ingredient_id(ingredient_id: int):
    db = SessionLocal()
    #Use joinedload to ensure recipes are loaded along with the recipe
    db_ingredient = db.query(Ingredient).options(joinedload(Ingredient.recipes)).filter(Ingredient.id == ingredient_id).first()
    return db_ingredient


#Search Ingredient by Name
@app.get("/ingredient/{ingredient_name}")
async def read_ingredient_name(ingredient_name: str):
    db = SessionLocal()
    db_ingredient = db.query(Ingredient).options(joinedload(Ingredient.recipes)).filter(Ingredient.name == ingredient_name).first()
    return db_ingredient


#Get all Ingredients
@app.get("/ingredients/")
async def get_all_ingredients():
    db = SessionLocal()
    db_ingredient = db.query(Ingredient).options(joinedload(Ingredient.recipes)).all()
    return db_ingredient


#Update Ingredient
@app.put("/ingredient/{ingredient_id}")
async def update_ingredient(ingredient_id: int, ingredient_name: str):
    db = SessionLocal()
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    db_ingredient.name = ingredient_name
    return {"message": f"Ingredient {db_ingredient.name} successfully updated."}


#Delete Ingredient
@app.delete("/ingredient/{ingredient_id}")
async def delete_ingredient(ingredient_id: int):
    db = SessionLocal()
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    db.delete(db_ingredient)
    db.commit()
    return {"message": f"Ingredient {db_ingredient.name} successfully deleted."}


#--------------------------------------------------------------------------


#Create Recipe
@app.post("/recipe/")
async def create_recipe(recipe_name: str, input_description: str):
    db = SessionLocal()

    #Check if the recipe already exists
    existing_recipe = db.query(Recipe).filter(Recipe.name == recipe_name).first()
    if existing_recipe:
        return {"message": f"Recipe {recipe_name} already exists."}

    #Create a new recipe
    db_recipe = Recipe(name = recipe_name,description = input_description)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return {"message": f"Recipe {db_recipe.name} successfully created."}


#Seach Recipe by Id
@app.get("/recipe/{recipe_id}")
async def read_recipe_id(recipe_id: int):
    db = SessionLocal()
    #Use joinedload to ensure ingredients are loaded along with the recipe
    db_recipe = db.query(Recipe).options(joinedload(Recipe.ingredients)).filter(Recipe.id == recipe_id).first()
    return db_recipe


#Seach Recipe by Name
@app.get("/recipe/{recipe_name}")
async def read_recipe_name(recipe_name: str):
    db = SessionLocal()
    #Use joinedload to ensure ingredients are loaded along with the recipe
    db_recipe = db.query(Recipe).options(joinedload(Recipe.ingredients)).filter(Recipe.name == recipe_name).first()
    return db_recipe


#Get all Recipes
@app.get("/recipes/")
async def get_all_recipes():
    db = SessionLocal()
    db_recipe = db.query(Recipe).options(joinedload(Recipe.ingredients)).all()
    return db_recipe


#Update Recipe
@app.put("/recipe/{recipe_id}")
async def update_recipe(recipe_id: int, recipe_name:str, input_description:str):
    db = SessionLocal()
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    db_recipe.name = recipe_name
    db_recipe.description = input_description
    db.commit()
    return {"message": f"Recipe {db_recipe.name} successfully updated."}


#Delete Recipe
@app.delete("/recipe/{recipe_id}")
async def delete_recipe(recipe_id: int):
    db = SessionLocal()
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    db.delete(db_recipe)
    return {"message": f"Recipe {db_recipe.name} successfully deleted."}


#--------------------------------------------------------------------------


#Add Ingredient to Recipe by Ingredient_Name
@app.put("/recipe/{recipe_id}/ingredient/{ingredient_name}")
async def add_ingredient_in_recipe(recipe_id: int, ingredient_name: str):
    db = SessionLocal()

    #Check if Recipe exists
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        return {"message": "No such Recipe exists"}

    #Check if Ingredient exists
    db_ingredient = db.query(Ingredient).filter(Ingredient.name == ingredient_name).first()
    if not db_ingredient:
        return {"message": "No such Ingredient exists"}

    #Add Ingredient
    if db_ingredient not in db_recipe.ingredients:
        db_recipe.ingredients.append(db_ingredient)
        db.commit()
        db.refresh(db_recipe)
        return {"message": f"Ingredient {db_ingredient.name} successfully added to recipe {db_recipe.name}."}
    else:
        return {"message": "Ingredient already in recipe"}


#Remove Ingredient from Recipe by Ingredient_Name
@app.delete("/recipe/{recipe_id}/ingredient/{ingredient_name}")
async def delete_ingredient_from_recipe(recipe_id: int, ingredient_name: str):
    db = SessionLocal()

    #Check if Recipe exists
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        return {"message": "No such Recipe exists"}

    #Check if Ingredient exists
    db_ingredient = db.query(Ingredient).filter(Ingredient.name == ingredient_name).first()
    if not db_ingredient:
        return {"message": "No such Ingredient exists"}

    #Remove Ingredient
    if db_ingredient in db_recipe.ingredients:
        db_recipe.ingredients.remove(db_ingredient)
        db.commit()
        db.refresh(db_recipe)
        return {"message": f"Ingredient {db_ingredient.name} successfully removed from recipe {db_recipe.name}."}
    else:
        return {"message": "Ingredient not in recipe"}


#Search Recipe by Ingredients
@app.get("/recipe/ingredient/{ingredients_name}")
async def read_recipe_by_ingredients(ingredients_names: str):
    ingredients_list = ingredients_names.split(",")
    db = SessionLocal()
    db_recipe = db.query(Recipe).join(Recipe.ingredients).filter(Ingredient.name.in_(ingredients_list)).options(joinedload(Recipe.ingredients)).all()
    return db_recipe


if __name__ == "__main__":
    uvicorn.run(app)