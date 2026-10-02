-- Bootstrap for an empty academic demo database. Never drops existing data.
CREATE TABLE IF NOT EXISTS cliente (
 id_cliente INT AUTO_INCREMENT PRIMARY KEY,
 nome VARCHAR(160) NOT NULL, cpf VARCHAR(14) NOT NULL UNIQUE,
 telefone VARCHAR(30), email VARCHAR(254) NOT NULL,
 data_nascimento DATE, cidade VARCHAR(100),
 torce_flamengo BOOLEAN NOT NULL DEFAULT FALSE,
 assiste_one_piece BOOLEAN NOT NULL DEFAULT FALSE
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS vendedor (
 id_vendedor INT AUTO_INCREMENT PRIMARY KEY,
 nome VARCHAR(160) NOT NULL, cpf VARCHAR(14) NOT NULL UNIQUE,
 email VARCHAR(254), telefone VARCHAR(30)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS produto (
 id_produto INT AUTO_INCREMENT PRIMARY KEY,
 nome VARCHAR(160) NOT NULL, descricao TEXT,
 preco DECIMAL(12,2) NOT NULL, quantidade INT NOT NULL,
 categoria VARCHAR(100) NOT NULL,
 fabricado_em_mari BOOLEAN NOT NULL DEFAULT FALSE,
 CHECK (preco >= 0), CHECK (quantidade >= 0)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS compra (
 id_compra INT AUTO_INCREMENT PRIMARY KEY,
 id_cliente INT NOT NULL, id_vendedor INT NOT NULL,
 data_compra TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 forma_pagamento VARCHAR(40) NOT NULL,
 status_pagamento VARCHAR(40) NOT NULL,
 desconto_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
 valor_total DECIMAL(12,2) NOT NULL DEFAULT 0,
 FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
 FOREIGN KEY (id_vendedor) REFERENCES vendedor(id_vendedor),
 CHECK (desconto_pct BETWEEN 0 AND 100), CHECK (valor_total >= 0)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS item_compra (
 id_item INT AUTO_INCREMENT PRIMARY KEY,
 id_compra INT NOT NULL, id_produto INT NOT NULL,
 quantidade INT NOT NULL, preco_unitario DECIMAL(12,2) NOT NULL,
 FOREIGN KEY (id_compra) REFERENCES compra(id_compra),
 FOREIGN KEY (id_produto) REFERENCES produto(id_produto),
 CHECK (quantidade > 0), CHECK (preco_unitario >= 0)
) ENGINE=InnoDB;
CREATE OR REPLACE VIEW vw_relatorio_mensal AS
 SELECT v.nome AS vendedor, YEAR(c.data_compra) AS ano,
 MONTH(c.data_compra) AS mes, COUNT(*) AS total_vendas,
 SUM(c.valor_total) AS faturamento, AVG(c.valor_total) AS ticket_medio
 FROM compra c JOIN vendedor v ON c.id_vendedor=v.id_vendedor
 GROUP BY v.id_vendedor,v.nome,YEAR(c.data_compra),MONTH(c.data_compra);
