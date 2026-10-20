# Lyceum — Backend

Asistente de estudio que convierte apuntes de clase en una base de conocimiento consultable: preguntas en lenguaje natural con cita a la fuente exacta, y generación de cuestionarios de repaso.

Pivot de [ContextForge](../ContextForge) reutilizando su pipeline de RAG híbrido (embeddings + búsqueda vectorial + full-text), ahora con multiusuario, asignaturas/temas y modo de repaso activo.

## Stack

FastAPI · PostgreSQL + pgvector · SQLAlchemy + Alembic · JWT (PyJWT + passlib) · sentence-transformers · Anthropic (LLM principal) / Ollama (dev opcional).

## Estado

Estructura base y módulo de autenticación (`/auth/register`, `/auth/login`, `/auth/me`) y de asignaturas (`/subjects`) implementados. Pendiente: `notes`, `query`, `quizzes`, `usage`, pipeline de ingestión en background y migraciones de Alembic.

Ver `CLAUDE.md` para el diseño completo (modelo de datos, endpoints, checklist de seguridad, roadmap de aprendizaje).
