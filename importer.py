import json
import mysql.connector

cnx = mysql.connector.connect(user="root", password="root", host="127.0.0.1", port=33060)

cur = cnx.cursor()

cur.execute("DROP DATABASE IF EXISTS bartender;")
cur.execute("CREATE DATABASE bartender;")
cur.execute("USE bartender;")

cur.execute("CREATE TABLE components (id int NOT NULL AUTO_INCREMENT, name VARCHAR(200), PRIMARY KEY (id));")
cur.execute(
    "CREATE TABLE recipes (id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT, name VARCHAR(200), components VARCHAR(1000), components_count integer);")
cur.execute("CREATE TABLE recipes_components ("
            "recipe_id INTEGER, "
            "component_id INTEGER, "
            "FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE, "
            "FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE"
            ");")
cnx.commit()

cocktails = json.load(open("items_webtender_6.json"))
len_cocktails = len(cocktails)
i = 0
for cocktail in cocktails:
    i = i + 1
    cur.execute(
        "INSERT INTO recipes (`name`, `components`, `components_count`) VALUES (%(name)s, %(components)s, %(components_count)s);",
        {"name": cocktail['name'], "components": "," + ",".join([str(item[2]) for item in cocktail['recipe']]) + ",",
         "components_count": len(cocktail['recipe'])})
    cnx.commit()
    recipe_id = cur.lastrowid
    for item in cocktail['recipe']:
        cur.execute("INSERT IGNORE INTO components VALUES(%(id)s, %(name)s);", {"id": item[2], "name": item[0]})
        cur.execute("INSERT INTO recipes_components VALUES(%(recipe_id)s, %(component_id)s);",
                    {"recipe_id": recipe_id, "component_id": item[2]})
    cnx.commit()
    print("{}/{}".format(i, len_cocktails))

cnx.close()
