#!/usr/bin/env python3
"""
Example: Load User Strategies into Pandas DataFrame
Demonstrates how to fetch strategies for a specific user and convert to DataFrame
"""

from cpz.common.cpz_ai import CPZAIClient
import pandas as pd

def load_user_strategies(user_id: str, api_key: str, secret_key: str, url: str):
    """
    Load all strategies for a specific user into a pandas DataFrame
    
    Args:
        user_id: The user's unique identifier (UUID format)
        api_key: Your CPZ AI API key
        secret_key: Your CPZ AI secret key  
        url: Your CPZ AI platform URL
    
    Returns:
        pandas.DataFrame: DataFrame containing user's strategies
    """
    
    # Create client for the specific user (not admin)
    client = CPZAIClient(
        url=url,
        api_key=api_key,
        secret_key=secret_key,
        user_id=user_id,
        is_admin=False
    )
    
    # Get all strategies for this user
    strategies = client.get_strategies()
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(strategies)
    
    return df

def main():
    """Example usage"""
    
    # IMPORTANT: Replace these with your actual values
    # DO NOT commit real API keys or user IDs to version control
    
    USER_ID = "your-user-uuid-here"  # Replace with actual user UUID
    API_KEY = "your-api-key-here"    # Replace with actual API key
    SECRET_KEY = "your-secret-key-here"  # Replace with actual secret key
    PLATFORM_URL = "https://api.cpz-lab.com"  # Replace with actual URL
    
    try:
        # Load user strategies
        df = load_user_strategies(USER_ID, API_KEY, SECRET_KEY, PLATFORM_URL)
        
        # Display results
        print(f"Found {len(df)} strategies for user {USER_ID}")
        
        if not df.empty:
            print("\nDataFrame shape:", df.shape)
            print("\nColumns:", df.columns.tolist())
            print("\nFirst few strategies:")
            print(df.head())
            
            # Show strategy titles if available
            if 'title' in df.columns:
                print("\nStrategy titles:")
                print(df['title'].tolist())
            
            # Show strategy types if available
            if 'strategy_type' in df.columns:
                print("\nStrategy types:")
                print(df['strategy_type'].tolist())
                
        else:
            print("No strategies found for this user")
            
    except Exception as e:
        print(f"Error loading strategies: {e}")

if __name__ == "__main__":
    main()
