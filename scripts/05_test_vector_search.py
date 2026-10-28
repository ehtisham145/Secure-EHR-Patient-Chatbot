import os 
from sqlalchemy import create_engine,text,URL
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

def test_vector_search():
    # 1. Load the Enviroment Variables
    load_dotenv()
    print("-----Load Env Variables Sucessfully------")

    #Set The Database
    engine = create_engine(URL.create(
            "postgresql+psycopg",
            username=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            database=os.getenv('DB_NAME'),
        ))
     
    #2.Load the Embedding the Model
    embed_model=SentenceTransformer('NeuML/bioclinical-modernbert-base-embeddings')
    print("------Embedding Model Loaded Successfully---")
    
    #3.Query Text
    query_text = "Patient presenting with severe liver disease and fluid retention needing diuretics"

    query_vector=embed_model.encode(query_text).tolist()
    print("Converted into Embedding vector")

    search_sql = text("""
        SELECT 
            id, 
            description, 
            drug, 
            clinical_embedding <=> CAST(:query_vector AS vector(768)) AS cosine_distance
        FROM patient_encounters
        WHERE clinical_embedding IS NOT NULL
        ORDER BY cosine_distance ASC
        LIMIT 3;
    """)

    print("---Starting the Database Connection---------")
    with engine.connect() as conn:
        results = conn.execute(search_sql, {"query_vector": str(query_vector)}).mappings().fetchall()
        
        print("\n Top 3 Semantic Matches:")
        for rank, row in enumerate(results, 1):
            print("-" * 65)
            print(f"Rank {rank} (Distance: {row['cosine_distance']:.4f})")
            print(f"Diagnosis : {row['description']}")
            print(f"Drug      : {row['drug']}")
            print(f"Record ID : {row['id']}")
            
if __name__ == "__main__":
    test_vector_search()
    