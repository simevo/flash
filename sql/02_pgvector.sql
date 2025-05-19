CREATE EXTENSION vector;

ALTER TABLE articles ADD COLUMN paraphrase_multilingual_mpnet_base_v2 halfvec(768);
ALTER TABLE articles ADD COLUMN use_cmlm_multilingual halfvec(768);

SET maintenance_work_mem='4GB';
CREATE INDEX
  ON articles
  USING hnsw (use_cmlm_multilingual halfvec_cosine_ops)
  WITH (
      m = 24,
      ef_construction = 200
  );

CREATE ROLE no_triggers;
ALTER ROLE no_triggers WITH LOGIN;
ALTER ROLE no_triggers WITH PASSWORD 'no_triggers';
ALTER ROLE no_triggers SET session_replication_role = 'replica';
GRANT SELECT ON articles TO no_triggers;
GRANT UPDATE ON articles TO no_triggers;
