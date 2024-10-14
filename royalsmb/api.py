import frappe
from frappe import _
from frappe.integrations.utils import make_post_request, make_request

#configure the system after the app is installed
def before_install():
    create_color("black", "000000")
    create_color("white", "ffffff")

    if not frappe.db.exists("Website Theme", "Royalsmb"):
        create_theme()


    #edit the systemsettings doctype
    frappe.db.set_value("System Settings", "System Settings", "enable_onboarding", 0)
    frappe.db.commit()

    #edit the website settings doctype
    web_settings = frappe.get_doc("Website Settings")
    web_settings.disable_signup = 1
    # web_settings.website_theme = "Erpera"
    web_settings.banner_image = "https://eu2.contabostorage.com/c1174160a74e4cd5969819a60bf2fad7:royalsmb-files/royalsmb-icon.png"
    web_settings.splash_image = "https://eu2.contabostorage.com/c1174160a74e4cd5969819a60bf2fad7:royalsmb-files/royalsmb-icon.png"
    web_settings.favicon = "https://eu2.contabostorage.com/c1174160a74e4cd5969819a60bf2fad7:royalsmb-files/royalsmb-icon.png"
    web_settings.footer_logo = "https://eu2.contabostorage.com/c1174160a74e4cd5969819a60bf2fad7:royalsmb-files/royalsmb-icon.png"
    web_settings.brand_html = "<img src='https://eu2.contabostorage.com/c1174160a74e4cd5969819a60bf2fad7:royalsmb-files/royalsmb-logo.png'>"
    web_settings.footer_powered = "Royalsmb"
    web_settings.hide_footer_signup = 1
    web_settings.app_name = "Royalsmb"
    web_settings.app_logo = "https://eu2.contabostorage.com/c1174160a74e4cd5969819a60bf2fad7:royalsmb-files/royalsmb-icon.png"
    web_settings.save()
    
    #navbar settings
    navbar = frappe.get_doc("Navbar Settings")
    navbar.app_logo = "https://eu2.contabostorage.com/c1174160a74e4cd5969819a60bf2fad7:royalsmb-files/royalsmb-logo.png"
    navbar.logo_width = 200
    navbar.save()
    frappe.db.set_value("Website Settings", "Website Settings", "website_theme", "Royalsmb")
    frappe.db.commit()

    #edit the erpnext settings doctype


#create a theme for the app
def create_theme():
    #create colors
    theme = frappe.new_doc("Website Theme")
    theme.theme = "Royalsmb"
    theme.custom = 1
    
    black = frappe.get_doc("Color", "black")
    white = frappe.get_doc("Color", "white")
    theme.text_color = black.name
    theme.light_color = white.name
    theme.dark_color = black.name
    theme.primary_color = black.name
    theme.button_shadowhs = 1
    theme.button_gradients = 1
    theme.save()
    frappe.db.commit()
    return theme.name

#create color
@frappe.whitelist()
def create_color(color, hex):
    try:
        if not hex.startswith('#'):
            hex = f"#{hex}"

        cl = frappe.get_doc({
            'doctype': 'Color',
            '__newname': color,
            'color': hex
        })
        cl.insert()
        frappe.db.commit()
        # return {"status": "success", "message": f"Color {color} created successfully with hex {hex}."}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_color")
        return {"status": "error", "message": str(e)}

#edit erpnext setting and erpera titles

    
    
@frappe.whitelist()
def fetch():
    """Fetch templates from meta."""

    # get credentials
    settings = frappe.get_doc("WhatsApp Settings", "WhatsApp Settings")
    token = settings.get_password("token")
    url = settings.url
    version = settings.version
    business_id = settings.business_id

    headers = {
        "authorization": f"Bearer {token}",
        "content-type": "application/json"
    }

    try:
        response = make_request(
            "GET",
            f"{url}/{version}/{business_id}/message_templates",
            headers=headers,
        )

        for template in response['data']:
            # set flag to insert or update
            flags = 1
            if frappe.db.exists("WhatsApp Templates", template['name']):
                doc = frappe.get_doc("WhatsApp Templates", template['name'])
            else:
                flags = 0
                doc = frappe.new_doc("WhatsApp Templates")
                doc.template_name = template['name']

            doc.status = template['status']
            doc.language_code = template['language']
            doc.category = template['category']
            doc.id = template['id']

            # update components
            for component in template['components']:

                # update header
                if component['type'] == "HEADER":
                    doc.header_type = component['format']

                    # if format is text update sample text
                    if component['format'] == 'TEXT':
                        doc.header = component['text']
                # Update footer text
                elif component['type'] == 'FOOTER':
                    doc.footer = component['text']

                # update template text
                elif component['type'] == 'BODY':
                    doc.template = component['text']
                    if component.get('example'):
                        doc.sample_values = ','.join(component['example']['body_text'][0])

            # if document exists update else insert
            # used db_update and db_insert to ignore hooks
            if flags:
                doc.db_update()
            else:
                # only insert if status is approved
                if doc.status == "APPROVED":
                    doc.db_insert()
            frappe.db.commit()

        # return {"message": "Templates fetched and updated successfully"}
        # return response json
        return frappe._dict(response)
        
    except Exception as e:
        frappe.log_error(f"Error fetching WhatsApp templates: {str(e)}", "fetch_templates_error")
        res = frappe.flags.integration_request.json().get('error', {})
        error_message = res.get('error_user_msg', res.get("message", str(e)))
        frappe.throw(
            msg=error_message,
            title=res.get("error_user_title", "Error"),
        )


@frappe.whitelist()
def get_contact_group(group):
    # Using SQL to fetch only the necessary fields
    contacts = frappe.db.sql("""
        SELECT name, custom_primary_contact
        FROM `tabContact`
        WHERE custom_group = %s
    """, (group,), as_dict=True)
    
    return contacts
@frappe.whitelist()
def set_document_status(doc):
    frappe.db.set_value("WhatsApp Message", doc, "new", 0)

@frappe.whitelist()
def play_audio():
    import os
    import requests
    import playsound

    url = 'https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3?timestamp='
    downloaded_file_location = '/tmp/audiofile.wav'

    # Downloading the audio file
    r = requests.get(url)
    with open(downloaded_file_location, 'wb') as f:
        f.write(r.content)

    # Playing the audio file
    playsound.playsound(downloaded_file_location, True)

    # Removing the audio file
    os.remove(downloaded_file_location)

@frappe.whitelist()
def remove_plus_sign(doc, method=None):
    if doc.custom_primary_contact.startswith("+"):
        contact = doc.custom_primary_contact[1:len(doc.custom_primary_contact)]
        doc.custom_primary_contact = contact

@frappe.whitelist()
def send_email():
    frappe.sendmail(
        recipients="khanmomodou101@gmail.com",
        subject="Test Email",
        message=f"""
        <div>
            <b> Hello 👋, </b> 
            <br> 
            <p>Thank you for registering with Reformiqo Private Ltd! We’re thrilled to have you on board. Your account has been successfully created.</p>  
            <br> 
            <p>You can now log in to your account and start exploring our ERPNext hosting services.
            If you have any questions or need assistance, please do not hesitate to contact our support team at support@erpera.io.</p>
            <p>Welcome again, and thank you for choosing Reformiqo Private Ltd!</p>
            <p>Best regards,</p>
        </div>
        """,
        now=True
    )
    return "Email sent successfully"



@frappe.whitelist(allow_guest=True)
def contact_webhook():
    try:
        data = frappe.local.form_dict
        lead = frappe.new_doc("CRM Lead")
        lead.first_name = data.get("first_name")
        lead.last_name = data.get("last_name")
        lead.email = data.get("email")
        lead.mobile_no = data.get("mobile")
        lead.source = "Website"
        lead.custom_message = data.get("message")

        lead.insert(ignore_permissions=True)   
        frappe.db.commit()
        return data
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "contact_webhook")