import re
import os
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from knowledge_base import knowledge_base

load_dotenv()

INTENT_PATTERNS = {
    "GREETING": [
        r"\b(hi|hello|hey|good\s*(morning|afternoon|evening)|greetings)\b",
    ],
    "MENU_QUERY": [
        r"\b(menu|show.*menu|what.*have|what.*offer|list.*items|food.*list|available|options)\b",
    ],
    "CATEGORY_QUERY": [
        r"\b(pizza|drink|dessert|side|appetizer|beverage|category)\b",
    ],
    "ITEM_DETAILS": [
        r"\b(tell.*about|describe|what.*is|details|ingredients|info.*about)\b",
    ],
    # TRACK_ORDER must come BEFORE ORDER_INTENT to prioritize tracking queries
    "TRACK_ORDER": [
        r"\b(track|where.*(is|my)|order\s*(status|#|number)|status.*order|how\s*long|my\s*order)\b",
    ],
    "CONFIRM_ORDER": [
        r"\b(yes|confirm|proceed|place.*order|go\s*ahead|sure|okay|ok|yep|yup)\b",
    ],
    "CANCEL_ORDER": [
        r"\b(cancel|remove|delete|never\s*mind|forget\s*it|don\'?t\s*want)\b",
    ],
    # ORDER_INTENT comes after TRACK_ORDER so tracking phrases match first
    "ORDER_INTENT": [
        r"\b(want|i\'?d\s*like|get\s*me|give\s*me|buy|purchase|add.*cart)\b",
        r"\border\b(?!\s*(status|#|number))",  # "order" but not "order status" or "order #"
    ],
    "SUPPORT": [
        r"\b(help|support|problem|issue|complaint|speak.*human|manager|wrong)\b",
    ],
    "PERSONA_QUERY": [
        r"\b(who.*are.*you|are.*you.*(real|ai|bot|human)|what.*can.*you.*do|your.*name|do.*you.*eat)\b",
    ],
    "KB_QUERY": [
        r"\b(allergy|allergen|gluten|nutrition|calorie|ingredient|policy|refund|delivery.*time|hours|open|contact|phone|email|promo|deal|discount|coupon|loyalty|reward|custom|modify|topping|history|origin|fact|trivia|dough|rise|yeast|science|reaction|oven|temp|pineapple|deep.*dish|thin.*crust)\b",
    ],
}

class RestaurantChatbot:
    """
    AI-powered chatbot for restaurant operations.
    Uses intent classification and context management.
    """
    
    def __init__(self):
        self.user_contexts: Dict[str, Dict[str, Any]] = {}
        self.restaurant_name = "🍕 AI Pizza Palace"
        self.restaurant_info = """
        Welcome to AI Pizza Palace! We are a fully AI-operated pizzeria offering 
        delicious handcrafted pizzas, refreshing drinks, and delightful desserts.
        Our AI assistant is here to help you 24/7!
        
        Hours: Open 24/7 (AI Never Sleeps!)
        Delivery: Free delivery on orders over $25
        """
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get or create user context for conversation management."""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {
                "cart": [],
                "pending_order": None,
                "last_intent": None,
                "order_history": [],
            }
        return self.user_contexts[user_id]
    
    def classify_intent(self, message: str) -> str:
        """Classify user intent using pattern matching."""
        message_lower = message.lower().strip()
        
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return intent
        
        return "UNKNOWN"
    
    def extract_menu_items(self, message: str, menu_items: List[Dict]) -> List[Dict]:
        """Extract mentioned menu items from user message (case-insensitive)."""
        # Normalize message to lowercase for case-insensitive matching
        message_lower = message.lower().strip()
        # Remove extra spaces and common filler words
        message_normalized = re.sub(r'\s+', ' ', message_lower)
        found_items = []
        
        for item in menu_items:
            item_name_lower = item["item"].lower()
            item_words = item_name_lower.split()
            
            # Check 1: Exact match (e.g., "margherita pizza" in message)
            if item_name_lower in message_normalized:
                if item not in found_items:
                    found_items.append(item)
                continue
            
            # Check 2: Main item name without category (e.g., "margherita" matches "Margherita Pizza")
            main_name = item_words[0] if item_words else ""
            if len(main_name) > 3 and main_name in message_normalized:
                if item not in found_items:
                    found_items.append(item)
                continue
            
            # Check 3: Any significant word match (e.g., "pepperoni" matches "Pepperoni Pizza")
            for word in item_words:
                # Skip common words like "pizza", "ice", "cream" unless they're the main identifier
                if len(word) > 3 and word in message_normalized:
                    if item not in found_items:
                        found_items.append(item)
                    break
            
            # Check 4: Handle compound names (e.g., "BBQ chicken" or "meat lovers")
            if len(item_words) >= 2:
                compound = " ".join(item_words[:2])
                if compound in message_normalized:
                    if item not in found_items:
                        found_items.append(item)
        
        return found_items
    
    def extract_quantity(self, message: str) -> int:
        """Extract quantity from message."""
        # Look for number words
        number_words = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }
        
        message_lower = message.lower()
        for word, num in number_words.items():
            if word in message_lower:
                return num
        
        # Look for digits
        numbers = re.findall(r'\d+', message)
        if numbers:
            return int(numbers[0])
        
        return 1
    
    def format_menu_response(self, menu_items: List[Dict], category: Optional[str] = None) -> str:
        """Format menu items as a nice response."""
        if category:
            items = [i for i in menu_items if i["category"].lower() == category.lower()]
        else:
            items = menu_items
        
        if not items:
            return "Sorry, no items found in that category."
        
        # Group by category
        categories = {}
        for item in items:
            cat = item["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        response = f"🍕 **{self.restaurant_name} Menu**\n\n"
        
        for cat, cat_items in categories.items():
            response += f"**{cat}**\n"
            for item in cat_items:
                response += f"  • {item['item']} - ${item['price']:.2f}\n"
                if item.get('description'):
                    response += f"    _{item['description']}_\n"
                if item.get('ingredients'):
                    response += f"    🥕 *Ingredients: {item['ingredients']}*\n"
            response += "\n"
        
        response += "\n💬 _Say 'order [item name]' to add to your cart!_"
        return response
    
    def format_cart_response(self, cart: List[Dict]) -> str:
        """Format cart as response."""
        if not cart:
            return "🛒 Your cart is empty. Browse our menu to add items!"
        
        response = "🛒 **Your Cart:**\n\n"
        total = 0
        for item in cart:
            subtotal = item["price"] * item["quantity"]
            total += subtotal
            response += f"  • {item['item']} x{item['quantity']} - ${subtotal:.2f}\n"
        
        response += f"\n**Total: ${total:.2f}**\n"
        response += "\n💬 _Say 'confirm' to place your order or 'cancel' to clear cart._"
        return response
    
    def process_message(
        self, 
        message: str, 
        user_id: str,
        menu_items: List[Dict],
        orders: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Process user message and return response with action.
        
        Returns:
            {
                "response": str,
                "action": str or None,
                "data": dict or None
            }
        """
        context = self.get_user_context(user_id)
        intent = self.classify_intent(message)
        context["last_intent"] = intent
        
        response = ""
        action = None
        data = None
        
        # Simulate "thinking" time
        time.sleep(1.5)
        
        # Handle different intents
        if intent == "PERSONA_QUERY":
            # Search specifically in persona category
            kb_results = knowledge_base.search(message, category="persona", limit=1)
            if kb_results:
                response = f"🤖 **{kb_results[0]['title']}**\n\n{kb_results[0]['content']}"
            else:
                response = "I'm the AI Pizza Palace Assistant! I can help you order pizza, check stock, and answer pizza-related questions."
            action = "persona_response"

        elif intent == "GREETING":
            response = f"""
👋 **Welcome to {self.restaurant_name}!**

I'm your AI assistant, ready to help you with:
• 📜 View our delicious menu
• 🛒 Place an order
• 📦 Track your order
• ❓ Get help

{self.restaurant_info}

_What would you like to do today?_
            """.strip()
        
        elif intent == "MENU_QUERY":
            response = self.format_menu_response(menu_items)
            action = "show_menu"
            data = {"items": menu_items}
        
        elif intent == "CATEGORY_QUERY":
            # Extract category from message
            message_lower = message.lower()
            category = None
            for cat in ["pizza", "drink", "dessert", "side", "appetizer", "beverage"]:
                if cat in message_lower:
                    category = cat.capitalize()
                    break
            
            response = self.format_menu_response(menu_items, category)
            action = "show_category"
            data = {"category": category}
        
        elif intent == "ITEM_DETAILS":
            found_items = self.extract_menu_items(message, menu_items)
            if found_items:
                item = found_items[0]
                response = f"""
🍕 **{item['item']}**

💰 Price: ${item['price']:.2f}
📂 Category: {item['category']}
📝 Description: {item.get('description', 'A delicious choice!')}
🥕 Ingredients: {item.get('ingredients', 'Ask me for details!')}

_Would you like to order this item?_
                """.strip()
                action = "show_item"
                data = {"item": item}
            else:
                response = "I couldn't find that item. Would you like to see our full menu?"
        
        elif intent == "ORDER_INTENT":
            found_items = self.extract_menu_items(message, menu_items)
            quantity = self.extract_quantity(message)
            
            if found_items:
                for item in found_items:
                    cart_item = {
                        "menu_item_id": item["id"],
                        "item": item["item"],
                        "price": item["price"],
                        "quantity": quantity
                    }
                    # Check if already in cart
                    existing = next((i for i in context["cart"] if i["menu_item_id"] == item["id"]), None)
                    if existing:
                        existing["quantity"] += quantity
                    else:
                        context["cart"].append(cart_item)
                
                response = f"✅ Added to cart!\n\n{self.format_cart_response(context['cart'])}"
                action = "add_to_cart"
                data = {"cart": context["cart"]}
            else:
                response = "What would you like to order? Please mention an item from our menu, or say 'menu' to see available options."
        
        elif intent == "CONFIRM_ORDER":
            if context["cart"]:
                total = sum(i["price"] * i["quantity"] for i in context["cart"])
                response = f"""
🎉 **Order Confirmed!**

{self.format_cart_response(context['cart'])}

Please provide your details to complete the order:
• Your name
• Phone number
• Delivery address (optional for pickup)

Or I can create the order now if you prefer pickup!
                """.strip()
                action = "confirm_order"
                data = {
                    "cart": context["cart"],
                    "total": total,
                    "requires_details": True
                }
            else:
                response = "Your cart is empty! Browse our menu first by saying 'show menu'."
        
        elif intent == "CANCEL_ORDER":
            if context["cart"]:
                context["cart"] = []
                response = "🗑️ Your cart has been cleared. Feel free to start a new order anytime!"
                action = "clear_cart"
            else:
                response = "There's nothing to cancel. Would you like to see our menu?"
        
        elif intent == "TRACK_ORDER":
            if orders:
                # Try to extract order ID from message
                order_id_match = re.search(r'#?(\d+)', message)
                order_id = int(order_id_match.group(1)) if order_id_match else None
                
                target_order = None
                
                if order_id:
                    # Find specific order by ID
                    target_order = next((o for o in orders if o.get("id") == order_id), None)
                else:
                    # Look for user's orders by phone/user_id
                    user_orders = [o for o in orders if str(o.get("customer_phone")) == user_id]
                    if user_orders:
                        target_order = user_orders[-1]  # Most recent
                    else:
                        # Show most recent order for anonymous users
                        if orders:
                            target_order = orders[0]  # Orders are sorted by created_at desc
                
                if target_order:
                    status_emoji = {
                        "Pending": "⏳",
                        "Confirmed": "✅",
                        "Preparing": "👨‍🍳",
                        "Ready": "📦",
                        "Delivered": "🚗",
                        "Cancelled": "❌"
                    }
                    status_progress = {
                        "Pending": "Your order has been received and is awaiting confirmation.",
                        "Confirmed": "Great news! Your order is confirmed and will be prepared soon.",
                        "Preparing": "Our chefs are crafting your delicious order right now!",
                        "Ready": "Your order is ready! It will be delivered shortly.",
                        "Delivered": "Your order has been delivered. Enjoy!",
                        "Cancelled": "This order was cancelled."
                    }
                    emoji = status_emoji.get(target_order["status"], "📋")
                    progress = status_progress.get(target_order["status"], "Processing your order...")
                    
                    response = f"""
📦 **Order #{target_order['id']} Status**

{emoji} Status: **{target_order['status']}**
💰 Total: ${target_order['total_amount']:.2f}
📅 Ordered: {target_order['created_at']}

_{progress}_

To track a different order, say "track order #<order_id>"
                    """.strip()
                    action = "show_order_status"
                    data = {"order": target_order}
                else:
                    if order_id:
                        response = f"I couldn't find order #{order_id}. Please check the order number and try again."
                    else:
                        response = "I couldn't find any orders. Please provide an order ID (e.g., 'track order #123')."
            else:
                response = """
I don't see any orders in the system yet. 

To place an order, just tell me what you'd like! For example:
• "I want a Pepperoni Pizza"
• "Order 2 Margherita Pizzas"

_After placing an order, you can track it by saying "track my order" or "track order #<ID>"_
                """.strip()
        
        elif intent == "KB_QUERY":
            # Search knowledge base for relevant information
            kb_results = knowledge_base.search(message, limit=2)
            if kb_results:
                result = kb_results[0]
                response = f"""
📚 **{result['title']}**

{result['content']}
                """.strip()
                
                if len(kb_results) > 1:
                    response += f"\n\n_Related: {kb_results[1]['title']}_"
                
                action = "kb_response"
                data = {"entries": kb_results}
            else:
                # Fallback to support
                response = """
I don't have specific information about that. Would you like me to:

• 📜 Show you our **menu**
• 📞 Connect you with **support** (1-800-AI-PIZZA)
• ❓ Answer other questions

_Just let me know how I can help!_
                """.strip()
                action = "kb_fallback"
        
        elif intent == "SUPPORT":
            response = f"""
🆘 **Customer Support**

I'm sorry if you're experiencing any issues! Here's how I can help:

• 📞 Call us: 1-800-AI-PIZZA
• 📧 Email: support@aipizzapalace.com
• 💬 Chat: You're already here!

Common issues I can help with:
• Order modifications
• Refund requests
• Delivery updates
• Menu questions

_How can I assist you today?_
            """.strip()
            action = "support"
        
        else:
            response = f"""
I'm not sure I understood that. Here's what I can help you with:

• Say **'menu'** to see our offerings
• Say **'order [item]'** to add to cart
• Say **'track order'** to check status
• Say **'help'** for support

_What would you like to do?_
            """.strip()
        
        return {
            "response": response,
            "action": action,
            "data": data
        }

# Global chatbot instance
chatbot = RestaurantChatbot()
