import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.get_database('big_data')
games_collection = db.get_collection('games')
publishers_collection = db.get_collection('publishers')

# Fetch the data
games = list(games_collection.find())
publishers = list(publishers_collection.find())

# Convert the data to pandas DataFrame
games_df = pd.DataFrame(games)
publishers_df = pd.DataFrame(publishers)

# Convert ObjectId to string
games_df['PublisherId'] = games_df['PublisherId'].astype(str)
publishers_df['_id'] = publishers_df['_id'].astype(str)

# Flatten the Sales field
sales_df = pd.json_normalize(games_df['Sales'])
sales_df.columns = ['Global_Sales', 'JP_Sales', 'EU_Sales', 'Other_Sales', 'NA_Sales']
games_df = games_df.drop(columns=['Sales']).join(sales_df)

# Merge games and publishers on PublisherId
merged_df = games_df.merge(publishers_df, left_on='PublisherId', right_on='_id', suffixes=('', '_Publisher'))
# Convert Year to numeric
merged_df['Year'] = pd.to_numeric(merged_df['Year'], errors='coerce')
merged_df = merged_df.dropna(subset=['Year'])
merged_df['Year'] = merged_df['Year'].astype(int)
# Pie Chart - Distribution of game genres
genre_counts = merged_df['Genre'].value_counts()
plt.figure(figsize=(10, 7))
plt.pie(genre_counts, labels=genre_counts.index, autopct='%1.1f%%', startangle=140)
plt.title('Distribution of Game Genres')
plt.show()

# Bar Chart - Global sales of games by publisher
publisher_sales = merged_df.groupby('Publisher')['Global_Sales'].sum().sort_values(ascending=False)
plt.figure(figsize=(12, 8))
publisher_sales.plot(kind='bar')
plt.title('Global Sales of Games by Publisher')
plt.xlabel('Publisher')
plt.ylabel('Global Sales (in millions)')
plt.show()

# Bar Chart - Sales distribution of top 5 games globally
top_games = merged_df.nlargest(5, 'Global_Sales')
top_games.set_index('Name', inplace=True)
top_games[['Global_Sales', 'JP_Sales', 'EU_Sales', 'Other_Sales', 'NA_Sales']].plot(kind='bar', figsize=(15, 10))
plt.title('Sales Distribution of Top 5 Games Globally')
plt.xlabel('Game')
plt.ylabel('Sales (in millions)')
plt.show()

# Bar Chart - Sales by Year
year_sales = merged_df.groupby('Year')['Global_Sales'].sum().sort_values(ascending=False)
plt.figure(figsize=(12, 8))
year_sales.plot(kind='bar')
plt.title('Global Sales of Games by Year')
plt.xlabel('Year')
plt.ylabel('Global Sales (in millions)')
plt.show()

# Pie Chart - Sales Distribution by Platform
platform_sales = merged_df.groupby('Platform')['Global_Sales'].sum()
plt.figure(figsize=(10, 7))
plt.pie(platform_sales, labels=platform_sales.index, autopct='%1.1f%%', startangle=140)
plt.title('Sales Distribution by Platform')
plt.show()

# Bar Chart - Sales Distribution of the Top Publisher's Games
top_publisher = merged_df['Publisher'].value_counts().idxmax()
top_publisher_games = merged_df[merged_df['Publisher'] == top_publisher]
top_publisher_games.set_index('Name', inplace=True)
top_publisher_games = top_publisher_games.sort_values(by='Global_Sales', ascending=False)
plt.figure(figsize=(15, 10))
top_publisher_games[['Global_Sales', 'JP_Sales', 'EU_Sales', 'Other_Sales', 'NA_Sales']].plot(kind='bar', stacked=True)
plt.title(f'Sales Distribution of {top_publisher}\'s Games')
plt.xlabel('Game')
plt.ylabel('Sales (in millions)')
plt.legend(loc='upper right')
plt.show()



# Line Chart - Global Sales Trend Over Years
year_sales = merged_df.groupby('Year')['Global_Sales'].sum().sort_index()
plt.figure(figsize=(12, 8))
year_sales.plot(kind='line', marker='o')
plt.title('Global Sales Trend Over Years')
plt.xlabel('Year')
plt.ylabel('Global Sales (in millions)')
plt.grid(True)
plt.show()

# Stacked Bar Chart - Sales Distribution by Genre
genre_sales = merged_df.groupby('Genre')[['Global_Sales', 'JP_Sales', 'EU_Sales', 'Other_Sales', 'NA_Sales']].sum()
genre_sales = genre_sales.sort_values(by='Global_Sales', ascending=False)
plt.figure(figsize=(15, 10))
genre_sales.plot(kind='bar', stacked=True)
plt.title('Sales Distribution by Genre')
plt.xlabel('Genre')
plt.ylabel('Sales (in millions)')
plt.legend(loc='upper right')
plt.show()

# Histogram - Distribution of Game Sales
plt.figure(figsize=(12, 8))
plt.hist(merged_df['Global_Sales'], bins=20, edgecolor='black')
plt.title('Distribution of Global Game Sales')
plt.xlabel('Global Sales (in millions)')
plt.ylabel('Number of Games')
plt.grid(True)
plt.show()

# Bar Chart - Top 10 Games by EU Sales
top_10_eu_sales = merged_df.sort_values(by='EU_Sales', ascending=False).head(10)
plt.figure(figsize=(15, 10))
plt.bar(top_10_eu_sales['Name'], top_10_eu_sales['EU_Sales'], color='skyblue')
plt.title('Top 10 Games by EU Sales')
plt.xlabel('Game')
plt.ylabel('EU Sales (in millions)')
plt.xticks(rotation=45, ha='right')
plt.show()


# Line Chart - Annual EU Sales Trend
annual_eu_sales = merged_df.groupby('Year')['EU_Sales'].sum()
plt.figure(figsize=(12, 8))
plt.plot(annual_eu_sales.index, annual_eu_sales.values, marker='o', linestyle='-', color='green')
plt.title('Annual EU Sales Trend')
plt.xlabel('Year')
plt.ylabel('EU Sales (in millions)')
plt.grid(True)
plt.show()