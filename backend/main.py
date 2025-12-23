from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import engine, get_db, Base
from models import MenuItem, Order, OrderItem
from schemas import (
    MenuItemCreate, MenuItemResponse,
    OrderCreate, OrderResponse, OrderStatusUpdate,
    ChatMessage, ChatResponse
)
from chatbot import chatbot
from knowledge_base import knowledge_base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="🍕 AI Pizza Palace API",
    description="AI-operated restaurant chatbot and management system",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== HEALTH CHECK ====================
@app.get("/")
def read_root():
    return {
        "message": "🍕 AI Pizza Palace API is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

# ==================== MENU ENDPOINTS ====================
@app.get("/menu", response_model=List[MenuItemResponse])
def get_menu(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all menu items, optionally filtered by category."""
    query = db.query(MenuItem)
    if category:
        query = query.filter(MenuItem.category.ilike(f"%{category}%"))
    return query.all()

@app.get("/menu/{item_id}", response_model=MenuItemResponse)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific menu item by ID."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@app.post("/menu", response_model=MenuItemResponse)
def create_menu_item(item: MenuItemCreate, db: Session = Depends(get_db)):
    """Create a new menu item (Admin)."""
    db_item = MenuItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/menu/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a menu item (Admin)."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}

# ==================== ORDER ENDPOINTS ====================
@app.get("/orders", response_model=List[OrderResponse])
def get_orders(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all orders, optionally filtered by status."""
    query = db.query(Order).order_by(Order.created_at.desc())
    if status:
        query = query.filter(Order.status == status)
    return query.all()

@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order by ID."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order."""
    # Calculate total
    total = 0
    order_items_data = []
    
    for item_data in order.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {item_data.menu_item_id} not found")
        
        item_total = menu_item.price * item_data.quantity
        total += item_total
        order_items_data.append({
            "menu_item_id": item_data.menu_item_id,
            "quantity": item_data.quantity,
            "price": menu_item.price
        })
    
    # Create order
    db_order = Order(
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_address=order.customer_address,
        total_amount=total,
        status="Pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items
    for item_data in order_items_data:
        db_order_item = OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(db_order_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order

@app.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update order status."""
    valid_statuses = ["Pending", "Confirmed", "Preparing", "Ready", "Delivered", "Cancelled"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status_update.status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order

@app.delete("/orders/{order_id}")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """Cancel/delete an order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = "Cancelled"
    db.commit()
    return {"message": "Order cancelled successfully"}

# ==================== ANALYTICS ENDPOINTS ====================
@app.get("/analytics/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    """Get analytics summary for dashboard."""
    from sqlalchemy import func
    from datetime import date
    
    today = date.today()
    
    # Total orders today
    orders_today = db.query(Order).filter(
        func.date(Order.created_at) == today
    ).count()
    
    # Total revenue today
    revenue_today = db.query(func.sum(Order.total_amount)).filter(
        func.date(Order.created_at) == today,
        Order.status != "Cancelled"
    ).scalar() or 0
    
    # Pending orders
    pending_orders = db.query(Order).filter(Order.status == "Pending").count()
    
    # Orders by status
    status_counts = db.query(
        Order.status,
        func.count(Order.id)
    ).group_by(Order.status).all()
    
    # Orders by category (top categories)
    category_revenue = db.query(
        MenuItem.category,
        func.sum(OrderItem.price * OrderItem.quantity).label('revenue')
    ).join(OrderItem).group_by(MenuItem.category).all()
    
    return {
        "orders_today": orders_today,
        "revenue_today": float(revenue_today),
        "pending_orders": pending_orders,
        "status_breakdown": {status: count for status, count in status_counts},
        "category_revenue": {cat: float(rev) for cat, rev in category_revenue}
    }

# ==================== CHATBOT ENDPOINT ====================
@app.post("/chat", response_model=ChatResponse)
def chat(message: ChatMessage, db: Session = Depends(get_db)):
    """Process chatbot message and return response."""
    # Get menu items for context
    menu_items = db.query(MenuItem).all()
    menu_data = [
        {
            "id": item.id,
            "item": item.item,
            "price": item.price,
            "category": item.category,
            "description": item.description,
            "ingredients": item.ingredients
        }
        for item in menu_items
    ]
    
    # Get orders for tracking
    orders = db.query(Order).all()
    orders_data = [
        {
            "id": o.id,
            "status": o.status,
            "total_amount": o.total_amount,
            "customer_phone": o.customer_phone,
            "created_at": o.created_at.isoformat() if o.created_at else None
        }
        for o in orders
    ]
    
    # Process message
    user_id = message.user_id or "anonymous"
    result = chatbot.process_message(
        message=message.message,
        user_id=user_id,
        menu_items=menu_data,
        orders=orders_data
    )
    
    # If user confirms order, create it in the database
    if result.get("action") == "confirm_order" and result.get("data"):
        cart = result["data"].get("cart", [])
        if cart:
            # Create the order
            total = sum(item["price"] * item["quantity"] for item in cart)
            
            db_order = Order(
                customer_name=f"Chat User ({user_id})",
                customer_phone=user_id if user_id != "anonymous" else None,
                total_amount=total,
                status="Pending"
            )
            db.add(db_order)
            db.commit()
            db.refresh(db_order)
            
            # Create order items
            for item in cart:
                db_order_item = OrderItem(
                    order_id=db_order.id,
                    menu_item_id=item["menu_item_id"],
                    quantity=item["quantity"],
                    price=item["price"]
                )
                db.add(db_order_item)
            
            db.commit()
            
            # Clear the user's cart
            chatbot.user_contexts[user_id]["cart"] = []
            
            # Update response with order ID
            result["response"] = f"""
🎉 **Order #{db_order.id} Placed Successfully!**

📋 **Order Details:**
{chr(10).join([f"  • {item['item']} x{item['quantity']} - ${item['price'] * item['quantity']:.2f}" for item in cart])}

💰 **Total: ${total:.2f}**

⏳ Status: **Pending**

Your order has been sent to the kitchen! You can track it by saying "track order #{db_order.id}" or check the dashboard.

_Thank you for ordering from AI Pizza Palace! 🍕_
            """.strip()
            result["data"]["order_id"] = db_order.id
    
    return ChatResponse(**result)

@app.post("/seed")
def seed_database(db: Session = Depends(get_db), force: bool = False):
    """Seed database with sample menu items."""
    # Check if already seeded (allow force reseed)
    if db.query(MenuItem).count() > 0:
        if force:
            db.query(MenuItem).delete()
            db.commit()
        else:
            return {"message": "Database already seeded. Use ?force=true to reseed."}
    
    sample_items = [
        # ==================== PIZZAS - Classic & Specialty ====================
        {"item": "Margherita Pizza", "price": 12.99, "category": "Pizza", "description": "Classic tomato, fresh mozzarella, and aromatic basil leaves", "ingredients": "San Marzano Tomato Sauce, Mozzarella di Bufala, Fresh Basil, EVOO", "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800&q=80"},
        {"item": "Pepperoni Pizza", "price": 14.99, "category": "Pizza", "description": "Loaded with premium pepperoni and extra melted cheese", "ingredients": "Tomato Sauce, Mozzarella, Pecorino, Spicy Pepperoni", "image_url": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=800&q=80"},
        {"item": "BBQ Chicken Pizza", "price": 16.99, "category": "Pizza", "description": "Grilled chicken, smoky BBQ sauce, red onions, and fresh cilantro", "ingredients": "BBQ Sauce, Mozzarella, Grilled Chicken, Red Onions, Cilantro", "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&q=80"},
        {"item": "Veggie Supreme Pizza", "price": 15.99, "category": "Pizza", "description": "Bell peppers, mushrooms, olives, tomatoes, and caramelized onions", "ingredients": "Tomato Sauce, Mozzarella, Bell Peppers, Mushrooms, Black Olives, Onions", "image_url": "https://images.unsplash.com/photo-1511689660979-10d2b1aada49?w=800&q=80"},
        {"item": "Hawaiian Pizza", "price": 14.99, "category": "Pizza", "description": "Sweet pineapple chunks with savory ham on mozzarella", "ingredients": "Tomato Sauce, Mozzarella, Ham, Pineapple", "image_url": "https://images.unsplash.com/photo-1565299507177-b0ac66763828?w=800&q=80"},
        {"item": "Meat Lovers Pizza", "price": 18.99, "category": "Pizza", "description": "Pepperoni, Italian sausage, crispy bacon, and glazed ham", "ingredients": "Tomato Sauce, Mozzarella, Pepperoni, Sausage, Bacon, Ham", "image_url": "https://images.unsplash.com/photo-1594007654729-407eedc4be65?w=800&q=80"},
        {"item": "Four Cheese Pizza", "price": 15.99, "category": "Pizza", "description": "Mozzarella, gorgonzola, parmesan, and ricotta blend", "ingredients": "Mozzarella, Gorgonzola, Parmesan, Ricotta, Garlic Sauce", "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&q=80"},
        {"item": "Buffalo Chicken Pizza", "price": 16.99, "category": "Pizza", "description": "Spicy buffalo chicken, ranch drizzle, and blue cheese crumbles", "ingredients": "Buffalo Sauce, Mozzarella, Chicken, Blue Cheese, Ranch", "image_url": "https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?w=800&q=80"},
        {"item": "Mushroom Truffle Pizza", "price": 19.99, "category": "Pizza", "description": "Wild mushrooms, truffle oil, and fresh thyme", "ingredients": "Garlic Cream Sauce, Fontina, Wild Mushrooms, Truffle Oil, Thyme", "image_url": "https://images.unsplash.com/photo-1571407970349-bc81e7e96d47?w=800&q=80"},
        {"item": "Mediterranean Pizza", "price": 17.99, "category": "Pizza", "description": "Feta cheese, olives, sun-dried tomatoes, and artichoke hearts", "ingredients": "Pesto, Mozzarella, Feta, Kalamata Olives, Sun-dried Tomatoes, Artichokes", "image_url": "https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?w=800&q=80"},
        {"item": "Spicy Italian Pizza", "price": 17.99, "category": "Pizza", "description": "Spicy salami, jalapeños, hot honey drizzle", "ingredients": "Tomato Sauce, Mozzarella, Soppressata, Jalapeños, Hot Honey", "image_url": "https://images.unsplash.com/photo-1605478371310-a9f1e96b4ff4?w=800&q=80"},
        {"item": "White Garlic Pizza", "price": 14.99, "category": "Pizza", "description": "Creamy garlic sauce, spinach, and roasted garlic cloves", "ingredients": "Garlic Parmesan Sauce, Mozzarella, Spinach, Roasted Garlic", "image_url": "https://images.unsplash.com/photo-1552539618-7eec9b4d1796?w=800&q=80"},
        
        # ==================== APPETIZERS & SIDES ====================
        {"item": "Garlic Bread", "price": 4.99, "category": "Side", "description": "Crispy Italian bread with garlic butter and herbs", "ingredients": "Baguette, Garlic Butter, Parsley, Parmesan", "image_url": "https://images.unsplash.com/photo-1619535860434-ba1d8fa12536?w=800&q=80"},
        {"item": "Cheesy Garlic Bread", "price": 6.99, "category": "Side", "description": "Garlic bread topped with melted mozzarella", "ingredients": "Baguette, Garlic Butter, Mozzarella, Provolone", "image_url": "https://images.unsplash.com/photo-1573140401552-3fab0b24306f?w=800&q=80"},
        {"item": "Caesar Salad", "price": 7.99, "category": "Side", "description": "Crisp romaine, shaved parmesan, croutons, caesar dressing", "ingredients": "Romaine Lettuce, Parmesan, Croutons, Caesar Dressing", "image_url": "https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=800&q=80"},
        {"item": "Greek Salad", "price": 8.99, "category": "Side", "description": "Tomatoes, cucumbers, olives, feta, and oregano vinaigrette", "ingredients": "Mixed Greens, Tomatoes, Cucumbers, Kalamata Olives, Feta", "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&q=80"},
        {"item": "Mozzarella Sticks", "price": 6.99, "category": "Side", "description": "6 crispy sticks with warm marinara dipping sauce", "ingredients": "Breaded Mozzarella, Marinara Sauce", "image_url": "https://images.unsplash.com/photo-1548340748-6d2b7d7da280?w=800&q=80"},
        {"item": "Buffalo Wings", "price": 9.99, "category": "Side", "description": "8 crispy wings tossed in spicy buffalo sauce", "ingredients": "Chicken Wings, Buffalo Sauce, Blue Cheese Dip", "image_url": "https://images.unsplash.com/photo-1608039755401-742074f0548d?w=800&q=80"},
        {"item": "Loaded Nachos", "price": 10.99, "category": "Side", "description": "Crispy tortilla chips with cheese, jalapeños, sour cream", "ingredients": "Tortilla Chips, Queso, Jalapeños, Pico de Gallo, Sour Cream", "image_url": "https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?w=800&q=80"},
        {"item": "Onion Rings", "price": 5.99, "category": "Side", "description": "Beer-battered onion rings with chipotle aioli", "ingredients": "Onions, Beer Batter, Chipotle Aioli", "image_url": "https://images.unsplash.com/photo-1639024471283-03518883512d?w=800&q=80"},
        {"item": "Bruschetta", "price": 7.99, "category": "Side", "description": "Toasted bread with fresh tomatoes, basil, and balsamic glaze", "ingredients": "Ciabatta, Tomatoes, Basil, Garlic, Balsamic Glaze", "image_url": "https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?w=800&q=80"},
        {"item": "Stuffed Mushrooms", "price": 8.99, "category": "Side", "description": "Mushroom caps filled with herbed cream cheese", "ingredients": "Mushrooms, Cream Cheese, Herbs, Breadcrumbs", "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800&q=80"},
        {"item": "Garlic Parmesan Fries", "price": 5.99, "category": "Side", "description": "Crispy fries with garlic butter and parmesan", "ingredients": "French Fries, Garlic Butter, Parmesan, Parsley", "image_url": "https://images.unsplash.com/photo-1630384060421-cb20acd7bf24?w=800&q=80"},
        
        # ==================== DRINKS - Refreshing Options ====================
        {"item": "Classic Cola", "price": 2.99, "category": "Drink", "description": "Refreshing classic cola served ice cold", "ingredients": "Cola", "image_url": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=800&q=80"},
        {"item": "Fresh Lemonade", "price": 3.49, "category": "Drink", "description": "House-made lemonade with fresh lemon slices", "ingredients": "Lemon Juice, Water, Sugar, Ice", "image_url": "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=800&q=80"},
        {"item": "Sweet Iced Tea", "price": 2.99, "category": "Drink", "description": "Southern-style sweet tea over ice", "ingredients": "Brewed Black Tea, Sugar, Lemon", "image_url": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=800&q=80"},
        {"item": "Sparkling Water", "price": 2.49, "category": "Drink", "description": "Premium Italian sparkling mineral water", "ingredients": "Mineral Water", "image_url": "https://images.unsplash.com/photo-1523362628745-0c100150b504?w=800&q=80"},
        {"item": "Mango Smoothie", "price": 4.99, "category": "Drink", "description": "Tropical mango blended with yogurt and honey", "ingredients": "Mango, Greek Yogurt, Honey, Ice", "image_url": "https://images.unsplash.com/photo-1546173159-315724a31696?w=800&q=80"},
        {"item": "Berry Blast Smoothie", "price": 4.99, "category": "Drink", "description": "Mixed berries with banana and almond milk", "ingredients": "Strawberries, Blueberries, Banana, Almond Milk", "image_url": "https://images.unsplash.com/photo-1553530666-ba11a7da3888?w=800&q=80"},
        {"item": "Italian Soda", "price": 3.99, "category": "Drink", "description": "Sparkling water with flavored syrup and cream", "ingredients": "Sparkling Water, Strawberry/Raspberry Syrup, Cream", "image_url": "https://images.unsplash.com/photo-1558642452-9d2a7deb7f62?w=800&q=80"},
        {"item": "Cold Brew Coffee", "price": 3.99, "category": "Drink", "description": "Smooth cold-brewed coffee over ice", "ingredients": "Coffee Beans, Water", "image_url": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=800&q=80"},
        {"item": "Hot Cappuccino", "price": 3.99, "category": "Drink", "description": "Rich espresso with steamed milk foam", "ingredients": "Espresso, Steamed Milk, Foam", "image_url": "https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=800&q=80"},
        {"item": "Milkshake", "price": 5.49, "category": "Drink", "description": "Creamy vanilla bean milkshake with whipped cream", "ingredients": "Vanilla Ice Cream, Milk, Whipped Cream", "image_url": "https://images.unsplash.com/photo-1579954115545-a95591f28bfc?w=800&q=80"},
        
        # ==================== DESSERTS - Sweet Finishes ====================
        {"item": "Chocolate Lava Cake", "price": 6.99, "category": "Dessert", "description": "Warm chocolate cake with molten center and vanilla ice cream", "ingredients": "Chocolate Cake, Chocolate Ganache, Vanilla Ice Cream", "image_url": "https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=800&q=80"},
        {"item": "Tiramisu", "price": 7.99, "category": "Dessert", "description": "Classic Italian layered coffee-mascarpone dessert", "ingredients": "Ladyfingers, Mascarpone, Espresso, Cocoa Powder", "image_url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=800&q=80"},
        {"item": "Ice Cream Sundae", "price": 5.99, "category": "Dessert", "description": "Three scoops with chocolate sauce, nuts, and cherry", "ingredients": "Vanilla Ice Cream, Chocolate Syrup, Nuts, Cherry", "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=800&q=80"},
        {"item": "New York Cheesecake", "price": 7.99, "category": "Dessert", "description": "Creamy cheesecake with strawberry compote", "ingredients": "Cream Cheese, Graham Cracker Crust, Strawberry Compote", "image_url": "https://images.unsplash.com/photo-1508737027454-e6454ef45afd?w=800&q=80"},
        {"item": "Cannoli", "price": 5.99, "category": "Dessert", "description": "Crispy shells filled with sweet ricotta and chocolate chips", "ingredients": "Pastry Shell, Ricotta, Chocolate Chips, Powdered Sugar", "image_url": "https://images.unsplash.com/photo-1551024506-0bccd828d307?w=800&q=80"},
        {"item": "Panna Cotta", "price": 6.99, "category": "Dessert", "description": "Silky Italian cream pudding with berry sauce", "ingredients": "Cream, Sugar, Gelatin, Vanilla, Mixed Berries", "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800&q=80"},
        {"item": "Brownie à la Mode", "price": 6.99, "category": "Dessert", "description": "Fudgy brownie with vanilla ice cream and caramel", "ingredients": "Chocolate Brownie, Vanilla Ice Cream, Caramel Sauce", "image_url": "https://images.unsplash.com/photo-1564355808539-22fda35bed7e?w=800&q=80"},
        {"item": "Apple Pie", "price": 5.99, "category": "Dessert", "description": "Warm apple pie with cinnamon and flaky crust", "ingredients": "Apples, Cinnamon, Pie Crust", "image_url": "https://images.unsplash.com/photo-1568571780765-9276ac8b75a2?w=800&q=80"},
        {"item": "Gelato", "price": 4.99, "category": "Dessert", "description": "Authentic Italian gelato - ask for today's flavors", "ingredients": "Milk, Sugar, Natural Flavors", "image_url": "https://images.unsplash.com/photo-1557142046-c704a3adf364?w=800&q=80"},
    ]
    
    for item_data in sample_items:
        db_item = MenuItem(**item_data)
        db.add(db_item)
    
    db.commit()
    return {"message": f"Database seeded with {len(sample_items)} items"}

# ==================== KNOWLEDGE BASE ENDPOINTS ====================
@app.get("/kb")
def get_kb_entries(category: Optional[str] = None):
    """Get all knowledge base entries, optionally filtered by category."""
    if category:
        return knowledge_base.get_by_category(category)
    return knowledge_base.get_all()

@app.get("/kb/search")
def search_kb(q: str, category: Optional[str] = None, limit: int = 5):
    """Search knowledge base with full-text search."""
    return knowledge_base.search(q, category=category, limit=limit)

@app.get("/kb/{entry_id}")
def get_kb_entry(entry_id: int):
    """Get a specific knowledge base entry."""
    entry = knowledge_base.get_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="KB entry not found")
    return entry

@app.post("/kb")
def create_kb_entry(
    category: str,
    title: str,
    content: str,
    tags: Optional[List[str]] = None
):
    """Create a new knowledge base entry."""
    return knowledge_base.add_entry(category, title, content, tags or [])

@app.put("/kb/{entry_id}")
def update_kb_entry(
    entry_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None
):
    """Update a knowledge base entry."""
    entry = knowledge_base.update_entry(entry_id, title, content, tags)
    if not entry:
        raise HTTPException(status_code=404, detail="KB entry not found")
    return entry

@app.delete("/kb/{entry_id}")
def delete_kb_entry(entry_id: int):
    """Delete a knowledge base entry."""
    if not knowledge_base.delete_entry(entry_id):
        raise HTTPException(status_code=404, detail="KB entry not found")
    return {"message": "KB entry deleted successfully"}
