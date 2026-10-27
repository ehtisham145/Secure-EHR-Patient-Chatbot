import pandas as pd
import os
from sqlalchemy import create_engine,text,URL
from dotenv import load_dotenv
def verify_ingestion():
    #1.Load the Enviromental Variables
    load_dotenv()

    print("Connecting to VPS to verify ingestion...")

    #2.Engine
    db_url = URL.create(
        "postgresql+psycopg",      # <-- psycopg2 ki jagah psycopg
        username=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        database=os.getenv('DB_NAME'),
        )
    engine=create_engine(db_url)

    #3.Run the query
    with engine.connect() as conn:
        result=conn.execute(text("SELECT COUNT(*) FROM patient_encounters")).scalar()

        if result==0:
            print("Ingestion May Failed Please Check Again !")

    #4.Query the Records from Database
        else:
            query = text("""
                SELECT 
                    subject_id, 
                    admission_type, 
                    drug, 
                    drg_severity 
                FROM patient_encounters 
                WHERE drug IS NOT NULL
                LIMIT 5
            """)
        
    #5.Read the SQL query
            df=pd.read_sql(query,conn)
            text_records=df.to_string(index=False)
            print(f"Patients Records are : {text_records}")
            print("\n✅ Verification complete. Legacy database state is confirmed.")


if __name__=="__main__":
    verify_ingestion()