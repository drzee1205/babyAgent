import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
OBJECTIVE = os.getenv("OBJECTIVE", "Solve world hunger.")
YOUR_TABLE_NAME = os.getenv("YOUR_TABLE_NAME", "documents")
YOUR_FIRST_TASK = os.getenv("YOUR_FIRST_TASK", "Develop a task list.")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Validate required environment variables
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required")
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is required")
if not SUPABASE_KEY:
    raise ValueError("SUPABASE_ANON_KEY environment variable is required")