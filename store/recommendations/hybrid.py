import pandas as pd

def load_your_dataframe():
    # Load the dataset
    df = pd.read_csv(r"C:\Users\27728\Downloads\rs\New folder\Amazon-Products.csv")
    
    # Print columns and data types for inspection
    print("Columns in DataFrame:", df.columns)
    print("Data types in DataFrame:", df.dtypes)
    
    # Clean the dataset: drop rows with missing user_id, product_id
    df.dropna(subset=['user_id', 'product_id'], inplace=True)  # Drop rows with missing user_id or product_id
    
    # Handle 'ratings' or 'score' column clean-up
    if 'ratings' in df.columns:
        df['ratings'] = pd.to_numeric(df['ratings'], errors='coerce')
        df.dropna(subset=['ratings'], inplace=True)  # Drop rows with invalid ratings after conversion
    elif 'score' in df.columns:
        df['score'] = pd.to_numeric(df['score'], errors='coerce')
        df.dropna(subset=['score'], inplace=True)  # Drop rows with invalid score after conversion
    
    # Display the first few rows to verify the data is cleaned
    print("Data after cleaning:", df.head())
    
    return df

def hybrid_recommendations(user_id, product_id):
    # Load and clean the data
    df = load_your_dataframe()
    
    # Print columns to confirm structure
    print("Columns in DataFrame:", df.columns)
    
    # Check if either 'ratings' or 'score' columns are present
    if 'ratings' in df.columns:
        # Use 'ratings' column if it exists
        pivot_df = df.pivot_table(index='user_id', columns='product_id', values='ratings', aggfunc='mean')
    elif 'score' in df.columns:
        # Use 'score' column if it exists
        pivot_df = df.pivot_table(index='user_id', columns='product_id', values='score', aggfunc='mean')
    else:
        # Raise an error if neither column is found
        raise ValueError("Expected 'ratings' or 'score' column not found in dataset")
    
    # Proceed with recommendation logic (for now, just return the pivot table)
    return pivot_df

# Example call to test
# Replace 'user_id' and 'product_id' with actual values you want to test with
print(hybrid_recommendations(user_id=1, product_id=1))
