import pandas as pd
from connection import engine


query = """
SELECT
    shipping_mode,
    COUNT(DISTINCT days_for_shipment_scheduled) AS nb_scheduled_days
FROM staging.orders
GROUP BY shipping_mode
HAVING COUNT(DISTINCT days_for_shipment_scheduled) > 1;
"""

result = pd.read_sql(query, engine)

print("\n🚚 Vérification Shipping :\n")

if result.empty:
    print("✅ Aucun conflit : chaque shipping_mode possède un seul nombre de jours.")
else:
    print("⚠️ Conflits détectés :")
    print(result.to_string(index=False))

#check_products

query = """
SELECT
    product_card_id,
    COUNT(DISTINCT product_name) AS nb_names,
    COUNT(DISTINCT product_price) AS nb_prices,
    COUNT(DISTINCT category_id) AS nb_categories
FROM staging.orders
WHERE product_card_id IS NOT NULL
GROUP BY product_card_id
HAVING
    COUNT(DISTINCT product_name) > 1
    OR COUNT(DISTINCT product_price) > 1
    OR COUNT(DISTINCT category_id) > 1;
"""

result = pd.read_sql(query, engine)

print("\n📦 Vérification Produits :\n")

if result.empty:
    print("✅ Aucun conflit détecté dans les produits.")
else:
    print("⚠️ Conflits détectés :")
    print(result.head(20).to_string(index=False))

#check_customers


query = """
SELECT
    customer_id,
    COUNT(DISTINCT customer_fname) AS nb_first_names,
    COUNT(DISTINCT customer_lname) AS nb_last_names,
    COUNT(DISTINCT customer_segment) AS nb_segments
FROM staging.orders
WHERE customer_id IS NOT NULL
GROUP BY customer_id
HAVING
    COUNT(DISTINCT customer_fname) > 1
    OR COUNT(DISTINCT customer_lname) > 1
    OR COUNT(DISTINCT customer_segment) > 1;
"""

result = pd.read_sql(query, engine)

print("\n👤 Vérification Clients :\n")

if result.empty:
    print("✅ Aucun conflit détecté dans les clients.")
else:
    print("⚠️ Conflits détectés :")
    print(result.head(20).to_string(index=False))
