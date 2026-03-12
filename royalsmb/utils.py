import frappe


@frappe.whitelist()
def update_price(doc, mehtod=None):
    # Get the item to check if it's a template
    item = frappe.get_doc("Item", doc.item_code)
    
    # List to store all item codes that need price updates (including variants)
    items_to_update = []
    
    # If this is a template item, get all its variants (but not the template itself)
    if item.has_variants:
        variants = frappe.get_all("Item", filters={"variant_of": doc.item_code}, fields=["name"])
        items_to_update.extend([variant.name for variant in variants])
    else:
        # If not a template, update only the item itself
        items_to_update = [doc.item_code]
    
    # Update buying price for all items (variants only for templates)
    if doc.buying_price:
        for item_code in items_to_update:
            if frappe.db.exists("Item Price", {"item_code": item_code, "price_list": "Standard Buying"}):
                frappe.db.set_value("Item Price", {"item_code": item_code, "price_list": "Standard Buying"}, "price_list_rate", doc.buying_price)
                frappe.db.commit()
            else:
                price_doc = frappe.new_doc("Item Price")
                price_doc.item_code = item_code
                price_doc.price_list = "Standard Buying"
                price_doc.price_list_rate = doc.buying_price
                price_doc.save()
                frappe.db.commit()
    
    # Update selling price for all items (variants only for templates)
    if doc.selling_price:
        for item_code in items_to_update:
            if frappe.db.exists("Item Price", {"item_code": item_code, "price_list": "Standard Selling"}):
                frappe.db.set_value("Item Price", {"item_code": item_code, "price_list": "Standard Selling"}, "price_list_rate", doc.selling_price)
                frappe.db.commit()
            else:
                price_doc = frappe.new_doc("Item Price")
                price_doc.item_code = item_code
                price_doc.price_list = "Standard Selling"
                price_doc.price_list_rate = doc.selling_price
                price_doc.save()
                frappe.db.commit()