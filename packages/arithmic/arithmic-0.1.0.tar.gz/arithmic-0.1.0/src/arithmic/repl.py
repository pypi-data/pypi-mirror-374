"""Arithmic REPL - Natural Language Interface"""

import os
import sys
import subprocess
from pathlib import Path

def _call_cli(args_list):
    """Call the CLI and return output"""
    proc = subprocess.run([sys.executable, "-m", "arithmic.cli", *args_list],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return (proc.stdout + "\n" + proc.stderr).strip()
    return proc.stdout

def main():
    """Main REPL loop"""
    tag = os.getenv("ARITHMIC_DEFAULT_TAG", "arithmic")
    top_k = int(os.getenv("ARITHMIC_DEFAULT_K", "8"))
    provider = os.getenv("ARITHMIC_PROVIDER", "groq")

    print("🤖 Arithmic AI — type plain English (':q' to quit)")
    print(f"   Defaults: tag={tag}  k={top_k}  provider={provider}")
    print("   Commands: :tag <name>, :k <number>, :provider <groq|ollama>, :q to quit")

    while True:
        try:
            q = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not q:
            continue

        # Handle commands
        if q in (":q", ":quit"):
            print("Bye.")
            break
        elif q.startswith(":tag "):
            tag = q.split(" ", 1)[1].strip()
            print(f"✓ tag set to '{tag}'")
            continue
        elif q.startswith(":k "):
            try:
                top_k = int(q.split(" ", 1)[1].strip())
                print(f"✓ top-k set to {top_k}")
            except ValueError:
                print("⚠︎ usage: :k 8")
            continue
        elif q.startswith(":provider "):
            new_provider = q.split(" ", 1)[1].strip().lower()
            if new_provider in ["groq", "ollama"]:
                provider = new_provider
                print(f"✓ provider set to '{provider}'")
            else:
                print("⚠︎ provider must be 'groq' or 'ollama'")
            continue

        # Process natural language query
        print("…thinking…")
        out = _call_cli(["ask", q, "--k", str(top_k), "--tag", tag, "--provider", provider])
        print(out)

if __name__ == "__main__":
    main()
