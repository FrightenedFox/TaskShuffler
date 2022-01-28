create table subjects
(
    subject_id integer generated always as identity
        primary key,
    name       text not null
);

alter table subjects
    owner to postgres;

create unique index subjects_uindex
    on subjects (subject_id);

create table topics
(
    topic_id integer generated always as identity
        constraint topics_pk
            primary key,
    name     text not null,
    folder   text not null
);

alter table topics
    owner to postgres;

create unique index topics_uindex
    on topics (topic_id, topic_id);

create table tasks
(
    task_id    integer generated always as identity
        primary key,
    task_tex   text              not null,
    difficulty integer default 3 not null
);

alter table tasks
    owner to postgres;

create unique index tasks_uindex
    on tasks (task_id);

create table subject_topic
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

alter table subject_topic
    owner to postgres;

create index fki_subject_topic_subject_fk
    on subject_topic (subject_id);

create index fki_subject_topic_topic_fk
    on subject_topic (topic_id);

create table topic_task
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

alter table topic_task
    owner to postgres;

create index fki_task_fk
    on topic_task (task_id);

create index fki_topic_fk
    on topic_task (topic_id);
