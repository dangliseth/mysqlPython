
ALTER TABLE items 
MODIFY COLUMN employee INT NULL,
ADD CONSTRAINT employee 
FOREIGN KEY (employee) REFERENCES employees(employee_id) 
ON DELETE SET NULL;