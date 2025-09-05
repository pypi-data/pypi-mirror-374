#!/usr/bin/env python3
"""
CPZ AI User-Specific Access Example
Demonstrates user-specific access control for strategies and files
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Add the current directory to Python path so we can import cpz
sys.path.insert(0, '.')

try:
    from cpz.common.cpz_ai import CPZAIClient
    print("✅ Successfully imported CPZAIClient")
except ImportError as e:
    print(f"❌ Failed to import CPZAIClient: {e}")
    sys.exit(1)

def create_sample_dataframe():
    """Create a sample DataFrame for testing"""
    data = {
        'symbol': ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA'],
        'price': [150.25, 2750.80, 310.45, 245.60, 450.30],
        'volume': [1000000, 500000, 800000, 1200000, 900000],
        'change': [2.5, -15.2, 8.7, 12.3, -5.8],
        'sector': ['Technology', 'Technology', 'Technology', 'Automotive', 'Technology']
    }
    return pd.DataFrame(data)

def demonstrate_user_specific_access():
    """Demonstrate user-specific access control"""
    
    print("🚀 CPZ AI User-Specific Access Demo")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API keys are set
    api_key = os.getenv("CPZ_AI_API_KEY")
    secret_key = os.getenv("CPZ_AI_SECRET_KEY")
    user_id = os.getenv("CPZ_AI_USER_ID", "user123")  # Default user ID for demo
    is_admin = os.getenv("CPZ_AI_IS_ADMIN", "false").lower() == "true"
    
    if not api_key or not secret_key:
        print("❌ Please set CPZ_AI_API_KEY and CPZ_AI_SECRET_KEY in your .env file")
        return False
    
    print(f"🔑 API Key: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"🔐 Secret Key: {'✅ Set' if secret_key else '❌ Missing'}")
    print(f"👤 User ID: {user_id}")
    print(f"👑 Admin Access: {'✅ Yes' if is_admin else '❌ No'}")
    
    # Create regular user client
    print(f"\n🔌 Creating regular user client for user: {user_id}")
    user_client = CPZAIClient(
        url="https://api.cpz-lab.com",
        api_key=api_key,
        secret_key=secret_key,
        user_id=user_id,
        is_admin=False
    )
    
    # Create admin client (if admin credentials provided)
    admin_client = None
    if is_admin:
        print(f"\n🔌 Creating admin client")
        admin_client = CPZAIClient(
            url="https://api.cpz-lab.com",
            api_key=api_key,
            secret_key=secret_key,
            user_id=None,
            is_admin=True
        )
    
    # Test connection
    if not user_client.health():
        print("❌ Platform health check failed")
        return False
    
    print("✅ Platform is healthy")
    
    # Test strategies access
    print(f"\n📊 Testing strategies access for user: {user_id}")
    
    # Get user's own strategies
    user_strategies = user_client.get_strategies()
    print(f"✅ User '{user_id}' found {len(user_strategies)} strategies")
    
    if user_strategies:
        print("User's strategies:")
        for i, strategy in enumerate(user_strategies[:3], 1):
            title = strategy.get('title', 'Unknown')
            desc = strategy.get('description', 'No description')
            print(f"  {i}. {title}: {desc}")
    
    # If admin, get all strategies
    if admin_client:
        print(f"\n📊 Admin access - getting ALL strategies:")
        all_strategies = admin_client.get_strategies()
        print(f"✅ Admin found {len(all_strategies)} total strategies")
        
        if all_strategies:
            print("All strategies (admin view):")
            for i, strategy in enumerate(all_strategies[:5], 1):
                title = strategy.get('title', 'Unknown')
                desc = strategy.get('description', 'No description')
                user = strategy.get('user_id', 'Unknown')
                print(f"  {i}. {title} (User: {user}): {desc}")
    
    # Test file operations with user-specific buckets
    print(f"\n📁 Testing user-specific file operations for user: {user_id}")
    
    # Create user-specific bucket
    bucket_name = "user-data"
    print(f"🪣 Creating user-specific bucket: {bucket_name}")
    
    if user_client.create_bucket(bucket_name):
        print(f"✅ User bucket '{bucket_name}-{user_id}' created successfully")
    else:
        print(f"⚠️  User bucket might already exist")
    
    # Create sample DataFrame
    print(f"\n📊 Creating sample DataFrame for user: {user_id}")
    df = create_sample_dataframe()
    print(f"✅ Created DataFrame with {len(df)} rows")
    
    # Upload DataFrame as CSV to user-specific location
    file_path = "stocks.csv"
    print(f"\n📤 Uploading DataFrame as CSV to user-specific location")
    csv_result = user_client.upload_dataframe(bucket_name, file_path, df, format="csv")
    if csv_result:
        print("✅ CSV upload successful to user-specific bucket")
    else:
        print("❌ CSV upload failed")
    
    # List files in user's bucket
    print(f"\n📋 Listing files in user's bucket:")
    user_files = user_client.list_files_in_bucket(bucket_name)
    if user_files:
        for file in user_files:
            name = file.get('name', 'Unknown')
            size = file.get('metadata', {}).get('size', 'Unknown')
            print(f"  📄 {name} (Size: {size} bytes)")
    else:
        print("  No files found in user bucket")
    
    # Download and verify user's file
    print(f"\n📥 Downloading user's CSV file...")
    downloaded_df = user_client.download_csv_to_dataframe(bucket_name, file_path)
    if downloaded_df is not None:
        print("✅ CSV download successful from user-specific bucket")
        print("Downloaded DataFrame:")
        print(downloaded_df.head())
        
        # Verify data integrity
        if df.equals(downloaded_df):
            print("✅ Data integrity verified - user's file is intact!")
        else:
            print("⚠️  Data integrity check failed")
    else:
        print("❌ CSV download failed")
    
    # If admin, test admin file access
    if admin_client:
        print(f"\n📁 Admin testing - accessing user '{user_id}' files:")
        
        # Admin can access user's bucket
        admin_user_files = admin_client.list_files_in_bucket(f"{bucket_name}-{user_id}")
        if admin_user_files:
            print(f"✅ Admin found {len(admin_user_files)} files in user's bucket")
            for file in admin_user_files:
                name = file.get('name', 'Unknown')
                print(f"  📄 {name}")
        else:
            print("  No files found in user's bucket (admin view)")
    
    # Test creating a new strategy for the user
    print(f"\n🚀 Testing strategy creation for user: {user_id}")
    new_strategy_data = {
        "title": f"User {user_id} Strategy",
        "description": f"Personal strategy created by {user_id}",
        "strategy_type": "momentum",
        "status": "active"
    }
    
    new_strategy = user_client.create_strategy(new_strategy_data)
    if new_strategy:
        print(f"✅ Created new strategy for user '{user_id}'")
        print(f"  Title: {new_strategy.get('title', 'Unknown')}")
        print(f"  User ID: {new_strategy.get('user_id', 'Unknown')}")
    else:
        print("❌ Failed to create strategy")
    
    # Verify user can only see their own strategies
    print(f"\n🔍 Verifying user isolation - user '{user_id}' should only see their own strategies:")
    updated_user_strategies = user_client.get_strategies()
    print(f"✅ User '{user_id}' now has {len(updated_user_strategies)} strategies")
    
    # Check that all strategies belong to this user
    user_owned_strategies = [s for s in updated_user_strategies if s.get('user_id') == user_id]
    print(f"✅ User owns {len(user_owned_strategies)} strategies")
    
    if len(user_owned_strategies) == len(updated_user_strategies):
        print("✅ User isolation verified - user only sees their own strategies!")
    else:
        print("⚠️  User isolation issue - user can see other users' strategies")
    
    print("\n🎉 User-specific access demo completed successfully!")
    return True

if __name__ == "__main__":
    success = demonstrate_user_specific_access()
    sys.exit(0 if success else 1)
