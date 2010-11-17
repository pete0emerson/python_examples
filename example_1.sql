DROP TABLE IF EXISTS `example1`;

CREATE TABLE `example1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

LOCK TABLES `example1` WRITE;
INSERT INTO `example1` VALUES (1,'This is my first title','2010-10-01 01:00:00');
INSERT INTO `example1` VALUES (2,'This is my second title','2010-10-02 02:00:00');
INSERT INTO `example1` VALUES (3,'This is my third title','2010-10-03 03:00:00');
UNLOCK TABLES;
