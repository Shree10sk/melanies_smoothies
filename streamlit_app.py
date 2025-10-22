import streamlit as st
from snowflake.snowpark.functions import col

import requests

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'],
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # insert the order into Snowflake
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()

        # ✅ show success message with green tick
        st.success(f"✅ Your smoothie is ordered, {name_on_order}!")


