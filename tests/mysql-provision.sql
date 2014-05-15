create database if not exists lordb_test ; use lordb_test ;

drop table if exists users ;
create table users_test (
	id smallint unsigned not null PRIMARY KEY AUTO_INCREMENT ,
	name varchar(100) not null ,
	age tinyint unsigned not null ,
	creation_date date not null
) ;