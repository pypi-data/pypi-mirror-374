"""RAG Core utilities for Arithmic"""

import os
import uuid
import pathlib
from typing import List, Optional, Iterable, Tuple
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from pypdf import PdfReader
import docx2txt

# Configuration
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "arithmic_docs")

# Initialize clients
embedder = SentenceTransformer(EMBED_MODEL)
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# File extensions
TEXT_EXTS = {".txt", ".md", ".rst", ".csv", ".log", ".json", ".yaml", ".yml"}
CODE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".rb", ".php",
             ".c", ".h", ".cpp", ".hpp", ".cs", ".swift", ".scala", ".sh", ".bash", ".zsh",
             ".dockerfile", ".toml", ".ini"}

def ensure_collection() -> None:
    """Ensure the Qdrant collection exists"""
    dim = embedder.get_sentence_embedding_dimension()
    cols = [c.name for c in qdrant.get_collections().collections]
    if QDRANT_COLLECTION not in cols:
        qdrant.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
        )

def chunk_text(text: str, max_chars: int = 1400, overlap: int = 120) -> List[str]:
    """Split text into overlapping chunks"""
    text = text.replace("\r", "")
    out, i, n = [], 0, len(text)
    while i < n:
        j = min(i + max_chars, n)
        out.append(text[i:j].strip())
        i = j - overlap
        if i <= 0: i = j
    return [c for c in out if c]

def _embed(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for text chunks"""
    return embedder.encode(texts, normalize_embeddings=True).tolist()

def read_text_file(p: pathlib.Path) -> str:
    """Read text file content"""
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def read_pdf(p: pathlib.Path) -> str:
    """Read PDF file content"""
    try:
        reader = PdfReader(str(p))
        return "\n".join([(pg.extract_text() or "") for pg in reader.pages])
    except Exception:
        return ""

def read_docx(p: pathlib.Path) -> str:
    """Read DOCX file content"""
    try:
        return docx2txt.process(str(p)) or ""
    except Exception:
        return ""

def iter_path_text(path: str) -> Iterable[Tuple[str, str]]:
    """Yield (file_path, text) for files under path"""
    p = pathlib.Path(path)

    def handle(fp: pathlib.Path) -> Optional[Tuple[str, str]]:
        ext = fp.suffix.lower()
        if ext in TEXT_EXTS or ext in CODE_EXTS:
            t = read_text_file(fp)
        elif ext == ".pdf":
            t = read_pdf(fp)
        elif ext == ".docx":
            t = read_docx(fp)
        else:
            return None
        return (str(fp), t) if t.strip() else None

    if p.is_dir():
        for fp in p.rglob("*"):
            if not fp.is_file():
                continue
            item = handle(fp)
            if item:
                yield item
    else:
        item = handle(p)
        if item:
            yield item

def upsert_chunks(file_path: str, chunks: List[str], tag: str) -> None:
    """Store text chunks in Qdrant"""
    vecs = _embed(chunks)
    pts = []
    for idx, (v, ch) in enumerate(zip(vecs, chunks)):
        pts.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=v,
            payload={"file_path": file_path, "file_tag": tag, "chunk_index": idx, "text": ch}
        ))
    qdrant.upsert(collection_name=QDRANT_COLLECTION, points=pts)

def retrieve(query: str, k: int = 8, tag: Optional[str] = None) -> List[dict]:
    """Retrieve relevant chunks for a query"""
    q_vec = _embed([query])[0]
    filt = Filter(must=[FieldCondition(key="file_tag", match=MatchValue(value=tag))]) if tag else None
    res = qdrant.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=q_vec,
        limit=k,
        query_filter=filt,
        with_payload=True
    )
    return [r.payload | {"_score": r.score} for r in res]

def build_prompt(question: str, contexts: list[dict]) -> str:
    """Build RAG prompt with context"""
    blocks = []
    for i, c in enumerate(contexts, 1):
        blocks.append(
            f"[{i}] file: {c.get('file_path')} | chunk: {c.get('chunk_index')} | score: {c.get('_score'):.3f}\n{c.get('text')}"
        )
    return (
        "You are an assistant that answers ONLY using the provided context. "
        "Cite sources with [#] that correspond to the context blocks.\n\n"
        f"Question: {question}\n\n"
        f"Context:\n" + "\n\n".join(blocks) + "\n\n"
        "Answer (with citations like [1], [2]):"
    )
