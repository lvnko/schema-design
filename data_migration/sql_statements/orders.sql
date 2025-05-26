CREATE TABLE orders(
    order_no INT PRIMARY KEY,
    product_no INT REFERENCES products ON DELETE SET NULL,
    quantity INT CHECK (quantity >= 0)
);
INSERT INTO orders (order_no, product_no, quantity)
VALUES (1, 1, 1);
INSERT INTO orders (order_no, product_no, quantity)
VALUES (2, 3, 3);
INSERT INTO orders (order_no, product_no, quantity)
VALUES (3, 3, 2);
INSERT INTO orders (order_no, product_no, quantity)
VALUES (4, 2, 1);

DELETE FROM orders WHERE order_id=1;