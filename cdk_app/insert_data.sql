-- Insert into Geography_Dim (expanded data)
INSERT INTO Geography_Dim (Geography_ID, Country, State, City) VALUES 
(1, 'USA', 'California', 'Los Angeles'),
(2, 'USA', 'New York', 'New York'),
(3, 'Canada', 'Ontario', 'Toronto'),
(4, 'UK', 'England', 'London'),
(5, 'Australia', 'New South Wales', 'Sydney');

-- Insert into Age_Group_Dim (expanded data)
INSERT INTO Age_Group_Dim (Age_Group_ID, Age_Range) VALUES 
(1, '18-25'),
(2, '26-35'),
(3, '36-45'),
(4, '46-55'),
(5, '56-65');

-- Insert into Category_Dim (expanded data)
INSERT INTO Category_Dim (Category_ID, Category_Name) VALUES 
(1, 'Electronics'),
(2, 'Apparel'),
(3, 'Home Appliances'),
(4, 'Books'),
(5, 'Beauty Products');

-- Insert into Manufacturer_Dim (expanded data)
INSERT INTO Manufacturer_Dim (Manufacturer_ID, Manufacturer_Name) VALUES 
(1, 'Apple'),
(2, 'Nike'),
(3, 'Samsung'),
(4, 'Sony'),
(5, 'LG');

-- Insert into Store_Type_Dim (expanded data)
INSERT INTO Store_Type_Dim (Store_Type_ID, Store_Type) VALUES 
(1, 'Physical'),
(2, 'Online'),
(3, 'Hybrid');

-- Insert into Month_Dim (expanded data)
INSERT INTO Month_Dim (Month_ID, Month_Name) VALUES 
(1, 'January'),
(2, 'February'),
(3, 'March'),
(4, 'April'),
(5, 'May');

-- Insert into Year_Dim (expanded data)
INSERT INTO Year_Dim (Year_ID, Year_Value) VALUES 
(1, 2024),
(2, 2023),
(3, 2022),
(4, 2021),
(5, 2020);

-- Insert into Time_Dim (expanded data)
INSERT INTO Time_Dim (Time_ID, Hour, Minute, Second) VALUES 
(1, 10, 30, 0),
(2, 12, 15, 0),
(3, 14, 45, 0),
(4, 16, 0, 0),
(5, 18, 30, 0);

-- Insert into Subcategory_Dim (expanded data)
INSERT INTO Subcategory_Dim (Subcategory_ID, Subcategory_Name, Category_ID) VALUES 
(1, 'Laptops', 1),
(2, 'Shirts', 2),
(3, 'Refrigerators', 3),
(4, 'Fiction', 4),
(5, 'Skincare', 5);

-- Insert into Customer_Dim (with SCD Type 2, expanded data)
INSERT INTO Customer_Dim (Customer_ID, Customer_Surrogate_Key, Customer_Name, Geography_ID, Age_Group_ID, Start_Date, End_Date, Is_Current) VALUES 
(101, 1, 'John Doe', 1, 1, '2021-01-01', '9999-12-31', TRUE),
(102, 2, 'Jane Smith', 2, 2, '2021-01-01', '9999-12-31', TRUE),
(103, 3, 'Tom Johnson', 3, 3, '2021-01-01', '9999-12-31', TRUE),
(104, 4, 'Alice Brown', 4, 4, '2021-01-01', '9999-12-31', TRUE),
(105, 5, 'Steve Clark', 5, 5, '2021-01-01', '9999-12-31', TRUE);

-- Insert into Product_Dim (expanded data)
INSERT INTO Product_Dim (Product_ID, Product_Name, Subcategory_ID, Manufacturer_ID) VALUES 
(1, 'MacBook Pro', 1, 1),
(2, 'T-shirt', 2, 2),
(3, 'Galaxy Refrigerator', 3, 3),
(4, 'Kindle', 4, 4),
(5, 'Face Cream', 5, 5);

-- Insert into Store_Dim (expanded data)
INSERT INTO Store_Dim (Store_ID, Store_Name, Geography_ID, Store_Type_ID) VALUES 
(1, 'Best Buy', 1, 1),
(2, 'Amazon', 2, 2),
(3, 'Walmart', 3, 1),
(4, 'eBay', 4, 2),
(5, 'Target', 5, 3);

-- Insert into Date_Dim (expanded data)
INSERT INTO Date_Dim (Date_ID, Date, Day, Month_ID, Year_ID, Time_ID) VALUES 
(1, '2024-01-01', 1, 1, 1, 1),
(2, '2024-02-15', 15, 2, 1, 2),
(3, '2023-03-20', 20, 3, 2, 3),
(4, '2023-04-10', 10, 4, 2, 4),
(5, '2022-05-25', 25, 5, 3, 5);

-- Insert into Promotion_Dim (expanded data)
INSERT INTO Promotion_Dim (Promotion_ID, Promotion_Type, Promotion_Desc, Discount_Percentage, Start_Date_ID, End_Date_ID) VALUES 
(1, 'Discount', 'New Year Sale', 10.00, 1, 2),
(2, 'Buy One Get One', 'Spring Sale', 50.00, 3, 4),
(3, 'Clearance', 'Summer Sale', 30.00, 4, 5);

-- Insert into Supplier_Dim (expanded data)
INSERT INTO Supplier_Dim (Supplier_ID, Supplier_Name, Geography_ID) VALUES 
(1, 'Tech Suppliers Inc.', 1),
(2, 'Clothing Co.', 2),
(3, 'Home Goods Ltd.', 3),
(4, 'Book Publishers Corp.', 4),
(5, 'Beauty Brands Inc.', 5);

-- Insert into Sales_Fact (expanded data)
INSERT INTO Sales_Fact (Sales_ID, Date_ID, Customer_ID, Product_ID, Store_ID, Promotion_ID, Supplier_ID, Quantity_Sold, Sales_Amount) VALUES 
(1, 1, 1, 1, 1, 1, 1, 2, 2000.00),
(2, 2, 2, 2, 2, 1, 2, 3, 60.00),
(3, 3, 3, 3, 3, 2, 3, 1, 1200.00),
(4, 4, 4, 4, 4, 2, 4, 5, 500.00),
(5, 5, 5, 5, 5, 3, 5, 10, 1000.00);

-- Insert into Return_Fact (expanded data)
INSERT INTO Return_Fact (Return_ID, Sales_ID, Date_ID, Product_ID, Customer_ID, Store_ID, Return_Quantity, Return_Amount) VALUES 
(1, 1, 2, 1, 1, 1, 1, 1000.00),
(2, 2, 3, 2, 2, 2, 1, 30.00),
(3, 3, 4, 3, 3, 3, 1, 600.00),
(4, 4, 5, 4, 4, 4, 2, 250.00),
(5, 5, 1, 5, 5, 5, 5, 500.00);