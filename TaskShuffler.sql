-- Table: public.solutions

-- DROP TABLE IF EXISTS public.solutions;

CREATE TABLE IF NOT EXISTS public.solutions
(
    solution_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    solution_path text COLLATE pg_catalog."default" NOT NULL,
    page integer NOT NULL,
    CONSTRAINT solutions_pkey PRIMARY KEY (solution_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.solutions
    OWNER to postgres;
-- Index: solutions_uindex

-- DROP INDEX IF EXISTS public.solutions_uindex;

CREATE UNIQUE INDEX IF NOT EXISTS solutions_uindex
    ON public.solutions USING btree
    (solution_id ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.subject_topic

-- DROP TABLE IF EXISTS public.subject_topic;

CREATE TABLE IF NOT EXISTS public.subject_topic
(
    subject_id integer NOT NULL,
    topic_id integer NOT NULL,
    CONSTRAINT subject_topic_pk PRIMARY KEY (subject_id, topic_id),
    CONSTRAINT subject_topic_subject_fk FOREIGN KEY (subject_id)
        REFERENCES public.subjects (subject_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT subject_topic_topic_fk FOREIGN KEY (topic_id)
        REFERENCES public.topics (topic_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.subject_topic
    OWNER to postgres;
-- Index: fki_subject_topic_subject_fk

-- DROP INDEX IF EXISTS public.fki_subject_topic_subject_fk;

CREATE INDEX IF NOT EXISTS fki_subject_topic_subject_fk
    ON public.subject_topic USING btree
    (subject_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: fki_subject_topic_topic_fk

-- DROP INDEX IF EXISTS public.fki_subject_topic_topic_fk;

CREATE INDEX IF NOT EXISTS fki_subject_topic_topic_fk
    ON public.subject_topic USING btree
    (topic_id ASC NULLS LAST)
    TABLESPACE pg_default;


-- Table: public.subjects

-- DROP TABLE IF EXISTS public.subjects;

CREATE TABLE IF NOT EXISTS public.subjects
(
    subject_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    name text COLLATE pg_catalog."default" NOT NULL,
    folder text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT subjects_pkey PRIMARY KEY (subject_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.subjects
    OWNER to postgres;
-- Index: subjects_uindex

-- DROP INDEX IF EXISTS public.subjects_uindex;

CREATE UNIQUE INDEX IF NOT EXISTS subjects_uindex
    ON public.subjects USING btree
    (subject_id ASC NULLS LAST)
    TABLESPACE pg_default;


-- Table: public.task_solution

-- DROP TABLE IF EXISTS public.task_solution;

CREATE TABLE IF NOT EXISTS public.task_solution
(
    task_id integer NOT NULL,
    solution_id integer NOT NULL,
    CONSTRAINT task_solution_pk PRIMARY KEY (task_id, solution_id),
    CONSTRAINT task_solution_solution_fk FOREIGN KEY (solution_id)
        REFERENCES public.solutions (solution_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT task_solution_task_fk FOREIGN KEY (task_id)
        REFERENCES public.tasks (task_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.task_solution
    OWNER to postgres;
-- Index: fki_task_solution_solution_fk

-- DROP INDEX IF EXISTS public.fki_task_solution_solution_fk;

CREATE INDEX IF NOT EXISTS fki_task_solution_solution_fk
    ON public.task_solution USING btree
    (solution_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: fki_task_solution_task_fk

-- DROP INDEX IF EXISTS public.fki_task_solution_task_fk;

CREATE INDEX IF NOT EXISTS fki_task_solution_task_fk
    ON public.task_solution USING btree
    (task_id ASC NULLS LAST)
    TABLESPACE pg_default;


-- Table: public.tasks

-- DROP TABLE IF EXISTS public.tasks;

CREATE TABLE IF NOT EXISTS public.tasks
(
    task_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    task_tex text COLLATE pg_catalog."default" NOT NULL,
    difficulty integer NOT NULL DEFAULT 3,
    CONSTRAINT tasks_pkey PRIMARY KEY (task_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.tasks
    OWNER to postgres;
-- Index: tasks_uindex

-- DROP INDEX IF EXISTS public.tasks_uindex;

CREATE UNIQUE INDEX IF NOT EXISTS tasks_uindex
    ON public.tasks USING btree
    (task_id ASC NULLS LAST)
    TABLESPACE pg_default;


-- Table: public.topic_task

-- DROP TABLE IF EXISTS public.topic_task;

CREATE TABLE IF NOT EXISTS public.topic_task
(
    topic_id integer NOT NULL,
    task_id integer NOT NULL,
    CONSTRAINT topic_task_id PRIMARY KEY (topic_id, task_id),
    CONSTRAINT task_fk FOREIGN KEY (task_id)
        REFERENCES public.tasks (task_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT topic_fk FOREIGN KEY (topic_id)
        REFERENCES public.topics (topic_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.topic_task
    OWNER to postgres;
-- Index: fki_task_fk

-- DROP INDEX IF EXISTS public.fki_task_fk;

CREATE INDEX IF NOT EXISTS fki_task_fk
    ON public.topic_task USING btree
    (task_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: fki_topic_fk

-- DROP INDEX IF EXISTS public.fki_topic_fk;

CREATE INDEX IF NOT EXISTS fki_topic_fk
    ON public.topic_task USING btree
    (topic_id ASC NULLS LAST)
    TABLESPACE pg_default;


-- Table: public.topics

-- DROP TABLE IF EXISTS public.topics;

CREATE TABLE IF NOT EXISTS public.topics
(
    topic_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    name text COLLATE pg_catalog."default" NOT NULL,
    folder text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT topics_pk PRIMARY KEY (topic_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.topics
    OWNER to postgres;
-- Index: topics_uindex

-- DROP INDEX IF EXISTS public.topics_uindex;

CREATE UNIQUE INDEX IF NOT EXISTS topics_uindex
    ON public.topics USING btree
    (topic_id ASC NULLS LAST, topic_id ASC NULLS LAST)
    TABLESPACE pg_default;


