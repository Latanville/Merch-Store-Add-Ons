import pandas as pd
from tkinter import Tk, Label, Button, filedialog, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from collections import defaultdict
import os

from PyPDF2 import PdfMerger
import pretty_errors


def combine_pdfs(pdf_list, output_filename):
    try:
        merger = PdfMerger()

        for pdf in pdf_list:
            merger.append(pdf)

        with open(output_filename, 'wb') as output_file:
            merger.write(output_file)

        print(f"Combined PDF saved as {output_filename}")
        return True
    except Exception as e:
        print(f"Failed to combine PDFs: {e}")
        return False
        

def load_csv_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if file_path:
        return file_path
    else:
        messagebox.showerror("Error", "No file selected")
        return None

def group_orders(file_path):
    try:
        orders_df = pd.read_csv(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV file: {e}")
        return None
    orders_grouped = defaultdict(list)
    for _, row in orders_df.iterrows():
        order_id = row['ORDER FRIENDLY ID']
        orders_grouped[order_id].append(row)
    return orders_grouped

def create_receipt_pdf(orders_grouped, output_file):
    try:
        
        # Create a new canvas
        c = canvas.Canvas(output_file, pagesize=letter)
        width, height = letter
        half_height = height / 2
        column_widths = [3.5 * inch, 1.5 * inch, 1.5 * inch]
        
        # For each order
        for idx, (order_id, order_details) in enumerate(orders_grouped.items()):

            # If is not first order
            #if idx % 2 == 0 and idx > 0:
            # If is not the first order
            if idx > 0:
                # Iterate to the next page
                c.showPage()

            # GEt the y position of the start of the text
            y_position = height - inch
            #if idx % 2 == 0:
            #    y_position = height - inch
            #else:
            #    y_position = half_height - inch

            # Size and position the logo
            orig_image_width = 2000
            orig_image_height = 689
            
            #y = height / 2.0
            logo_width = .1 * orig_image_width
            logo_height = .1 * orig_image_height
            
            x = (width / 2.0) - (0.5 * logo_width)
            y = logo_height * 0.5

            # Draw logo 
            # Make sure "Your_Logo.png" is the name of the PNG file with your preferred logo
            c.drawImage('Your_Logo.png', x, y_position, width=logo_width, height=logo_height, mask ='auto')
            # Move cursor down
            y_position -= 0.15 * inch
            # Words you might want to appear under your logo. I like the website name personally
            website = "www.yawebsitehere.com" 
            # feel free to adjust this font
            c.setFont("Courier-Bold", 14)
            text_width = c.stringWidth(website, "Courier-Bold", 14)
            x_position = (width - text_width) / 2
            c.drawString(x_position, y_position + 5, website)
            # Move cursor down
            y_position -= 0.05 * inch
            # Add a line under the image... I just think its neat! 
            c.line(50, y_position, width-50, y_position+2)
            # Move cursor down
            y_position -= 0.5 * inch
            
            # Header
            c.setFont("Courier-Bold", 14)
            c.drawString(inch, y_position, f"Order ID: {order_id}")
            # Move cursor down
            y_position -= 0.5 * inch

            # Customer Information. This will be ripped from the CSV file fourthwall provides. 
            customer_name = order_details[0]['SHIPPING NAME']
            shipping_address_1 = order_details[0]['SHIPPING ADDRESS 1']
            shipping_address_2 = order_details[0]['SHIPPING ADDRESS 2'] if pd.notna(order_details[0]['SHIPPING ADDRESS 2']) else ''
            shipping_city = order_details[0]['SHIPPING CITY']
            shipping_state = order_details[0]['SHIPPING STATE']
            shipping_postal_code = order_details[0]['SHIPPING POSTAL CODE']
            shipping_country = order_details[0]['SHIPPING COUNTRY']

            c.setFont("Courier-Bold", 12)
            c.drawString(inch, y_position, f"Customer Name: {customer_name}")
            y_position -= 0.3 * inch
            c.drawString(inch, y_position, f"Address: {shipping_address_1} {shipping_address_2}")
            y_position -= 0.3 * inch
            c.drawString(inch, y_position, f"{shipping_city}, {shipping_state}, {shipping_postal_code}, {shipping_country}")
            y_position -= 0.5 * inch

            # Ordered Items Table Header
            c.setFont("Courier-Bold", 12)
            c.drawString(inch, y_position, "Sticker")
            #c.drawString(inch + column_widths[0], y_position, "Size")
            c.drawString(inch + column_widths[0] + column_widths[1], y_position, "Quantity")
            y_position -= 0.3 * inch

            # Ordered Items Table Rows
            c.setFont("Courier", 12)
            for item in order_details:
                item_name = str(item['ITEM NAME']) if pd.notna(item['ITEM NAME']) else ''
                item_quantity = str(item['QUANTITY']) if pd.notna(item['QUANTITY']) else ''
                #item_size = str(item['SIZE']) if pd.notna(item['SIZE']) else ''

                c.drawString(inch, y_position, item_name)
                #c.drawString(inch + column_widths[0], y_position, item_size)
                c.drawString(inch + column_widths[0] + column_widths[1], y_position, item_quantity)
                y_position -= 0.3 * inch

            y_position -= 0.5 * inch

        c.save()

        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create PDF: {e}")
        return False

def generate_receipts():
    file_path = load_csv_file()
    if file_path:
        orders_grouped = group_orders(file_path)
        if orders_grouped:
            output_file = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if output_file:
                success = create_receipt_pdf(orders_grouped, output_file)
                if success:
                    if os.path.exists(output_file):
                        messagebox.showinfo("Success", f"Receipts generated and saved to {output_file}")
                    else:
                        messagebox.showerror("Error", "PDF file was not saved. Please check the file path and permissions.")
                else:
                    messagebox.showerror("Error", "Failed to create PDF. Please check the log for details.")



# Setup the GUI
root = Tk()
root.title("Receipt Generator")

label = Label(root, text="Click the button to load a CSV file and generate receipts.")
label.pack(pady=20)

generate_button = Button(root, text="Generate Receipts", command=generate_receipts)
generate_button.pack(pady=20)

root.mainloop()
