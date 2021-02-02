from odoo import api, fields, models, SUPERUSER_ID
import base64
from odoo.exceptions import Warning
from datetime import datetime


class SalesReportWizard(models.TransientModel):
    _name = "pharmacy.cost.profit.report"

    def _get_company_id(self):
        group_multi_company = self.env.user.has_group('base.group_multi_company')
        if group_multi_company:
            company_ids = [x.id for x in self.env['res.company'].search([('id', 'in', self.env.user.company_ids.ids)])]
            domain_company = [('id', 'in', company_ids)]
        else:
            domain_company = [('id', '=', self.env.user.company_id.id)]
        return domain_company

    company_id = fields.Many2one('res.company', "Company", domain=_get_company_id, required=True)
    period_start = fields.Date("Period From", required=True, default=fields.Date.context_today)
    period_stop = fields.Date("Period To", required=True, default=fields.Date.context_today)
    # pdt_ids = fields.Many2many(comodel_name='product.product',string="Drugs",
    #                            domain=[('is_medicament', '=', True)])
    pdt_ids = fields.Many2many(comodel_name='product.product',string="Products")                           

    @api.model
    def default_get(self, fields):
        res = super(SalesReportWizard, self).default_get(fields)
        self._get_company_id()
        res['company_id'] = self.env.user.company_id.id
        return res

    # @api.multi
    # def send_pharmacy_sales_report(self):
    #     pdt_ids = []
    #     pdt_name = ''
    #     for i in self.pdt_ids:
    #         pdt_ids.append(i.id)
    #         pdt_name = pdt_name + i.name_get()[0][1] + ' ,'
    #     data = {
    #         'period_start': self.period_start,
    #         'period_stop': self.period_stop,
    #         'show_drug': self.show_drug,
    #         'pdt_ids': pdt_ids,
    #         'pdt_name': pdt_name,
    #         'company_id': [self.company_id.id, self.company_id.name],
    #     }
    #     report_id = 'pharmacy_sales_report.pharmacy_sales_report'
    #     pdf = self.env.ref(report_id).render_qweb_pdf(self.ids, data=data)
    #     b64_pdf = base64.b64encode(pdf[0])
    #     attachment_name = 'Sales Report: ' + str(self.period_start) + " To " + str(self.period_stop)
    #     attachment_id = self.env['ir.attachment'].create({
    #         'name': attachment_name,
    #         'type': 'binary',
    #         'datas': b64_pdf,
    #         'datas_fname': attachment_name + '.pdf',
    #         # 'store_fname': attachment_name,
    #         'res_model': self._name,
    #         'res_id': self.id,
    #         'mimetype': 'application/x-pdf'
    #     })
    #     attach = {
    #         attachment_id.id,
    #     }
    #     user = self.env['res.users'].browse(SUPERUSER_ID)
    #     from_email = user.partner_id.email
    #     mail_values = {
    #         'reply_to': from_email,
    #         'email_to': from_email,
    #         'subject': attachment_name,
    #         'body_html': """<div>
    #         <p>Hello,</p>
    #         <p>This email was created automatically by Odoo H Care. Please find the attached Pharmacy sales reports.</p>
    #                         </div>
    #                         <div>Thank You</div>""",
    #         'attachment_ids': [(6, 0, attach)]
    #     }
    #     mail_id = self.env['mail.mail'].create(mail_values)
    #     mail_id.send()
    #     if mail_id.state == 'exception':
    #         message = mail_id.failure_reason
    #         raise Warning(message)
        # else:
        #     message = "Daily report mail sent successfully."
        #     self.env.user.notify_info(message, title='Email sent', sticky=True)

    # @api.multi
    def pharmacy_sales_report(self):
        pdt_ids = []
        pdt_name = ''
        for i in self.pdt_ids:
            pdt_ids.append(i.id)
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'pdt_ids': pdt_ids,
            'company_id': [self.company_id.id, self.company_id.name],
        }
        return self.env.ref('cost_profit_report.pharmacy_cost_profit_report').report_action(self, data=data)


class ReportSale(models.AbstractModel):
    _name = 'report.cost_profit_report.pharmacy_report_pdf'

    def get_active_orders(self, period_start=False, period_stop=False,
                          company_id=False, product_ids=False):
        s_domain = [
            ('invoice_date', '>=', period_start),
            ('invoice_date', '<=', period_stop),
            ('state', 'in', ['posted']),
            ('company_id', '=', company_id[0])]
        invoices = self.env['account.move'].search(s_domain)

        orders = self.env['sale.order']
        for inv in invoices:
            if product_ids:
                for inv_line in inv.invoice_line_ids:
                    if inv_line.product_id.id in product_ids:
                        orders |= inv_line.mapped('sale_line_ids').mapped(
                            'order_id')
            else:
                for inv_line in inv.invoice_line_ids:
                    orders |= inv_line.mapped('sale_line_ids').mapped('order_id')
        return orders

    @api.model
    def get_sale_details(self, period_start=False, period_stop=False, pdt_ids=False, company_id=False):
        pdt_dict = {}
        journal_obj = self.env['account.journal']
        journal_ids = journal_obj.search([
            ('company_id', '=', company_id[0])])
        jrnl_data = {}
        for j in journal_ids:
            jrnl_data[j.id] = {'name': j.name, 'sum': 0}
        if pdt_ids:
            for p in pdt_ids:
                p_name = self.env['product.product'].search(
                    [('id', '=', p)]).name_get()[0][1]
                pdt_dict[p] = {
                    'name': p_name,
                    'orders': [],
                    'qty': 0,
                    'total': 0
                }
        order_list = []

        product_dict ={}
        for order in self.get_active_orders(period_start, period_stop, company_id, pdt_ids):
            for line in order.order_line :
                if pdt_ids :
                    if line.product_id.id in pdt_ids :
                        if line.product_id.id in product_dict.keys():
                            product_dict[line.product_id.id]['sold_qty'] =product_dict[line.product_id.id]['sold_qty'] + line.qty_invoiced
                            product_dict[line.product_id.id]['total'] =product_dict[line.product_id.id]['total'] + line.price_subtotal
                            product_dict[line.product_id.id]['cost'] =product_dict[line.product_id.id]['cost'] + line.product_id.standard_price
                        else:
                            product_dict[line.product_id.id] = {
                                'name':line.product_id.name,
                                'sold_qty': line.qty_invoiced,
                                'total':line.price_subtotal,
                                'cost':line.product_id.standard_price,

                            }
                else :
                    if line.product_id.id in product_dict.keys():
                        product_dict[line.product_id.id]['sold_qty'] =product_dict[line.product_id.id]['sold_qty'] + line.qty_invoiced
                        product_dict[line.product_id.id]['total'] =product_dict[line.product_id.id]['total'] + line.price_subtotal
                        product_dict[line.product_id.id]['cost'] =product_dict[line.product_id.id]['cost'] + line.product_id.standard_price
                    else:
                        product_dict[line.product_id.id] = {
                            'name':line.product_id.name,
                            'sold_qty': line.qty_invoiced,
                            'total':line.price_subtotal,
                            'cost':line.product_id.standard_price,

                        }
        return {'product_dict':product_dict}

    # @api.multi
    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_sale_details(period_start=data['period_start'],
                                          period_stop=data['period_stop'],
                                          pdt_ids=data['pdt_ids'],
                                          company_id=data['company_id']))
        data['period_start'] = datetime.strptime(data['period_start'], '%Y-%m-%d')
        data['period_stop'] = datetime.strptime(data['period_stop'], '%Y-%m-%d')
        return data
