# -*- coding: utf-8 -*-
import time
from odoo import api, models, _
from odoo.exceptions import UserError
from datetime import datetime


class ReportIncomeByProcedure(models.AbstractModel):
    _name = 'report.cost_profit_report.report_income_procedure_profit'
    
    def get_income_procedure(self, start_date, end_date, treatment_ids, detailed, company_id):
        dom = [('invoice_date', '>=', start_date),
              ('invoice_date', '<=', end_date),
              ('company_id', '=', company_id[0]),
            #   ('is_patient', '=', True),
              ('state', 'in', ['open', 'paid'])]
        # if doctor:
        #     dom.append(('dentist', '=', doctor[0]))
        history_ids = self.env['account.move'].search(dom)
        detailed_list = []
        detailed_dict = {}
        total_count = 0
        total_income = 0
        total_cost = 0
        total_profit = 0
        prod_dict = {}
        for income in history_ids:
            if income:
                for line in income.invoice_line_ids:
                    # if treatment_ids:
                    #     contition_here = line.product_id.is_treatment and line.product_id.id in treatment_ids
                    # else:
                    #     contition_here = line.product_id.is_treatment
                    # if contition_here:
                    total_income += line.price_subtotal
                    total_cost += line.product_id.standard_price
                    total_count += 1
                    # patient_name = income.patient.name.name
                    # if income.patient.patient_id:
                    #     patient_name = '[' + income.patient.patient_id + ']' + patient_name
                    
                    if treatment_ids: 
                        if line.product_id.id in treatment_ids:
                            detailed_dict = {'name': income.number, 'count': 1, 'price_unit': line.price_subtotal,
                                                'product': line.product_id.id, 
                                                # 'patient':patient_name,
                                                'cost': line.product_id.standard_price}
                            detailed_list.append(detailed_dict)
                            if line.product_id.id in prod_dict:
                                prod_dict[line.product_id.id][1] += 1
                                prod_dict[line.product_id.id][2] += line.price_subtotal
                            else:
                                prod_dict[line.product_id.id] = [line.product_id.name, 1, line.price_subtotal,
                                                                    line.product_id.id, line.product_id.standard_price ]
                    else:
                        detailed_dict = {'name': income.number, 'count': 1, 'price_unit': line.price_subtotal,
                                            'product': line.product_id.id, 
                                            # 'patient':patient_name,
                                            'cost': line.product_id.standard_price}
                        detailed_list.append(detailed_dict)
                        if line.product_id.id in prod_dict:
                            prod_dict[line.product_id.id][1] += 1
                            prod_dict[line.product_id.id][2] += line.price_subtotal
                        else:
                            prod_dict[line.product_id.id] = [line.product_id.name, 1, line.price_subtotal,
                                                                line.product_id.id, line.product_id.standard_price ]                                            
        total_profit = total_income - total_cost
        return [prod_dict], detailed_list, total_count, total_income, total_cost, total_profit

    # @api.multi
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        start_date = data['form']['date_start']
        end_date = data['form']['date_end']
        detailed = data['form']['detailed']
        categories = data['categories']
        based_on = data['based_on']
        treatment_ids = data['treatment_ids']
        treatments = ""
        treatment_list = []
        for tmt in treatment_ids:
            if treatments != '':
                treatments += ', '
            tmt_rec = self.env['product.product'].browse(tmt)
            treatments += tmt_rec.name
            treatment_list.append(tmt_rec.id)
        # doctor = data['doctor']
        company_id = data['company_id']
        final_records, detailed_list, total_count, total_income, total_cost, total_profit  = self.get_income_procedure(start_date, end_date, treatment_list, detailed, company_id)
        period_start = datetime.strptime(start_date, '%Y-%m-%d')
        period_stop = datetime.strptime(end_date, '%Y-%m-%d')
        # doctor_name = False
        # if doctor:
        #     doctor_name = doctor[1]
        return {
            'period_start': period_start,
            'period_stop': period_stop,
            # 'doctor': doctor_name,
            'detailed_list': detailed_list,
            'detailed': detailed,
            'total_count': total_count,
            'total_income': total_income,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'company_id': company_ids,
            'categories': categories,
            'based_on': based_on,
            'treatments': treatments,
            'doc_ids': self.ids,
            'doc_model': 'income.procedure.profit',
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_income_procedure': final_records,
        }
    
    def formatLang(self, value, digits=None, date=False, date_time=False, grouping=True, monetary=False, dp=False,
                   currency_obj=False, lang=False):
        if lang:
            self.env.context['lang'] = lang
        return super(ReportIncomeByProcedure, self).formatLang(value, digits=digits, date=date, date_time=date_time,
                                                               grouping=grouping, monetary=monetary, dp=dp,
                                                               currency_obj=currency_obj)
