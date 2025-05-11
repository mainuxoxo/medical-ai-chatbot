from huggingface_hub import HfApi
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get token from environment variable
TEST_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

if not TEST_TOKEN:
    print("❌ HF_TOKEN is not set in environment variables.")
else:
    try:
        # Initialize API client
        api = HfApi(token=TEST_TOKEN)
        
        # Get user info
        user_info = api.whoami()
        
        print("✅ Token is valid!")
        print(f"Username: {user_info['name']}")
        print(f"Email: {user_info['email']}")
        print(f"Organizations: {user_info['orgs']}")

    except Exception as e:
        print("❌ Token validation failed!")
        print(f"Error: {str(e)}")
