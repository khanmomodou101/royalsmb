// Copyright (c) 2024, royalsmb and contributors
// For license information, please see license.txt

frappe.ui.form.on('Brodcast Message', {
	refresh: function(frm) {
		frm.trigger("load_template")
	},
	template: function(frm){
		frm.trigger("load_template")
	},
	load_template: function(frm){
		frappe.db.get_value(
			"WhatsApp Templates",
			frm.doc.template,
			["template", "header_type"],
			(r) => {
				if (r && r.template) {
					frm.set_value('header_type', r.header_type)
					frm.refresh_field("header_type")
					if (['DOCUMENT', "IMAGE"].includes(r.header_type)){
						frm.toggle_display("custom_attachment", false);
						frm.toggle_display("attach_document_print", false);
						if (!frm.doc.custom_attachment){
							frm.set_value("attach_document_print", 1)
						}
					}else{
						frm.toggle_display("custom_attachment", false);
						frm.toggle_display("attach_document_print", false);
						frm.set_value("attach_document_print", 0)
						frm.set_value("custom_attachment", 0)
					}

					frm.refresh_field("custom_attachment")

					frm.set_value("code", r.template);
					frm.refresh_field("code")
				}
			}
		)
	},
	custom_attachment: function(frm){
		if(frm.doc.custom_attachment == 1 &&  ['DOCUMENT', "IMAGE"].includes(frm.doc.header_type)){
			frm.set_df_property('file_name', 'reqd', frm.doc.custom_attachment)
		}else{
			frm.set_df_property('file_name', 'reqd', 0)
		}

		// frm.toggle_display("attach_document_print", !frm.doc.custom_attachment);
		if(frm.doc.header_type){
			frm.set_value("attach_document_print", !frm.doc.custom_attachment)
		}
	},
	attach_document_print: function(frm){
		// frm.toggle_display("custom_attachment", !frm.doc.attach_document_print);
		if(['DOCUMENT', "IMAGE"].includes(frm.doc.header_type)){
			frm.set_value("custom_attachment", !frm.doc.attach_document_print)
		}
	},
	contact_group: function(frm) {
		if(frm.doc.contact_group){
			frappe.call(
				{
					method: "royalsmb.api.get_contact_group",
					args: {
						"group": frm.doc.contact_group
					},
					callback: function(r){
						if(r.message){
							// append the contacts to the table
								
							r.message.forEach(function(contact){
								let row = frm.add_child("contacts");
								row.contact = contact.name;
								row.phone = contact.phone;
								frm.refresh_field("contacts");
							})
					}
					}
				}
			)
		}
	}
});
