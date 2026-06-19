# MÓDULO 0 — Relatório de Auditoria · VetLândia

> Documento gerado na fase de auditoria da evolução estratégica da plataforma.
> Estado do código auditado em: 2026-06-19. Sem alterações de código nesta fase.

## 1. Ambiente e infraestrutura

| Item | Estado |
|---|---|
| Stack | FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL (prod) / SQLite (`vetlandia.db`, dev local) |
| Deploy | Railway, autodeploy via push `origin/main`; `startCommand` roda `alembic upgrade head` antes do Uvicorn |
| Migrations | 11, lineares e historicamente aditivas (`alembic/versions/`) |
| CDN/DNS | Cloudflare (cacheia CSS/JS ~4h; HTML é DYNAMIC) |
| Ambientes | Apenas **localhost** e **produção**. Não há staging. Sem backup configurado. |

## 2. Modelos existentes (`app/models/`)

| Tabela | Papel | Campos-chave relevantes à evolução |
|---|---|---|
| `users` | conta + auth | `email`, `password_hash`, `user_type` (tutor/veterinarian/clinic/admin), `is_active` |
| `tutors` | perfil tutor | `full_name`, `cpf`, `pets` (JSON em Text), `photo_url` |
| `veterinarians` | perfil vet | `crmv` (único), `specialty` (singular, String 100), `bio`, `clinic_id` (FK única → 1 clínica), `is_approved`, `is_founder`, `photo_url`/`cover_photo_url`, `aplica_vacinas`, `animal_species` (JSON Text) |
| `clinics` | perfil clínica | `name`, `cnpj`, `specialties`/`convenios`/`animal_species` (JSON Text), `is_approved`, `is_founder`, `num_veterinarios` (texto manual) |
| `reviews` | avaliações | `author_id`→user, `reviewee_type` (vet/clinic), `reviewee_id`, `rating` 1–5, `status`. Unique (author+reviewee). Autor sempre tutor (regra na rota) |
| `comments` | comentário em review | `review_id` (CASCADE), `author_id` |
| `clinical_cases` + `case_comments` | casos clínicos internos | autor = vet; `status` moderado |
| `administrators` | perfil admin | `full_name` |

**Estruturais decisivos:**
- Vet → Clínica é 1:N (`clinic_id` único no vet). Não há N:N.
- Especialidade do vet é única (string). Clínica já tem `specialties` (lista JSON em texto).
- Selos: só existe `is_founder` (booleano) = "Parceiro". Não existe "Perfil Verificado".

## 3. Autenticação
- JWT HS256 (`python-jose`), payload `{sub, user_type}`, exp 24h; cookie httpOnly `access_token` (samesite=lax, secure=False), max_age 30d.
- `get_current_user`/`require_admin` em `app/core/deps.py`.
- Existe um `get_current_user` legado (HTTPBearer) em `app/core/dependencies.py` — **não usado** pelas rotas atuais.

## 4. Fluxo de aprovação
- Vet/clínica nascem `is_approved=False`. Só aparecem em público se `True` (filtro em todas as rotas públicas).
- Admin Aprovar = `is_approved=True`.
- **Risco crítico:** "Reprovar" (`reject_vet`/`reject_clinic`) faz **DELETE físico** do registro + reviews — não é ocultação. Conflita com Regras 9–13 e com o Módulo 9.
- Não existe "Visualizar Perfil" no admin (aprova/reprova direto pelos cards).

## 5. Exibição dos atores
- Renderização 100% server-side via Jinja, injetando objetos SQLAlchemy diretamente. Métricas (`avg_rating`, `review_count`) anexadas em runtime.
- Visitante/Tutor/Clínica/Admin veem o mesmo HTML. Não há camada de visibilidade por papel.
- Perfis públicos por slug: `/veterinario/{slug}`, `/clinica/{slug}` (404 se não aprovado).

## 6. Upload e serialização (centrais para a evolução)
- **Upload:** não há endpoint nem storage. Fotos são redimensionadas no navegador (canvas → `toDataURL` JPEG) e gravadas como **data URL base64** em colunas `Text`. Sem S3/Cloudinary.
- **Serialização:** não há serializers Pydantic para conteúdo público. `response_model` só no auth (`Token`). Rotas JSON: `POST /api/auth/*`, `POST /api/reviews`, `PUT /api/perfil/*`, `POST /api/casos-clinicos/*`. Não há "contrato JSON público" a quebrar.

## 7. Busca (`pages.py`)
- `/buscar`, `/buscar/veterinarios`, `/buscar/clinicas`. Filtros cidade/UF/especialidade/texto/24h, ordenado por rating. Sempre `is_approved=True`. Retorna HTML.

## 8. Admin (`/admin`)
- Dashboard único com pendências e listas. Ações: approve/reject/delete de vet, clínica, review, caso, comentário; block/unblock/delete de usuário (trata FKs); `set-badge` (founder); ações em massa.

## 9. Validação de CRMV
- Apenas formato por regex `CRMV-UF NNNNN` (`app/utils/validators.py`). Sem consulta oficial nem revalidação.

## 10. Impacto por módulo futuro

| Módulo | Tabelas impactadas | Rotas/endpoints | Riscos |
|---|---|---|---|
| 1 — Enriquecer vet | Novas: `vet_educations`, links/redes; colunas aditivas em `veterinarians`; especialidades múltiplas (nova tabela ou JSON) | `PUT /api/perfil/veterinarian`, `minha-conta`, perfil vet | `specialty` singular × múltiplas; manter campo antigo oculto; decisão CRMV |
| Selos | `veterinarians`/`clinics`: add `is_verified` | admin | Não confundir com `is_founder` (=Parceiro). Só 2 selos |
| 2 — Disponibilidades | flags booleanas opcionais em `veterinarians` | perfil/minha-conta | Restringir visibilidade (Módulo 6) |
| 3 — Experiência/grafo | Nova `vet_clinic_links` (N:N com cargo/período); manter `clinic_id` | perfis vet/clínica | Duplicação com `clinic_id` legado; fonte de verdade |
| 4 — Conteúdo profissional | Nova `vet_external_links`; ocultar casos (não apagar) | esconder `/casos-clinicos*`; perfil vet | Regra 13: só ocultar |
| 5 — Recomendações | Nova `recommendations` (vet/clínica → vet, moderada) | nova rota + moderação | Distinta de `reviews`; moderação obrigatória |
| 6 — Visibilidade | nenhuma | criar serializações novas; não tocar rotas públicas | Vazar campos de recrutamento |
| 7 — Perfil clínicas | faixas de preço em `clinics` | perfil clínica | Nunca preço exato — só faixa |
| 8 — Piloto/entitlements | Nova `clinic_entitlements` | só admin, oculto | Preparar p/ monetização sem expor |
| 9 — Admin "Visualizar Perfil" | nenhuma | nova rota de preview do perfil publicável | Trocar "reject = delete" por reversível |

## 11. Recomendações pré-evolução
1. "Reprovar" hoje deleta — mudar para estado reversível (Módulo 9), alinhando Regras 9–13.
2. `app/core/dependencies.py` (auth por header) está órfão — manter (Regra 10), apenas registrado.
3. Especialidade do vet: decidir N:N vs JSON, mantendo `specialty` legado oculto.
4. Fotos base64 no banco aumentam o peso da linha — monitorar, não bloqueador.

## Confirmações
- Ambientes: localhost + produção (sem staging).
- Backup: inexistente até esta data — ver `docs/plano_seguranca_modificacoes.md`.
</content>
