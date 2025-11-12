"""
ETERNO E-Commerce Platform - Excel Export Utility
Exports database records to Excel file
"""
import pandas as pd
from app.models import User, Product, Sale, Order
from app.utils.helpers import format_datetime_sg

def export_to_excel():
    """
    Export all database records to Excel file with separate sheets
    Creates eterno_data.xlsx with Users, Products, POS_Sales, and Customer_Orders sheets
    """
    try:
        # Export Users
        users = User.query.all()
        users_data = [{
            'ID': u.id,
            'Username': u.username,
            'Email': u.email,
            'Role': u.role,
            'Created': format_datetime_sg(u.created_at)
        } for u in users]
        df_users = pd.DataFrame(users_data)
        
        # Export Products
        products = Product.query.all()
        products_data = [{
            'ID': p.id,
            'Name': p.name,
            'Description': p.description,
            'Price': p.price,
            'Stock': p.stock,
            'Category': p.category,
            'Image_URL': p.image_url,
            'Created': format_datetime_sg(p.created_at)
        } for p in products]
        df_products = pd.DataFrame(products_data)
        
        # Export POS Sales
        sales = Sale.query.all()
        sales_data = [{
            'Sale_ID': s.id,
            'User_ID': s.user_id,
            'Total_Amount': s.total_amount,
            'Payment_Method': s.payment_method,
            'Discount_Type': s.discount_type or 'None',
            'Discount_Amount': s.discount_amount,
            'Items': s.items,
            'Date': format_datetime_sg(s.created_at)
        } for s in sales]
        df_sales = pd.DataFrame(sales_data)
        
        # Export Customer Orders
        orders = Order.query.all()
        orders_data = [{
            'Order_ID': o.id,
            'User_ID': o.user_id,
            'Customer_Name': o.customer_name,
            'Customer_Email': o.customer_email,
            'Customer_Address': o.customer_address or 'N/A',
            'Subtotal': o.subtotal,
            'Shipping_Fee': o.shipping_fee,
            'Total_Amount': o.total_amount,
            'Payment_Method': o.payment_method,
            'Status': o.status,
            'Items': o.items,
            'Purchase_Date': format_datetime_sg(o.created_at)
        } for o in orders]
        df_orders = pd.DataFrame(orders_data)
        
        # Write all data to Excel with multiple sheets
        with pd.ExcelWriter('eterno_data.xlsx', engine='openpyxl') as writer:
            df_users.to_excel(writer, sheet_name='Users', index=False)
            df_products.to_excel(writer, sheet_name='Products', index=False)
            df_sales.to_excel(writer, sheet_name='POS_Sales', index=False)
            df_orders.to_excel(writer, sheet_name='Customer_Orders', index=False)
        
        return True
    
    except Exception as e:
        # Silently fail export - it's not critical for app operation
        print(f"Warning: Could not export to Excel: {e}")
        return False