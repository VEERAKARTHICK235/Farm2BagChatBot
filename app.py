from flask import Flask, request, jsonify, render_template, session
import requests, os, csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAwRv53sBqgQuzK8GSjvcZ6UYZT3EcJKfA")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# Load products from CSV
products_data = []
with open("cleaned_products.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        products_data.append({
            "Product Name": row.get("Product Name", ""),
            "Price": row.get("Price", ""),
            "Stock": row.get("Stock", ""),
            "Link": row.get("Link", "#"),
            "Image Link": row.get("Image Link", "")  # Load image link
        })

def get_product_info(product_name):
    product_name = product_name.lower()
    for product in products_data:
        if product_name in product["Product Name"].lower():
            return {
                "product": product["Product Name"],
                "price": product["Price"],
                "stock": product["Stock"],
                "link": product["Link"],
                "image": product.get("Image Link", "")
            }
    return None

def check_order_query(user_message):
    order_keywords = ["where is my order", "track my order", "order status"]
    return any(keyword in user_message.lower() for keyword in order_keywords)

def get_gemini_response(user_input):
    try:
        headers = {"Content-Type": "application/json"}
        data = { "contents": [{ "parts": [{ "text": user_input }] }] }
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I'm facing some technical issues. Please try again later."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_product', methods=['GET'])
def get_product():
    user_message = request.args.get("product")
    if not user_message:
        return jsonify({"error": "No product name provided."})

    if check_order_query(user_message):
        tracking_link = "https://www.google.com/maps?q=your-order-location"
        return jsonify({"message": f"Track your order here: <a href='{tracking_link}' target='_blank'>Order Tracking</a>"})

    if "buy now" in user_message.lower():
        return buy_now(user_message)
    elif "add to cart" in user_message.lower():
        return add_to_cart(user_message)
    elif "view cart" in user_message.lower():
        return view_cart()
    elif "clear cart" in user_message.lower():
        session["cart"] = []
        return jsonify({"message": "Your cart has been cleared."})
    elif "place order" in user_message.lower():
        return place_order()

    product = get_product_info(user_message)
    if product:
        return jsonify(product)
    else:
        ai_reply = get_gemini_response(user_message)
        return jsonify({"message": ai_reply})

def buy_now(message):
    name = message.replace("buy now", "").strip()
    product = get_product_info(name)
    if not product:
        return jsonify({"message": f"❌ Product '{name}' not found."})
    return jsonify({
        "message": f"🛍️ You chose to buy <strong>{product['product']}</strong> for ₹{product['price']}!<br>👉 <a href='{product['link']}' target='_blank'>Click here to Pay Now</a>",
        "link": product["link"]
    })

def add_to_cart(message):
    name = message.replace("add to cart", "").strip()
    product = get_product_info(name)
    if not product:
        return jsonify({"message": f"Product '{name}' not found."})
    cart = session.get("cart", [])
    cart.append(product)
    session["cart"] = cart
    return jsonify({"message": f"✅ {product['product']} added to your cart."})

def view_cart():
    cart = session.get("cart", [])
    if not cart:
        return jsonify({"message": "🛒 Your cart is empty."})
    cart_msg = "🛍️ Your cart contains:<br>"
    for item in cart:
        cart_msg += f"- {item['product']} (₹{item['price']})<br>"
    return jsonify({"message": cart_msg})

def place_order():
    cart = session.get("cart", [])
    if not cart:
        return jsonify({"message": "🛒 Your cart is empty. Please add items before placing an order."})
    session["cart"] = []
    return jsonify({"message": "🎉 Your order has been placed! You will receive a confirmation soon."})

if __name__ == '__main__':
    app.run(debug=True)
