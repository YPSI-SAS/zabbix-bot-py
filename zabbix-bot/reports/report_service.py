
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Spacer, Image, Table, TableStyle
from reportlab.lib.units import cm
from action import get_date_value_depending_period, get_val_time
from reports.report import Report
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ReportService(Report):
    def __init__(self, api, service_id, LANG) -> None:
        super().__init__(api, LANG)
        self.service_id = service_id
        self.host_ids = []
        self.trigger_ids = []
        try:
            self.information_service = self.api.get_service_info(self.service_id)[0]
        except Exception as e:
            logger.error("Error to get service information")
            raise Exception(e)

    def write_general_information(self, part, _):
        """Write general information of service in report"""
        self.write_paragraph(
            part+". "+_("General informations"), 'Heading1Set')
        self.write_paragraph(
            "<b>"+_("Status")+":</b> "+self.convert_severity_to_text(self.information_service['status'], _), 'Normal')
        self.write_paragraph(
            "<b>"+_("Algorithm")+":</b> "+self.convert_algorithm_to_text(self.information_service['algorithm'], _), 'Normal')
        self.write_paragraph(
            "<b>"+_("Sort order")+":</b> "+str(self.information_service['sortorder']), 'Normal')
        self.write_paragraph(
            "<b>"+_("Description")+":</b> "+str(self.information_service['description']), 'Normal')
        self.write_paragraph(
            "<b>"+_("Created at")+":</b> " + self.convert_datetime_to_text(self.information_service['created_at']), 'Normal')

        self.write_table_tag(self.information_service['tags'], _)

        self.write_paragraph(
            "<b>"+_("Problem tags")+":</b> ", 'Normal')
        self.story.append(Spacer(1, 12))
        data_tag = [[_('Name'), _('Operator'), _('Value')]]
        for tag in self.information_service['problem_tags']:
            tag_val = []
            tag_val.append(tag['tag'])
            tag_val.append(self.convert_operator_to_text(tag['operator'], _))
            tag_val.append(tag['value'])
            data_tag.append(tag_val)
        table = Table(data_tag, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica'),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        self.story.append(table)

    def write_sla_information(self,part,_):
        """Write SLA information of service"""
        sla_service = self.api.get_sla_by_service(service_id=self.information_service['serviceid'])
        self.write_paragraph(
            part+". "+_("SLA"), 'Heading1Set')

        if len(sla_service) != 0:    
            for sla in sla_service:
                index = sla_service.index(sla)+1
                sla_report = self.api.get_sla_report_by_service(sla_id=sla['slaid'], service_id=self.information_service['serviceid'])
                sla_report_period = sla_report['periods']
                sla_report_period.reverse()
                sla_report_sli = list()
                for i in range(len(sla_report_period)):
                    sla_report_sli.append(sla_report['sli'][i][0])
                sla_report_sli.reverse()

                self.write_paragraph(
                    part+"."+str(index)+" " +sla['name'], 'Heading2Set')

                self.story.append(Spacer(1, 12))
                data_sla = [[self.get_column_name(sla['period'], _), _('SLO'), _('SLI'), _('Uptime'), _('Downtime'), _('Error budget')]]

                for i in range(len(sla_report_period)):
                    sla_val = []
                    sla_val.append(get_date_value_depending_period(sla['period'], sla_report_period[i]['period_from'], sla_report_period[i]['period_to']))
                    sla_val.append(sla['slo'])
                    sla_val.append(float(np.round(sla_report_sli[i]['sli'], 4)))
                    sla_val.append(get_val_time(sla_report_sli[i]['uptime']))
                    sla_val.append(get_val_time(sla_report_sli[i]['downtime']))
                    error_budget = get_val_time(abs(sla_report_sli[i]['error_budget']))
                    if sla_report_sli[i]['error_budget'] < 0:
                        error_budget = "-" + error_budget
                    sla_val.append(error_budget)
                    data_sla.append(sla_val)

                table = Table(data_sla, hAlign='LEFT')
                table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ]))
                self.story.append(table)

    def get_column_name(self,period, _):
        """Convert period to text"""
        switcher = {
            "0": _("Day"),
            "1": _("Week"),
            "2": _("Month"),
            "3": _("Quarter"),
            "4": _("Year")
        }
        return switcher.get(period, "invalid status")

    def write_parents_information(self, part, _):
        """Write parents information of service"""
        self.write_paragraph(
            part+". "+_("Parents"), 'Heading1Set')
        for parent in self.information_service['parents']:
            index = self.information_service['parents'].index(parent)+1
            self.write_paragraph(
                part+"."+str(index)+" " + parent['name'], 'Heading2Set')
            self.write_paragraph(
                "<b>"+_("Status")+":</b> "+self.convert_severity_to_text(parent['status'], _), 'Normal')
            self.write_paragraph(
                "<b>"+_("Algorithm")+":</b> "+self.convert_algorithm_to_text(parent['algorithm'], _), 'Normal')
            self.write_paragraph(
                "<b>"+_("Sort order")+":</b> "+str(parent['sortorder']), 'Normal')
            self.write_paragraph(
                "<b>"+_("Description")+":</b> "+str(parent['description']), 'Normal')
            self.write_paragraph(
                "<b>"+_("Created at")+":</b> " + self.convert_datetime_to_text(parent['created_at']), 'Normal')

    def write_children_information(self, part, _):
        """Write children information of service"""
        self.write_paragraph(
            part+". "+_("Children"), 'Heading1Set')
        for child in self.information_service['children']:
            index = self.information_service['children'].index(child)+1
            self.write_paragraph(
                part+"."+str(index)+" " + child['name'], 'Heading2Set')
            self.write_paragraph(
                "<b>"+_("Status")+":</b> "+self.convert_severity_to_text(child['status'], _), 'Normal')
            self.write_paragraph(
                "<b>"+_("Algorithm")+":</b> "+self.convert_algorithm_to_text(child['algorithm'], _), 'Normal')
            self.write_paragraph(
                "<b>"+_("Sort order")+":</b> "+str(child['sortorder']), 'Normal')
            self.write_paragraph(
                "<b>"+_("Description")+":</b> "+str(child['description']), 'Normal')
            self.write_paragraph(
                "<b>"+_("Created at")+":</b> " + self.convert_datetime_to_text(child['created_at']), 'Normal')

    def write_problems_information(self, part, _, problems_list):
        """Write problems information of service"""
        for event in problems_list:
            event_info = self.api.get_problem_info(event['eventid'])[0]
            if event_info['hosts'][0]['hostid'] not in self.host_ids:
                self.host_ids.append(event_info['hosts'][0]['hostid'])
            if event_info['object'] == "0":
                if event_info['relatedObject']['triggerid'] not in self.trigger_ids:
                    self.trigger_ids.append(
                        event_info['relatedObject']['triggerid'])
        super().write_problems_information(part, _, problems_list)

    def create_report(self, version):
        """Create report for a specific service"""

        name_file = "../documents/services/%s.pdf" % (
            self.information_service['name'])
        doc = SimpleDocTemplate(name_file,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        self.write_paragraph(
            self._("Service")+" : "+self.information_service['name'], 'TitleSet')
        self.write_general_information("1", self._)
        self.write_sla_information("2", self._)
        self.write_parents_information("3", self._)
        self.write_children_information("4", self._)
        self.write_problems_information(
            "5", self._, self.information_service['problem_events'])
        self.write_host_information("6", self._, self.host_ids, version)
        self.write_trigger_information("7", self._, self.trigger_ids)
        doc.build(self.story)
        return name_file, self.list_images
