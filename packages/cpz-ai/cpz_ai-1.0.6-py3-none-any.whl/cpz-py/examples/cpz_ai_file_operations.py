#!/usr/bin/env python3
"""
CPZ AI File Operations Example
Demonstrates file upload/download, CSV handling, and DataFrame operations
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

def demonstrate_file_operations():
    """Demonstrate all file operations"""
    
    print("🚀 CPZ AI File Operations Demo")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API keys are set
    api_key = os.getenv("CPZ_AI_API_KEY")
    secret_key = os.getenv("CPZ_AI_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("❌ Please set CPZ_AI_API_KEY and CPZ_AI_SECRET_KEY in your .env file")
        return False
    
    # Create client
    client = CPZAIClient(
        url="https://api.cpz-lab.com",
        api_key=api_key,
        secret_key=secret_key
    )
    
    print("🔌 CPZ AI client created successfully")
    
    # Test connection
    if not client.health():
        print("❌ Platform health check failed")
        return False
    
    print("✅ Platform is healthy")
    
    # Create a storage bucket for our files
    bucket_name = "cpz-ai-data"
    print(f"\n🪣 Creating storage bucket: {bucket_name}")
    
    if client.create_bucket(bucket_name):
        print(f"✅ Bucket '{bucket_name}' created successfully")
    else:
        print(f"⚠️  Bucket '{bucket_name}' might already exist or creation failed")
    
    # Create sample DataFrame
    print("\n📊 Creating sample DataFrame...")
    df = create_sample_dataframe()
    print(f"✅ Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
    print(df.head())
    
    # Upload DataFrame as CSV
    print(f"\n📤 Uploading DataFrame as CSV to {bucket_name}/sample_data.csv")
    csv_result = client.upload_dataframe(bucket_name, "sample_data.csv", df, format="csv")
    if csv_result:
        print("✅ CSV upload successful")
    else:
        print("❌ CSV upload failed")
    
    # Upload DataFrame as JSON
    print(f"\n📤 Uploading DataFrame as JSON to {bucket_name}/sample_data.json")
    json_result = client.upload_dataframe(bucket_name, "sample_data.json", df, format="json")
    if json_result:
        print("✅ JSON upload successful")
    else:
        print("❌ JSON upload failed")
    
    # Upload DataFrame as Parquet
    print(f"\n📤 Uploading DataFrame as Parquet to {bucket_name}/sample_data.parquet")
    parquet_result = client.upload_dataframe(bucket_name, "sample_data.parquet", df, format="parquet")
    if parquet_result:
        print("✅ Parquet upload successful")
    else:
        print("❌ Parquet upload failed")
    
    # List files in bucket
    print(f"\n📋 Listing files in bucket '{bucket_name}':")
    files = client.list_files_in_bucket(bucket_name)
    if files:
        for file in files:
            name = file.get('name', 'Unknown')
            size = file.get('metadata', {}).get('size', 'Unknown')
            print(f"  📄 {name} (Size: {size} bytes)")
    else:
        print("  No files found")
    
    # Download and load CSV back to DataFrame
    print(f"\n📥 Downloading CSV and loading to DataFrame...")
    downloaded_df = client.download_csv_to_dataframe(bucket_name, "sample_data.csv")
    if downloaded_df is not None:
        print("✅ CSV download and DataFrame load successful")
        print("Downloaded DataFrame:")
        print(downloaded_df.head())
        
        # Verify data integrity
        if df.equals(downloaded_df):
            print("✅ Data integrity verified - uploaded and downloaded DataFrames match!")
        else:
            print("⚠️  Data integrity check failed - DataFrames don't match")
    else:
        print("❌ CSV download failed")
    
    # Download and load JSON back to DataFrame
    print(f"\n📥 Downloading JSON and loading to DataFrame...")
    downloaded_json_df = client.download_json_to_dataframe(bucket_name, "sample_data.json")
    if downloaded_json_df is not None:
        print("✅ JSON download and DataFrame load successful")
        print("Downloaded JSON DataFrame:")
        print(downloaded_json_df.head())
    else:
        print("❌ JSON download failed")
    
    # Download and load Parquet back to DataFrame
    print(f"\n📥 Downloading Parquet and loading to DataFrame...")
    downloaded_parquet_df = client.download_parquet_to_dataframe(bucket_name, "sample_data.parquet")
    if downloaded_parquet_df is not None:
        print("✅ Parquet download and DataFrame load successful")
        print("Downloaded Parquet DataFrame:")
        print(downloaded_parquet_df.head())
    else:
        print("❌ Parquet download failed")
    
    # Test file deletion
    print(f"\n🗑️  Testing file deletion...")
    if client.delete_file(bucket_name, "sample_data.csv"):
        print("✅ CSV file deleted successfully")
    else:
        print("❌ CSV file deletion failed")
    
    # List files again to confirm deletion
    print(f"\n📋 Files in bucket after deletion:")
    remaining_files = client.list_files_in_bucket(bucket_name)
    if remaining_files:
        for file in remaining_files:
            name = file.get('name', 'Unknown')
            print(f"  📄 {name}")
    else:
        print("  No files remaining")
    
    print("\n🎉 File operations demo completed successfully!")
    return True

if __name__ == "__main__":
    success = demonstrate_file_operations()
    sys.exit(0 if success else 1)
