-- seed.sql: multi-tenant sample
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS tenants;

CREATE TABLE tenants (
  id serial PRIMARY KEY,
  name text NOT NULL,
  slug text UNIQUE NOT NULL
);

INSERT INTO tenants (name, slug) VALUES ('Demo Corp', 'demo'), ('Acme Inc', 'acme');

CREATE TABLE sales (
  id serial PRIMARY KEY,
  tenant_id int REFERENCES tenants(id) NOT NULL,
  date date NOT NULL,
  region text,
  product text,
  revenue numeric,
  units integer
);

INSERT INTO sales (tenant_id, date, region, product, revenue, units) VALUES
(1,'2023-07-01','North','A',1000,10),
(1,'2023-07-15','North','B',1500,15),
(1,'2023-08-01','South','A',900,9),
(1,'2023-08-15','South','B',1200,12),
(1,'2023-09-01','East','A',1100,11),
(2,'2023-09-15','West','C',1300,13),
(2,'2023-10-01','North','A',1400,14),
(1,'2023-10-15','South','B',1250,12),
(2,'2023-11-01','East','C',1600,16);

CREATE VIEW sales_summary AS
SELECT tenant_id, date, region, SUM(revenue) as revenue, SUM(units) as units
FROM sales
GROUP BY tenant_id, date, region;
