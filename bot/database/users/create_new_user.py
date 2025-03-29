from ..connect import get_db_connection

def create_user(user_id: int, username: str) -> bool:
    """
    Create a new user in the users table
    
    Args:
        user_id (int): The unique identifier for the user
        username (str): The username of the user
        
    Returns:
        bool: True if user was created successfully, False otherwise
    """
    conn = get_db_connection()
    if not conn:
        return False
        
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (user_id, username)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
            RETURNING user_id
        """, (user_id, username))
        
        result = cur.fetchone()
        conn.commit()
        
        # If result is None, it means the user already existed
        success = result is not None
        return success
        
    except Exception as e:
        print(f"Error creating user: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

# Example usage:
#if __name__ == "__main__":
    # Example: Create a test user
#    success = create_user(user_id=123456789, username="test_user")
#    if success:
#        print("User created successfully")
#    else:
#        print("Failed to create user (might already exist)")