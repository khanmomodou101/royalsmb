import frappe


@frappe.whitelist()
def update_price(doc, method=None):
    items_to_update = []

    if doc.has_variants:
        variants = frappe.get_all("Item", filters={"variant_of": doc.name}, pluck="name")
        items_to_update = variants
    else:
        items_to_update = [doc.name]

    buying_price = doc.buying_price
    selling_price = doc.selling_price

    # Update buying price for all items
    if buying_price:
        for item_code in items_to_update:
            # Update the custom field on variant items
            if item_code != doc.name:
                frappe.db.set_value("Item", item_code, "buying_price", buying_price, update_modified=False)

            # Update or create Item Price
            if frappe.db.exists("Item Price", {"item_code": item_code, "price_list": "Standard Buying"}):
                frappe.db.set_value("Item Price", {"item_code": item_code, "price_list": "Standard Buying"}, "price_list_rate", buying_price)
            else:
                price_doc = frappe.new_doc("Item Price")
                price_doc.item_code = item_code
                price_doc.price_list = "Standard Buying"
                price_doc.price_list_rate = buying_price
                price_doc.save(ignore_permissions=True)

    # Update selling price for all items
    if selling_price:
        for item_code in items_to_update:
            # Update the custom field on variant items
            if item_code != doc.name:
                frappe.db.set_value("Item", item_code, "selling_price", selling_price, update_modified=False)

            # Update or create Item Price
            if frappe.db.exists("Item Price", {"item_code": item_code, "price_list": "Standard Selling"}):
                frappe.db.set_value("Item Price", {"item_code": item_code, "price_list": "Standard Selling"}, "price_list_rate", selling_price)
            else:
                price_doc = frappe.new_doc("Item Price")
                price_doc.item_code = item_code
                price_doc.price_list = "Standard Selling"
                price_doc.price_list_rate = selling_price
                price_doc.save(ignore_permissions=True)

    frappe.db.commit()