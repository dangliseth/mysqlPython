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
-- Table structure for table `audit_tree`
--

DROP TABLE IF EXISTS `audit_tree`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_tree` (
  `id` int NOT NULL,
  `item` int DEFAULT NULL,
  `user` int DEFAULT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_tree`
--

LOCK TABLES `audit_tree` WRITE;
/*!40000 ALTER TABLE `audit_tree` DISABLE KEYS */;
/*!40000 ALTER TABLE `audit_tree` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees` (
  `employee_id` int NOT NULL,
  `employee_number` varchar(45) DEFAULT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `department` varchar(45) NOT NULL,
  `position` varchar(45) NOT NULL,
  `user_account` int DEFAULT NULL,
  PRIMARY KEY (`employee_id`),
  UNIQUE KEY `user_account_UNIQUE` (`user_account`),
  UNIQUE KEY `employee_number_UNIQUE` (`employee_number`),
  KEY `user_account_idx` (`user_account`),
  CONSTRAINT `user_account` FOREIGN KEY (`user_account`) REFERENCES `user_accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
INSERT INTO `employees` VALUES (1,NULL,'Seth Owen','Dangli','Management Information System','Intern',2),(2,NULL,'Aron','Ramilo','Marketing','Assistant',NULL),(3,NULL,'Cassandra','Lopez','Marketing','Head',NULL),(4,NULL,'Joydee','Ricafort','Library','Librarian',NULL),(5,NULL,'Joyce','Borbon','Library','Librarian',NULL),(6,NULL,'Joan','Ugdamina','Library','Librarian',NULL),(7,NULL,'Michelle','Esteban','Library','Head',NULL),(8,NULL,'Rhia','Vicente','Senior High School','Faculty',NULL),(9,NULL,'Rio','Alajar','Senior High School','Faculty',NULL),(10,NULL,'Joseph Paul','Loveria','Management Information System','Supervisor',NULL),(11,NULL,'Genaro','Moloboco','Management Information System','Head',NULL),(12,NULL,'Ariel','Serencio','Registrar','Registrar',NULL),(13,NULL,'Cherry','Sevidal','Registrar','Registrar',NULL),(14,NULL,'Floriam','Argawanon','Registrar','Registrar',NULL),(15,NULL,'Myra','Ramos','Registrar','Head',NULL),(16,NULL,'Dennis','Salvador','Registrar','Registrar',NULL),(17,NULL,'Janella','Gatchalian','School of Engineering','Secretary',NULL),(18,NULL,'Shaira','Baduya','School of Architecture','Secretary',NULL),(19,NULL,'Ramon','Ducusin','General Services','Head',NULL),(20,NULL,'Jun','N/A','General Services','Maintainance',NULL),(21,NULL,'Omarcy','Llave','Human Resources','Assistant',NULL),(22,NULL,'Ceejae','Andrade','Human Resources','Assistant',NULL),(23,NULL,'Edward','Bora','Human Resources','Assistant',NULL),(24,NULL,'Mar','Isic','Human Resources','Head',NULL),(25,NULL,'Anna','Romero','Accounting','Head',NULL),(26,NULL,'Astrid Gail','De Guzman','Accounting','Assistant',NULL),(27,NULL,'Roseller','Soriano','Accounting','Assistant',NULL),(28,NULL,'Lorena','Gregorio','Accounting','Assistant',NULL),(29,NULL,'Pia','Caccam','Center for Student Affairs and Wellbeing','Consultant',NULL),(30,NULL,'Severino','Angelano','Center for Student Affairs and Wellbeing','Assistant',NULL),(31,NULL,'Elainne','Alajar','Center for Student Affairs and Wellbeing','Deputy Head',NULL),(32,NULL,'Margarette','Dela Cruz','Student Engagement and Services Office','OIC - Head',NULL),(33,NULL,'Junnelyne','Cagobcob','Accounting','Cashier',NULL),(34,NULL,'Paula','Navalta','Office of the President','Secretary',NULL),(35,NULL,'Lucille','Ortile','Office of the President','Vice President',NULL),(36,NULL,'Leo','Abrilla','School of Criminal Justice','Secretary',NULL),(37,NULL,'Charmaine','Pineda','School of Law','Secretary',NULL),(38,NULL,'Teresa Marie','Cacdac','School of Law','Secretary',NULL),(39,NULL,'Galahad Pe','Benito','School of Law','Secretary',NULL),(40,NULL,'Tonette','Nuñez','School of Law','Secretary',NULL),(41,NULL,'Feliza','Hernandez','School of Graduate Studies','Secretary',NULL),(42,NULL,'Joy Anne','Vicente','School of Business','Secretary',NULL),(43,NULL,'Eden','Ferrer','School of Business','Secretary',NULL),(44,NULL,'Joana','Jose','Senior High School','Principal',NULL),(45,NULL,'Ms. Mina','Vizcarra','Quality Assurance and Compliance Office','Consultant',NULL),(46,NULL,'Jonathan','Pasamonte','Admission','Admission',NULL),(47,NULL,'Annymay','N/A TEMPORARY','Registrar','Registrar',NULL),(48,NULL,'Rossana','Dangli','Registrar','Registrar',NULL),(49,NULL,'April','unknown (PLS. CHANGE)','Senior High School','Faculty',NULL),(50,NULL,'Ar Ar','incomplete','Accounting','Assistant',NULL),(51,NULL,'Lala','Generales','School of Business','Dean',NULL),(52,NULL,'Vincent','incomplete','Center for Student Affairs and Wellbeing','Assistant',NULL),(53,NULL,'Margarette Ann','Dela Cruz','Student Engagement and Services Office','Head',NULL);
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item_assignment_history`
--

DROP TABLE IF EXISTS `item_assignment_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_assignment_history` (
  `history_id` int NOT NULL AUTO_INCREMENT,
  `item` varchar(32) NOT NULL,
  `employee` int DEFAULT NULL,
  `assigned_date` datetime NOT NULL,
  `removed_date` datetime DEFAULT NULL,
  PRIMARY KEY (`history_id`),
  KEY `item_assignment_history_ibfk_2` (`employee`) /*!80000 INVISIBLE */,
  CONSTRAINT `item_assignment_history_ibfk_2` FOREIGN KEY (`employee`) REFERENCES `employees` (`employee_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=436 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item_assignment_history`
--

LOCK TABLES `item_assignment_history` WRITE;
/*!40000 ALTER TABLE `item_assignment_history` DISABLE KEYS */;
INSERT INTO `item_assignment_history` VALUES (434,'MLQU-0000186',44,'2025-07-29 11:55:22',NULL),(435,'MLQU-0000187',44,'2025-07-29 11:56:39',NULL);
/*!40000 ALTER TABLE `item_assignment_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `item_id` varchar(12) NOT NULL,
  `serial_number` varchar(70) DEFAULT NULL,
  `item_name` varchar(75) NOT NULL,
  `model_name` varchar(75) DEFAULT NULL,
  `brand_name` varchar(45) NOT NULL,
  `subcategory` int NOT NULL,
  `description` mediumtext,
  `specification` longtext NOT NULL,
  `comment` varchar(75) DEFAULT NULL,
  `employee` int DEFAULT NULL,
  `status` varchar(45) NOT NULL,
  PRIMARY KEY (`item_id`),
  KEY `employee_idx` (`employee`),
  KEY `subcategory_idx` (`subcategory`),
  CONSTRAINT `employee` FOREIGN KEY (`employee`) REFERENCES `employees` (`employee_id`) ON DELETE SET NULL,
  CONSTRAINT `subcategory` FOREIGN KEY (`subcategory`) REFERENCES `subcategories` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES ('MLQU-0000001',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LED','24\"',NULL,2,'assigned'),('MLQU-0000002',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i7; 10gb; RAM; 500gb HDD',NULL,2,'assigned'),('MLQU-0000003',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,46,'assigned'),('MLQU-0000004',NULL,'Samsung LS19PUYKF','LS19PUYKF','Samsung',1,NULL,'19\"',NULL,10,'assigned'),('MLQU-0000006',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,46,'assigned'),('MLQU-0000007',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,23,'assigned'),('MLQU-0000010',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD; NVIDIA GT630',NULL,46,'assigned'),('MLQU-0000012',NULL,'Acer P166HQL','P166HQL','Acer',1,NULL,'16\"',NULL,46,'assigned'),('MLQU-0000013',NULL,'Acer P166HQL','P166HQL','Acer',1,NULL,'16\"',NULL,46,'assigned'),('MLQU-0000014',NULL,'Epson L120','L120','Epson',3,NULL,'inkjet',NULL,2,'assigned'),('MLQU-0000015',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,10,'assigned'),('MLQU-0000016',NULL,'Samsung LS20B300BS','LS20B300BS','Samsung',1,NULL,'20\"',NULL,2,'assigned'),('MLQU-0000017',NULL,'Epson L210','L210','Epson',3,NULL,'inkjet',NULL,46,'assigned'),('MLQU-0000018',NULL,'BNP CX-D80HS','CX-D80HS','BNP',3,NULL,'card printer',NULL,10,'assigned'),('MLQU-0000019',NULL,'Clone',NULL,'Clone',2,'ID Computer','Intel i7; 16gb RAM',NULL,10,'assigned'),('MLQU-0000020',NULL,'Samsung LS20B300BS','LS20B300BS','Samsung',1,NULL,'20\"',NULL,46,'assigned'),('MLQU-0000021',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,2,'assigned'),('MLQU-0000022',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,46,'assigned'),('MLQU-0000023',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,46,'assigned'),('MLQU-0000024',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,10,'assigned'),('MLQU-0000025',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,2,'assigned'),('MLQU-0000026',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,46,'assigned'),('MLQU-0000027',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 150GB HDD',NULL,41,'assigned'),('MLQU-0000028',NULL,'Samsung LS20B300BS','LS20B300BS','Samsung',1,NULL,'20\"',NULL,23,'assigned'),('MLQU-0000029',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,23,'assigned'),('MLQU-0000030',NULL,'Brother DCP-L2540DW','DCP-L2540DW','Brother',3,NULL,'inkjet',NULL,23,'assigned'),('MLQU-0000031',NULL,'Samsung LS19D300NY','LS19D300NY','Samsung',1,NULL,'19\"',NULL,41,'assigned'),('MLQU-0000032',NULL,'Eco Power',NULL,'Eco Power',4,NULL,'relay type',NULL,41,'assigned'),('MLQU-0000033',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,47,'assigned'),('MLQU-0000034',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,12,'assigned'),('MLQU-0000035',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,48,'assigned'),('MLQU-0000036',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,49,'assigned'),('MLQU-0000037',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 1TB HDD',NULL,15,'assigned'),('MLQU-0000038',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i7; 16GB RAM; 1TB HDD',NULL,9,'assigned'),('MLQU-0000039',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 120GB SSD',NULL,19,'assigned'),('MLQU-0000040',NULL,'Dell',NULL,'Dell',2,NULL,'Intel Core 2 Duo; 2GB RAM; 160GB HDD',NULL,20,'assigned'),('MLQU-0000041',NULL,'Protec',NULL,'Protec',4,NULL,'relay type',NULL,19,'assigned'),('MLQU-0000042',NULL,'Sunstar',NULL,'Sunstar',4,NULL,'relay type',NULL,12,'assigned'),('MLQU-0000043',NULL,'Secure',NULL,'Secure',4,NULL,'relay type',NULL,48,'assigned'),('MLQU-0000044',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,15,'assigned'),('MLQU-0000045',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,20,'assigned'),('MLQU-0000046',NULL,'Giant Power',NULL,'Giant Power',4,NULL,'relay type',NULL,9,'assigned'),('MLQU-0000047',NULL,'Protec',NULL,'Protec',4,NULL,'relay type',NULL,47,'assigned'),('MLQU-0000048',NULL,'Protec',NULL,'Protec',4,NULL,'relay type',NULL,49,'assigned'),('MLQU-0000049',NULL,'Acer V206HQL','V206HQL','Acer',1,NULL,'20\"',NULL,47,'assigned'),('MLQU-0000050',NULL,'Samsung LS19PUYKF','LS19PUYKF','Samsung',1,NULL,'19\"',NULL,12,'assigned'),('MLQU-0000051',NULL,'Samsung LS19PUYKF','LS19PUYKF','Samsung',1,NULL,'19\"',NULL,49,'assigned'),('MLQU-0000052',NULL,'Acer V206HQL','V206HQL','Acer',1,NULL,'20\"',NULL,48,'assigned'),('MLQU-0000053',NULL,'Samsung LS20B300BS','LS20B300BS','Samsung',1,NULL,'20\"',NULL,9,'assigned'),('MLQU-0000054',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LEDe','24\"',NULL,15,'assigned'),('MLQU-0000055',NULL,'Samsung LS19A300BS','LS19A300BS','Samsung',1,NULL,'19\"',NULL,20,'assigned'),('MLQU-0000056',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,12,'assigned'),('MLQU-0000057',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,9,'assigned'),('MLQU-0000058',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,19,'assigned'),('MLQU-0000059',NULL,'Epson L14150','L14150','Epson',3,NULL,'inkjet',NULL,15,'assigned'),('MLQU-0000061',NULL,'Cisco Linksys E1250','Linksys E1250','Cisco',5,NULL,'AP',NULL,19,'assigned'),('MLQU-0000062',NULL,'DLink DES 1024D','DES 1024D','DLink',6,NULL,'switch',NULL,19,'assigned'),('MLQU-0000063',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LED','24\"',NULL,19,'assigned'),('MLQU-0000064',NULL,'Samsung LS20B300BS','LS20B300BS','Samsung',1,NULL,'20\"',NULL,4,'assigned'),('MLQU-0000065',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i7; 16GB RAM; 1TB HDD',NULL,4,'assigned'),('MLQU-0000066',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,4,'assigned'),('MLQU-0000067',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,6,'assigned'),('MLQU-0000068',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i5; 16GB RAM; 256GB SSD; 1TB HDD',NULL,6,'assigned'),('MLQU-0000069',NULL,'Epson L120','L120','Epson',3,NULL,'inkjet',NULL,6,'assigned'),('MLQU-0000070',NULL,'Acer',NULL,'Acer',1,NULL,'25\"',NULL,6,'assigned'),('MLQU-0000071',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 8GB RAM; 128GB SSD',NULL,7,'assigned'),('MLQU-0000072','CN-0R49DY-64180-18S-18TU','Dell',NULL,'Dell',1,NULL,'17\"',NULL,7,'assigned'),('MLQU-0000073',NULL,'Secure',NULL,'Secure',4,NULL,'relay type',NULL,7,'assigned'),('MLQU-0000074',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i7; 8GB RAM; 148GB SSD; NVIDIA GT730',NULL,7,'assigned'),('MLQU-0000075','NDEJHMEZ903160E','Samsung',NULL,'Samsung',1,NULL,'19\"',NULL,7,'assigned'),('MLQU-0000076',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,7,'assigned'),('MLQU-0000077',NULL,'Clone',NULL,'Clone',2,'ID Computer','Intel i7; 16gb RAM; 500GB HDD',NULL,7,'assigned'),('MLQU-0000078','V8CFH9NB604','Samsung',NULL,'Samsung',1,NULL,'19\"',NULL,7,'assigned'),('MLQU-0000079',NULL,'Secure',NULL,'Secure',4,NULL,'relay type',NULL,7,'assigned'),('MLQU-0000080',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,17,'assigned'),('MLQU-0000081',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,36,'assigned'),('MLQU-0000082',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,3,'assigned'),('MLQU-0000083',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,36,'assigned'),('MLQU-0000084',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,17,'assigned'),('MLQU-0000085',NULL,'Giant Power',NULL,'Giant Power',4,NULL,'relay type',NULL,3,'assigned'),('MLQU-0000086',NULL,'Epson L14150','L14150','Epson',3,NULL,'inkjet',NULL,3,'assigned'),('MLQU-0000087',NULL,'Epson L360','L360','Epson',3,NULL,'inkjet',NULL,17,'assigned'),('MLQU-0000088',NULL,'Samsung LS19PUYKF','LS19PUYKF','Samsung',1,NULL,'19\"',NULL,36,'assigned'),('MLQU-0000089',NULL,'Samsung LS19C150FS','LS19C150FS','Samsung',1,NULL,'19\"',NULL,17,'assigned'),('MLQU-0000090',NULL,'Samsung',NULL,'Samsung',1,NULL,'incomplete',NULL,3,'assigned'),('MLQU-0000091',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,28,'assigned'),('MLQU-0000092',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,33,'assigned'),('MLQU-0000093',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,25,'assigned'),('MLQU-0000094',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 1TB HDD',NULL,25,'assigned'),('MLQU-0000095',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i7; 16GB RAM; 1TB HDD',NULL,26,'assigned'),('MLQU-0000096',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,28,'assigned'),('MLQU-0000097',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,25,'assigned'),('MLQU-0000098',NULL,'Secure',NULL,'Secure',4,NULL,'relay type',NULL,26,'assigned'),('MLQU-0000099',NULL,'Sunstar',NULL,'Sunstar',4,NULL,'relay type',NULL,33,'assigned'),('MLQU-0000100',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,28,'assigned'),('MLQU-0000101',NULL,'Epson L360','L360','Epson',3,NULL,'inkjet',NULL,26,'assigned'),('MLQU-0000102',NULL,'Epson L360','L360','Epson',3,NULL,'inkjet',NULL,25,'assigned'),('MLQU-0000103',NULL,'Epson L360','L360','Epson',3,NULL,'inkjet',NULL,33,'assigned'),('MLQU-0000104',NULL,'Epson LQ-310','LQ-310','Epson',3,NULL,'inkjet',NULL,33,'assigned'),('MLQU-0000105',NULL,'Epson LQ-310','LQ-310','Epson',3,NULL,'inkjet',NULL,25,'assigned'),('MLQU-0000106',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LED','24\"',NULL,28,'assigned'),('MLQU-0000107',NULL,'Samsung 81930N','81930N','Samsung',1,NULL,'19\"',NULL,25,'assigned'),('MLQU-0000108',NULL,'Samsung 522F355FHE','522F355FHE','Samsung',1,NULL,'22\"',NULL,33,'assigned'),('MLQU-0000109',NULL,'Samsung LS20B300BS','LS20B300BS','Samsung',1,NULL,'20\"',NULL,26,'assigned'),('MLQU-0000110',NULL,'Samsung LS20B300BS','LS20B300BS','Samsung',1,NULL,'20\"',NULL,25,'assigned'),('MLQU-0000111',NULL,'Samsung LS19PUYKF','LS19PUYKF','Samsung',1,NULL,'19\"',NULL,50,'assigned'),('MLQU-0000112',NULL,'Lenovo',NULL,'Lenovo',1,NULL,'22\"',NULL,25,'assigned'),('MLQU-0000113',NULL,'Lenovo',NULL,'Lenovo',2,NULL,'Intel i7; 8GB RAM; 500GB SSD',NULL,25,'assigned'),('MLQU-0000114',NULL,'Epson L14150','L14150','Epson',3,NULL,'inkjet',NULL,25,'assigned'),('MLQU-0000115',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,25,'assigned'),('MLQU-0000116',NULL,'Epson L120','L120','Epson',3,NULL,'inkjet',NULL,50,'assigned'),('MLQU-0000117',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 2GB RAM; 500GB HDD',NULL,50,'assigned'),('MLQU-0000118',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,50,'assigned'),('MLQU-0000119',NULL,'Samsung LS19C150FS','LS19C150FS','Samsung',1,NULL,'19\"',NULL,18,'assigned'),('MLQU-0000120',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,18,'assigned'),('MLQU-0000121',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,43,'assigned'),('MLQU-0000123',NULL,'Lenovo',NULL,'Lenovo',2,NULL,'Intel i7; 8GB RAM; 500GB SSD',NULL,51,'assigned'),('MLQU-0000124',NULL,'Epson L360','L360','Epson',3,NULL,'inkjet',NULL,18,'assigned'),('MLQU-0000125',NULL,'Epson L5290','L5290','Epson',3,NULL,'inkjet',NULL,43,'assigned'),('MLQU-0000126',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,51,'assigned'),('MLQU-0000128',NULL,'Samsung LS19PUYKF','LS19PUYKF','Samsung',1,NULL,'19\"',NULL,43,'assigned'),('MLQU-0000129',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LED','24\"',NULL,43,'assigned'),('MLQU-0000130',NULL,'Lenovo',NULL,'Lenovo',1,NULL,'22\"',NULL,51,'assigned'),('MLQU-0000131',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,43,'assigned'),('MLQU-0000132',NULL,'Powersafe',NULL,'Powersafe',4,NULL,'relay type',NULL,43,'assigned'),('MLQU-0000133',NULL,'Brochure',NULL,'Brochure',4,NULL,'relay type',NULL,18,'assigned'),('MLQU-0000134',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,51,'assigned'),('MLQU-0000135',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,13,'assigned'),('MLQU-0000136',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,16,'assigned'),('MLQU-0000137',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,15,'assigned'),('MLQU-0000138',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 6GB RAM; 150GB HDD',NULL,14,'assigned'),('MLQU-0000139',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,13,'assigned'),('MLQU-0000140',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,16,'assigned'),('MLQU-0000141',NULL,'Epson L360','L360','Epson',3,NULL,'inkjet',NULL,14,'assigned'),('MLQU-0000142',NULL,'Epson Dotmatrix LX-300T','Dotmatrix LX-300T','Epson',5,NULL,'Dotmatrix',NULL,15,'assigned'),('MLQU-0000143',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,13,'assigned'),('MLQU-0000144',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,14,'assigned'),('MLQU-0000145',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,15,'assigned'),('MLQU-0000146',NULL,'Eco Power',NULL,'Eco Power',4,NULL,'relay type',NULL,15,'assigned'),('MLQU-0000147',NULL,'Giant Power',NULL,'Giant Power',4,NULL,'relay type',NULL,16,'assigned'),('MLQU-0000148',NULL,'Richo IMC2000','IMC2000','Richo',3,NULL,'Richo',NULL,15,'assigned'),('MLQU-0000149',NULL,'Samsung LS20D300BY','LS20D300BY','Samsung',1,NULL,'20\"',NULL,13,'assigned'),('MLQU-0000150',NULL,'Samsung LS19C150FS','LS19C150FS','Samsung',1,NULL,'19\"',NULL,16,'assigned'),('MLQU-0000151',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LED','24\"',NULL,14,'assigned'),('MLQU-0000152',NULL,'Dell E170SC','E170SC','Dell',1,NULL,'17\"',NULL,15,'assigned'),('MLQU-0000153',NULL,'Acer P166HQL','P166HQL','Acer',1,NULL,'16\"',NULL,15,'assigned'),('MLQU-0000154',NULL,'Clone',NULL,'Clone',2,NULL,'Intel Core 2 Duo; 2GB RAM; 500GB HDD',NULL,15,'assigned'),('MLQU-0000155',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LED','24\"',NULL,22,'assigned'),('MLQU-0000156',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LED','24\"',NULL,30,'assigned'),('MLQU-0000157',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LED','24\"',NULL,31,'assigned'),('MLQU-0000158',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,34,'assigned'),('MLQU-0000159',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,31,'assigned'),('MLQU-0000160',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,30,'assigned'),('MLQU-0000161',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,31,'assigned'),('MLQU-0000162',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 6GB RAM; 500GB HDD',NULL,52,'assigned'),('MLQU-0000163',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 8GB RAM; 128GB SSD; 1TB HDD',NULL,21,'assigned'),('MLQU-0000164',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 8GB RAM; 128GB SSD',NULL,22,'assigned'),('MLQU-0000165',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i7; 16GB RAM; 1TB HDD',NULL,31,'assigned'),('MLQU-0000166',NULL,'Samsung LS19D300NY','LS19D300NY','Samsung',1,NULL,'19\"',NULL,21,'assigned'),('MLQU-0000167',NULL,'Samsung LS19D300NY','LS19D300NY','Samsung',1,NULL,'19\"',NULL,34,'assigned'),('MLQU-0000168',NULL,'Dell E170SC','E170SC','Dell',1,NULL,'17\"',NULL,52,'assigned'),('MLQU-0000169',NULL,'Acer P166HQL','P166HQL','Acer',1,NULL,'16\"',NULL,31,'assigned'),('MLQU-0000170',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,22,'assigned'),('MLQU-0000171',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,52,'assigned'),('MLQU-0000172',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,31,'assigned'),('MLQU-0000173',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,31,'assigned'),('MLQU-0000174',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,34,'assigned'),('MLQU-0000175',NULL,'DTS',NULL,'DTS',4,NULL,'relay type',NULL,30,'assigned'),('MLQU-0000176',NULL,'Protec',NULL,'Protec',4,NULL,'relay type',NULL,21,'assigned'),('MLQU-0000177',NULL,'Secure',NULL,'Secure',4,NULL,'relay type',NULL,31,'assigned'),('MLQU-0000178',NULL,'Epson L360','L360','Epson',3,NULL,'inkjet',NULL,22,'assigned'),('MLQU-0000179',NULL,'Epson L120','L120','Epson',3,NULL,'inkjet',NULL,21,'assigned'),('MLQU-0000180',NULL,'Epson L14150','L14150','Epson',3,NULL,'inkjet',NULL,34,'assigned'),('MLQU-0000181',NULL,'Epson L3210','L3210','Epson',3,NULL,'inkjet',NULL,31,'assigned'),('MLQU-0000182',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i3; 4GB RAM; 500GB HDD',NULL,53,'assigned'),('MLQU-0000183',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LED','24\"',NULL,53,'assigned'),('MLQU-0000184',NULL,'Epson L455','L455','Epson',3,NULL,'inkjet',NULL,53,'assigned'),('MLQU-0000185',NULL,'Micropulse',NULL,'Micropulse',4,NULL,'relay type',NULL,53,'assigned'),('MLQU-0000186',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LED','24\"',NULL,44,'assigned'),('MLQU-0000187',NULL,'Samsung LS24FB350FHEXXP','LS24FB350FHEXXP','Samsung',1,'LED','24\"',NULL,44,'assigned'),('MLQU-0000188',NULL,'Clone',NULL,'Clone',2,NULL,'Intel i7; 16GB RAM; 1TB HDD',NULL,44,'assigned');
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items_categories`
--

DROP TABLE IF EXISTS `items_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items_categories` (
  `id` int NOT NULL,
  `category` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `category_UNIQUE` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items_categories`
--

LOCK TABLES `items_categories` WRITE;
/*!40000 ALTER TABLE `items_categories` DISABLE KEYS */;
INSERT INTO `items_categories` VALUES (1,'assets'),(2,'test');
/*!40000 ALTER TABLE `items_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `items_groups`
--

DROP TABLE IF EXISTS `items_groups`;
/*!50001 DROP VIEW IF EXISTS `items_groups`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `items_groups` AS SELECT 
 1 AS `group_name`,
 1 AS `subcategory_id`,
 1 AS `brand_name`,
 1 AS `item_count`,
 1 AS `assigned_count`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `subcategories`
--

DROP TABLE IF EXISTS `subcategories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subcategories` (
  `id` int NOT NULL,
  `subcategory` varchar(45) NOT NULL,
  `category` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id_idx` (`category`),
  CONSTRAINT `category_id` FOREIGN KEY (`category`) REFERENCES `items_categories` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subcategories`
--

LOCK TABLES `subcategories` WRITE;
/*!40000 ALTER TABLE `subcategories` DISABLE KEYS */;
INSERT INTO `subcategories` VALUES (1,'monitor',1),(2,'system unit',1),(3,'printer',1),(4,'avr',1),(5,'access point',1),(6,'switch',1);
/*!40000 ALTER TABLE `subcategories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_accounts`
--

DROP TABLE IF EXISTS `user_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_accounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(45) NOT NULL,
  `password` varchar(255) NOT NULL,
  `account_type` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_accounts`
--

LOCK TABLES `user_accounts` WRITE;
/*!40000 ALTER TABLE `user_accounts` DISABLE KEYS */;
INSERT INTO `user_accounts` VALUES (1,'admin','scrypt:32768:8:1$DnkE7P7s13Wt6dqb$f65c7ba1efab91b825f4d89b7aa9d64e444daa3ed53cf9ed3a23e77d63e21aba3a2f6f3d7a816e2116e4c2c2cae145835b34423ab47340aaf5cd78bd8d0205db','admin'),(2,'user','scrypt:32768:8:1$R5PVwfI4RywZCo3q$a8907a0bff5280df6a88aead39524bbe47a02dc3f0bbf53279486bcadf3901e5b201de6ec081f707bfa45271972126b5e256c977cb8d9c6805c31454f978d31e','user'),(3,'MIS','scrypt:32768:8:1$4PH5ApPCjAJ5IFjv$a6b7ab66a04dbbd4183cc4625dd4e177ca804530131f236b86825180de193ff358c387b35f108e0429bf15e1d7fa51baaaef4f1ff72d636664cefaa9ad193094','admin'),(5,'user1','scrypt:32768:8:1$1cp4IRQbYB89AIAL$ab1ed698b175e9fa8a18d65ea354ed51ff1bfb6255a8b498ea5d497c980e55416d7ae9cb13e6125776e1ef54e6f247f20e09805622ba99702af9b4d58325ab95','user');
/*!40000 ALTER TABLE `user_accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `items_groups`
--

/*!50001 DROP VIEW IF EXISTS `items_groups`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `items_groups` AS select concat(`subcategories`.`subcategory`,' | ',`items`.`brand_name`) AS `group_name`,`subcategories`.`id` AS `subcategory_id`,`items`.`brand_name` AS `brand_name`,count(`items`.`item_id`) AS `item_count`,sum((`items`.`status` = 'assigned')) AS `assigned_count` from (`items` join `subcategories` on((`items`.`subcategory` = `subcategories`.`id`))) group by `subcategories`.`id`,`items`.`brand_name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-29 16:34:52
