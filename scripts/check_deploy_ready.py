#!/usr/bin/env python3
"""
Verifica se o projeto está pronto para deploy.
Execute: python scripts/check_deploy_ready.py
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Verifica se arquivo existe"""
    exists = Path(filepath).exists()
    symbol = "✅" if exists else "❌"
    print(f"{symbol} {description}: {filepath}")
    return exists

def check_env_var(var_name, check_value=None):
    """Verifica variável de ambiente"""
    value = os.getenv(var_name)
    exists = value is not None

    if check_value and exists:
        is_dev = value == check_value
        if is_dev:
            print(f"⚠️  {var_name}={value} (valor de desenvolvimento!)")
            return False

    symbol = "✅" if exists else "❌"
    print(f"{symbol} {var_name} configurado")
    return exists

def main():
    print("=" * 70)
    print("🚀 Verificando se projeto está pronto para deploy")
    print("=" * 70)
    print()

    checks = []

    # Arquivos essenciais
    print("📁 Arquivos de Deploy:")
    checks.append(check_file_exists("requirements.txt", "Dependencies"))
    checks.append(check_file_exists("Procfile", "Procfile"))
    checks.append(check_file_exists("railway.json", "Railway config"))
    checks.append(check_file_exists("runtime.txt", "Python version"))
    checks.append(check_file_exists("alembic.ini", "Alembic config"))
    print()

    # Estrutura do projeto
    print("📂 Estrutura:")
    checks.append(check_file_exists("app/main.py", "FastAPI app"))
    checks.append(check_file_exists("app/models", "Models"))
    checks.append(check_file_exists("app/routers", "Routers"))
    checks.append(check_file_exists("app/templates", "Templates"))
    checks.append(check_file_exists("app/static", "Static files"))
    print()

    # Migrations
    print("🗄️  Database:")
    checks.append(check_file_exists("alembic/versions", "Migrations folder"))
    migrations = list(Path("alembic/versions").glob("*.py"))
    migration_count = len([m for m in migrations if not m.name.startswith("__")])
    if migration_count > 0:
        print(f"✅ {migration_count} migration(s) encontrada(s)")
        checks.append(True)
    else:
        print("❌ Nenhuma migration encontrada")
        checks.append(False)
    print()

    # Git
    print("🔧 Git:")
    if Path(".git").exists():
        print("✅ Repositório Git inicializado")

        # Verifica remote
        import subprocess
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                check=True
            )
            if "github.com" in result.stdout:
                print("✅ Remote GitHub configurado")
                checks.append(True)
            else:
                print("⚠️  Remote GitHub não encontrado")
                checks.append(False)
        except:
            print("⚠️  Erro ao verificar remote")
            checks.append(False)
    else:
        print("❌ Git não inicializado")
        checks.append(False)
    print()

    # Segurança
    print("🔐 Segurança:")
    gitignore_ok = False
    if Path(".gitignore").exists():
        with open(".gitignore") as f:
            content = f.read()
            if ".env" in content and "*.db" in content:
                print("✅ .gitignore protege .env e *.db")
                gitignore_ok = True
            else:
                print("⚠️  .gitignore pode não proteger arquivos sensíveis")
    else:
        print("❌ .gitignore não encontrado")
    checks.append(gitignore_ok)
    print()

    # Resumo
    print("=" * 70)
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"📊 Resultado: {passed}/{total} verificações passaram ({percentage:.0f}%)")
    print("=" * 70)

    if all(checks):
        print("\n🎉 Projeto pronto para deploy no Railway!")
        print("\n📝 Próximos passos:")
        print("   1. git push origin main")
        print("   2. Criar projeto no Railway")
        print("   3. Adicionar PostgreSQL")
        print("   4. Configurar variáveis de ambiente")
        print("   5. Deploy automático!")
        print("\n📖 Consulte DEPLOY.md para instruções detalhadas\n")
        return 0
    else:
        print("\n⚠️  Corrija os itens acima antes de fazer deploy")
        return 1

if __name__ == "__main__":
    sys.exit(main())
