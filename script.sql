DROP DATABASE IF EXISTS 'familytreedb';
CREATE DATABASE 'familytreedb';
CREATE USER 'familytreedefault'@'localhost' IDENTIFIED BY 'familytreedefaultpwd';
USE 'mysql';
GRANT ALL PRIVILEGES ON 'familytreedb'.* TO 'familytreedefault'@'localhost' IDENTIFIED BY 'familytreedefaultpwd WITH GRANT OPTION;
FLUSH PRIVILEGES;
