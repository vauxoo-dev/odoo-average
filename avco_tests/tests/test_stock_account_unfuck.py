# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestStockCard(TransactionCase):

    def setUp(self):
        super(TestStockCard, self).setUp()
        self.aml_obj = self.env['account.move.line']
        self.radiogram_id = self.env.ref(
            'avco_tests.product_02_radiogram')
        self.val_id = self.radiogram_id.\
            categ_id.property_stock_valuation_account_id
        self.srp_obj = self.env['stock.return.picking']
        self.sp_obj = self.env['stock.picking']
        self.so_obj = self.env['sale.order']
        self.po_obj = self.env['purchase.order']
        self.res = {
            '01': {
                'act': 'purchase', 'xml': True, 'xml_id': "sau_po_ut_01",
                'avg': 100, 'qty': 10, 'debit': 1000, 'credit': 0, },
            '02': {
                'act': 'sale', 'xml': True, 'xml_id': "sau_so_ut_01",
                'avg': 100, 'qty': 6, 'debit': 1000, 'credit': 400, },
            '03': {
                'act': 'sale', 'xml': True, 'xml_id': "sau_so_ut_02",
                'avg': 100, 'qty': 1, 'debit': 1000, 'credit': 900, },
            '04': {
                'act': 'purchase', 'xml': True, 'xml_id': "sau_po_ut_02",
                'avg': 250, 'qty': 4, 'debit': 1900, 'credit': 900, },
            '05': {
                'act': 'sale', 'xml': True, 'xml_id': "sau_so_ut_03",
                'avg': 250, 'qty': 1, 'debit': 1900, 'credit': 1650, },
            '06': {
                'act': 'sale-ret', 'qty-ret': 1, 'xml_id': "sau_so_ut_01",
                'avg': 175, 'qty': 2, 'debit': 2000, 'credit': 1650, },
            '07': {
                'act': 'purchase', 'xml': True, 'xml_id': "sau_po_ut_03",
                'avg': 207.14, 'qty': 7, 'debit': 3100, 'credit': 1650, },
            '08': {
                'act': 'purchase', 'xml': True, 'xml_id': "sau_po_ut_04",
                'avg': 265, 'qty': 10, 'debit': 4300, 'credit': 1650, },
            '09': {
                'act': 'purchase-ret', 'qty-ret': 5, 'xml_id': "sau_po_ut_03",
                'avg': 310, 'qty': 5, 'debit': 4300, 'credit': 2750, },
            '10': {
                'act': 'purchase-ret', 'qty-ret': 1, 'xml_id': "sau_po_ut_02",
                'avg': 312.5, 'qty': 4, 'debit': 4300, 'credit': 3050, },
            '11': {
                'act': 'purchase-ret', 'qty-ret': 1, 'xml_id': "sau_po_ut_01",
                'avg': 383.33, 'qty': 3, 'debit': 4300, 'credit': 3150, },
            '12': {
                'act': 'purchase-ret', 'qty-ret': 3, 'xml_id': "sau_po_ut_04",
                'avg': 383.33, 'qty': 0, 'debit': 4300, 'credit': 4299.99, },
            '13': {
                'act': 'purchase', 'xml': True, 'xml_id': "sau_po_ut_05",
                'avg': 280, 'qty': 6, 'debit': 5980, 'credit': 4299.99, },
            '14': {
                'act': 'sale-ret', 'qty-ret': 3, 'xml_id': "sau_so_ut_03",
                'avg': 270, 'qty': 9, 'debit': 6730, 'credit': 4299.99, },
            '15': {
                'act': 'sale', 'xml': True, 'xml_id': "sau_so_ut_04",
                'avg': 270, 'qty': 6, 'debit': 6730, 'credit': 5109.99, },
        }

    def process_picking(self, sp_brws):
        sp_brws.action_confirm()
        sp_brws.action_assign()
        while sp_brws.filtered(lambda x: x.state == 'assigned'):
            sp_brw = sp_brws.filtered(lambda x: x.state == 'assigned')
            res_dict = sp_brw.button_validate()
            wizard = self.env[(res_dict.get('res_model'))].browse(
                res_dict.get('res_id'))
            wizard.process()
        return

    def do_sale_return(self, record):
        xml_id = record['xml_id']
        so_id = self.ref("avco_tests.%s" % xml_id)
        so_brw = self.so_obj.browse(so_id)
        active_id = so_brw.picking_ids.filtered(
            lambda x: x.picking_type_code == 'outgoing').id
        ctx = {'active_id': active_id, 'active_ids': [active_id]}
        stock_return_picking = self.srp_obj.with_context(ctx).create({})
        stock_return_picking.product_return_moves.quantity = record['qty-ret']
        stock_return_picking_action = stock_return_picking.create_returns()
        return_pick = self.env['stock.picking'].browse(
            stock_return_picking_action['res_id'])
        return_pick.move_lines[0].move_line_ids[0].qty_done = record['qty-ret']
        return_pick.action_done()
        # self.process_picking(sp_brw)
        return

    def do_sale(self, xml_id):
        so_id = self.ref("avco_tests.%s" % xml_id)
        so_brw = self.so_obj.browse(so_id)
        so_brw.action_confirm()
        self.process_picking(so_brw.picking_ids)
        return

    def do_purchase_return(self, record):
        xml_id = record['xml_id']
        po_id = self.ref("avco_tests.%s" % xml_id)
        po_brw = self.po_obj.browse(po_id)
        active_id = po_brw.picking_ids[0].id
        ctx = {'active_id': active_id, 'active_ids': [active_id]}

        stock_return_picking = self.srp_obj.with_context(ctx).create({})
        stock_return_picking.product_return_moves.quantity = record['qty-ret']
        stock_return_picking_action = stock_return_picking.create_returns()
        return_pick = self.env['stock.picking'].browse(
            stock_return_picking_action['res_id'])
        return_pick.move_lines[0].move_line_ids[0].qty_done = record['qty-ret']
        return_pick.do_transfer()

        # self.process_picking(sp_brw)
        return

    def do_purchase(self, xml_id):
        po_id = self.ref("avco_tests.%s" % xml_id)
        po_brw = self.po_obj.browse(po_id)
        po_brw.button_confirm()
        self.process_picking(po_brw.picking_ids)
        return

    def return_transaction(self, record):
        if record['act'] in ('sale', ):
            self.do_sale(record['xml_id'])
        elif record['act'] in ('sale-ret', ):
            self.do_sale_return(record)
        elif record['act'] in ('purchase', ):
            self.do_purchase(record['xml_id'])
        elif record['act'] in ('purchase-ret', ):
            self.do_purchase_return(record)
        return

    def test_10_average_qty_flow(self):
        for index in range(1, 16):
            res = self.res["%02d" % index]
            self.return_transaction(res)

            self.assertEqual(
                round(self.radiogram_id.qty_available, 2), res["qty"],
                "Operation: %02d - Qty Available should be %s" % (
                    index, res["qty"]))
        return

    def test_20_average_computation(self):
        for index in range(1, 16):
            res = self.res["%02d" % index]
            self.return_transaction(res)

            self.assertEqual(
                round(self.radiogram_id.average_price, 2), res["avg"],
                "operation: %02d - expected average - cost price is %s" % (
                    index, res["avg"]))
        return

    def test_30_accounting_booking(self):
        for index in range(1, 16):
            res = self.res["%02d" % index]
            self.return_transaction(res)

            aml_ids = self.aml_obj.search(
                [('product_id', '=', self.radiogram_id.id),
                 ('account_id', '=', self.val_id.id)])

            debit = sum([aml.debit for aml in aml_ids])
            credit = sum([aml.credit for aml in aml_ids])

            self.assertEqual(
                debit, res["debit"],
                "operation: %02d - expected debit %s" % (
                    index, res["debit"]))
            self.assertEqual(
                credit, res["credit"],
                "operation: %02d - expected credit %s" % (
                    index, res["credit"]))
        return
