CREATE DATABASE IF NOT EXISTS HEARTHEALTH;
USE HEARTHEALTH;

CREATE TABLE  IF NOT EXISTS User(
    UserID INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    FirstName VARCHAR(30) NOT NULL,
    LastName VARCHAR(30) NOT NULL,
    Username VARCHAR(30) NOT NULL,
    Password VARCHAR(30) NOT NULL, 
    EmailAddress VARCHAR(40) NOT NULL,
    ProviderID INT,
    IsAdmin BOOLEAN DEFAULT 0
);

    
INSERT INTO User (FirstName, LastName, Username, Password, EmailAddress, ProviderID, IsAdmin) VALUES 
( "Soma", "Ezzadpanah","soma.ezzadpanah", "password", "soma.ezzadpanah@example.com",NULL, 1),
( "Adel", "Mahfooz","adel.mahfooz", "password", "adel.mahfooz@example.com", NULL, 1),
( "Joseph", "May","joseph.may", "password", "joseph.may@example.com", NULL, 1 ),
("Taylor", "Hartman","taylor.hartman", "password", "taylor.hartman@example.com", NULL,1),
("John", "Smith","john.smith", "password", "john.smith@example.com",105, 0 ),
( "Jane", "Doe","jane.doe", "password", "jane.doe@example.com", 106, 0);
    
Select *
From User;
    
Drop Table User;