DROP DATABASE IF EXISTS familytreedb;
CREATE DATABASE familytreedb;
CREATE USER 'familytreedefault'@'localhost' IDENTIFIED BY 'familytreedefaultpwd';
GRANT ALL PRIVILEGES ON *.* TO 'familytreedefault'@'localhost' IDENTIFIED BY 'familytreedefaultpwd' WITH GRANT OPTION;
FLUSH PRIVILEGES;
