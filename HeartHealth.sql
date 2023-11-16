

CREATE DATABASE IF NOT EXISTS HEARTHEALTH;
USE HEARTHEALTH;

CREATE TABLE  IF NOT EXISTS User(
    UserID INT PRIMARY KEY NOT NULL,
    Username VARCHAR(30) NOT NULL,
    Password VARCHAR(30) NOT NULL, 
    EmailAddress VARCHAR(40) NOT NULL,
    ProviderID INT,
    FirstName VARCHAR(30),
    LastName VARCHAR(30)
);
    
CREATE TABLE  IF NOT EXISTS Admin (
	AdminID INT PRIMARY KEY,
    UserID INT NOT NULL,
    FOREIGN KEY (UserID) REFERENCES User(UserID)
);
    
INSERT INTO User (Username, Password, EmailAddress, ProviderID) VALUES 
("soma.ezzadpanah", "password", "soma.ezzadpanah@example.com", 101),
("adel.mahfooz", "password", "adel.mahfooz@example.com", 102),
("joseph.may", "password", "joseph.may@example.com", 103),
("taylor.hartman", "password", "taylor.hartman@example.com", 104),
("john.smith", "password", "john.smith@example.com",105),
("jane.doe", "password", "jane.doe@example.com", 106);
    