#!/usr/bin/env python3
"""
Gera SECRET_KEY seguro para produção.
Execute: python scripts/generate_secret_key.py
"""
import secrets

if __name__ == "__main__":
    secret_key = secrets.token_urlsafe(32)
    print("=" * 70)
    print("🔐 SECRET_KEY gerado para produção:")
    print("=" * 70)
    print(f"\n{secret_key}\n")
    print("=" * 70)
    print("⚠️  COPIE e adicione no Railway em Variables:")
    print(f"   SECRET_KEY={secret_key}")
    print("=" * 70)
    print("\n⚠️  NUNCA commite este valor no Git!")
    print("⚠️  Guarde em local seguro (gerenciador de senhas)\n")
