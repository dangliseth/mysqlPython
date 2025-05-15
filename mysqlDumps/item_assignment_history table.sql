CREATE TABLE `item_assignment_history` (
  `history_id` int NOT NULL AUTO_INCREMENT,
  `item_id` varchar(32) NOT NULL,
  `employee_id` int DEFAULT NULL,
  `assigned_date` datetime NOT NULL,
  `removed_date` datetime DEFAULT NULL,
  PRIMARY KEY (`history_id`),
  KEY `item_assignment_history_ibfk_2` (`employee_id`),
  KEY `item_assignment_history_ibfk_1` (`item_id`),
  CONSTRAINT `item_assignment_history_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`item_id`),
  CONSTRAINT `item_assignment_history_ibfk_2` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
