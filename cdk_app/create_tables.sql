-- 1. Create Geography_Dim (no dependencies)
CREATE TABLE IF NOT EXISTS Geography_Dim (
    Geography_ID INT PRIMARY KEY,
    Country VARCHAR(100),
    State VARCHAR(100),
    City VARCHAR(100)
);

-- 2. Create Age_Group_Dim (no dependencies)
CREATE TABLE IF NOT EXISTS Age_Group_Dim (
    Age_Group_ID INT PRIMARY KEY,
    Age_Range VARCHAR(50)
);

-- 3. Create Category_Dim (no dependencies)
CREATE TABLE IF NOT EXISTS Category_Dim (
    Category_ID INT PRIMARY KEY,
    Category_Name VARCHAR(100)
);

-- 4. Create Manufacturer_Dim (no dependencies)
CREATE TABLE IF NOT EXISTS Manufacturer_Dim (
    Manufacturer_ID INT PRIMARY KEY,
    Manufacturer_Name VARCHAR(255)
);

-- 5. Create Store_Type_Dim (no dependencies)
CREATE TABLE IF NOT EXISTS Store_Type_Dim (
    Store_Type_ID INT PRIMARY KEY,
    Store_Type VARCHAR(50)
);

-- 6. Create Month_Dim (no dependencies)
CREATE TABLE IF NOT EXISTS Month_Dim (
    Month_ID INT PRIMARY KEY,
    Month_Name VARCHAR(50)
);

-- 7. Create Year_Dim (no dependencies)
CREATE TABLE IF NOT EXISTS Year_Dim (
    Year_ID INT PRIMARY KEY,
    Year_Value INT
);

-- 8. Create Time_Dim (no dependencies)
CREATE TABLE IF NOT EXISTS Time_Dim (
    Time_ID INT PRIMARY KEY,
    Hour INT,
    Minute INT,
    Second INT
);

-- 9. Create Subcategory_Dim (depends on Category_Dim)
CREATE TABLE IF NOT EXISTS Subcategory_Dim (
    Subcategory_ID INT PRIMARY KEY,
    Subcategory_Name VARCHAR(100),
    Category_ID INT,
    FOREIGN KEY (Category_ID) REFERENCES Category_Dim(Category_ID)
);

-- 10. Create Customer_Dim (depends on Geography_Dim and Age_Group_Dim)
CREATE TABLE IF NOT EXISTS Customer_Dim (
    Customer_ID INT,
    Customer_Surrogate_Key INT PRIMARY KEY,
    Customer_Name VARCHAR(255),
    Geography_ID INT,
    Age_Group_ID INT,
    Start_Date DATE,
    End_Date DATE,
    Is_Current BOOLEAN,
    FOREIGN KEY (Geography_ID) REFERENCES Geography_Dim(Geography_ID),
    FOREIGN KEY (Age_Group_ID) REFERENCES Age_Group_Dim(Age_Group_ID)
);

-- 11. Create Product_Dim (depends on Subcategory_Dim and Manufacturer_Dim)
CREATE TABLE IF NOT EXISTS Product_Dim (
    Product_ID INT PRIMARY KEY,
    Product_Name VARCHAR(255),
    Subcategory_ID INT,
    Manufacturer_ID INT,
    FOREIGN KEY (Subcategory_ID) REFERENCES Subcategory_Dim(Subcategory_ID),
    FOREIGN KEY (Manufacturer_ID) REFERENCES Manufacturer_Dim(Manufacturer_ID)
);

-- 12. Create Store_Dim (depends on Geography_Dim and Store_Type_Dim)
CREATE TABLE IF NOT EXISTS Store_Dim (
    Store_ID INT PRIMARY KEY,
    Store_Name VARCHAR(255),
    Geography_ID INT,
    Store_Type_ID INT,
    FOREIGN KEY (Geography_ID) REFERENCES Geography_Dim(Geography_ID),
    FOREIGN KEY (Store_Type_ID) REFERENCES Store_Type_Dim(Store_Type_ID)
);

-- 13. Create Promotion_Dim (depends on Date_Dim)
CREATE TABLE IF NOT EXISTS Promotion_Dim (
    Promotion_ID INT PRIMARY KEY,
    Promotion_Type VARCHAR(50),
    Promotion_Desc VARCHAR(255),
    Discount_Percentage DECIMAL(5, 2),
    Start_Date_ID INT,
    End_Date_ID INT,
    FOREIGN KEY (Start_Date_ID) REFERENCES Date_Dim(Date_ID),
    FOREIGN KEY (End_Date_ID) REFERENCES Date_Dim(Date_ID)
);

-- 14. Create Supplier_Dim (depends on Geography_Dim)
CREATE TABLE IF NOT EXISTS Supplier_Dim (
    Supplier_ID INT PRIMARY KEY,
    Supplier_Name VARCHAR(255),
    Geography_ID INT,
    FOREIGN KEY (Geography_ID) REFERENCES Geography_Dim(Geography_ID)
);

-- 15. Create Date_Dim (depends on Month_Dim, Year_Dim, and Time_Dim)
CREATE TABLE IF NOT EXISTS Date_Dim (
    Date_ID INT PRIMARY KEY,
    Date DATE,
    Day INT,
    Month_ID INT,
    Year_ID INT,
    Time_ID INT,
    FOREIGN KEY (Month_ID) REFERENCES Month_Dim(Month_ID),
    FOREIGN KEY (Year_ID) REFERENCES Year_Dim(Year_ID),
    FOREIGN KEY (Time_ID) REFERENCES Time_Dim(Time_ID)
);

-- 16. Create Sales_Fact (depends on all dimensions)
CREATE TABLE IF NOT EXISTS Sales_Fact (
    Sales_ID INT PRIMARY KEY,
    Date_ID INT,
    Customer_ID INT,
    Product_ID INT,
    Store_ID INT,
    Promotion_ID INT,
    Supplier_ID INT,
    Quantity_Sold INT,
    Sales_Amount DECIMAL(10, 2),
    FOREIGN KEY (Date_ID) REFERENCES Date_Dim(Date_ID),
    FOREIGN KEY (Customer_ID) REFERENCES Customer_Dim(Customer_Surrogate_Key),
    FOREIGN KEY (Product_ID) REFERENCES Product_Dim(Product_ID),
    FOREIGN KEY (Store_ID) REFERENCES Store_Dim(Store_ID),
    FOREIGN KEY (Promotion_ID) REFERENCES Promotion_Dim(Promotion_ID),
    FOREIGN KEY (Supplier_ID) REFERENCES Supplier_Dim(Supplier_ID)
);

-- 17. Create Return_Fact (depends on Sales_Fact and dimensions)
CREATE TABLE IF NOT EXISTS Return_Fact (
    Return_ID INT PRIMARY KEY,
    Sales_ID INT,
    Date_ID INT,
    Product_ID INT,
    Customer_ID INT,
    Store_ID INT,
    Return_Quantity INT,
    Return_Amount DECIMAL(10, 2),
    FOREIGN KEY (Sales_ID) REFERENCES Sales_Fact(Sales_ID),
    FOREIGN KEY (Date_ID) REFERENCES Date_Dim(Date_ID),
    FOREIGN KEY (Product_ID) REFERENCES Product_Dim(Product_ID),
    FOREIGN KEY (Customer_ID) REFERENCES Customer_Dim(Customer_Surrogate_Key),
    FOREIGN KEY (Store_ID) REFERENCES Store_Dim(Store_ID)
);