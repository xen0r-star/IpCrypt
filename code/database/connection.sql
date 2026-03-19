create database if not exists connectionIpCrypt character set = 'utf8';

create table if not exists userConnectionIpCrypt(
    userName varchar(15) not null,
    userPassword(255) varchar not null,
    isAdmin boolean default 0,
    primary key(userName)
)engine=innodb;

insert into userConnectionIpCrypt(userName,userPassword,isAdmin) values
('nomAdmin','passwordhash',true);

