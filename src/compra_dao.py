import json
from dataclasses import dataclass
from typing import List, Optional
from mysql.connector import Error
from db import get_conn


@dataclass(frozen=True)
class ItemCompra:
    id_item: int
    id_compra: int
    id_produto: int
    nome_produto: str
    quantidade: int
    preco_unitario: float

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario


@dataclass(frozen=True)
class Compra:
    id_compra: int
    id_cliente: int
    nome_cliente: str
    id_vendedor: int
    nome_vendedor: str
    data_compra: str
    forma_pagamento: str
    status_pagamento: str
    desconto_pct: float
    valor_total: float


class CompraDAO:

    @staticmethod
    def realizar(id_cliente: int, id_vendedor: int,
                 forma_pagamento: str,
                 itens: list) -> int:
        """
        itens = [{"id_produto": 1, "quantidade": 2}, ...]
        Regras:
        - Desconto 10% se cliente torce pro Flamengo, assiste One Piece ou é de Sousa
        - Bloqueia se qualquer produto sem estoque suficiente
        - Status 'confirmado' para dinheiro, 'pendente' para outros
        """
        # Verifica desconto
        with get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT torce_flamengo, assiste_one_piece, cidade FROM cliente WHERE id_cliente=%s",
                    (id_cliente,)
                )
                row = cur.fetchone()
                if not row:
                    raise RuntimeError("Cliente não encontrado.")
                torce, one_piece, cidade = row
                desconto = 10.0 if (torce or one_piece or
                                    (cidade and cidade.lower() == 'sousa')) else 0.0

                # Verifica estoque
                for item in itens:
                    cur.execute("SELECT nome, quantidade FROM produto WHERE id_produto=%s",
                                (item["id_produto"],))
                    prod = cur.fetchone()
                    if not prod:
                        raise RuntimeError(f"Produto ID {item['id_produto']} não encontrado.")
                    if prod[1] < item["quantidade"]:
                        raise RuntimeError(
                            f"Estoque insuficiente para '{prod[0]}'. "
                            f"Disponível: {prod[1]}, solicitado: {item['quantidade']}."
                        )

                # Status
                status = "confirmado" if forma_pagamento == "dinheiro" else "pendente"

                # Cria compra
                cur.execute(
                    """INSERT INTO compra
                       (id_cliente,id_vendedor,forma_pagamento,status_pagamento,desconto_pct,valor_total)
                       VALUES (%s,%s,%s,%s,%s,0.00)""",
                    (id_cliente, id_vendedor, forma_pagamento, status, desconto)
                )
                id_compra = cur.lastrowid

                # Insere itens e abate estoque
                total = 0.0
                for item in itens:
                    cur.execute("SELECT preco FROM produto WHERE id_produto=%s",
                                (item["id_produto"],))
                    preco = float(cur.fetchone()[0])
                    subtotal = preco * item["quantidade"]
                    total += subtotal
                    cur.execute(
                        "INSERT INTO item_compra (id_compra,id_produto,quantidade,preco_unitario) VALUES (%s,%s,%s,%s)",
                        (id_compra, item["id_produto"], item["quantidade"], preco)
                    )
                    cur.execute(
                        "UPDATE produto SET quantidade = quantidade - %s WHERE id_produto=%s",
                        (item["quantidade"], item["id_produto"])
                    )

                # Aplica desconto
                total_com_desconto = total * (1 - desconto / 100)
                cur.execute("UPDATE compra SET valor_total=%s WHERE id_compra=%s",
                            (total_com_desconto, id_compra))

                conn.commit()
                return id_compra

            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Erro ao realizar compra: {e}")
            finally:
                cur.close()

    @staticmethod
    def confirmar_pagamento(id_compra: int) -> int:
        with get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "UPDATE compra SET status_pagamento='confirmado' WHERE id_compra=%s",
                    (id_compra,)
                )
                conn.commit(); return int(cur.rowcount)
            except Error as e:
                conn.rollback(); raise RuntimeError(f"Erro ao confirmar pagamento: {e}")
            finally:
                cur.close()

    @staticmethod
    def listar_todas() -> List[Compra]:
        sql = """
        SELECT c.id_compra, c.id_cliente, cl.nome, c.id_vendedor, v.nome,
               c.data_compra, c.forma_pagamento, c.status_pagamento,
               c.desconto_pct, c.valor_total
        FROM compra c
        JOIN cliente cl ON cl.id_cliente = c.id_cliente
        JOIN vendedor v  ON v.id_vendedor  = c.id_vendedor
        ORDER BY c.data_compra DESC
        """
        with get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute(sql)
                return [Compra(r[0],r[1],r[2],r[3],r[4],
                               str(r[5]),r[6],r[7],float(r[8]),float(r[9]))
                        for r in cur.fetchall()]
            except Error as e:
                raise RuntimeError(f"Erro ao listar compras: {e}")
            finally:
                cur.close()

    @staticmethod
    def listar_por_cliente(id_cliente: int) -> List[Compra]:
        sql = """
        SELECT c.id_compra, c.id_cliente, cl.nome, c.id_vendedor, v.nome,
               c.data_compra, c.forma_pagamento, c.status_pagamento,
               c.desconto_pct, c.valor_total
        FROM compra c
        JOIN cliente cl ON cl.id_cliente = c.id_cliente
        JOIN vendedor v  ON v.id_vendedor  = c.id_vendedor
        WHERE c.id_cliente = %s
        ORDER BY c.data_compra DESC
        """
        with get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute(sql, (id_cliente,))
                return [Compra(r[0],r[1],r[2],r[3],r[4],
                               str(r[5]),r[6],r[7],float(r[8]),float(r[9]))
                        for r in cur.fetchall()]
            except Error as e:
                raise RuntimeError(f"Erro ao listar compras do cliente: {e}")
            finally:
                cur.close()

    @staticmethod
    def buscar_itens(id_compra: int) -> List[ItemCompra]:
        sql = """
        SELECT ic.id_item, ic.id_compra, ic.id_produto, p.nome,
               ic.quantidade, ic.preco_unitario
        FROM item_compra ic
        JOIN produto p ON p.id_produto = ic.id_produto
        WHERE ic.id_compra = %s
        """
        with get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute(sql, (id_compra,))
                return [ItemCompra(r[0],r[1],r[2],r[3],r[4],float(r[5]))
                        for r in cur.fetchall()]
            except Error as e:
                raise RuntimeError(f"Erro ao buscar itens: {e}")
            finally:
                cur.close()

    @staticmethod
    def relatorio_mensal(ano: int, mes: int) -> List[dict]:
        """Usa a view vw_relatorio_mensal."""
        sql = """SELECT vendedor, total_vendas, faturamento, ticket_medio
                 FROM vw_relatorio_mensal WHERE ano=%s AND mes=%s"""
        with get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute(sql, (ano, mes))
                return [{"vendedor": r[0], "total_vendas": r[1],
                         "faturamento": float(r[2]), "ticket_medio": float(r[3])}
                        for r in cur.fetchall()]
            except Error as e:
                raise RuntimeError(f"Erro no relatório mensal: {e}")
            finally:
                cur.close()

    @staticmethod
    def gerar_relatorio_geral() -> dict:
        sql = """SELECT COUNT(*), SUM(valor_total),
                        SUM(status_pagamento='confirmado'),
                        SUM(status_pagamento='pendente'),
                        AVG(valor_total)
                 FROM compra"""
        with get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute(sql)
                r = cur.fetchone()
                return {
                    "total_compras":     r[0] or 0,
                    "faturamento_total": float(r[1] or 0),
                    "confirmadas":       r[2] or 0,
                    "pendentes":         r[3] or 0,
                    "ticket_medio":      float(r[4] or 0),
                }
            except Error as e:
                raise RuntimeError(f"Erro no relatório: {e}")
            finally:
                cur.close()
                #Fechando cursor no finally para garantir que ele seja fechado mesmo em caso de erro.

