#!/usr/bin/env python3
"""
Remove TODOS os dados fictícios do banco.
Mantém apenas estrutura (tabelas vazias).
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.veterinarian import Veterinarian
from app.models.clinic import Clinic
from app.models.tutor import Tutor
from app.models.administrator import Administrator
from app.models.review import Review
from app.models.case import ClinicalCase, CaseComment
from app.models.comment import Comment


def clean_database():
    """Remove todos os dados, mantém apenas estrutura."""
    db = SessionLocal()

    try:
        print("🧹 Iniciando limpeza completa do banco de dados...")
        print("⚠️  ATENÇÃO: Todos os dados serão removidos!\n")

        # Contagem antes
        reviews_count = db.query(Review).count()
        comments_count = db.query(Comment).count()
        case_comments_count = db.query(CaseComment).count()
        cases_count = db.query(ClinicalCase).count()
        vets_count = db.query(Veterinarian).count()
        clinics_count = db.query(Clinic).count()
        tutors_count = db.query(Tutor).count()
        admins_count = db.query(Administrator).count()
        users_count = db.query(User).count()

        print(f"📊 REGISTROS ENCONTRADOS:")
        print(f"   - {reviews_count} avaliações")
        print(f"   - {comments_count} comentários em avaliações")
        print(f"   - {case_comments_count} comentários em casos")
        print(f"   - {cases_count} casos clínicos")
        print(f"   - {vets_count} veterinários")
        print(f"   - {clinics_count} clínicas")
        print(f"   - {tutors_count} tutores")
        print(f"   - {admins_count} administradores")
        print(f"   - {users_count} usuários\n")

        # Deletar na ordem correta (respeitar foreign keys)
        db.query(CaseComment).delete()
        print("✅ Comentários de casos removidos")

        db.query(Comment).delete()
        print("✅ Comentários de avaliações removidos")

        db.query(Review).delete()
        print("✅ Avaliações removidas")

        db.query(ClinicalCase).delete()
        print("✅ Casos clínicos removidos")

        db.query(Veterinarian).delete()
        print("✅ Veterinários removidos")

        db.query(Clinic).delete()
        print("✅ Clínicas removidas")

        db.query(Tutor).delete()
        print("✅ Tutores removidos")

        db.query(Administrator).delete()
        print("✅ Administradores removidos")

        db.query(User).delete()
        print("✅ Usuários removidos")

        db.commit()

        print("\n🎉 LIMPEZA CONCLUÍDA!")
        print("📦 Banco de dados limpo e pronto para dados reais.")
        print("🔐 Próximo passo: Criar administrador principal.\n")

    except Exception as e:
        db.rollback()
        print(f"\n❌ ERRO: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    clean_database()
