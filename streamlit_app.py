import streamlit as st
from snowflake.snowpark.functions import col
import requests

# 🧋 App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# 🧾 Input: Name on smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# ❄️ Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# 🍉 Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

                                                                                             # 🍍 Let user select up to 5 fruits
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'],
    max_selections=5
)

# 🍎 Show nutrition info for each selected fruit
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        # Display fruit name as subheader
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Get nutrition info from Smoothiefroot API
        try:
            smoothiefroot_response = requests.get(
                "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
            )
            smoothiefroot_response.raise_for_status()  # Check if response is OK
            fruit_data = smoothiefroot_response.json()

           

        except Exception as e:
            # If fruit not found or API fails
            st.error(f"Sorry, {fruit_chosen} is not in our database.")

    # 🧾 Submit Order Button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Insert order details into Snowflake
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()

        # ✅ Success message
        st.success(f"✅ Your smoothie is ordered, {name_on_order}!")
