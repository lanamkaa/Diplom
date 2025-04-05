from ..connect import get_db_connection

def create_answers_table(conn=None):
    """
    Create answers table if it doesn't exist.
    Args:
        conn: Optional database connection. If not provided, creates a new connection.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        # Create answers table without foreign key constraints
        cur.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            answer_id SERIAL PRIMARY KEY,
            question_id INTEGER,
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            answer_text TEXT,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("Answers table created successfully")
        
    except Exception as e:
        print(f"Error while creating answers table: {e}")
        conn.rollback()
    finally:
        cur.close()
        if should_close:
            conn.close()

def add_answers_constraints(conn=None):
    """
    Add foreign key constraints to answers table.
    Args:
        conn: Optional database connection. If not provided, creates a new connection.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        # Add foreign key constraint if it doesn't exist
        cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'answers_question_id_fkey'
            ) THEN
                ALTER TABLE answers
                ADD CONSTRAINT answers_question_id_fkey
                FOREIGN KEY (question_id)
                REFERENCES questions(question_id)
                ON DELETE CASCADE;
            END IF;
        END
        $$;
        """)

        conn.commit()
        print("Answers table constraints added successfully")
        
    except Exception as e:
        print(f"Error while adding answers table constraints: {e}")
        conn.rollback()
    finally:
        cur.close()
        if should_close:
            conn.close()
