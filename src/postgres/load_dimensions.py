from sqlalchemy import text
from connection import engine


def load_customers():

    query = """
    INSERT INTO dwh.dim_customer (
        customer_id,
        first_name,
        last_name,
        segment,
        city,
        state,
        country,
        zipcode
    )

    SELECT DISTINCT
        customer_id,
        customer_fname,
        customer_lname,
        customer_segment,
        customer_city,
        customer_state,
        customer_country,
        customer_zipcode

    FROM staging.orders

    WHERE customer_id IS NOT NULL

    ON CONFLICT (customer_id)
    DO NOTHING;
    """

    with engine.begin() as connection:
        connection.execute(text(query))

    print("✅ dim_customer chargée")

def load_products():

    query = """
    INSERT INTO dwh.dim_product (
        product_card_id,
        product_name,
        category_id,
        category_name,
        department_id,
        department_name,
        product_price,
        product_status
    )

    SELECT DISTINCT
        product_card_id,
        product_name,
        category_id,
        category_name,
        department_id,
        department_name,
        product_price,
        product_status

    FROM staging.orders

    WHERE product_card_id IS NOT NULL

    ON CONFLICT (product_card_id)
    DO NOTHING;
    """

    with engine.begin() as connection:
        connection.execute(text(query))

    print("✅ dim_product chargée")

def load_shipping():

    query = """
    INSERT INTO dwh.dim_shipping (
        shipping_mode,
        scheduled_days
    )

    SELECT DISTINCT
        shipping_mode,
        CAST(days_for_shipment_scheduled AS INTEGER)

    FROM staging.orders

    WHERE shipping_mode IS NOT NULL

    ON CONFLICT (shipping_mode)
    DO NOTHING;
    """

    with engine.begin() as connection:
        connection.execute(text(query))

    print("✅ dim_shipping chargée")

def load_locations():

    query = """
    INSERT INTO dwh.dim_location (
        city,
        state,
        country,
        region,
        market,
        latitude,
        longitude
    )

    SELECT DISTINCT
        order_city,
        order_state,
        order_country,
        order_region,
        market,
        latitude,
        longitude

    FROM staging.orders

    WHERE order_city IS NOT NULL

    ON CONFLICT (city, state, country, region, market)
    DO NOTHING;
    """

    with engine.begin() as connection:
        connection.execute(text(query))

    print("✅ dim_location chargée")

def load_dates():

    query = """
    INSERT INTO dwh.dim_date (
        date_key,
        full_date,
        year,
        month,
        month_name,
        day,
        day_of_week,
        quarter
    )

    SELECT DISTINCT

        CAST(
            TO_CHAR(
                TO_DATE(order_date_dateorders, 'YYYY-MM-DD'),
                'YYYYMMDD'
            )
            AS INTEGER
        ) AS date_key,

        TO_DATE(
            order_date_dateorders,
            'YYYY-MM-DD'
        ) AS full_date,

        order_year,
        order_month,
        order_month_name,
        order_day,
        order_day_of_week,
        order_quarter

    FROM staging.orders

    WHERE order_date_dateorders IS NOT NULL

    ON CONFLICT (date_key)
    DO NOTHING;
    """

    with engine.begin() as connection:
        connection.execute(text(query))

    print("✅ dim_date chargée")

if __name__ == "__main__":

    load_customers()
    load_products()
    load_shipping()
    load_locations()
    load_dates()

    print("\n🎉 Toutes les dimensions sont chargées !")