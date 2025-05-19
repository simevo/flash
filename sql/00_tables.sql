CREATE TABLE feeds (
    id INTEGER GENERATED ALWAYS AS IDENTITY (MINVALUE 0 START WITH 0) PRIMARY KEY,
    homepage text NOT NULL,
    url text NOT NULL,
    language text NOT NULL,
    title text NOT NULL,
    license text,
    active boolean DEFAULT false,
    last_polled timestamp with time zone,
    incomplete boolean DEFAULT false,
    tags text[] DEFAULT ARRAY[]::text[],
    salt_url boolean DEFAULT false,
    rating integer,
    premium boolean DEFAULT false,
    cookies text,
    exclude text,
    main text,
    tor boolean DEFAULT false,
    asy boolean DEFAULT true,
    script text,
    frequency text
);

CREATE TABLE articles (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stamp timestamp with time zone DEFAULT now() NOT NULL,
    author text,
    title_original text,
    title text,
    content_original text,
    content text,
    language text,
    url text,
    feed_id integer REFERENCES feeds(id),
    tsv TSVECTOR
);

DROP TRIGGER IF EXISTS tsvectorupdate ON articles;

CREATE OR REPLACE FUNCTION articles_tsv_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.tsv := to_tsvector('pg_catalog.simple',
        coalesce(NEW.title, NEW.title_original) || ' ' ||
        coalesce(NEW.content, NEW.content_original)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tsvectorupdate
BEFORE INSERT OR UPDATE ON articles
FOR EACH ROW EXECUTE PROCEDURE articles_tsv_trigger();

-- UPDATE articles
-- SET tsv = to_tsvector(
--   'pg_catalog.simple',
--   COALESCE(title, title_original) || ' ' || COALESCE(content, content_original)
-- );

CREATE INDEX articles_tsv_idx ON articles USING GIN (tsv);
