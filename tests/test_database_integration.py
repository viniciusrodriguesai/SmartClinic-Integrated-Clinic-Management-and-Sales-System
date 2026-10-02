"""Real MySQL-compatible integration tests; require a dedicated disposable database."""
from datetime import datetime
from pathlib import Path
import os
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from bootstrap_database import bootstrap
from cliente_dao import ClienteDAO
from vendedor_dao import VendedorDAO
from produto_dao import ProdutoDAO
from compra_dao import CompraDAO
from db import get_conn


class DatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.getenv('SMARTCLINIC_TEST_DATABASE') != os.getenv('DB_NAME'):
            raise RuntimeError('Set SMARTCLINIC_TEST_DATABASE=DB_NAME for a disposable test database')
        bootstrap()

    def setUp(self):
        token = uuid.uuid4().hex[:11]
        self.client = ClienteDAO.inserir('Fictional test client', token, None,
                                        'example@example.invalid', '2000-01-01', 'Sousa')
        self.seller = VendedorDAO.inserir('Fictional test seller', token, 'seller@example.invalid', None)
        self.product = ProdutoDAO.inserir('Test product', 'Fictional inventory', 10, 5, 'Test')

    def tearDown(self):
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE i FROM item_compra i JOIN compra c ON i.id_compra=c.id_compra WHERE c.id_cliente=%s', (self.client,))
            cursor.execute('DELETE FROM compra WHERE id_cliente=%s', (self.client,))
            cursor.execute('DELETE FROM produto WHERE id_produto=%s', (self.product,))
            cursor.execute('DELETE FROM vendedor WHERE id_vendedor=%s', (self.seller,))
            cursor.execute('DELETE FROM cliente WHERE id_cliente=%s', (self.client,))
            conn.commit()
            cursor.close()

    def test_purchase_discount_stock_payment_and_report(self):
        purchase = CompraDAO.realizar(self.client, self.seller, 'pix', [{'id_produto':self.product,'quantidade':2}])
        self.assertEqual(ProdutoDAO.buscar_por_id(self.product).quantidade, 3)
        record = next(c for c in CompraDAO.listar_por_cliente(self.client) if c.id_compra == purchase)
        self.assertEqual(record.valor_total, 18)
        self.assertEqual(record.status_pagamento, 'pendente')
        self.assertEqual(len(CompraDAO.buscar_itens(purchase)), 1)
        self.assertEqual(CompraDAO.confirmar_pagamento(purchase), 1)
        now = datetime.now()
        self.assertTrue(CompraDAO.relatorio_mensal(now.year, now.month))

    def test_insufficient_duplicate_and_negative_quantities_do_not_change_stock(self):
        for items in ([{'id_produto':self.product,'quantidade':6}],
                      [{'id_produto':self.product,'quantidade':3},{'id_produto':self.product,'quantidade':3}],
                      [{'id_produto':self.product,'quantidade':-1}], []):
            with self.assertRaises((ValueError,RuntimeError)):
                CompraDAO.realizar(self.client,self.seller,'dinheiro',items)
            self.assertEqual(ProdutoDAO.buscar_por_id(self.product).quantidade, 5)
            self.assertEqual(CompraDAO.listar_por_cliente(self.client), [])
