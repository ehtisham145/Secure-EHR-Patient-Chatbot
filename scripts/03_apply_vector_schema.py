import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine,text,URL

def apply_pg_vector_schema():
    #1.Load the Enviroment Variable
    load_dotenv()
    print("Connecting to VPS to apply pgvector schema upgrade...")
    
    #2.Create the engine
    db_url = URL.create(
            "postgresql+psycopg",      # <-- psycopg2 ki jagah psycopg
            username=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            database=os.getenv('DB_NAME'),
            )
    engine=create_engine(db_url)
    try:
        #3.Add the Embedding Vector Column
        print("Adding 'clinical_embedding' column (768 dimensions)...")
        with engine.begin() as conn:
            embed_column=conn.execute(text("ALTER TABLE patient_encounters ADD COLUMN IF NOT EXISTS clinical_embedding vector(768);"))

        #4. Verify the Embedding column
            if not embed_column:
                print("Embedding Column is not added !")

            verify_embed_column=conn.execute(text(
                """
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'patient_encounters' AND column_name = 'clinical_embedding';
                """
            ))

            if verify_embed_column:
                print("Schema Upgraded and Clinical Embedding column is added in table")
            else:
                print(" Column not found after alter attempt.")

    except Exception as e:
        print(f"Error applying schema: {e}")


if __name__=="__main__":
    apply_pg_vector_schema()
    