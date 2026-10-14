import pandas as pd
from connection import engine

#commandes par mode de livraison
query = """
SELECT
    shipping_mode,
    COUNT(*) AS total_orders

FROM staging.orders

GROUP BY shipping_mode

ORDER BY total_orders DESC;
"""

result = pd.read_sql(query, engine)

print("\n Commandes par mode de livraison :")
print(result)

#Taux de retard par mode de livraison

query = """
SELECT
    shipping_mode,

    COUNT(*) AS total_orders,

    SUM(
        CASE
            WHEN late_delivery_risk = 1
            THEN 1
            ELSE 0
        END
    ) AS late_orders,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN late_delivery_risk = 1
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS late_rate

FROM staging.orders

GROUP BY shipping_mode

ORDER BY late_rate DESC;
"""


result = pd.read_sql(query, engine)

print("\n🚚 Taux de retard par mode de livraison :")
print(result)

#Taux de retard par mode de livraison
query = """
SELECT
    shipping_mode,

    COUNT(*) AS total_orders,

    SUM(
        CASE
            WHEN late_delivery_risk = 1
            THEN 1
            ELSE 0
        END
    ) AS late_orders,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN late_delivery_risk = 1
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS late_rate

FROM staging.orders

GROUP BY shipping_mode

ORDER BY late_rate DESC;
"""


result = pd.read_sql(query, engine)

print("\n🚚 Taux de retard par mode de livraison :")
print(result)

#Analyse par région

query = """
SELECT
    order_region,

    COUNT(*) AS total_orders,

    SUM(
        CASE
            WHEN late_delivery_risk = 1
            THEN 1
            ELSE 0
        END
    ) AS late_orders,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN late_delivery_risk = 1
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS late_rate

FROM staging.orders

GROUP BY order_region

ORDER BY late_rate DESC;
"""


result = pd.read_sql(query, engine)

print("\n🌍 Taux de retard par région :")
print(result)

#Analyse par mois

query = """
SELECT
    order_year,
    order_month,
    COUNT(*) AS total_orders,

    SUM(
        CASE
            WHEN late_delivery_risk = 1
            THEN 1
            ELSE 0
        END
    ) AS late_orders

FROM staging.orders

GROUP BY
    order_year,
    order_month

ORDER BY
    order_year,
    order_month;
"""


result = pd.read_sql(query, engine)

print("\n📅 Commandes et retards par mois :")
print(result)

