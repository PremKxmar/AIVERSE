try:
    from supabase import create_client
    print("Success")
except Exception as e:
    print(f"Error: {e}")
