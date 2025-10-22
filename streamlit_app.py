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
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)

# Convert to pandas dataframe
pd_df = my_dataframe.to_pandas()

# 🍍 Let user select up to 5 fruits
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# 🍎 Show nutrition info for each selected fruit
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get the SEARCH_ON value for that fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        # Display fruit name as subheader
        st.subheader(f"{fruit_chosen} Nutrition Information")

       
           # 🍎 Get nutrition info from Smoothiefroot API
        try:
            api_url = "https://my.smoothiefroot.com/api/fruit/" + search_on.strip()
            st.write(f"🔍 Fetching: {api_url}")   # 👈 debug line

            smoothiefroot_response = requests.get(api_url)
            smoothiefroot_response.raise_for_status()
            fruit_data = smoothiefroot_response.json()


            # ✅ Display nutrition info cleanly
            if "nutritions" in fruit_data:
                nutrients = fruit_data["nutritions"]
                st.write(f"**Genus:** {fruit_data.get('genus', 'N/A')}")
                st.write(f"**Family:** {fruit_data.get('family', 'N/A')}")
                st.write("### 🥗 Nutrition per 100g:")
                st.table({
                    "Calories": [nutrients.get("calories", "N/A")],
                    "Sugar": [nutrients.get("sugar", "N/A")],
                    "Fat": [nutrients.get("fat", "N/A")],
                    "Carbohydrates": [nutrients.get("carbohydrates", "N/A")],
                    "Protein": [nutrients.get("protein", "N/A")]
                })
            else:
                st.warning("No nutrition data found for this fruit.")

        except Exception as e:
            st.error(f"Sorry, {fruit_chosen} is not in our database.")

    # 🧾 Submit Order Button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your smoothie is ordered, {name_on_order}!")
