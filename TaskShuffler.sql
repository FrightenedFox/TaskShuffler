create table subjects
(
    subject_id integer generated always as identity
        constraint subjects_pkey
            primary key,
    name       text not null
);

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

create unique index topics_uindex
    on topics (topic_id, topic_id);

create table tasks
(
    task_id          integer generated always as identity
        constraint tasks_pkey
            primary key,
    task_tex         text              not null,
    difficulty       integer default 3 not null,
    numerical_answer double precision
);

create unique index tasks_uindex
    on tasks (task_id);

create unique index tasks_task_tex_uindex
    on tasks (task_tex);

create table subject_topic
(
    subject_id integer not null
        constraint subject_topic_subject_fk
            references subjects
            on update cascade on delete restrict,
    topic_id   integer not null
        constraint subject_topic_topic_fk
            references topics
            on update cascade on delete restrict,
    constraint subject_topic_pk
        primary key (subject_id, topic_id)
);

create index fki_subject_topic_subject_fk
    on subject_topic (subject_id);

create index fki_subject_topic_topic_fk
    on subject_topic (topic_id);

create table topic_task
(
    topic_id integer not null
        constraint topic_fk
            references topics
            on update cascade on delete restrict,
    task_id  integer not null
        constraint task_fk
            references tasks
            on update cascade on delete restrict,
    constraint topic_task_id
        primary key (topic_id, task_id)
);

create index fki_task_fk
    on topic_task (task_id);

create index fki_topic_fk
    on topic_task (topic_id);

create table solutions
(
    solution_id       integer generated always as identity
        constraint solutions_pk
            primary key,
    task_id           integer not null
        constraint solution_task_fk
            references tasks
            on update cascade on delete cascade,
    solution_filetype text    not null
);

create unique index solutions_solution_id_uindex
    on solutions (solution_id);


