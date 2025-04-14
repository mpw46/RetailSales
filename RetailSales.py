# Markus Walker, Matthew Pulsipher, Logan Hodges, Saxon Cullimore, Scott Peterson
# IS 303, Section 004
# When the user selects 1, this code takes data from an excel sheet and loads it into a data frame, separates the name column into two separate first and last name columns and fixes the category column based on the dictionary
# Then the data frame is saved in a database called "sale" and prints a message after doing so
# When the user selects 2, this code displays the categories with a number associated and asks the user to select one
# Then, the sum and average of sales and the sum of quanitity sold are displayed and a table is displayed organizing the data by product
# The code continues asking the user to input 1 or 2 until the user inputs something else, at which time a message is displayed and the program ends

# import libraries
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plot

# initialize selection variable to begin loop, dictionary for the category column, and establish connection string
iSelection = "1"
productCategoriesDict = {
    'Camera': 'Technology',
    'Laptop': 'Technology',
    'Gloves': 'Apparel',
    'Smartphone': 'Technology',
    'Watch': 'Accessories',
    'Backpack': 'Accessories',
    'Water Bottle': 'Household Items',
    'T-shirt': 'Apparel',
    'Notebook': 'Stationery',
    'Sneakers': 'Apparel',
    'Dress': 'Apparel',
    'Scarf': 'Apparel',
    'Pen': 'Stationery',
    'Jeans': 'Apparel',
    'Desk Lamp': 'Household Items',
    'Umbrella': 'Accessories',
    'Sunglasses': 'Accessories',
    'Hat': 'Apparel',
    'Headphones': 'Technology',
    'Charger': 'Technology'}
username = "postgres"
password = "admin"
host = "localhost"
port = "5432"
database = "is303"
engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')

# loop to end program when user inputs something other than 1 or 2
while (iSelection == "1") or (iSelection == "2"):
    # receive user input to determine which block of code to run or exit program
    iSelection = input("If you want to import data, enter 1. If you want to see summaries of stored data, enter 2. Enter any other value to exit the program: ")

    if iSelection == "1":
        # read excel file and assign to data frame variable
        dfSales = pd.read_excel("Retail_Sales_Data.xlsx")

        # create first_name and last_name columns from name column (split by underscore), drop name column, and reorder columns
        dfSales[['first_name', 'last_name']] = dfSales['name'].str.split('_', expand=True)
        dfSales = dfSales.drop('name', axis=1)
        dfSales = dfSales[["sale_id", "first_name", "last_name", "product", "category", "quantity_sold", "sale_date", "unit_price", "total_price", "customer_age_group", "customer_gender", "payment_method"]]

        # fix the category column to match the product that was sold
        dfSales["category"] = dfSales["product"].map(productCategoriesDict)

        # save updated table to is303 postgres database and call it "sale"
        dfSales.to_sql("sale", engine, if_exists = 'replace', index = False)

        # print success message
        print("You've imported the excel file into your postgres database.")

    elif iSelection == "2":
        # import data from database as data frame and create a list of all the unique categories
        dfImported = pd.read_sql_query("SELECT * FROM sale", engine)
        lstCategories = dfImported["category"].unique()

        # print categories
        print("The following are all the categories that have been sold:")
        for iCount in range(0, len(lstCategories)):
            print(f"{str(iCount + 1)}: {lstCategories[iCount]}")

        # ask user to input which category they would like to see
        iCategorySelection = int(input("Please enter the number of the category you want to see summarized: "))

        # create new dataframe that incldues only the rows with the category selected by the user
        iCategorySelection -= 1
        dfCategory = dfImported.query(f'category == "{lstCategories[iCategorySelection]}"')

        # calculate sum and average of sales and sum of quanitity and display
        iSalesSum = dfCategory["total_price"].sum()
        fSalesAvg = round(dfCategory["total_price"].mean(), 2)
        iQuantitySum = dfCategory["quantity_sold"].sum()
        print(f"Total sales for {lstCategories[iCategorySelection]}: {iSalesSum}")
        print(f"Average sale amount for {lstCategories[iCategorySelection]}: {fSalesAvg}")
        print(f"Total units sold for {lstCategories[iCategorySelection]}: {iQuantitySum}")

        # group category dataframe by product, then calculate sum of total price for each product
        dfProductSales = dfCategory.groupby('product')['total_price'].sum()

        # create and display chart
        dfProductSales.plot(kind="bar")
        plot.title(f"Total Sales by Product in {lstCategories[iCategorySelection]}")
        plot.xlabel("Product")
        plot.ylabel("Total Sales")
        plot.show()

    else:
        print("Closing the program.")