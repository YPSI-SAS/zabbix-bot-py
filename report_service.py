
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch, cm
from action import get_time, get_image_data

from report import Report


class ReportService(Report):
    def __init__(self, api, service_id, LANG) -> None:
        super().__init__(api, LANG)
        self.service_id = service_id
        self.host_ids = []
        self.trigger_ids = []
        self.information_service = self.api.get_service_info(self.service_id)[
            0]

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
            tag_val.append(self.convert_operator_to_text(tag['operator']))
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

    def create_report(self):
        """Create report for a specific service"""

        name_file = "./documents/services/%s.pdf" % (
            self.information_service['name'])
        doc = SimpleDocTemplate(name_file,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        self.write_paragraph(
            self._("Service")+" : "+self.information_service['name'], 'TitleSet')
        self.write_general_information("1", self._)
        self.write_parents_information("2", self._)
        self.write_children_information("3", self._)
        self.write_problems_information(
            "4", self._, self.information_service['problem_events'])
        self.write_host_information("5", self._, self.host_ids)
        self.write_trigger_information("6", self._, self.trigger_ids)
        doc.build(self.story)
        return name_file
