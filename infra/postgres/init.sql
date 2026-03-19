-- Inicialização do banco de dados
-- Este script roda uma única vez quando o container do PostgreSQL é criado

-- Extensão para busca vetorial (MVP 4 — RAG)
-- Será habilitada quando pgvector estiver instalado na imagem
-- CREATE EXTENSION IF NOT EXISTS vector;

-- Índices adicionais podem ser criados aqui conforme necessário
-- As tabelas são criadas via Alembic ou SQLAlchemy metadata.create_all

-- Garantir timezone correto
SET timezone = 'UTC';
