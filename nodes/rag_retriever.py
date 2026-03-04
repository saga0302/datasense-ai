import chromadb
import json
from pathlib import Path

# Initialize ChromaDB in-memory vector store
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("past_incidents")

def index_past_incidents():
    """Read all saved JSON incidents and load them into ChromaDB"""
    incidents_path = Path("incidents")
    if not incidents_path.exists():
        return

    for json_file in incidents_path.glob("*.json"):
        with open(json_file) as f:
            data = json.load(f)

        for pipeline in data.get("pipelines", []):
            doc_id = f"{data['incident_id']}_{pipeline['name']}"
            document = f"""
            Pipeline: {pipeline['name']}
            Failure Type: {pipeline.get('failure_type', 'UNKNOWN')}
            Severity: {pipeline.get('severity', 'UNKNOWN')}
            Error: {pipeline.get('error', '')}
            Fix Time: {pipeline.get('estimated_fix_time', 'Unknown')}
            """
            try:
                collection.add(
                    documents=[document],
                    ids=[doc_id],
                    metadatas=[{
                        "incident_id": data["incident_id"],
                        "pipeline": pipeline["name"]
                    }]
                )
            except Exception:
                pass  # Skip duplicates

def retrieve_similar_incidents(error_message: str, n_results: int = 3) -> str:
    """Find past incidents similar to the current error"""
    index_past_incidents()

    if collection.count() == 0:
        return "No historical incidents found."

    results = collection.query(
        query_texts=[error_message],
        n_results=min(n_results, collection.count())
    )

    if not results["documents"][0]:
        return "No similar incidents found."

    context = "HISTORICAL CONTEXT FROM SIMILAR PAST INCIDENTS:\n"
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        context += f"\n[{meta['incident_id']}] {doc.strip()}\n"

    return context