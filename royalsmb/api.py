import frappe
from frappe import _

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
    web_settings.banner_image = "https://www.royalsmb.com/files/royalsmb%20logo02dbe2.png"
    web_settings.splash_image = "https://www.royalsmb.com/files/royalsmb%20logo02dbe2.png"
    web_settings.favicon = "https://www.royalsmb.com/files/royalsmb%20logo02dbe2.png"
    web_settings.footer_logo = "https://www.royalsmb.com/files/royalsmb%20logo02dbe2.png"
    web_settings.footer_powered = "Royalsmb"
    web_settings.hide_footer_signup = 1
    web_settings.app_name = "Royalsmb"
    web_settings.app_logo = "https://www.royalsmb.com/files/royalsmb%20logo02dbe2.png"
    web_settings.save()
    
    #navbar settings
    navbar = frappe.get_doc("Navbar Settings")
    navbar.app_logo = "https://www.royalsmb.com/files/royalsmb logo image.png"
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

    
    
