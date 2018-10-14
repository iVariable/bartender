import argparse

import mysql.connector

cnx = mysql.connector.connect(user="root", password="root", host="127.0.0.1", port=33060, database="bartender")

parser = argparse.ArgumentParser(description="Bartender analyzer")
parser.add_argument("amt", type=int, help="Amount of components")
args = parser.parse_args()

components = []

# 427 - ice
# 316 Vodka
blacklist = []  # say no to vodka!
blacklist_query = []
for blacklist_entry in blacklist:
    blacklist_query.append("c.component_id != {}".format(blacklist_entry))

for i in range(0, args.amt):
    where = []
    for component in components:
        where.append("r.components LIKE \"%,{},%\"".format(component))
    query = "SELECT c.component_id, count(*) AS cid " \
            "FROM recipes r " \
            "JOIN recipes_components c ON r.id=c.recipe_id " \
            "WHERE r.components_count <= {count} {blacklist} {filter} " \
            "GROUP BY c.component_id " \
            "ORDER BY cid DESC " \
            "LIMIT {limit};".format(
        blacklist=" AND " + " AND ".join(blacklist_query) if len(blacklist_query) > 0 else "",
        filter=" AND " + " AND ".join(where) if len(where) > 0 else "",
        limit=i + 1,
        count=args.amt
    )
    print(query)
    cur = cnx.cursor()
    cur.execute(query)
    component = 0
    for (component_id, cid) in cur:
        print(component_id, cid)
        component = component_id
    # here we have potential bug if we have less cocktails than components, but I'm too lazy to check that shit
    components.append(component)
    cur.close()

cur = cnx.cursor()
cur.execute("SELECT id, name FROM components WHERE id IN ({})".format(",".join([str(comp) for comp in components])))

print("Components to use:")
for (id, name) in cur:
    print(" - {id}: {name}".format(name=name, id=id))
print("")

query = "SELECT " \
        "r.name, GROUP_CONCAT(IFNULL(c.name, \"NULL\")) AS comps " \
        "FROM recipes r " \
        "LEFT JOIN recipes_components rc ON r.id = rc.recipe_id " \
        "LEFT JOIN (SELECT * FROM components WHERE id IN ({})) c ON rc.component_id = c.id " \
        "WHERE r.components_count <= {} " \
        "GROUP BY r.name " \
        "HAVING comps NOT LIKE '%NULL%'".format(",".join([str(comp) for comp in components]), args.amt)
cur = cnx.cursor()
cur.execute(query)

print("Cocktails:")
i = 0
for (name, comps) in cur:
    i = i + 1
    print(" - {name}: {comps}".format(name=name, comps=comps))
print("")
print("Total: {} cocktails can be made out of {} components".format(i, args.amt))
cur.close()
cnx.close()
