import sqlite3

def connect_db():
    return sqlite3.connect('bobert.db')

#Create tables function
def create_tables(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS INGREDIENTS
        (INGREDIENT_ID TEXT PRIMARY KEY NOT NULL,
         INGREDIENT TEXT NOT NULL);
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS MEASUREMENTS
        (MEASUREMENT_ID TEXT PRIMARY KEY NOT NULL,
         MEASUREMENT TEXT NOT NULL);
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS RECIPES
        (RECIPE_ID TEXT PRIMARY KEY NOT NULL,
         RECIPE_NAME TEXT NOT NULL);
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS INSTRUCTIONS
        (INSTRUCTION_ID TEXT PRIMARY KEY NOT NULL,
         INSTRUCTION TEXT NOT NULL,
         RECIPE_ID TEXT NOT NULL,
         STEP INT NOT NULL,
         FOREIGN KEY (RECIPE_ID) REFERENCES RECIPES(RECIPE_ID));
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS RECIPE_INGREDIENTS
        (RECIPE_ID TEXT NOT NULL,
         INGREDIENT_ID TEXT NOT NULL,
         QUANTITY FLOAT NOT NULL,
         MEASUREMENT_ID TEXT NOT NULL,
         PRIMARY KEY (RECIPE_ID, INGREDIENT_ID),
         FOREIGN KEY (RECIPE_ID) REFERENCES RECIPES(RECIPE_ID),
         FOREIGN KEY (INGREDIENT_ID) REFERENCES INGREDIENTS(INGREDIENT_ID),
         FOREIGN KEY (MEASUREMENT_ID) REFERENCES MEASUREMENTS(MEASUREMENT_ID));
    ''')
    print("Tables created successfully")

#Insert data function
def insert_data(conn, table, data):
    placeholders = ', '.join(['?'] * len(data))
    query = f"INSERT INTO {table} VALUES ({placeholders})"
    conn.execute(query, data)
    conn.commit()
    print(f"Data inserted into {table} successfully")

#Update data function
def update_data(conn, table, column, value, condition_column, condition_value):
    query = f"UPDATE {table} SET {column} = ? WHERE {condition_column} = ?"
    conn.execute(query, (value, condition_value))
    conn.commit()
    print(f"Data in {table} updated successfully")

#Delete data function
def delete_data(conn, table, condition_column, condition_value):
    query = f"DELETE FROM {table} WHERE {condition_column} = ?"
    conn.execute(query, (condition_value,))
    conn.commit()
    print(f"Data from {table} deleted successfully")

#Retrieve data function
def retrieve_data(conn, table):
    cursor = conn.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

#Add a new recipe function
def add_recipe(conn, recipe_id, recipe_name, instructions, ingredients):
    try:
        # Insert the recipe into the RECIPES table
        conn.execute('''
            INSERT INTO RECIPES (RECIPE_ID, RECIPE_NAME)
            VALUES (?, ?)
        ''', (recipe_id, recipe_name))
        
        # Insert instructions into the INSTRUCTIONS table
        for instruction in instructions:
            conn.execute('''
                INSERT INTO INSTRUCTIONS (INSTRUCTION_ID, INSTRUCTION, RECIPE_ID, STEP)
                VALUES (?, ?, ?, ?)
            ''', instruction)
        
        # Insert ingredients into the RECIPE_INGREDIENTS table
        for ingredient in ingredients:
            conn.execute('''
                INSERT INTO RECIPE_INGREDIENTS (RECIPE_ID, INGREDIENT_ID, QUANTITY, MEASUREMENT_ID)
                VALUES (?, ?, ?, ?)
            ''', ingredient)
        
        conn.commit()
        print(f"Recipe '{recipe_name}' added successfully")
    except sqlite3.Error as e:
        print(f"An error occurred while adding the recipe: {e}")

#Delete recipe function
def delete_recipe(conn, recipe_id):
    try:
        # Delete the recipe from the RECIPES table
        conn.execute('''
            DELETE FROM RECIPES WHERE RECIPE_ID = ?
        ''', (recipe_id,))
        
        # Delete instructions related to the recipe from the INSTRUCTIONS table
        conn.execute('''
            DELETE FROM INSTRUCTIONS WHERE RECIPE_ID = ?
        ''', (recipe_id,))
        
        # Delete ingredients related to the recipe from the RECIPE_INGREDIENTS table
        conn.execute('''
            DELETE FROM RECIPE_INGREDIENTS WHERE RECIPE_ID = ?
        ''', (recipe_id,))
        
        conn.commit()
        print(f"Recipe with ID '{recipe_id}' deleted successfully")
    except sqlite3.Error as e:
        print(f"An error occurred while deleting the recipe: {e}")

#Retrieve recipe function
def retrieve_recipe(conn, recipe_id):
    recipe_name_query = '''
        SELECT RECIPE_NAME FROM RECIPES WHERE RECIPE_ID = ?
    '''
    recipe_name = conn.execute(recipe_name_query, (recipe_id,)).fetchone()[0]

    ingredients_query = '''
        SELECT INGREDIENTS.INGREDIENT, RECIPE_INGREDIENTS.QUANTITY, MEASUREMENTS.MEASUREMENT
        FROM RECIPE_INGREDIENTS
        JOIN INGREDIENTS ON RECIPE_INGREDIENTS.INGREDIENT_ID = INGREDIENTS.INGREDIENT_ID
        JOIN MEASUREMENTS ON RECIPE_INGREDIENTS.MEASUREMENT_ID = MEASUREMENTS.MEASUREMENT_ID
        WHERE RECIPE_INGREDIENTS.RECIPE_ID = ?
    '''
    ingredients = conn.execute(ingredients_query, (recipe_id,)).fetchall()

    instructions_query = '''
        SELECT STEP, INSTRUCTION FROM INSTRUCTIONS WHERE RECIPE_ID = ? ORDER BY STEP
    '''
    instructions = conn.execute(instructions_query, (recipe_id,)).fetchall()

    print(f"Recipe: {recipe_name}\n")
    print("Ingredients:")
    for ingredient, quantity, measurement in ingredients:
        print(f"- {quantity} {measurement} of {ingredient}")

    print("\nInstructions:")
    for step, instruction in instructions:
        print(f"Step {step}: {instruction}")


def main():
    conn = connect_db()
    create_tables(conn)

    # Initial data
    insert_data(conn, 'INGREDIENTS', ('01', 'Granny Smith Apples'))
    insert_data(conn, 'INGREDIENTS', ('02', 'Granulated Sugar'))
    insert_data(conn, 'INGREDIENTS', ('03', 'Brown Sugar'))
    insert_data(conn, 'INGREDIENTS', ('04', 'All-Purpose Flour'))
    insert_data(conn, 'INGREDIENTS', ('05', 'Ground Cinnamon'))
    insert_data(conn, 'INGREDIENTS', ('06', 'Ground Nutmeg'))
    insert_data(conn, 'INGREDIENTS', ('07', 'Eggs'))
    insert_data(conn, 'INGREDIENTS', ('08', 'Pie Crust'))
    insert_data(conn, 'MEASUREMENTS', ('1', 'Cups'))
    insert_data(conn, 'MEASUREMENTS', ('2', 'Teaspoon'))
    insert_data(conn, 'MEASUREMENTS', ('3', 'Tablespoon'))
    insert_data(conn, 'MEASUREMENTS', ('4', 'Unit'))

    # Adding new recipes
    add_recipe(
        conn,
        '1',
        'Apple Pie',
        [
            ('01', 'Preheat oven to 400°F (200°C).', '1', 1),
            ('02', 'Peel and slice apples.', '1', 2),
            ('03', 'In a large bowl, combine ingredients.', '1', 3),
            ('04', 'Bake for 45 mins.', '1', 4)
        ],
        [
            ('1', '01', 7, '4'),
            ('1', '02', 0.5, '1'),
            ('1', '03', 0.5, '1'),
            ('1', '04', 2, '3'),
            ('1', '05', 1, '2'),
            ('1', '06', 0.125, '2'),
            ('1', '07', 1, '4'),
            ('1', '08', 1, '4')
        ]
    )

    add_recipe(
        conn,
        '2',
        'Sourdough Banana Bread',
        [
            ('05', 'Preheat oven to 350°F (176°C) and lightly grease a 9" x 5" loaf pan.', '2', 1),
            ('06', 'Whisk together flour, salt and baking soda and mash bananas until smooth.', '2', 2),
            ('07', 'Preheat oven to 350°F (176°C) and lightly grease a 9" x 5" loaf pan.', '2', 3),
            ('08', 'Melt butter and combine with brown sugar, sourdough starter, vanilla extract, sour cream, and mashed bananas.', '2', 4),
            ('09', 'Combine wet and dry ingredients and pour batter into pan.', '2', 5),
            ('10', 'Bake for 50-60 minutes.', '2', 6)
        ],
        [
            ('2', '09', 8, '3'),
            ('2', '03', 1, '1'),
            ('2', '07', 2, '4'),
            ('2', '10', 3, '4'),
            ('2', '11', 3, '3'),
            ('2', '12', 1, '2'),
            ('2', '13', 0.5, '1')
        ]
    )

    # Update data example
    update_data(conn, 'INGREDIENTS', 'INGREDIENT', 'Golden Delicious Apples', 'INGREDIENT_ID', '01')

    # Delete data example
    delete_data(conn, 'INGREDIENTS', 'INGREDIENT_ID', '02')

    # Retrieve data from tables
    print("\nINGREDIENTS table:")
    retrieve_data(conn, 'INGREDIENTS')

    print("\nMEASUREMENTS table:")
    retrieve_data(conn, 'MEASUREMENTS')

    print("\nRECIPES table:")
    retrieve_data(conn, 'RECIPES')

    print("\nINSTRUCTIONS table:")
    retrieve_data(conn, 'INSTRUCTIONS')

    print("\nRECIPE_INGREDIENTS table:")
    retrieve_data(conn, 'RECIPE_INGREDIENTS')

    # Display recipes
    print("\nDisplaying Apple Pie Recipe:")
    retrieve_recipe(conn, '1')

    print("\nDisplaying Sourdough Banana Bread Recipe:")
    retrieve_recipe(conn, '2')

    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()