create database if not exists lordb ; use lordb ;

drop table if exists users ;
create table users (
	id smallint unsigned not null PRIMARY KEY AUTO_INCREMENT ,
	name varchar(100) not null ,
	age tinyint unsigned not null ,
	creation_date date not null
) ;