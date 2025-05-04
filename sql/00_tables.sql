CREATE TABLE feeds (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
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
    tsv TSVECTOR,
    tsv_simple TSVECTOR
);

DROP TRIGGER IF EXISTS tsvectorupdate ON articles;

CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
ON articles FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(tsv, 'pg_catalog.italian', title, content);

DROP TRIGGER IF EXISTS tsvectorsimpleupdate ON articles;

CREATE TRIGGER tsvectorsimpleupdate BEFORE INSERT OR UPDATE
ON articles FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(tsv_simple, 'pg_catalog.simple', title_original, content_original);
