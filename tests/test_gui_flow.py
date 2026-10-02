"""Tk form callbacks against a disposable real database; run under Xvfb."""
import os
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'interface'))
import test_database_integration as dbtests

ClienteDAO=dbtests.ClienteDAO
VendedorDAO=dbtests.VendedorDAO
ProdutoDAO=dbtests.ProdutoDAO
CompraDAO=dbtests.CompraDAO


@unittest.skipUnless(os.getenv('DISPLAY'), 'GUI flow requires a display (use xvfb-run)')
class GuiFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dbtests.DatabaseTests.setUpClass()

    def setUp(self):
        dbtests.DatabaseTests.setUp(self)

    def tearDown(self):
        if hasattr(self,'app'):
            self.app.root.destroy()
        dbtests.DatabaseTests.tearDown(self)

    def test_edit_forms_purchase_stock_payment_and_navigation(self):
        import tkinter as tk
        import interface as ui

        def fail_dialog(title, message, **kwargs):
            raise AssertionError(f'{title}: {message}')

        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)

        def invoke(form, text):
            buttons=[w for w in descendants(form) if isinstance(w,tk.Button) and text in str(w.cget('text'))]
            self.assertEqual(len(buttons),1)
            buttons[0].invoke()
            self.app.root.update_idletasks()

        with patch.object(tk.Tk,'mainloop',return_value=None), \
             patch.object(ui.messagebox,'showerror',side_effect=fail_dialog), \
             patch.object(ui.messagebox,'showwarning',side_effect=fail_dialog), \
             patch.object(ui.messagebox,'askyesno',return_value=True):
            self.assertTrue(ui.DB_DISPONIVEL)
            self.app=ui.SmartClinic()
            for page in ['Dashboard','Clientes','Vendedores','Produtos','Compras']:
                self.app._switch(page)
                self.assertEqual(self.app.active_page,page)
            saved=[]
            form=ui.ClienteForm(self.app.pages['Clientes'],self.app.root,saved.append,
                               ClienteDAO.buscar_por_id(self.client))
            form.e_nome.delete(0,'end');form.e_nome.insert(0,'Edited fictional client')
            invoke(form,'Salvar')
            self.assertEqual(saved[-1].nome,'Edited fictional client')
            form=ui.VendedorForm(self.app.pages['Vendedores'],self.app.root,saved.append,
                                VendedorDAO.buscar_por_id(self.seller))
            form.e_nome.delete(0,'end');form.e_nome.insert(0,'Edited fictional seller')
            invoke(form,'Salvar')
            self.assertEqual(saved[-1].nome,'Edited fictional seller')
            form=ui.ProdutoForm(self.app.pages['Produtos'],self.app.root,saved.append,
                               ProdutoDAO.buscar_por_id(self.product))
            form.e_preco.delete(0,'end');form.e_preco.insert(0,'12.50')
            invoke(form,'Salvar')
            self.assertEqual(saved[-1].preco,12.5)
            form=ui.NovaCompraForm(self.app.pages['Compras'],self.app.root,saved.append)
            form.v_cli.set(next(k for k,c in form.cli_opts.items() if c.id_cliente==self.client))
            form.v_vnd.set(next(k for k,v in form.vnd_opts.items() if v.id_vendedor==self.seller))
            form.v_prod.set(next(k for k,p in form.prod_opts.items() if p.id_produto==self.product))
            form.v_pag.set('pix');form.e_qtd.delete(0,'end');form.e_qtd.insert(0,'2')
            invoke(form,'Adicionar ao Carrinho')
            self.assertEqual(len(form.itens_carrinho),1)
            invoke(form,'Finalizar Compra')
            purchase=saved[-1]
            self.assertEqual(ProdutoDAO.buscar_por_id(self.product).quantidade,3)
            record=next(c for c in CompraDAO.listar_por_cliente(self.client) if c.id_compra==purchase)
            self.assertEqual(record.valor_total,22.5)
            self.assertEqual(CompraDAO.confirmar_pagamento(purchase),1)
            self.app.pages['Compras']._reload()
            self.app.pages['Dashboard']._atualizar()
            self.assertEqual(len(CompraDAO.buscar_itens(purchase)),1)
