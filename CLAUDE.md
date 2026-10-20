# Lyceum — Backend

Pitch: convierte apuntes de clase en un tutor consultable — preguntas en lenguaje natural con cita a la fuente exacta, y genera cuestionarios de repaso sobre lo ya estudiado.

Pivot de ContextForge (`../ContextForge`), reutilizando su pipeline de RAG híbrido (embeddings + búsqueda vectorial + full-text con RRF), pero con multiusuario real, organización por asignatura/tema y modo de repaso activo. Audiencia: estudiantes en general, no solo el autor — de ahí que haya autenticación real en vez de ser una app de escritorio de un solo usuario.

## Decisiones de arquitectura

- App web hospedada (no desktop/local): PostgreSQL + pgvector, FastAPI, JWT (email/password) para auth.
- Monolito modular — correcto para esta escala, no hay necesidad de microservicios. El límite real de rendimiento no es la estructura, es si el embedding/generación se ejecutan de forma bloqueante.
- Clave de Anthropic propia del servidor (no que cada usuario traiga la suya). Intención futura de monetizar por suscripción, pero el MVP de portfolio NO integra billing real — solo el gancho (`User.plan` default `"free"` + tabla `UsageLog` para limitar uso mensual).
- SQLAlchemy + Alembic en vez del SQL crudo que usa ContextForge (con 7+ tablas relacionadas, SQL manual se vuelve frágil).

## Estructura

```
app/
├── main.py, config.py
├── db/ (session.py, base.py, models/ por entidad)
├── schemas/ (Pydantic, por recurso)
├── auth/ (security.py, dependencies.py con get_current_user, router.py)
├── routers/ (subjects.py, notes.py, query.py, quizzes.py)
├── services/ (ingestion.py, embeddings.py, retrieval/hybrid.py, generation/answer.py, quiz_generator.py)
└── alembic/ (migraciones)
```

## Modelo de datos

`User(id, email, password_hash, plan, created_at)` · `Subject(id, user_id, name, created_at)` · `Note(id, user_id, subject_id, title, topic, source_type, original_filename, status, created_at)` · `Chunk(id, note_id, text, chunk_index, embedding, created_at)` · `Conversation(id, user_id, subject_id)` + `Message(id, conversation_id, role, content, sources)` · `Quiz(id, user_id, subject_id, topic)` + `QuizQuestion(id, quiz_id, question, correct_answer, source_chunk_id)` + `QuizAttempt(id, quiz_question_id, user_answer, is_correct)` · `UsageLog(id, user_id, action, created_at)`.

`user_id` se duplica en tablas de primer nivel (no solo vía `Note`) a propósito, para aislamiento directo sin depender de JOINs.

`Note.status: pending|processing|ready|failed` — una nota con `status != ready` nunca es visible para `/query` ni `/quizzes`, para evitar respuestas basadas en datos a medio indexar.

Embeddings: `sentence-transformers/all-MiniLM-L6-v2`, dimensión 384 (igual que ContextForge).

## Endpoints

Todos requieren `Authorization: Bearer <token>` excepto `/auth/register` y `/auth/login`. El `user_id` usado para filtrar **siempre** viene del token verificado vía `get_current_user`, nunca de un parámetro/body/query del cliente.

- Auth: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- Subjects: `GET /subjects`, `POST /subjects`, `DELETE /subjects/{id}` (bloquea si tiene notas asociadas)
- Notes: `GET /notes?subject_id=`, `POST /notes` (multipart file o JSON manual, responde 202 con `status=pending`), `GET /notes/{id}`, `DELETE /notes/{id}`
- Query: `POST /query` (filtra solo notas `status=ready`, 429 si excede límite de uso), `GET /conversations?subject_id=`, `GET /conversations/{id}/messages`
- Quizzes: `POST /quizzes` (nunca devuelve `correct_answer` al cliente), `GET /quizzes/{id}`, `POST /quizzes/{id}/attempts`
- Usage: `GET /usage/me`

## Pipeline de ingestión

`POST /notes` responde de inmediato (202, `status=pending`); el procesamiento real (extracción → chunking → embeddings → insert) corre en background (`BackgroundTasks` para empezar). Al terminar, se actualiza a `status=ready` o `failed`.

## Checklist de seguridad JWT

- El algoritmo de firma se especifica explícitamente al decodificar (`algorithms=["HS256"]"`) — nunca abierto, para evitar confusión de algoritmo o `alg: none`.
- `SECRET_KEY` aleatoria y larga, solo en `.env`, nunca en el repo.
- Todo token lleva `exp` corto (1h por defecto); sesiones largas usarían refresh tokens, no tokens sin expiración.
- Un JWT no se puede modificar sin invalidar su firma — el riesgo real nunca es "editar el token", es confiar en datos del cliente en vez del token verificado (por eso ningún endpoint acepta `user_id` como input).

## Roadmap de aprendizaje

Este proyecto es un vehículo para aprender tecnologías nuevas, no solo un MVP mínimo: no descartar una tecnología solo porque "no se necesita aún a esta escala" — anotarla aquí para implementarla cuando llegue su turno.

- [ ] Celery + Redis como cola de tareas para la ingestión (reemplazando `BackgroundTasks`), con reintentos y persistencia de trabajos ante reinicio del servidor.

## Estado actual

Implementado: estructura base, modelos SQLAlchemy completos, `auth/` (`register`/`login`/`me`) y `subjects` (`GET`/`POST`/`DELETE`).

Pendiente: `notes` (incluyendo pipeline de ingestión), `query` (hybrid search + generación), `quizzes`, `usage`, migraciones de Alembic (aún no inicializado), tests.
