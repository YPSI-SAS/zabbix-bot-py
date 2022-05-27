from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch, cm
from action import get_time, get_image_data

from report import Report


class ReportHost(Report):

    def __init__(self, api, host_id, LANG) -> None:
        super().__init__(api, LANG)
        self.host_id = host_id
        self.information_host = self.api.get_host_info(self.host_id)[
            0]

    def write_general_information(self, part, _):
        """Write general information of service in report"""
        self.write_paragraph(
            part+". "+_("General informations"), 'Heading1Set')

        self.write_paragraph(
            "<b>"+_("Status")+":</b> "+self.convert_general_status_to_text(self.information_host['status'], _), 'Normal')
        self.write_paragraph(
            "<b>"+_("Availability")+":</b> "+self.convert_availability_to_text(self.information_host['interfaces'][0]['available'], _), 'Normal')
        if type(self.information_host['inventory']) != list and self.information_host['inventory']['location_lat'] != "" and self.information_host['inventory']['location_lon'] != "":
            self.write_paragraph(
                "<b>"+_("Latitude")+":</b> "+self.information_host['inventory']['location_lat']+" <b>"+_("Longitude")+":</b> " + self.information_host['inventory']['location_lon'], 'Normal')

        self.write_table_tag(self.information_host['tags'], _)

    def write_item_information(self, items, part, _):
        self.write_paragraph(
            part+". "+_("Items"), 'Heading1Set')
        super().write_item_information(items=items, part=part, _=_)

    def write_problems_information(self, part, _):
        problems_list = self.api.get_host_problem(
            self.information_host['hostid'])
        super().write_problems_information(part, _, problems_list)

    def write_trigger_information(self, part, _):
        list_triggers = list()
        for trigger in self.information_host['triggers']:
            list_triggers.append(trigger['triggerid'])
        super().write_trigger_information(part, _, list_triggers)

    def create_report(self):
        """Create report for a specific service"""

        name_file = "./documents/hosts/%s.pdf" % (
            self.information_host['name'])
        doc = SimpleDocTemplate(name_file,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        self.write_paragraph(
            '<a name="HOST_'+self.information_host['hostid']+'"/>'+self._("Host")+" : "+self.information_host['name'], 'TitleSet')
        self.write_general_information("1", self._)
        self.write_item_information(
            items=self.information_host['items'], part="2", _=self._)
        self.write_trigger_information(
            "3", self._)
        self.write_problems_information(
            "4", self._)
        doc.build(self.story)
        return name_file, self.list_images
