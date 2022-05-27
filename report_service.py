from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.fonts import tt2ps
from reportlab.rl_config import canvas_basefontname as _baseFontName
from datetime import datetime
from action import get_time, get_image_data
import gettext

_baseFontNameB = tt2ps(_baseFontName, 1, 0)


class reportService:
    def __init__(self, api, service_id) -> None:
        self.api = api
        self.service_id = service_id
        self.story = []
        self.host_ids = []
        self.trigger_ids = []
        self.information_service = self.api.get_service_info(self.service_id)[
            0]
        self.styles = getSampleStyleSheet()
        self.set_styles()

    def set_styles(self):
        """Define many styles use in report"""
        self.styles.add(ParagraphStyle(name='TitleSet', alignment=TA_CENTER,
                        fontSize=22, fontName=_baseFontNameB, leading=22))
        self.styles.add(ParagraphStyle(name="Heading1Set", fontName=_baseFontNameB,
                                       fontSize=18, leading=22, spaceAfter=4, spaceBefore=12, leftIndent=10))
        self.styles.add(ParagraphStyle(name="Heading2Set", fontName=_baseFontNameB,
                                       fontSize=14, leading=18, spaceBefore=12, spaceAfter=6, leftIndent=10))
        self.styles.add(ParagraphStyle(name="Heading3Set", fontName=_baseFontNameB,
                                       fontSize=12, leading=18, spaceBefore=12, spaceAfter=6, leftIndent=10))
        self.styles.add(ParagraphStyle(name="NormalSet",
                        fontName=_baseFontName, fontSize=12,  leading=12))

    def write_paragraph(self, text, style):
        """Write paragraph in report with specific style"""
        self.story.append(
            Paragraph(text, self.styles[style]))

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

    def write_problems_information(self, part, _):
        """Write problems information of service"""
        self.write_paragraph(
            part+". "+_("Problems"), 'Heading1Set')
        for event in self.information_service['problem_events']:
            event_info = self.api.get_problem_info(event['eventid'])[0]
            index = self.information_service['problem_events'].index(event)+1
            self.write_paragraph(
                part+"."+str(index)+" "+event_info['name']+" - "+self.convert_datetime_to_text(event_info["clock"]), 'Heading2Set')
            self.write_paragraph(
                "<b>"+_("Severity")+":</b> "+self.convert_severity_to_text(event_info['severity'], _), 'Normal')
            self.write_paragraph(
                "<b>"+_("Acknowledged")+":</b> "+self.convert_acknowledge_to_text(event_info['acknowledged'], _), 'Normal')
            self.write_paragraph(
                "<b>"+_("Duration")+":</b> "+get_time(event_info['clock']), 'Normal')
            self.write_paragraph(
                '<b>'+_("Host")+':</b> <a href="#HOST_'+str(event_info['hosts'][0]['hostid'])+'" color="blue">' + event_info['hosts'][0]['name']+"</a>", 'Normal')
            if event_info['hosts'][0]['hostid'] not in self.host_ids:
                self.host_ids.append(event_info['hosts'][0]['hostid'])
            if event_info['object'] == "0":
                self.write_paragraph(
                    '<b>'+_("Trigger")+':</b> <a href="#TRIGGER_'+str(event_info['relatedObject']['triggerid'])+'" color="blue">' + event_info['relatedObject']['description']+"</a>", 'Normal')
                if event_info['relatedObject']['triggerid'] not in self.trigger_ids:
                    self.trigger_ids.append(
                        event_info['relatedObject']['triggerid'])
            if len(event_info['acknowledges']) != 0:
                self.write_acknowledge_informations(event_info, index, part, _)

    def write_acknowledge_informations(self, event, index, part, _):
        """Write acknowledge information of problem"""
        self.write_paragraph(
            part+"."+str(index)+".1 "+_("Acknowledge actions"), 'Heading3Set')
        for ack in event['acknowledges']:
            severity = False
            message = False
            if ack['action'] == "2":
                self.write_paragraph(
                    "<b>"+_("Acknowledge event")+"</b>", 'Normal')
            elif ack['action'] == "4":
                self.write_paragraph(
                    "<b>"+_("Add message")+"</b>", 'Normal')
                message = True
            elif ack['action'] == "6":
                self.write_paragraph(
                    "<b>"+_("Acknowledge event + Add message")+"</b>", 'Normal')
                message = True
            elif ack['action'] == "8":
                self.write_paragraph(
                    "<b>"+_("Change severity")+"</b>", 'Normal')
                severity = True
            elif ack['action'] == "10":
                self.write_paragraph(
                    "<b>"+_("Acknowledge event + Change severity")+"</b>", 'Normal')
                severity = True
            elif ack['action'] == "12":
                self.write_paragraph(
                    "<b>"+_("Add message + Change severity")+"</b>", 'Normal')
                severity = True
                message = True
            elif ack['action'] == "12":
                self.write_paragraph(
                    "<b>"+_("Add message + Change severity")+"</b>", 'Normal')
                severity = True
                message = True
            elif ack['action'] == "14":
                self.write_paragraph(
                    "<b>"+_("Acknowledge event + Add message + Change severity")+"</b>", 'Normal')
                severity = True
                message = True
            elif ack['action'] == "16":
                self.write_paragraph(
                    "<b>"+_("Unacknowledge event")+"</b>", 'Normal')
            elif ack['action'] == "20":
                self.write_paragraph(
                    "<b>"+_("Unacknowledge event + Add message")+"</b>", 'Normal')
                message = True
            elif ack['action'] == "24":
                self.write_paragraph(
                    "<b>"+_("Unacknowledge event + Change severity")+"</b>", 'Normal')
                severity = True
            elif ack['action'] == "28":
                self.write_paragraph(
                    "<b>"+_("Unacknowledge event + Add message + Change severity")+"</b>", 'Normal')
                severity = True
                message = True

            if message == True:
                self.write_paragraph(
                    "<b>"+_("Message")+":</b> " + ack['message'], 'Normal')
            if severity == True:
                self.write_paragraph(
                    "<b>"+_("Old severity")+":</b> " + self.convert_severity_to_text(ack['old_severity'], _), 'Normal')
                self.write_paragraph(
                    "<b>"+_("New severity")+":</b> " + self.convert_severity_to_text(ack['new_severity'], _), 'Normal')
            self.write_paragraph(
                "<b>"+_("At")+":</b> " + self.convert_datetime_to_text(ack['clock']), 'Normal')
            self.write_paragraph(
                "<b>"+_("By")+":</b> " + ack['username'], 'Normal')
            self.story.append(Spacer(1, 12))

    def write_host_information(self, part, _):
        """Write host information which attached to problem"""
        self.write_paragraph(
            part+". "+_("Hosts"), 'Heading1Set')
        for host_id in self.host_ids:
            host_info = self.api.get_host_info(host_id)[0]
            index = self.host_ids.index(host_id)+1
            self.write_paragraph(
                '<a name="HOST_'+host_id+'"/>'+part+'.'+str(index) + " "+host_info['name'], 'Heading2Set')
            self.write_paragraph(
                "<b>"+_("Status")+":</b> "+self.convert_general_status_to_text(host_info['status'], _), 'Normal')
            self.write_paragraph(
                "<b>"+_("Availability")+":</b> "+self.convert_availability_to_text(host_info['interfaces'][0]['available'], _), 'Normal')
            if type(host_info['inventory']) != list and host_info['inventory']['location_lat'] != "" and host_info['inventory']['location_lon'] != "":
                self.write_paragraph(
                    "<b>"+_("Latitude")+":</b> "+host_info['inventory']['location_lat']+" <b>"+_("Longitude")+":</b> " + host_info['inventory']['location_lon'], 'Normal')

            self.write_table_tag(host_info['tags'], _)
            self.write_item_information(host_info['items'], index, part, _)

    def write_item_information(self, items, index, part, _):
        """Write item information which attached to host"""
        for item in items:
            item_index = items.index(item)+1
            items_info = self.api.get_item_info(item['itemid'])
            item_info = items_info[0]
            self.write_paragraph(
                '<a name="ITEM_'+item_info['itemid']+'"/>'+part+'.'+str(index)+"."+str(item_index)+" "+_("Item")+" - "+item_info['name'], 'Heading3Set')
            self.write_paragraph(
                "<b>"+_("Status")+":</b> "+self.convert_general_status_to_text(item_info['status'], _), 'Normal')
            self.write_paragraph(
                "<b>"+_("Last value")+":</b> " + item_info['lastvalue'], 'Normal')
            self.write_paragraph(
                "<b>"+_("Last check")+"</b> " + self.convert_datetime_to_text(item_info['lastclock']), 'Normal')
            self.story.append(Spacer(1, 12))
            self.write_table_tag(item_info['tags'], _)
            if item_info["value_type"] == "0" or item_info["value_type"] == "3":
                data = self.api.get_list_history_item(
                    item_info['itemid'], item_info['value_type'])
                name_file = get_image_data(
                    data=data, list_item=items_info, LANG="en")
                im = Image(name_file, 8*inch, 4*inch)
                self.story.append(im)

    def write_trigger_information(self, part, _):
        """Write trigger information which attached to problem"""
        self.write_paragraph(
            part+". "+_("Triggers"), 'Heading1Set')
        for trigger in self.trigger_ids:
            index = self.trigger_ids.index(trigger)+1
            trigger_info = self.api.get_trigger_info(trigger)[0]
            self.write_paragraph(
                '<a name="TRIGGER_'+trigger+'"/>'+part+'.'+str(index) + " "+trigger_info['description'], 'Heading2Set')
            self.write_paragraph(
                "<b>"+_("Status")+":</b> "+self.convert_general_status_to_text(trigger_info['status'], _), 'Normal')
            self.write_paragraph(
                "<b>"+_("Expression")+":</b> " + trigger_info['expression'], 'Normal')
            self.write_paragraph(
                "<b>"+_("Severity")+":</b> "+self.convert_severity_to_text(trigger_info['priority'], _), 'Normal')
            self.write_paragraph(
                "<b>"+_("Value")+":</b> "+self.convert_value_to_text(trigger_info['value'], _)+" since "+get_time(trigger_info['lastchange']), 'Normal')
            self.write_paragraph(
                '<b>'+_("Host")+':</b> <a href="#HOST_'+str(trigger_info['hosts'][0]['hostid'])+'" color="blue">' + trigger_info['hosts'][0]['name']+"</a>", 'Normal')
            self.write_paragraph(
                '<b>'+_("Item")+':</b> <a href="#ITEM_'+str(trigger_info['items'][0]['itemid'])+'" color="blue">' + trigger_info['items'][0]['name']+"</a>", 'Normal')
            self.story.append(Spacer(1, 12))
            self.write_table_tag(trigger_info['tags'], _)

    def create_report(self, LANG):
        """Create report for a specific service"""
        lang_translations = gettext.translation(
            'reportService', localedir='locales', languages=[LANG])
        lang_translations.install()
        _ = lang_translations.gettext
        name_file = "./documents/%s.pdf" % (
            self.information_service['name'])
        doc = SimpleDocTemplate(name_file,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        self.write_paragraph(
            _("Service")+" : "+self.information_service['name'], 'TitleSet')
        self.write_general_information("1", _)
        self.write_parents_information("2", _)
        self.write_children_information("3", _)
        self.write_problems_information("4", _)
        self.write_host_information("5", _)
        self.write_trigger_information("6", _)
        doc.build(self.story)
        return name_file

    def convert_algorithm_to_text(self, algorithm, _):
        """Convert algorithm value of service into text"""
        switcher = {
            "0": _('set status to OK'),
            "1": _('most critical if all children have problems'),
            "2": _('most critical of child services')
        }
        return switcher.get(algorithm, "invalid algorithm")

    def convert_general_status_to_text(self, status_host, _):
        """Convert general status of object into text"""
        switcher = {
            "0": _('enabled'),
            "1": _('disabled')
        }
        return switcher.get(status_host, "invalid status_host")

    def convert_availability_to_text(self, availability, _):
        """Convert availability value of host into text"""
        switcher = {
            "0": "<font textColor='#7c7d80'>"+_("Unknown")+"</font>",
            "1": "<font textColor='green'>"+_("Available")+"</font>",
            "2": "<font textColor='red'>"+_("Not available")+"</font>"
        }
        return switcher.get(availability, "invalid status")

    def convert_operator_to_text(self, operator, _):
        """Convert operator for tags problem into text"""
        switcher = {
            "0": _('equals'),
            "2": _('like')
        }
        return switcher.get(operator, "invalid operator")

    def convert_severity_to_text(self, status, _):
        """Convert status of items into text"""
        switcher = {
            "-1": "<font textColor='green'>"+_("OK")+"</font>",
            "0": "<font textColor='#7c7d80'>"+_("Not classified")+"</font>",
            "1": "<font textColor='blue'>"+_("Information")+"</font>",
            "2": "<font textColor='#f7b80c'>"+_("Warning")+"</font>",
            "3": "<font textColor='#f7910c'>"+_("Average")+"</font>",
            "4": "<font textColor='#f76e0c'>"+_("High")+"</font>",
            "5": "<font textColor='red'>"+_("Disaster")+"</font>",
        }
        return switcher.get(status, "invalid status")

    def convert_acknowledge_to_text(self, acknwoledge, _):
        """Convert acknowledge value into text"""
        switcher = {
            "0": _('NO'),
            "1": _('YES')
        }
        return switcher.get(acknwoledge, "invalid acknwoledge")

    def convert_datetime_to_text(self, created_at):
        """Convert timestamp value into text"""
        date = datetime.fromtimestamp(
            int(created_at))
        text = date.strftime("%Y-%m-%d %H:%M:%S")
        return text

    def convert_value_to_text(self, value, _):
        """Convert value of problem into text"""
        switcher = {
            "0": "<font textColor='green'>"+_("OK")+"</font>",
            "1": "<font textColor='red'>"+_("PROBLEM")+"</font>"
        }
        return switcher.get(value, "invalid value")

    def write_table_tag(self, tags, _):
        """Write tags values for object"""
        self.write_paragraph(
            "<b>Tags:</b> ", 'Normal')
        self.story.append(Spacer(1, 12))
        data_tag = [[_('Name'), _('Value')]]
        for tag in tags:
            tag_val = []
            tag_val.append(tag['tag'])
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
        self.story.append(Spacer(1, 12))