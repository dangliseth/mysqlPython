-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: inventory_database
-- ------------------------------------------------------
-- Server version	9.3.0-commercial

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `audit_tree`
--

LOCK TABLES `audit_tree` WRITE;
/*!40000 ALTER TABLE `audit_tree` DISABLE KEYS */;
/*!40000 ALTER TABLE `audit_tree` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
INSERT INTO `employees` VALUES (1,NULL,'Seth Owen','Dangli','Management Information System','Intern',2),(2,NULL,'Aron','Ramilo','Marketing','Assistant',NULL),(3,NULL,'Cassandra','Lopez','Marketing','Head',NULL),(4,NULL,'Joydee','Ricafort','Library','Librarian',NULL),(5,NULL,'Joyce','Borbon','Library','Librarian',NULL),(6,NULL,'Joan','Ugdamina','Library','Librarian',NULL),(7,NULL,'Michelle','Esteban','Library','Head',NULL),(8,NULL,'Rhia','Vicente','Senior High School','Faculty',NULL),(9,NULL,'Rio','Alajar','Senior High School','Faculty',NULL),(10,NULL,'Joseph Paul','Loveria','Management Information System','Supervisor',NULL),(11,NULL,'Genaro','Moloboco','Management Information System','Head',NULL),(12,NULL,'Ariel','Serencio','Registrar','Registrar',NULL),(13,NULL,'Cherry','Sevidal','Registrar','Registrar',NULL),(14,NULL,'Floriam','Argawanon','Registrar','Registrar',NULL),(15,NULL,'Myra','Ramos','Registrar','Head',NULL),(16,NULL,'Dennis','Salvador','Registrar','Registrar',NULL),(17,NULL,'Janella','Gatchalian','School of Engineering','Secretary',NULL),(18,NULL,'Shaira','Baduya','School of Architecture','Secretary',NULL),(19,NULL,'Ramon','Ducusin','General Services','Head',NULL),(20,NULL,'Jun','N/A','General Services','Maintainance',NULL),(21,NULL,'Omarcy','Llave','Human Resources','Assistant',NULL),(22,NULL,'Ceejae','Andrade','Human Resources','Assistant',NULL),(23,NULL,'Edward','Bora','Human Resources','Assistant',NULL),(24,NULL,'Mar','Isic','Human Resources','Head',NULL),(25,NULL,'Anna','Romero','Accounting','Head',NULL),(26,NULL,'Astrid Gail','De Guzman','Accounting','Assistant',NULL),(27,NULL,'Roseller','Soriano','Accounting','Assistant',NULL),(28,NULL,'Lorena','Gregorio','Accounting','Assistant',NULL),(29,NULL,'Pia','Caccam','Center for Student Affairs and Wellbeing','Consultant',NULL),(30,NULL,'Severino','Angelano','Center for Student Affairs and Wellbeing','Assistant',NULL),(31,NULL,'Elainne','Alajar','Center for Student Affairs and Wellbeing','Deputy Head',NULL),(32,NULL,'Margarette','Dela Cruz','Student Engagement and Services Office','OIC - Head',NULL),(33,NULL,'Junnelyne','Cagobcob','Accounting','Cashier',NULL),(34,NULL,'Paula','Navalta','Office of the President','Secretary',NULL),(35,NULL,'Lucille','Ortile','Office of the President','Vice President',NULL),(36,NULL,'Leo','Abrilla','School of Criminal Justice','Secretary',NULL),(37,NULL,'Charmaine','Pineda','School of Law','Secretary',NULL),(38,NULL,'Teresa Marie','Cacdac','School of Law','Secretary',NULL),(39,NULL,'Galahad Pe','Benito','School of Law','Secretary',NULL),(40,NULL,'Tonette','Nuñez','School of Law','Secretary',NULL),(41,NULL,'Feliza','Hernandez','School of Graduate Studies','Secretary',NULL),(42,NULL,'Joy Anne','Vicente','School of Business','Secretary',NULL),(43,NULL,'Eden','Ferrer','School of Business','Secretary',NULL),(44,NULL,'Joana','Jose','Senior High School','Principal',NULL),(45,NULL,'Ms. Mina','Vizcarra','Quality Assurance and Compliance Office','Consultant',NULL),(46,NULL,'Jonathan','Pasamonte','Admission','Admission',NULL),(47,NULL,'Annymay','N/A TEMPORARY','Registrar','Registrar',NULL),(48,NULL,'Rossana','Dangli','Registrar','Registrar',NULL);
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `item_assignment_history`
--

LOCK TABLES `item_assignment_history` WRITE;
/*!40000 ALTER TABLE `item_assignment_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `item_assignment_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES ('MLQU-0000001',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',5,'LEDe','24\"',NULL,2,'assigned'),('MLQU-0000002',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i7; 10gb; RAM; 500gb HDD',NULL,2,'assigned'),('MLQU-0000003',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,46,'assigned'),('MLQU-0000004',NULL,'Samsung LS19PUYKF','LS19PUYKF','Samsung',1,NULL,'19\"',NULL,10,'assigned'),('MLQU-0000006',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,46,'assigned'),('MLQU-0000007',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,23,'assigned'),('MLQU-0000010',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD; NVIDIA GT630',NULL,46,'assigned'),('MLQU-0000012',NULL,'Acer P166HQL','P166HQL','Acer',1,NULL,'16\"',NULL,46,'assigned'),('MLQU-0000013',NULL,'Acer P166HQL','P166HQL','Acer',1,NULL,'16\"',NULL,46,'assigned'),('MLQU-0000014',NULL,'Epson L120','L120','Epson',3,NULL,'inkjet',NULL,2,'assigned'),('MLQU-0000015',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,10,'assigned'),('MLQU-0000016',NULL,'Samsung LS20B300BS','LS20B300BS','Samsung',1,NULL,'20\"',NULL,2,'assigned'),('MLQU-0000017',NULL,'Epson L210','L210','Epson',3,NULL,'inkjet',NULL,46,'assigned'),('MLQU-0000018',NULL,'BNP CX-D80HS','CX-D80HS','BNP',3,NULL,'card printer',NULL,10,'assigned'),('MLQU-0000019',NULL,'Clone',NULL,'Clone',2,'ID Computer','Intel i7; 16gb RAM',NULL,10,'assigned'),('MLQU-0000020',NULL,'Samsung LS20B300BS','LS20B300BS','Samsung',1,NULL,'20\"',NULL,46,'assigned'),('MLQU-0000021',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,2,'assigned'),('MLQU-0000022',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,46,'assigned'),('MLQU-0000023',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,46,'assigned'),('MLQU-0000024',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,10,'assigned'),('MLQU-0000025',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,2,'assigned'),('MLQU-0000026',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,46,'assigned'),('MLQU-0000027',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 150GB HDD',NULL,41,'assigned'),('MLQU-0000028',NULL,'Samsung LS20B300BS','LS20B300BS','Samsung',1,NULL,'20\"',NULL,23,'assigned'),('MLQU-0000029',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,23,'assigned'),('MLQU-0000030',NULL,'Brother DCP-L2540DW','DCP-L2540DW','Brother',3,NULL,'inkjet',NULL,23,'assigned'),('MLQU-0000031',NULL,'Samsung LS19D300NY','LS19D300NY','Samsung',1,NULL,'19\"',NULL,41,'assigned'),('MLQU-0000032',NULL,'Eco Power',NULL,'Eco Power',4,NULL,'relay type',NULL,41,'assigned'),('MLQU-0000033',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,47,'assigned'),('MLQU-0000034',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,NULL,'active'),('MLQU-0000035',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,NULL,'active'),('MLQU-0000036',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,NULL,'active'),('MLQU-0000037',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 1TB HDD',NULL,NULL,'active'),('MLQU-0000038',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i7; 16GB RAM; 1TB HDD',NULL,NULL,'active'),('MLQU-0000039',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 120GB SSD',NULL,NULL,'active'),('MLQU-0000040',NULL,'Dell',NULL,'Dell',5,NULL,'Intel Core 2 Duo; 2GB RAM; 160GB HDD',NULL,NULL,'active'),('MLQU-0000041',NULL,'Protec',NULL,'Protec',4,NULL,'relay type',NULL,NULL,'active'),('MLQU-0000042',NULL,'Sunstar',NULL,'Sunstar',4,NULL,'relay type',NULL,NULL,'active'),('MLQU-0000043',NULL,'Secure',NULL,'Secure',4,NULL,'relay type',NULL,NULL,'active'),('MLQU-0000044',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,NULL,'active'),('MLQU-0000045',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,NULL,'active'),('MLQU-0000046',NULL,'Giant Power',NULL,'Giant Power',4,NULL,'relay type',NULL,NULL,'active'),('MLQU-0000047',NULL,'Protec',NULL,'Protec',4,NULL,'relay type',NULL,47,'assigned'),('MLQU-0000048',NULL,'Protec',NULL,'Protec',4,NULL,'relay type',NULL,NULL,'active'),('MLQU-0000049',NULL,'Acer V206HQL','V206HQL','Acer',1,NULL,'20\"',NULL,47,'assigned'),('MLQU-0000050',NULL,'Samsung LS19PUYKF','LS19PUYKF','Samsung',1,NULL,'19\"',NULL,NULL,'active'),('MLQU-0000051',NULL,'Samsung LS19PUYKF','LS19PUYKF','Samsung',1,NULL,'19\"',NULL,NULL,'active'),('MLQU-0000052',NULL,'Acer V206HQL','V206HQL','Acer',1,NULL,'20\"',NULL,NULL,'active'),('MLQU-0000053',NULL,'Samsung LS20B300BS','LS20B300BS','Samsung',1,NULL,'20\"',NULL,NULL,'active'),('MLQU-0000054',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LEDe','24\"',NULL,NULL,'active'),('MLQU-0000055',NULL,'Samsung LS19A300BS','LS19A300BS','Samsung',1,NULL,'19\"',NULL,NULL,'active'),('MLQU-0000056',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,NULL,'active'),('MLQU-0000057',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,NULL,'active'),('MLQU-0000058',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,NULL,'active'),('MLQU-0000059',NULL,'Epson L14150','L14150','Epson',3,NULL,'inkjet',NULL,NULL,'active'),('MLQU-0000060',NULL,'Epson L360','L360','Epson',3,NULL,'inkjet',NULL,NULL,'active'),('MLQU-0000061',NULL,'Cisco Linksys E1250','Linksys E1250','Cisco',5,NULL,'AP',NULL,NULL,'active'),('MLQU-0000062',NULL,'DLink DES 1024D','DES 1024D','DLink',6,NULL,'switch',NULL,NULL,'active');
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `items_categories`
--

LOCK TABLES `items_categories` WRITE;
/*!40000 ALTER TABLE `items_categories` DISABLE KEYS */;
INSERT INTO `items_categories` VALUES (1,'assets'),(2,'test');
/*!40000 ALTER TABLE `items_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `subcategories`
--

LOCK TABLES `subcategories` WRITE;
/*!40000 ALTER TABLE `subcategories` DISABLE KEYS */;
INSERT INTO `subcategories` VALUES (1,'monitor',1),(2,'system unit',1),(3,'printer',1),(4,'avr',1),(5,'access point',1),(6,'switch',1);
/*!40000 ALTER TABLE `subcategories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `user_accounts`
--

LOCK TABLES `user_accounts` WRITE;
/*!40000 ALTER TABLE `user_accounts` DISABLE KEYS */;
INSERT INTO `user_accounts` VALUES (1,'admin','scrypt:32768:8:1$DnkE7P7s13Wt6dqb$f65c7ba1efab91b825f4d89b7aa9d64e444daa3ed53cf9ed3a23e77d63e21aba3a2f6f3d7a816e2116e4c2c2cae145835b34423ab47340aaf5cd78bd8d0205db','admin'),(2,'user','scrypt:32768:8:1$R5PVwfI4RywZCo3q$a8907a0bff5280df6a88aead39524bbe47a02dc3f0bbf53279486bcadf3901e5b201de6ec081f707bfa45271972126b5e256c977cb8d9c6805c31454f978d31e','user'),(3,'MIS','scrypt:32768:8:1$4PH5ApPCjAJ5IFjv$a6b7ab66a04dbbd4183cc4625dd4e177ca804530131f236b86825180de193ff358c387b35f108e0429bf15e1d7fa51baaaef4f1ff72d636664cefaa9ad193094','admin'),(5,'user1','scrypt:32768:8:1$1cp4IRQbYB89AIAL$ab1ed698b175e9fa8a18d65ea354ed51ff1bfb6255a8b498ea5d497c980e55416d7ae9cb13e6125776e1ef54e6f247f20e09805622ba99702af9b4d58325ab95','user');
/*!40000 ALTER TABLE `user_accounts` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-28 17:02:09
