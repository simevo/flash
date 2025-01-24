CREATE TABLE feeds (
    id integer NOT NULL PRIMARY KEY,
    homepage text NOT NULL,
    url text NOT NULL,
    language text NOT NULL,
    title text NOT NULL,
    license text,
    icon text NOT NULL,
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
    iconblob bytea,
    script text,
    frequency text
);

CREATE TABLE public.articles (
    id integer NOT NULL PRIMARY KEY,
    stamp timestamp with time zone DEFAULT now() NOT NULL,
    author text,
    title_original text,
    title text,
    content_original text,
    content text,
    language text,
    url text,
    comments integer DEFAULT 0,
    feed_id integer REFERENCES feeds(id),
    topic_id integer
);
