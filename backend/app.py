from flask import Flask, request, jsonify, session, send_file, send_from_directory
from flask_cors import CORS
import mysql.connector
import hashlib
import webbrowser
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import time
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import calendar
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = "shopledger_secret_key_2024"
CORS(app, supports_credentials=True)

# ─── DB CONFIG ────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "G.Abishek123",
    "database": "shopledger"
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ─── EMAIL CONFIG ─────────────────────────────────────────
EMAIL_SENDER = "bunspot2@gmail.com"
EMAIL_PASSWORD = "mdqw ugue efzt nagj"
EMAIL_RECEIVER = "bunspot2@gmail.com"

def send_restock_alert(product):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "✅ ShopLedger Stock Restocked!"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    html = f"""
    <html><body style="font-family:Arial;background:#f4f4f4;padding:20px">
    <div style="background:white;padding:20px;border-radius:10px;max-width:600px;margin:auto">
    <h2 style="color:#16a34a">✅ Stock Restocked — ShopLedger</h2>
    <p>The following product has been restocked:</p>
    <table width="100%" border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse">
    <tr style="background:#16a34a;color:white"><th>Product</th><th>Current Stock</th><th>Status</th></tr>
    <tr><td>{product['name']}</td><td style="color:green;font-weight:bold">{product['stock']} units</td><td>✅ Back in Stock</td></tr>
    </table>
    <p style="color:#666;margin-top:20px"><b>— ShopLedger Auto Alert</b></p>
    </div></body></html>
    """
    msg.attach(MIMEText(html, "html"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("✅ Restock alert email sent!")
    except Exception as e:
        print(f"❌ Email error: {e}")

def send_low_stock_alert(products):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "⚠️ ShopLedger Low Stock Alert!"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    html = """
    <html><body style="font-family:Arial;background:#f4f4f4;padding:20px">
    <div style="background:white;padding:20px;border-radius:10px;max-width:600px;margin:auto">
    <h2 style="color:#ff6b00">⚠️ Low Stock Alert — ShopLedger</h2>
    <p>The following products are running low (below 10 units):</p>
    <table width="100%" border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse">
    <tr style="background:#ff6b00;color:white"><th>Product</th><th>Stock Left</th><th>Status</th></tr>
    """
    for p in products:
        html += f"<tr><td>{p['name']}</td><td style='color:red;font-weight:bold'>{p['stock']} units</td><td>⚠️ Reorder Now</td></tr>"
    html += "</table><p style='color:#666;margin-top:20px'>Please restock these items as soon as possible.<br><b>— ShopLedger Auto Alert</b></p></div></body></html>"
    msg.attach(MIMEText(html, "html"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("✅ Low stock alert email sent!")
    except Exception as e:
        print(f"❌ Email error: {e}")

def send_restock_alert(product):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "✅ ShopLedger Stock Restocked!"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    html = f"""
    <html><body style="font-family:Arial;background:#f4f4f4;padding:20px">
    <div style="background:white;padding:20px;border-radius:10px;max-width:600px;margin:auto">
    <h2 style="color:#16a34a">✅ Stock Restocked — ShopLedger</h2>
    <p>The following product has been restocked:</p>
    <table width="100%" border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse">
    <tr style="background:#16a34a;color:white"><th>Product</th><th>Current Stock</th><th>Status</th></tr>
    <tr><td>{product['name']}</td><td style="color:green;font-weight:bold">{product['stock']} units</td><td>✅ Back in Stock</td></tr>
    </table>
    <p style="color:#666;margin-top:20px"><b>— ShopLedger Auto Alert</b></p>
    </div></body></html>
    """
    msg.attach(MIMEText(html, "html"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("✅ Restock alert email sent!")
    except Exception as e:
        print(f"❌ Email error: {e}")
def send_login_summary():
    try:
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT name, quantity_remaining AS stock FROM products WHERE quantity_remaining <= 10")
        low = cursor.fetchall()
        cursor.close(); db.close()

        if not low:
            print("✅ No low stock items — login summary skipped.")
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "⚠️ ShopLedger — Low Stock Alert on Login"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        low_html = "".join([f"<tr><td>{p['name']}</td><td style='color:red;font-weight:bold'>{p['stock']} units</td><td>⚠️ Reorder Now</td></tr>" for p in low])
        html = f"""
        <html><body style="font-family:Arial;background:#f4f4f4;padding:20px">
        <div style="background:white;padding:20px;border-radius:10px;max-width:600px;margin:auto">
        <h2 style="color:#ff6b00">⚠️ Low Stock Alert — ShopLedger</h2>
        <p>Admin logged in at {datetime.now().strftime('%d %b %Y, %I:%M %p')}. The following products are running low:</p>
        <table width="100%" border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse">
        <tr style="background:#ff6b00;color:white"><th>Product</th><th>Stock Left</th><th>Status</th></tr>
        {low_html}
        </table>
        <p style="color:#666;margin-top:20px">Please restock these items as soon as possible.<br><b>— ShopLedger Auto Alert</b></p>
        </div></body></html>
        """
        msg.attach(MIMEText(html, "html"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("✅ Login low stock alert sent!")
    except Exception as e:
        print(f"❌ Login summary error: {e}")

# ─── SERVE HTML FILES ─────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'Login.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)

# ─── LOGIN ────────────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required."}), 400
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s",
            (username, hash_password(password)))
        user = cursor.fetchone()
        cursor.close(); db.close()
        if user:
            session['user'] = username
            threading.Thread(target=send_login_summary).start()
            return jsonify({"success": True, "message": "Login successful", "username": username})
        else:
            return jsonify({"success": False, "message": "Invalid username or password."}), 401
    except Exception as e:
        if username == "admin" and password == "admin1234":
            session['user'] = username
            threading.Thread(target=send_login_summary).start()
            return jsonify({"success": True, "message": "Demo login successful", "username": username})
        return jsonify({"success": False, "message": f"DB error: {str(e)}"}), 500
# ─── LOGOUT ───────────────────────────────────────────────
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"success": True, "message": "Logged out."})

# ─── CHECK SESSION ────────────────────────────────────────
@app.route('/api/session', methods=['GET'])
def check_session():
    if 'user' in session:
        return jsonify({"logged_in": True, "username": session['user']})
    return jsonify({"logged_in": False}), 401

# ─── DASHBOARD ────────────────────────────────────────────
@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    month = request.args.get('month', 6)
    year  = request.args.get('year', 2025)
    try:
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COALESCE(SUM(total_amount),0) AS v FROM purchases WHERE MONTH(purchase_date)=%s AND YEAR(purchase_date)=%s", (month, year))
        purchases = float(cursor.fetchone()['v'])
        cursor.execute("SELECT COALESCE(SUM(total_amount),0) AS v FROM sales WHERE MONTH(sale_date)=%s AND YEAR(sale_date)=%s", (month, year))
        sales = float(cursor.fetchone()['v'])
        cursor.execute("SELECT COALESCE(SUM(amount),0) AS v FROM expenses WHERE MONTH(expense_date)=%s AND YEAR(expense_date)=%s", (month, year))
        expenses = float(cursor.fetchone()['v'])
        profit = sales - purchases - expenses
        margin = round((profit/sales*100) if sales>0 else 0, 1)

        trend = []
        for i in range(5, -1, -1):
            cursor.execute("SELECT COALESCE(SUM(total_amount),0) AS v FROM sales WHERE YEAR(sale_date)*100+MONTH(sale_date) = YEAR(NOW())*100+MONTH(NOW())-%s", (i,))
            r = float(cursor.fetchone()['v'])
            cursor.execute("SELECT COALESCE(SUM(total_amount),0) AS v FROM purchases WHERE YEAR(purchase_date)*100+MONTH(purchase_date) = YEAR(NOW())*100+MONTH(NOW())-%s", (i,))
            c = float(cursor.fetchone()['v'])
            cursor.execute("SELECT COALESCE(SUM(amount),0) AS v FROM expenses WHERE YEAR(expense_date)*100+MONTH(expense_date) = YEAR(NOW())*100+MONTH(NOW())-%s", (i,))
            e = float(cursor.fetchone()['v'])
            trend.append({"label": f"M-{i}" if i>0 else "Now", "revenue": r, "cost": c, "expenses": e, "profit": r-c-e})

        cursor.execute("""
            SELECT p.name, SUM(s.quantity) AS qty_sold, SUM(s.total_amount) AS revenue
            FROM sales s JOIN products p ON s.product_id=p.id
            WHERE MONTH(s.sale_date)=%s AND YEAR(s.sale_date)=%s
            GROUP BY p.id ORDER BY revenue DESC LIMIT 5
        """, (month, year))
        top = cursor.fetchall()

        cursor.execute("""
            SELECT category, SUM(amount) AS total FROM expenses
            WHERE MONTH(expense_date)=%s AND YEAR(expense_date)=%s
            GROUP BY category
        """, (month, year))
        exp_breakdown = cursor.fetchall()

        cursor.close(); db.close()
        return jsonify({
            "kpi": {"stock_cost": purchases, "total_revenue": sales, "op_expenses": expenses, "net_profit": profit, "profit_margin": margin},
            "trend": trend,
            "top_products": [{"name": r['name'], "qty_sold": float(r['qty_sold']), "revenue": float(r['revenue'])} for r in top],
            "exp_breakdown": [{"category": r['category'], "total": float(r['total'])} for r in exp_breakdown]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── PRODUCTS ─────────────────────────────────────────────
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products ORDER BY name")
        products = cursor.fetchall()
        cursor.close(); db.close()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()
    try:
        db = get_db(); cursor = db.cursor()
        cursor.execute("SELECT id FROM products WHERE name=%s", (data['name'],))
        if cursor.fetchone():
            cursor.close(); db.close()
            return jsonify({"error": "Product '" + data['name'] + "' already exists!"}), 400
        cursor.execute(
            "INSERT INTO products (name, category, unit) VALUES (%s,%s,%s)",
            (data['name'], data.get('category',''), data.get('unit','pcs'))
        )
        db.commit(); cursor.close(); db.close()
        return jsonify({"success": True, "message": "Product added."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    try:
        db = get_db(); cursor = db.cursor()
        cursor.execute("DELETE FROM purchases WHERE product_id=%s", (pid,))
        cursor.execute("DELETE FROM sales WHERE product_id=%s", (pid,))
        cursor.execute("DELETE FROM products WHERE id=%s", (pid,))
        db.commit(); cursor.close(); db.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── INVENTORY ────────────────────────────────────────────
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    try:
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.id, p.name, p.category, p.unit,
                COALESCE(SUM(pu.quantity),0) AS total_purchased,
                COALESCE(SUM(pu.total_amount),0) AS total_cost,
                COALESCE((SELECT SUM(s.quantity) FROM sales s WHERE s.product_id=p.id),0) AS total_sold,
                COALESCE((SELECT SUM(s.total_amount) FROM sales s WHERE s.product_id=p.id),0) AS total_revenue,
                p.quantity_remaining AS remaining_stock
            FROM products p
            LEFT JOIN purchases pu ON pu.product_id = p.id
            GROUP BY p.id
        """)
        rows = cursor.fetchall()
        cursor.close(); db.close()
        for r in rows:
            r['gross_profit'] = float(r['total_revenue']) - float(r['total_cost'])
            r['total_purchased'] = float(r['total_purchased'])
            r['total_sold'] = float(r['total_sold'])
            r['total_cost'] = float(r['total_cost'])
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── PURCHASES ────────────────────────────────────────────
@app.route('/api/purchases', methods=['GET'])
def get_purchases():
    month = request.args.get('month', 6)
    year  = request.args.get('year', 2025)
    try:
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, pr.name AS product_name
            FROM purchases p
            LEFT JOIN products pr ON p.product_id = pr.id
            WHERE MONTH(p.purchase_date)=%s AND YEAR(p.purchase_date)=%s
            ORDER BY p.purchase_date DESC
        """, (month, year))
        rows = cursor.fetchall()
        cursor.close(); db.close()
        for r in rows:
            if r.get('purchase_date'): r['purchase_date'] = str(r['purchase_date'])
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/purchases', methods=['POST'])
def add_purchase():
    data = request.get_json()
    try:
        db = get_db(); cursor = db.cursor()
        qty = float(data['quantity'])
        cpu = float(data['cost_per_unit'])
        total = qty * cpu

        cursor.execute("SELECT id FROM purchases WHERE product_id=%s AND DATE(purchase_date)=DATE(%s)", (data['product_id'], data['purchase_date']))
        if cursor.fetchone():
            cursor.close(); db.close()
            return jsonify({"error": "Purchase for this product already recorded on this date!"}), 400

        cursor.execute("""
            INSERT INTO purchases (product_id, quantity, cost_per_unit, total_amount, purchase_date, notes)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (data['product_id'], qty, cpu, total, data['purchase_date'], data.get('notes','')))
        cursor.execute("UPDATE products SET quantity_remaining = quantity_remaining + %s WHERE id = %s", (qty, data['product_id']))
        db.commit()

        # Check if restocked above 10 — send update email
        cursor2 = db.cursor(dictionary=True)
        cursor2.execute("SELECT name, quantity_remaining AS stock FROM products WHERE id=%s", (data['product_id'],))
        updated = cursor2.fetchone()
        cursor2.close()
        cursor.close(); db.close()

        if updated and updated['stock'] > 10:
            threading.Thread(target=send_restock_alert, args=(updated,)).start()

        return jsonify({"success": True, "message": "Purchase recorded."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/purchases/<int:pid>', methods=['DELETE'])
def delete_purchase(pid):
    try:
        db = get_db(); cursor = db.cursor()
        cursor.execute("DELETE FROM purchases WHERE id=%s", (pid,))
        db.commit(); cursor.close(); db.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── SALES ────────────────────────────────────────────────
@app.route('/api/sales', methods=['GET'])
def get_sales():
    month = request.args.get('month', 6)
    year  = request.args.get('year', 2025)
    try:
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, pr.name AS product_name
            FROM sales s
            LEFT JOIN products pr ON s.product_id = pr.id
            WHERE MONTH(s.sale_date)=%s AND YEAR(s.sale_date)=%s
            ORDER BY s.sale_date DESC
        """, (month, year))
        rows = cursor.fetchall()
        cursor.close(); db.close()
        for r in rows:
            if r.get('sale_date'): r['sale_date'] = str(r['sale_date'])
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sales', methods=['POST'])
def add_sale():
    data = request.get_json()
    try:
        db = get_db(); cursor = db.cursor()
        qty = float(data['quantity'])
        spu = float(data['sell_price_per_unit'])
        total = qty * spu

        # Check sufficient stock
        cursor.execute("SELECT quantity_remaining FROM products WHERE id=%s", (data['product_id'],))
        product = cursor.fetchone()
        if not product or float(product[0]) < qty:
            cursor.close(); db.close()
            return jsonify({"error": "Not enough stock! Only " + str(product[0]) + " units available."}), 400

        # Check duplicate
        cursor.execute("SELECT id FROM sales WHERE product_id=%s AND DATE(sale_date)=DATE(%s)", (data['product_id'], data['sale_date']))
        if cursor.fetchone():
            cursor.close(); db.close()
            return jsonify({"error": "Sale for this product already recorded on this date!"}), 400

        # Save sale
        cursor.execute("""
            INSERT INTO sales (product_id, quantity, sell_price_per_unit, total_amount, sale_date, notes)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (data['product_id'], qty, spu, total, data['sale_date'], data.get('notes','')))
        cursor.execute("UPDATE products SET quantity_remaining = quantity_remaining - %s WHERE id = %s", (qty, data['product_id']))
        db.commit()

        # Auto low stock check — send email if any product <= 10
        cursor2 = db.cursor(dictionary=True)
        cursor2.execute("SELECT name, quantity_remaining AS stock FROM products WHERE quantity_remaining <= 10")
        low_stock_products = cursor2.fetchall()
        cursor2.close()
        cursor.close(); db.close()

        if low_stock_products:
            threading.Thread(target=send_low_stock_alert, args=(low_stock_products,)).start()

        return jsonify({"success": True, "message": "Sale recorded."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sales/<int:sid>', methods=['DELETE'])
def delete_sale(sid):
    try:
        db = get_db(); cursor = db.cursor()
        cursor.execute("DELETE FROM sales WHERE id=%s", (sid,))
        db.commit(); cursor.close(); db.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── EXPENSES ─────────────────────────────────────────────
@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    month = request.args.get('month', 6)
    year  = request.args.get('year', 2025)
    try:
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM expenses
            WHERE MONTH(expense_date)=%s AND YEAR(expense_date)=%s
            ORDER BY expense_date DESC
        """, (month, year))
        rows = cursor.fetchall()
        cursor.close(); db.close()
        for r in rows:
            if r.get('expense_date'): r['expense_date'] = str(r['expense_date'])
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.get_json()
    try:
        db = get_db(); cursor = db.cursor()
        cursor.execute(
            "INSERT INTO expenses (category, description, amount, expense_date) VALUES (%s,%s,%s,%s)",
            (data['category'], data.get('description',''), data['amount'], data['expense_date'])
        )
        db.commit(); cursor.close(); db.close()
        return jsonify({"success": True, "message": "Expense added."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expenses/<int:eid>', methods=['DELETE'])
def delete_expense(eid):
    try:
        db = get_db(); cursor = db.cursor()
        cursor.execute("DELETE FROM expenses WHERE id=%s", (eid,))
        db.commit(); cursor.close(); db.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── ANALYTICS ────────────────────────────────────────────
@app.route('/api/analytics/low-stock', methods=['GET'])
def low_stock():
    try:
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT name, category, unit, quantity_remaining AS remaining_stock FROM products WHERE quantity_remaining <= 10")
        rows = cursor.fetchall()
        cursor.close(); db.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/profit-trend', methods=['GET'])
def profit_trend():
    try:
        db = get_db(); cursor = db.cursor(dictionary=True)
        results = []
        for i in range(11, -1, -1):
            cursor.execute("SELECT COALESCE(SUM(total_amount),0) AS v FROM sales WHERE YEAR(sale_date)*100+MONTH(sale_date) = YEAR(NOW())*100+MONTH(NOW())-%s", (i,))
            rev = float(cursor.fetchone()['v'])
            cursor.execute("SELECT COALESCE(SUM(total_amount),0) AS v FROM purchases WHERE YEAR(purchase_date)*100+MONTH(purchase_date) = YEAR(NOW())*100+MONTH(NOW())-%s", (i,))
            cost = float(cursor.fetchone()['v'])
            cursor.execute("SELECT COALESCE(SUM(amount),0) AS v FROM expenses WHERE YEAR(expense_date)*100+MONTH(expense_date) = YEAR(NOW())*100+MONTH(NOW())-%s", (i,))
            exp = float(cursor.fetchone()['v'])
            profit = rev - cost - exp
            results.append({"label": f"M-{i}" if i>0 else "Now", "revenue": rev, "cost": cost, "expenses": exp, "profit": profit, "rolling_avg": 0, "profit_margin": round((profit/rev*100) if rev>0 else 0, 1)})
        cursor.close(); db.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/product-performance', methods=['GET'])
def product_performance():
    try:
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.name, p.unit,
                COALESCE(SUM(pu.quantity),0) AS total_purchased,
                COALESCE((SELECT SUM(s.quantity) FROM sales s WHERE s.product_id=p.id),0) AS total_sold,
                p.quantity_remaining AS remaining_stock,
                COALESCE(SUM(pu.total_amount),0) AS total_cost,
                COALESCE((SELECT SUM(s.total_amount) FROM sales s WHERE s.product_id=p.id),0) AS total_revenue
            FROM products p LEFT JOIN purchases pu ON pu.product_id=p.id
            GROUP BY p.id
        """)
        rows = cursor.fetchall()
        cursor.close(); db.close()
        for r in rows:
            tp = float(r['total_purchased']); ts = float(r['total_sold'])
            tc = float(r['total_cost']);      tr = float(r['total_revenue'])
            r['total_purchased'] = tp; r['total_sold'] = ts
            r['gross_profit'] = tr - tc
            r['sell_through_rate'] = round((ts/tp*100) if tp>0 else 0, 1)
            r['roi_percent'] = round(((tr-tc)/tc*100) if tc>0 else 0, 1)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── LOW STOCK BACKGROUND CHECKER ────────────────────────
def check_low_stock():
    while True:
        time.sleep(3600)
# ─── SEND LOW STOCK ALERT MANUALLY ───────────────────────
@app.route('/api/send-low-stock-alert', methods=['POST'])
def send_alert():
    try:
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT name, quantity_remaining FROM products WHERE quantity_remaining < 10")
        rows = cursor.fetchall()
        cursor.close(); db.close()
        if not rows:
            return jsonify({"success": False, "message": "No low stock items found."})
        send_low_stock_alert([{"name": r["name"], "stock": r["quantity_remaining"]} for r in rows])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── PDF EXPORT ───────────────────────────────────────────
@app.route('/api/export-pdf')
def export_pdf():
    month = request.args.get('month')
    year  = request.args.get('year')
    if not month:
        return jsonify({'error': 'Month is required'}), 400
    try:
        if year and '-' not in str(month):
            mon = int(month)
            year = int(year)
        else:
            year, mon = map(int, month.split('-'))
        month_name = calendar.month_name[mon]
        start_date = f"{year}-{mon:02d}-01"
        last_day = calendar.monthrange(year, mon)[1]
        end_date = f"{year}-{mon:02d}-{last_day}"

        conn = get_db(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COALESCE(SUM(total_amount),0) AS total FROM sales WHERE DATE(sale_date) BETWEEN %s AND %s", (start_date, end_date))
        total_sales = float(cursor.fetchone()['total'])
        cursor.execute("SELECT COALESCE(SUM(total_amount),0) AS total FROM purchases WHERE DATE(purchase_date) BETWEEN %s AND %s", (start_date, end_date))
        total_purchases = float(cursor.fetchone()['total'])
        cursor.execute("SELECT COALESCE(SUM(amount),0) AS total FROM expenses WHERE DATE(expense_date) BETWEEN %s AND %s", (start_date, end_date))
        total_expenses = float(cursor.fetchone()['total'])
        net_profit = total_sales - total_purchases - total_expenses

        cursor.execute("SELECT p.name AS product, s.quantity, s.total_amount, s.sale_date FROM sales s JOIN products p ON s.product_id=p.id WHERE DATE(s.sale_date) BETWEEN %s AND %s ORDER BY s.sale_date DESC", (start_date, end_date))
        sales_rows = cursor.fetchall()
        cursor.execute("SELECT p.name AS product, pu.quantity, pu.total_amount, pu.purchase_date FROM purchases pu JOIN products p ON pu.product_id=p.id WHERE DATE(pu.purchase_date) BETWEEN %s AND %s ORDER BY pu.purchase_date DESC", (start_date, end_date))
        purchase_rows = cursor.fetchall()
        cursor.execute("SELECT description, amount, expense_date FROM expenses WHERE DATE(expense_date) BETWEEN %s AND %s ORDER BY expense_date DESC", (start_date, end_date))
        expense_rows = cursor.fetchall()
        cursor.close(); conn.close()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)

        ORANGE=colors.HexColor('#ff6b35'); DARK=colors.HexColor('#1a1a2e')
        WHITE=colors.white; LIGHT_GRAY=colors.HexColor('#f8f9ff')
        GREEN=colors.HexColor('#16a34a'); RED=colors.HexColor('#dc2626')
        MID_GRAY=colors.HexColor('#888888'); ROW_ALT=colors.HexColor('#fafafa')

        style_brand   = ParagraphStyle('brand', fontSize=22, textColor=ORANGE, fontName='Helvetica-Bold', leading=26)
        style_meta    = ParagraphStyle('meta', fontSize=10, textColor=DARK, fontName='Helvetica-Bold', alignment=TA_RIGHT, leading=14)
        style_section = ParagraphStyle('section', fontSize=11, textColor=ORANGE, fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=6)
        style_kpi_label  = ParagraphStyle('kpi_label', fontSize=9, textColor=MID_GRAY, fontName='Helvetica', alignment=TA_CENTER)
        style_kpi_value  = ParagraphStyle('kpi_value', fontSize=17, textColor=DARK, fontName='Helvetica-Bold', alignment=TA_CENTER)
        style_kpi_profit = ParagraphStyle('kpi_profit', fontSize=17, textColor=GREEN, fontName='Helvetica-Bold', alignment=TA_CENTER)
        style_kpi_loss   = ParagraphStyle('kpi_loss', fontSize=17, textColor=RED, fontName='Helvetica-Bold', alignment=TA_CENTER)
        style_empty  = ParagraphStyle('empty', fontSize=10, textColor=MID_GRAY, fontName='Helvetica-Oblique', alignment=TA_CENTER)
        style_footer = ParagraphStyle('footer', fontSize=9, textColor=MID_GRAY, fontName='Helvetica', alignment=TA_CENTER)

        page_width = A4[0] - 3*cm
        elements = []

        now_str = datetime.now().strftime('%d %b %Y, %I:%M %p')
        header_data = [[Paragraph('ShopLedger', style_brand), Paragraph(f'Monthly Report — {month_name} {year}<br/><font size="9" color="#888888">Generated: {now_str}</font>', style_meta)]]
        ht = Table(header_data, colWidths=[page_width*0.5, page_width*0.5])
        ht.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
        elements.append(ht)
        elements.append(HRFlowable(width="100%", thickness=2, color=ORANGE, spaceAfter=16))

        profit_val_style = style_kpi_profit if net_profit >= 0 else style_kpi_loss
        profit_prefix = '+' if net_profit >= 0 else ''
        kpi_data = [[[Paragraph('💰 TOTAL SALES',style_kpi_label),Paragraph(f'Rs.{total_sales:,.2f}',style_kpi_value)],[Paragraph('📦 PURCHASES',style_kpi_label),Paragraph(f'Rs.{total_purchases:,.2f}',style_kpi_value)],[Paragraph('🧾 EXPENSES',style_kpi_label),Paragraph(f'Rs.{total_expenses:,.2f}',style_kpi_value)],[Paragraph('📈 NET PROFIT',style_kpi_label),Paragraph(f'{profit_prefix}Rs.{net_profit:,.2f}',profit_val_style)]]]
        col_w = page_width/4
        kt = Table(kpi_data, colWidths=[col_w]*4, rowHeights=[60])
        kt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT_GRAY),('LINEABOVE',(0,0),(2,0),2,ORANGE),('LINEABOVE',(3,0),(3,0),2,GREEN if net_profit>=0 else RED),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
        elements.append(kt)
        elements.append(Spacer(1,18))

        def build_table(headers, rows, col_widths):
            data = [headers] + (rows if rows else [[Paragraph('No records found for this month',style_empty)]+['']*(len(headers)-1)])
            t = Table(data, colWidths=col_widths)
            cmds = [('BACKGROUND',(0,0),(-1,0),DARK),('TEXTCOLOR',(0,0),(-1,0),WHITE),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,0),9),('TOPPADDING',(0,0),(-1,0),7),('BOTTOMPADDING',(0,0),(-1,0),7),('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,1),(-1,-1),9),('TOPPADDING',(0,1),(-1,-1),6),('BOTTOMPADDING',(0,1),(-1,-1),6),('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,ROW_ALT]),('LINEBELOW',(0,0),(-1,-1),0.3,colors.HexColor('#e0e0e0')),('VALIGN',(0,0),(-1,-1),'MIDDLE')]
            if not rows: cmds += [('SPAN',(0,1),(-1,1)),('ALIGN',(0,1),(-1,1),'CENTER')]
            t.setStyle(TableStyle(cmds))
            return t

        elements.append(Paragraph('🛒  Sales Transactions', style_section))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#ffe0d3'), spaceAfter=6))
        sales_data = [[str(i), r['product'], str(r['quantity']), (r['sale_date'].strftime('%d %b %Y') if hasattr(r['sale_date'],'strftime') else str(r['sale_date'])[:10]), f"Rs.{float(r['total_amount']):,.2f}"] for i,r in enumerate(sales_rows,1)]
        st = build_table(['#','Product','Qty','Date','Amount (Rs.)'], sales_data, [page_width*w for w in [0.06,0.40,0.12,0.22,0.20]])
        st.setStyle(TableStyle([('ALIGN',(4,0),(4,-1),'RIGHT'),('ALIGN',(2,0),(2,-1),'CENTER')]))
        elements.append(st); elements.append(Spacer(1,14))

        elements.append(Paragraph('📦  Purchase Transactions', style_section))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#ffe0d3'), spaceAfter=6))
        pur_data = [[str(i), r['product'], str(r['quantity']), (r['purchase_date'].strftime('%d %b %Y') if hasattr(r['purchase_date'],'strftime') else str(r['purchase_date'])[:10]), f"Rs.{float(r['total_amount']):,.2f}"] for i,r in enumerate(purchase_rows,1)]
        pt = build_table(['#','Product','Qty','Date','Cost (Rs.)'], pur_data, [page_width*w for w in [0.06,0.40,0.12,0.22,0.20]])
        pt.setStyle(TableStyle([('ALIGN',(4,0),(4,-1),'RIGHT'),('ALIGN',(2,0),(2,-1),'CENTER')]))
        elements.append(pt); elements.append(Spacer(1,14))

        elements.append(Paragraph('🧾  Expense Breakdown', style_section))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#ffe0d3'), spaceAfter=6))
        exp_data = [[str(i), r['description'] or '-', (r['expense_date'].strftime('%d %b %Y') if hasattr(r['expense_date'],'strftime') else str(r['expense_date'])[:10]), f"Rs.{float(r['amount']):,.2f}"] for i,r in enumerate(expense_rows,1)]
        et = build_table(['#','Description','Date','Amount (Rs.)'], exp_data, [page_width*w for w in [0.06,0.52,0.22,0.20]])
        et.setStyle(TableStyle([('ALIGN',(3,0),(3,-1),'RIGHT')]))
        elements.append(et); elements.append(Spacer(1,24))

        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#eeeeee'), spaceAfter=8))
        elements.append(Paragraph(f'ShopLedger — Shop Management System  |  {month_name} {year} Report  |  Confidential', style_footer))

        doc.build(elements)
        buffer.seek(0)
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f'ShopLedger_Report_{month_name}_{year}.pdf')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ─── START BACKGROUND THREAD ──────────────────────────────
threading.Thread(target=check_low_stock, daemon=True).start()

# ─── RUN ──────────────────────────────────────────────────
if __name__ == '__main__':
    try:
        chrome = webbrowser.get('C:/Program Files/Google/Chrome/Application/chrome.exe %s')
        threading.Timer(1.0, lambda: chrome.open('http://127.0.0.1:5000')).start()
    except:
        threading.Timer(1.0, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run(debug=True, use_reloader=False)