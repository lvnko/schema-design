CREATE TABLE products(
    product_no int PRIMARY KEY,
    name VARCHAR NOT NULL,
    price FLOAT CHECK (price > 0),
    discounted FLOAT CHECK (discounted > 0),
    stock INT CHECK (stock >= 0),
    CHECK (price > discounted)
);
INSERT INTO products (product_no, name, price, discounted, stock)
VALUES (1, 'ASUS Laptop', 999.99, 200, 10);
INSERT INTO products (product_no, name, price, discounted, stock)
VALUES (2, 'Samsung G50', 2, 1, 5);
INSERT INTO products (product_no, name, price, discounted, stock)
VALUES (3, 'Dell XPS', 1299.99, 1000, 15);
INSERT INTO products (product_no, name, price, discounted, stock)
VALUES (4, 'HP Spectre', 1399.99, 1288, 8);

DELETE FROM products WHERE product_no=1;