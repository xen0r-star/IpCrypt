create database if not exists connectionIpCrypt character set = 'utf8';

create table if not exists userConnectionIpCrypt(
    userId int not null auto increment
    userName varchar(15) not null,
    userPassword(255) varchar not null,
    isAdmin boolean default 0,
    primary key(userName)
)engine=innodb;

insert into userConnectionIpCrypt() values
();

