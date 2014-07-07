create database if not exists loremdb_test ; use loremdb_test ;

drop table if exists users ;
create table users (
    id smallint unsigned not null PRIMARY KEY AUTO_INCREMENT ,
    name varchar(25) not null ,
    age tinyint unsigned not null ,
    sex enum('male','female') NOT NULL,
    roles set('user','admin') NOT NULl DEFAULT 'user',
    creation_date date not null
) ;