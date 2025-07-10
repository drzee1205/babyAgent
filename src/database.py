from src.config import supabase, YOUR_TABLE_NAME


def setup_supabase_table():
    """Set up the Supabase table for storing task results with embeddings."""
    try:
        # Create table with vector support
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {YOUR_TABLE_NAME} (
            id BIGSERIAL PRIMARY KEY,
            content TEXT,
            metadata JSONB,
            embedding VECTOR(1024),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
        );
        """
        
        # Create indexes for better performance
        create_index_sql = f"""
        CREATE INDEX IF NOT EXISTS {YOUR_TABLE_NAME}_embedding_idx 
        ON {YOUR_TABLE_NAME} 
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """
        
        # Create similarity search function
        create_function_sql = f"""
        CREATE OR REPLACE FUNCTION match_documents(
            query_embedding VECTOR(1024),
            match_count INT DEFAULT 5,
            filter JSONB DEFAULT '{{}}'
        )
        RETURNS TABLE(
            id BIGINT,
            content TEXT,
            metadata JSONB,
            similarity FLOAT
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RETURN QUERY
            SELECT
                {YOUR_TABLE_NAME}.id,
                {YOUR_TABLE_NAME}.content,
                {YOUR_TABLE_NAME}.metadata,
                1 - ({YOUR_TABLE_NAME}.embedding <=> query_embedding) AS similarity
            FROM {YOUR_TABLE_NAME}
            WHERE {YOUR_TABLE_NAME}.metadata @> filter
            ORDER BY {YOUR_TABLE_NAME}.embedding <=> query_embedding
            LIMIT match_count;
        END;
        $$;
        """
        
        # Execute SQL commands
        supabase.sql(create_table_sql).execute()
        supabase.sql(create_index_sql).execute()
        supabase.sql(create_function_sql).execute()
        
        print(f"✅ Supabase table '{YOUR_TABLE_NAME}' set up successfully")
        
    except Exception as e:
        print(f"❌ Error setting up Supabase table: {e}")
        # Try a simpler table creation without vector extensions
        try:
            simple_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {YOUR_TABLE_NAME} (
                id BIGSERIAL PRIMARY KEY,
                content TEXT,
                metadata JSONB,
                embedding TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
            );
            """
            supabase.sql(simple_table_sql).execute()
            print(f"✅ Supabase table '{YOUR_TABLE_NAME}' created with basic schema")
        except Exception as e2:
            print(f"❌ Error creating basic table: {e2}")


def cleanup_supabase_table():
    """Delete the Supabase table."""
    try:
        supabase.sql(f"DROP TABLE IF EXISTS {YOUR_TABLE_NAME};").execute()
        print(f"🗑️  Supabase table '{YOUR_TABLE_NAME}' deleted.")
    except Exception as e:
        print(f"❌ Error deleting Supabase table: {e}")


def store_task_result(task_id: str, task_name: str, result: str, embedding: list):
    """Store a task result in the database."""
    try:
        supabase.table(YOUR_TABLE_NAME).insert({
            "content": result,
            "metadata": {"task": task_name, "result": result, "task_id": task_id},
            "embedding": embedding
        }).execute()
        return True
    except Exception as e:
        print(f"❌ Error storing result in Supabase: {e}")
        return False