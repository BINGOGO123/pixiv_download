-- 数据库格式，供参考

drop database if exists pixiv_download;

create database pixiv_download;

use pixiv_download;

create table file (
  url varchar(1000) not null,
  storage_path varchar(500) primary key,
  md5 char(32) not null,
  download_time datetime default CURRENT_TIMESTAMP
);

-- alter table file add md5 char(32) not null;