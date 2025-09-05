"""Arithmic CLI with Typer"""

import os
import json
import pathlib
import typer
from typing import Optional
from .provider import get_provider, get_available_providers
from .rag_core import ensure_collection, iter_path_text, chunk_text, upsert_chunks, retrieve, build_prompt

app = typer.Typer(help="Arithmic CLI (Multi-provider RAG)")

@app.command(help="Simple chat with the model (no retrieval)")
def chat(prompt: str,
         model: str = "kimi-2",
         provider: Optional[str] = typer.Option(None, help="Inference provider (groq/ollama)")):
    """Chat with model directly"""
    try:
        client = get_provider(provider)
        resp = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=model
        )
        print(resp)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

@app.command(help="List available models")
def models(provider: Optional[str] = typer.Option(None, help="Inference provider (groq/ollama)")):
    """List available models"""
    try:
        client = get_provider(provider)
        available_models = client.list_models()
        print(f"Available models for {provider or 'default'} provider:")
        for model in available_models:
            print(f"  - {model}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

@app.command(help="List available providers")
def providers():
    """List available inference providers"""
    available = get_available_providers()
    print("Available providers:")
    for p in available:
        print(f"  - {p}")
    current = os.environ.get("ARITHMIC_PROVIDER", "groq")
    print(f"\nCurrent default: {current}")
    print("Set ARITHMIC_PROVIDER environment variable to change default")

@app.command(help="Index a file or folder into Qdrant")
def index(path: str, tag: Optional[str] = typer.Option(None, help="Logical tag (e.g., 'arithmic')")):
    """Index files into the vector database"""
    ensure_collection()
    file_tag = tag or pathlib.Path(path).stem
    total = 0

    with typer.progressbar(iter_path_text(path), label="Indexing") as progress:
        for fp, text in progress:
            chunks = chunk_text(text)
            if not chunks:
                continue
            upsert_chunks(fp, chunks, file_tag)
            total += len(chunks)

    typer.echo(f"✅ Done. Total chunks: {total} (tag={file_tag})")

@app.command(help="Index a repo tree (code + docs)")
def repo(path: str = ".", tag: Optional[str] = typer.Option(None, help="Repo tag")):
    """Index a repository"""
    return index(path, tag)

@app.command(help="Ask a question over indexed data (RAG)")
def ask(question: str,
        k: int = typer.Option(8, help="Top-k chunks"),
        tag: Optional[str] = typer.Option(None, help="Restrict to a tag"),
        model: str = "kimi-2",
        provider: Optional[str] = typer.Option(None, help="Inference provider (groq/ollama)")):
    """Ask a question using RAG"""
    ensure_collection()
    hits = retrieve(question, k=k, tag=tag)

    if not hits:
        typer.echo("No context found. Try indexing with `arithmic-cli index . --tag arithmic`.")
        raise typer.Exit(1)

    prompt = build_prompt(question, hits)
    try:
        client = get_provider(provider)
        resp = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=0.2
        )

        print("\n──────── ANSWER ────────\n")
        print(resp)
        print("\n──────── SOURCES ────────")
        for i, h in enumerate(hits, 1):
            print(f"[{i}] {h['file_path']} (chunk {h['chunk_index']}) score={h['_score']:.3f} tag={h.get('file_tag')}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
