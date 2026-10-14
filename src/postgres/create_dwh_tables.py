from sqlalchemy import text
from connection import engine


queries = [

    # =========================
    # DIMENSION DATE
    # =========================
    """
    CREATE TABLE IF NOT EXISTS dwh.dim_date (
        date_key INTEGER PRIMARY KEY,
        full_date DATE,
        year INTEGER,
        month INTEGER,
        month_name VARCHAR(20),
        day INTEGER,
        day_of_week VARCHAR(20),
        quarter INTEGER
    );
    """,

    # =========================
    # DIMENSION CUSTOMER
    # =========================
    """
    CREATE TABLE IF NOT EXISTS dwh.dim_customer (
        customer_key SERIAL PRIMARY KEY,
        customer_id BIGINT UNIQUE,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        segment VARCHAR(100),
        city VARCHAR(150),
        state VARCHAR(150),
        country VARCHAR(150),
        zipcode DOUBLE PRECISION
    );
    """,

    # =========================
    # DIMENSION PRODUCT
    # =========================
    """
    CREATE TABLE IF NOT EXISTS dwh.dim_product (
        product_key SERIAL PRIMARY KEY,
        product_card_id BIGINT UNIQUE,
        product_name TEXT,
        category_id BIGINT,
        category_name VARCHAR(150),
        department_id BIGINT,
        department_name VARCHAR(150),
        product_price DOUBLE PRECISION,
        product_status BIGINT
    );
    """,

    # =========================
    # DIMENSION SHIPPING
    # =========================
    """
    CREATE TABLE IF NOT EXISTS dwh.dim_shipping (
        shipping_key SERIAL PRIMARY KEY,
        shipping_mode VARCHAR(100) UNIQUE,
        scheduled_days INTEGER
    );
    """,

    # =========================
    # DIMENSION LOCATION
    # =========================
    """
    CREATE TABLE IF NOT EXISTS dwh.dim_location (
        location_key SERIAL PRIMARY KEY,
        city VARCHAR(150),
        state VARCHAR(150),
        country VARCHAR(150),
        region VARCHAR(150),
        market VARCHAR(100),
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION,
        UNIQUE(city, state, country, region, market)
    );
    """,

    # =========================
    # FACT ORDERS
    # =========================
    """
    CREATE TABLE IF NOT EXISTS dwh.fact_orders (
        order_item_key BIGINT PRIMARY KEY,

        order_id BIGINT,
        order_item_id BIGINT,

        date_key INTEGER,
        customer_key INTEGER,
        product_key INTEGER,
        shipping_key INTEGER,
        location_key INTEGER,

        quantity INTEGER,
        sales DOUBLE PRECISION,
        discount DOUBLE PRECISION,
        discount_rate DOUBLE PRECISION,
        product_price DOUBLE PRECISION,
        profit_ratio DOUBLE PRECISION,
        benefit_per_order DOUBLE PRECISION,
        order_profit DOUBLE PRECISION,

        days_for_shipping_real INTEGER,
        days_for_shipment_scheduled INTEGER,
        delivery_delay INTEGER,

        late_delivery_risk INTEGER,

        FOREIGN KEY (date_key)
            REFERENCES dwh.dim_date(date_key),

        FOREIGN KEY (customer_key)
            REFERENCES dwh.dim_customer(customer_key),

        FOREIGN KEY (product_key)
            REFERENCES dwh.dim_product(product_key),

        FOREIGN KEY (shipping_key)
            REFERENCES dwh.dim_shipping(shipping_key),

        FOREIGN KEY (location_key)
            REFERENCES dwh.dim_location(location_key)
    );
    """
]


try:

    with engine.begin() as connection:

        for query in queries:
            connection.execute(text(query))

    print("✅ Toutes les tables du Data Warehouse ont été créées !")


except Exception as e:

    print("❌ Erreur :")
    print(e)