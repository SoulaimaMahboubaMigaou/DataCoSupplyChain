from sqlalchemy import text
from connection import engine


query = """
INSERT INTO dwh.fact_orders (
    order_item_key,
    order_id,
    order_item_id,

    date_key,
    customer_key,
    product_key,
    shipping_key,
    location_key,

    quantity,
    sales,
    discount,
    discount_rate,
    product_price,
    profit_ratio,
    benefit_per_order,
    order_profit,

    days_for_shipping_real,
    days_for_shipment_scheduled,
    delivery_delay,

    late_delivery_risk
)

SELECT
    o.order_item_id AS order_item_key,

    o.order_id,
    o.order_item_id,

    d.date_key,
    c.customer_key,
    p.product_key,
    s.shipping_key,
    l.location_key,

    CAST(o.order_item_quantity AS INTEGER),
    o.sales,
    o.order_item_discount,
    o.order_item_discount_rate,
    o.order_item_product_price,
    o.order_item_profit_ratio,
    o.benefit_per_order,
    o.order_profit_per_order,

    CAST(o.days_for_shipping_real AS INTEGER),
    CAST(o.days_for_shipment_scheduled AS INTEGER),
    CAST(o.delivery_delay AS INTEGER),

    CAST(o.late_delivery_risk AS INTEGER)

FROM staging.orders o

JOIN dwh.dim_date d
    ON d.full_date =
       CAST(o.order_date_dateorders AS TIMESTAMP)::DATE

JOIN dwh.dim_customer c
    ON c.customer_id = o.customer_id

JOIN dwh.dim_product p
    ON p.product_card_id = o.product_card_id

JOIN dwh.dim_shipping s
    ON s.shipping_mode = o.shipping_mode

JOIN dwh.dim_location l
    ON l.city = o.order_city
    AND l.state = o.order_state
    AND l.country = o.order_country
    AND l.region = o.order_region
    AND l.market = o.market

ON CONFLICT (order_item_key)
DO NOTHING;
"""


try:

    with engine.begin() as connection:

        result = connection.execute(text(query))

        print(" fact_orders chargée !")
        print(" Lignes insérées :", result.rowcount)

except Exception as e:

    print(" Erreur pendant le chargement de fact_orders :")
    print(e)