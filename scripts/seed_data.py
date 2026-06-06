#!/usr/bin/env python3
"""
Popula banco com dados de exemplo para visualização.
Execute: python scripts/seed_data.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserType
from app.models.veterinarian import Veterinarian
from app.models.clinic import Clinic
from app.models.tutor import Tutor
from app.models.administrator import Administrator
from app.models.review import Review, RevieweeType, ReviewStatus
from app.models.case import ClinicalCase
from app.utils.slugify import slugify


def seed_database():
    db = SessionLocal()

    try:
        print("🌱 Iniciando seed do banco de dados...")

        # Limpar dados existentes
        db.query(Review).delete()
        db.query(ClinicalCase).delete()
        db.query(Veterinarian).delete()
        db.query(Clinic).delete()
        db.query(Tutor).delete()
        db.query(Administrator).delete()
        db.query(User).delete()
        db.commit()
        print("✅ Dados anteriores removidos")

        # Criar administrador
        admin_user = User(
            email="admin@vetlandia.com.br",
            password_hash=get_password_hash("admin123"),
            user_type=UserType.ADMIN,
        )
        db.add(admin_user)
        db.flush()

        admin = Administrator(
            user_id=admin_user.id,
            full_name="Administrador VetLândia",
        )
        db.add(admin)
        db.commit()
        print(f"✅ 1 administrador criado (email: admin@vetlandia.com.br, senha: admin123)")

        # Criar tutores
        tutores_data = [
            ("Maria Silva", "maria@email.com", "(11) 98765-4321"),
            ("João Santos", "joao@email.com", "(21) 97654-3210"),
            ("Ana Costa", "ana@email.com", "(11) 96543-2109"),
        ]

        tutores = []
        for nome, email, telefone in tutores_data:
            user = User(
                email=email,
                password_hash=get_password_hash("senha123"),
                user_type=UserType.TUTOR,
            )
            db.add(user)
            db.flush()

            tutor = Tutor(
                user_id=user.id,
                full_name=nome,
                phone=telefone,
            )
            db.add(tutor)
            tutores.append((user, tutor))

        db.commit()
        print(f"✅ {len(tutores)} tutores criados")

        # Criar veterinários
        vets_data = [
            ("Dr. João Silva", "joao.vet@email.com", "CRMV-SP 12345", "Cardiologia", "São Paulo", "SP", "15 anos salvando corações caninos e felinos"),
            ("Dra. Ana Costa", "ana.vet@email.com", "CRMV-RJ 23456", "Dermatologia", "Rio de Janeiro", "RJ", "Especialista em dermatite atópica"),
            ("Dr. Pedro Lima", "pedro.vet@email.com", "CRMV-DF 34567", "Cirurgia", "Brasília", "DF", "Pioneiro em cirurgias minimamente invasivas"),
            ("Dra. Mariana Souza", "mariana.vet@email.com", "CRMV-SP 45678", "Ortopedia", "Campinas", "SP", "Tratamento de displasia coxofemoral"),
            ("Dr. Carlos Oliveira", "carlos.vet@email.com", "CRMV-MG 56789", "Oftalmologia", "Belo Horizonte", "MG", "Cirurgias oculares em cães e gatos"),
            ("Dra. Juliana Ferreira", "juliana.vet@email.com", "CRMV-RS 67890", "Oncologia", "Porto Alegre", "RS", "Tratamento oncológico humanizado"),
        ]

        veterinarians = []
        for nome, email, crmv, especialidade, cidade, estado, bio in vets_data:
            user = User(
                email=email,
                password_hash=get_password_hash("senha123"),
                user_type=UserType.VETERINARIAN,
            )
            db.add(user)
            db.flush()

            slug = slugify(f"{nome} {cidade}")

            vet = Veterinarian(
                user_id=user.id,
                full_name=nome,
                crmv=crmv,
                specialty=especialidade,
                bio=bio,
                phone=f"(11) 9{len(veterinarians)}000-0000",
                city=cidade,
                state=estado,
                slug=slug,
                is_approved=True,  # Aprovado para demo
            )
            db.add(vet)
            veterinarians.append((user, vet))

        db.commit()
        print(f"✅ {len(veterinarians)} veterinários criados")

        # Criar clínicas
        clinicas_data = [
            ("Clínica Vida Animal", "contato@vidaanimal.com.br", "Rio de Janeiro", "RJ", "Rua das Flores, 123", "22040-020", "(21) 3333-4444", "Clínica completa com centro cirúrgico e UTI 24h"),
            ("PetCare Center", "contato@petcare.com.br", "São Paulo", "SP", "Av. Paulista, 1000", "01310-100", "(11) 4444-5555", "15 especialistas e estrutura de hospital"),
            ("VetLife", "contato@vetlife.com.br", "Belo Horizonte", "MG", "Rua dos Pets, 456", "30130-100", "(31) 5555-6666", "Diagnóstico por imagem e laboratório próprio"),
        ]

        clinicas = []
        for nome, email, cidade, estado, endereco, cep, telefone, descricao in clinicas_data:
            user = User(
                email=email,
                password_hash=get_password_hash("senha123"),
                user_type=UserType.CLINIC,
            )
            db.add(user)
            db.flush()

            slug = slugify(f"{nome} {cidade}")

            clinic = Clinic(
                user_id=user.id,
                name=nome,
                description=descricao,
                address=endereco,
                city=cidade,
                state=estado,
                zip_code=cep,
                phone=telefone,
                email=email,
                slug=slug,
                is_approved=True,  # Aprovado para demo
            )
            db.add(clinic)
            clinicas.append((user, clinic))

        db.commit()
        print(f"✅ {len(clinicas)} clínicas criadas")

        # Criar avaliações para veterinários
        import random
        avaliacoes_count = 0
        avaliacoes_aprovadas = 0
        avaliacoes_pendentes = 0

        for tutor_user, tutor in tutores:
            for vet_user, vet in veterinarians[:4]:  # Avaliar primeiros 4 vets
                rating = random.choice([4, 5, 5, 5])  # Maioria alta
                comentarios = [
                    "Excelente profissional! Muito atencioso com meu pet.",
                    "Salvou a vida do meu cachorro. Extremamente competente e dedicado.",
                    "Atendimento maravilhoso, explica tudo com muita clareza.",
                    "Recomendo de olhos fechados. Meu gato ficou ótimo após o tratamento.",
                ]

                # 80% aprovadas, 20% pendentes (para demo de moderação)
                status = ReviewStatus.APPROVED if random.random() < 0.8 else ReviewStatus.PENDING

                review = Review(
                    author_id=tutor_user.id,
                    reviewee_type=RevieweeType.VETERINARIAN,
                    reviewee_id=vet.id,
                    rating=rating,
                    comment=random.choice(comentarios),
                    status=status,
                )
                db.add(review)
                avaliacoes_count += 1
                if status == ReviewStatus.APPROVED:
                    avaliacoes_aprovadas += 1
                else:
                    avaliacoes_pendentes += 1

        # Avaliar clínicas
        for tutor_user, tutor in tutores:
            for clinic_user, clinic in clinicas[:2]:
                rating = random.choice([4, 5, 5])
                comentarios_clinica = [
                    "Estrutura impecável! Equipe muito profissional e atenciosa.",
                    "Melhor clínica da região. Equipamentos modernos e ótimo atendimento.",
                    "Confio de olhos fechados. Já salvaram meu pet várias vezes.",
                ]

                # 80% aprovadas, 20% pendentes
                status = ReviewStatus.APPROVED if random.random() < 0.8 else ReviewStatus.PENDING

                review = Review(
                    author_id=tutor_user.id,
                    reviewee_type=RevieweeType.CLINIC,
                    reviewee_id=clinic.id,
                    rating=rating,
                    comment=random.choice(comentarios_clinica),
                    status=status,
                )
                db.add(review)
                avaliacoes_count += 1
                if status == ReviewStatus.APPROVED:
                    avaliacoes_aprovadas += 1
                else:
                    avaliacoes_pendentes += 1

        db.commit()
        print(f"✅ {avaliacoes_count} avaliações criadas ({avaliacoes_aprovadas} aprovadas, {avaliacoes_pendentes} pendentes)")

        # Criar casos clínicos
        casos_data = [
            (
                veterinarians[0][1],  # Dr. João Silva - Cardiologista
                "Sopro Cardíaco em Golden Retriever: Diagnóstico Precoce Salvou Vidas",
                "Canino",
                "Golden Retriever",
                "Cardiologia",
                """Paciente Golden Retriever, macho, 6 anos, apresentou-se para consulta de rotina.
                Durante auscultação, identificamos sopro grau III/VI em foco mitral.
                Ecocardiograma revelou degeneração mixomatosa da válvula mitral com regurgitação moderada.

                Iniciamos protocolo com IECA e diurético. Após 3 meses, paciente apresentou melhora significativa
                na qualidade de vida. Caso demonstra importância do diagnóstico precoce em cardiologia veterinária."""
            ),
            (
                veterinarians[1][1],  # Dra. Ana Costa - Dermatologista
                "Dermatite Atópica em Golden: Protocolo que Revolucionou Tratamento",
                "Canino",
                "Golden Retriever",
                "Dermatologia",
                """Paciente de 3 anos com histórico de prurido intenso e lesões recorrentes há 18 meses.
                Realizamos testes alérgicos e identificamos sensibilidade a múltiplos alérgenos ambientais.

                Implementamos protocolo integrado: imunoterapia específica, shampoo terapêutico com clorexidina,
                suplementação com ômega-3 e controle ambiental rigoroso.

                Após 6 meses, remissão completa dos sintomas. Caso evidencia eficácia da abordagem multifatorial."""
            ),
            (
                veterinarians[2][1],  # Dr. Pedro Lima - Cirurgião
                "Cirurgia Minimamente Invasiva em Cão com Torção Gástrica",
                "Canino",
                "Pastor Alemão",
                "Cirurgia",
                """Pastor Alemão, 7 anos, admitido em emergência com sinais clássicos de dilatação-vólvulo gástrico.

                Optamos por gastropexia laparoscópica preventiva após estabilização. Procedimento realizado
                com 3 portais de 5mm. Tempo cirúrgico: 45 minutos. Recuperação pós-operatória excelente.

                Paciente recebeu alta em 48h. Técnica minimamente invasiva reduziu dor e tempo de recuperação
                significativamente comparado à cirurgia convencional."""
            ),
        ]

        casos_count = 0
        for vet, titulo, especie, raca, especialidade, conteudo in casos_data:
            case = ClinicalCase(
                author_id=vet.id,
                title=titulo,
                species=especie,
                breed=raca,
                specialty=especialidade,
                content=conteudo,
            )
            db.add(case)
            casos_count += 1

        db.commit()
        print(f"✅ {casos_count} casos clínicos criados")

        print("\n🎉 Seed concluído com sucesso!")
        print("\n📊 Resumo:")
        print(f"   - {len(tutores)} tutores")
        print(f"   - {len(veterinarians)} veterinários")
        print(f"   - {len(clinicas)} clínicas")
        print(f"   - {avaliacoes_count} avaliações")
        print(f"   - {casos_count} casos clínicos")
        print("\n🔐 Credenciais de teste:")
        print("   Email: maria@email.com | Senha: senha123 (Tutor)")
        print("   Email: joao.vet@email.com | Senha: senha123 (Veterinário)")
        print("   Email: contato@vidaanimal.com.br | Senha: senha123 (Clínica)")
        print("\n✨ Acesse http://localhost:8000 para ver o redesign!")

    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
