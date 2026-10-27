import os
import pandas as pd
from sqlalchemy import create_engine,text
from sqlalchemy.engine import URL
from dotenv import load_dotenv
from pathlib import Path

def ingest_data():
    # 1. Load the Enviroment Variable
    load_dotenv()

    #2.Resolve the path
    script_dir=Path(__file__).resolve().parent
    root_dir=script_dir.parent

    print(f"Script Dir : {script_dir}")
    print(f"Root Dir : {root_dir}")

    #3. Schema and CSV Path
    csv_path = root_dir/'data'/'MIMIC_IV_Trasncript.csv'
    schema_path = root_dir/'src'/'database'/'schema.sql'

    #4. Check the file Path
    if not csv_path.exists() or not schema_path.exists():
        raise FileNotFoundError(f"One path is missing from these two ")

    #5. Set the Database Connection
    db_url = URL.create(
    "postgresql+psycopg",      # <-- psycopg2 ki jagah psycopg
    username=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT')),
    database=os.getenv('DB_NAME'),
    )
    engine = create_engine(db_url)

    #6.Run the Conn
    with engine.begin() as conn:
        with open(schema_path,'r') as file:
            conn.execute(text(file.read()))

    #7.Run the dataframe
    df=pd.read_csv(csv_path)
    df=df.where(pd.notnull(df),None)

    df.to_sql('patient_encounters', engine, if_exists='append', index=False)

    print(f"Data Ingested Successfully !")


if __name__=="__main__":
    ingest_data()