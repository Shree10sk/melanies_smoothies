import streamlit as st
from snowflake.snowpark.context import get_active_session

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").to_pandas()

# ✅ Use the correct column name here
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'],   # change this if your column name differs
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')
