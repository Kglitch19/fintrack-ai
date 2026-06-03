import pandas as pd

# Load the CSV
data = pd.read_csv("data/financial_data.csv")

# Show first few rows
print("Sample Financial Data:")
print(data.head())
