create table if not exists subjects
(
    subject_id integer generated always as identity
        constraint subjects_pkey
            primary key,
    name       text not null
);

create unique index if not exists subjects_uindex
    on subjects (subject_id);

create table if not exists topics
(
    topic_id integer generated always as identity
        constraint topics_pk
            primary key,
    name     text not null,
    folder   text not null
);

create unique index if not exists topics_uindex
    on topics (topic_id, topic_id);

create table if not exists tasks
(
    task_id    integer generated always as identity
        constraint tasks_pkey
            primary key,
    task_tex   text              not null,
    difficulty integer default 3 not null,
    filetype   text              not null
);

create unique index if not exists tasks_uindex
    on tasks (task_id);

create table if not exists subject_topic
(
    subject_id integer not null
        constraint subject_topic_subject_fk
            references subjects,
    topic_id   integer not null
        constraint subject_topic_topic_fk
            references topics,
    constraint subject_topic_pk
        primary key (subject_id, topic_id)
);

create index if not exists fki_subject_topic_subject_fk
    on subject_topic (subject_id);

create index if not exists fki_subject_topic_topic_fk
    on subject_topic (topic_id);

create table if not exists topic_task
(
    topic_id integer not null
        constraint topic_fk
            references topics,
    task_id  integer not null
        constraint task_fk
            references tasks,
    constraint topic_task_id
        primary key (topic_id, task_id)
);

create index if not exists fki_task_fk
    on topic_task (task_id);

create index if not exists fki_topic_fk
    on topic_task (topic_id);


