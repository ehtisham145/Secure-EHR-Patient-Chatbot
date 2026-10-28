import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


def generate_embeddings():
    load_dotenv()

    model = SentenceTransformer('NeuML/bioclinical-modernbert-base-embeddings')
    if model.get_embedding_dimension() != 768:
        raise ValueError("Dimension mismatch Error")

    engine = create_engine(URL.create(
        "postgresql+psycopg",
        username=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        database=os.getenv('DB_NAME'),
    ))

    batch_size = 32
    max_rows = 500

    select_query = text("""
        SELECT id, admission_type, drug, test_name, drg_severity, description, comments
        FROM patient_encounters
        WHERE clinical_embedding IS NULL
        ORDER BY id
        LIMIT :batch_size
    """)

    update_query = text("""
        UPDATE patient_encounters
        SET clinical_embedding = CAST(:embedding AS vector)
        WHERE id = :id
    """)

    with engine.connect() as conn:
        total = conn.execute(text(
            "SELECT COUNT(*) FROM patient_encounters WHERE clinical_embedding IS NULL"
        )).scalar()
        total = min(total, max_rows)
        print(f"Embedding Remaining : {total} rows")

        with tqdm(total=total, desc="Vectorizing", unit="rows") as pbar:
            processed = 0

            while processed < max_rows:
                current_batch = min(batch_size, max_rows - processed)
                batch = conn.execute(
                    select_query, {"batch_size": current_batch}
                ).mappings().fetchall()

                if not batch:
                    break

                ids, texts = [], []
                for row in batch:
                    parts = []
                    if row['admission_type']: parts.append(f"Admission: {row['admission_type']}")
                    if row['drug']: parts.append(f"Prescribed: {row['drug']}")
                    if row['test_name']: parts.append(f"Lab Test: {row['test_name']}")
                    if row['drg_severity']: parts.append(f"Severity Level: {row['drg_severity']}")
                    if row['description']: parts.append(f"Diagnosis: {row['description']}")
                    if row['comments']: parts.append(f"Notes: {row['comments'][:250]}")
                    ids.append(row['id'])
                    texts.append(" | ".join(parts) if parts else "No clinical data")

                embeddings = model.encode(texts, batch_size=batch_size).tolist()

                result = conn.execute(update_query, [
                    {"id": i, "embedding": str(e)} for i, e in zip(ids, embeddings)
                ])
                conn.commit()

                if result.rowcount == 0:
                    raise RuntimeError("No row has been updated")

                processed += len(batch)
                pbar.update(len(batch))

    print("Embeddings Completed Successfully !")


if __name__ == "__main__":
    generate_embeddings()