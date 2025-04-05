from .connect import get_db_connection
from .users.create_table import create_user_table
from .faq.create_faq_table import create_faq_table
from .answers.create_answers_table import create_answers_table, add_answers_constraints
from .questions.create_questions_table import create_questions_table, add_questions_constraints
from .text_responses.create_text_responses_table import create_text_responses_table
import sys

def initialize_database():
    """
    Initialize database connection and create tables if they don't exist.
    Returns True if successful, False otherwise.
    """
    conn = get_db_connection()
    if not conn:
        print("Failed to establish database connection", file=sys.stderr)
        return False
    
    try:
        # Phase 1: Create all tables without circular foreign keys
        create_user_table(conn)
        create_faq_table(conn)
        create_questions_table(conn)
        create_answers_table(conn)
        create_text_responses_table(conn)
        
        # Phase 2: Add foreign key constraints for circular references
        add_questions_constraints(conn)
        add_answers_constraints(conn)
        
        print("Database initialization successful")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()
