#!/usr/bin/env python3
"""
CPZ AI Platform Integration Example

This example shows how to:
1. Connect to your CPZ AI Platform account
2. Access your strategies from public.strategies table
3. Access your files from the files table
4. Create, update, and delete strategies and files

Prerequisites:
1. Install cpz-ai: pip install cpz-ai
2. Set up your .env file with CPZ_AI_API_KEY and CPZ_AI_SECRET_KEY
3. Have an account at https://ai.cpz-lab.com (for API keys)
"""

import os
from dotenv import load_dotenv
from cpz.common.cpz_ai import CPZAIClient

# Load environment variables
load_dotenv()

def main():
    """Main function demonstrating CPZ AI Platform integration"""
    
    print("🚀 CPZ AI Platform Integration Example")
    print("=" * 50)
    
    # 1. Connect to CPZ AI
    print("\n1. Connecting to CPZ AI...")
    platform = CPZAIClient.from_env()
    
    # Check connection health
    if not client.health():
        print("❌ Failed to connect to CPZ AI")
        print("Please check your API keys and network connection")
        return
    
    print("✅ Successfully connected to CPZ AI!")
    
    # 2. Access Strategies
    print("\n2. Accessing your strategies...")
    
    # Get all strategies
    strategies = client.get_strategies()
    print(f"📊 Found {len(strategies)} strategies")
    
    if strategies:
        print("Your strategies:")
        for strategy in strategies:
            print(f"  - {strategy.get('name', 'Unknown')}: {strategy.get('description', 'No description')}")
    
    # 3. Access Files
    print("\n3. Accessing your files...")
    
    # Get all files
    files = client.get_files()
    print(f"📁 Found {len(files)} files")
    
    if files:
        print("Your files:")
        for file in files:
            print(f"  - {file.get('name', 'Unknown')} ({file.get('type', 'Unknown type')})")
    
    # 4. Create a New Strategy
    print("\n4. Creating a new strategy...")
    new_strategy = client.create_strategy({
        "name": "Example Momentum Strategy",
        "description": "A simple momentum-based trading strategy",
        "code": """
def analyze_momentum(symbol, lookback_days=5):
    \"\"\"
    Simple momentum analysis
    Returns: 'BUY', 'SELL', or 'HOLD'
    \"\"\"
    # This is example code - implement your actual logic
    import random
    momentum = random.uniform(-1, 1)
    
    if momentum > 0.3:
        return 'BUY'
    elif momentum < -0.3:
        return 'SELL'
    else:
        return 'HOLD'

def execute_strategy(symbols):
    \"\"\"
    Execute the momentum strategy on a list of symbols
    \"\"\"
    results = {}
    for symbol in symbols:
        action = analyze_momentum(symbol)
        results[symbol] = action
    return results
        """,
        "tags": ["momentum", "example", "automated"],
        "risk_level": "low"
    })
    
    if new_strategy:
        print(f"✅ Created strategy: {new_strategy['name']}")
        print(f"   ID: {new_strategy.get('id', 'Unknown')}")
    else:
        print("❌ Failed to create strategy")
    
    # 5. Create a New File
    print("\n5. Creating a new file...")
    new_file = client.upload_file({
        "name": "trading_notes.txt",
        "content": "This is a sample trading notes file created via CPZ AI SDK.\n\nKey insights:\n- Market volatility is increasing\n- Tech stocks showing momentum\n- Consider defensive positions",
        "type": "text",
        "tags": ["notes", "trading", "example"]
    })
    
    if new_file:
        print(f"✅ Created file: {new_file['name']}")
        print(f"   ID: {new_file.get('id', 'Unknown')}")
    else:
        print("❌ Failed to create file")
    
    # 6. Platform Information
    print("\n6. Platform information...")
    tables = client.list_tables()
    print(f"📋 Available tables: {', '.join(tables) if tables else 'None'}")
    
    # 7. Cleanup (optional - uncomment to delete test data)
    """
    print("\n7. Cleaning up test data...")
    if new_strategy:
        if client.delete_strategy(new_strategy['id']):
            print("✅ Test strategy deleted")
        else:
            print("❌ Failed to delete test strategy")
    
    if new_file:
        if client.delete_file(new_file['id']):
            print("✅ Test file deleted")
        else:
            print("❌ Failed to delete test file")
    """
    
    print("\n🎉 CPZ AI integration example completed!")
    print("\nNext steps:")
    print("1. Customize the strategy code for your needs")
    print("2. Implement real trading logic")
    print("3. Set up automated strategy execution")
    print("4. Monitor your strategies and files")

if __name__ == "__main__":
    main()
