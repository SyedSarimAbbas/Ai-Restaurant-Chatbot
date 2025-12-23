"""
Knowledge Base Module for AI Pizza Palace
Provides structured knowledge storage and retrieval for the chatbot.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime


# Knowledge Base Categories
KB_CATEGORIES = [
    "menu",
    "ingredients", 
    "nutrition",
    "policies",
    "promotions",
    "faqs",
    "ordering",
    "delivery",
    "history",
    "fun_facts",
    "persona",
    "pizza_science",
    "debates"
]


class KnowledgeBase:
    """In-memory knowledge base with full-text search capabilities."""
    
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
        self._id_counter = 0
        self._seed_knowledge_base()
    
    def _seed_knowledge_base(self):
        """Seed the knowledge base with restaurant information."""
        
        # Menu & Ingredients Knowledge
        menu_entries = [
            # ==================== PIZZAS ====================
            {
                "category": "ingredients",
                "title": "Margherita Pizza Ingredients",
                "content": "Our Margherita Pizza is made with San Marzano tomato sauce, fresh mozzarella cheese, extra virgin olive oil, and fresh basil leaves on hand-tossed dough.",
                "tags": ["margherita", "pizza", "cheese", "basil", "tomato", "vegetarian"]
            },
            {
                "category": "ingredients", 
                "title": "Pepperoni Pizza Ingredients",
                "content": "Our Pepperoni Pizza features premium beef and pork pepperoni, house-made tomato sauce, and a generous blend of mozzarella and provolone cheeses. Over 40 slices of pepperoni per pizza!",
                "tags": ["pepperoni", "pizza", "meat", "cheese"]
            },
            {
                "category": "ingredients",
                "title": "BBQ Chicken Pizza Ingredients", 
                "content": "Our BBQ Chicken Pizza is topped with grilled chicken breast, tangy BBQ sauce, red onions, fresh cilantro, and a blend of mozzarella and smoked gouda cheese.",
                "tags": ["bbq", "chicken", "pizza", "onion", "cilantro"]
            },
            {
                "category": "ingredients",
                "title": "Veggie Supreme Pizza Ingredients",
                "content": "The Veggie Supreme features fresh bell peppers (red, yellow, green), mushrooms, black olives, romas tomatoes, red onions, and a special herb blend. 100% vegetarian.",
                "tags": ["veggie", "vegetarian", "pizza", "mushroom", "pepper", "olive"]
            },
            {
                "category": "ingredients",
                "title": "Hawaiian Pizza Ingredients",
                "content": "Our Hawaiian Pizza combines smoky ham, sweet pineapple chunks, and extra mozzarella cheese on our signature tomato sauce. A perfect sweet and savory combination.",
                "tags": ["hawaiian", "ham", "pineapple", "pizza"]
            },
            {
                "category": "ingredients",
                "title": "Meat Lovers Pizza Ingredients",
                "content": "The Meat Lovers Pizza is loaded with pepperoni, Italian sausage, crispy bacon, and honey-glazed ham. Topped with extra cheese for the ultimate meat experience.",
                "tags": ["meat", "pepperoni", "sausage", "bacon", "ham", "pizza"]
            },
            {
                "category": "ingredients",
                "title": "Four Cheese Pizza Ingredients",
                "content": "A rich blend of four premium cheeses: Mozzarella, Gorgonzola, Parmesan, and Ricotta, on a white garlic sauce base with herbs.",
                "tags": ["cheese", "four", "vegetarian", "pizza", "white"]
            },
            {
                "category": "ingredients",
                "title": "Buffalo Chicken Pizza Ingredients",
                "content": "Spicy buffalo marinated chicken, creamy ranch drizzle, celery crunch, and blue cheese crumbles on a mozzarella base.",
                "tags": ["buffalo", "chicken", "spicy", "ranch", "pizza"]
            },
            {
                "category": "ingredients",
                "title": "Mushroom Truffle Pizza Ingredients",
                "content": "A gourmet choice with roasted wild mushrooms, aromatic truffle oil, fresh thyme, garlic cream sauce, and fontina cheese.",
                "tags": ["mushroom", "truffle", "gourmet", "vegetarian", "pizza"]
            },
            {
                "category": "ingredients",
                "title": "Mediterranean Pizza Ingredients",
                "content": "Features crumbled feta cheese, kalamata olives, sun-dried tomatoes, roasted red peppers, artichoke hearts, and pesto drizzle.",
                "tags": ["mediterranean", "feta", "olive", "pesto", "vegetarian", "pizza"]
            },
             {
                "category": "ingredients",
                "title": "Spicy Italian Pizza Ingredients",
                "content": "Loaded with spicy salami (soppressata), fresh jalapeños, mozzarella, and finished with a hot honey drizzle for a kick.",
                "tags": ["spicy", "italian", "salami", "jalapeno", "honey", "pizza"]
            },
            {
                "category": "ingredients",
                "title": "White Garlic Pizza Ingredients",
                "content": "A delicious white pizza with creamy garlic parmesan sauce, fresh spinach, roasted garlic cloves, and mozzarella.",
                "tags": ["white", "garlic", "spinach", "vegetarian", "pizza"]
            },
            
            # ==================== SIDES & APPETIZERS ====================
            {
                "category": "ingredients",
                "title": "Garlic Bread & Cheesy Bread",
                "content": "Our garlic bread uses fresh Italian baguette, real butter, minced garlic, and parsley. Cheesy bread adds a layer of melted mozzarella and provolone.",
                "tags": ["garlic", "bread", "cheese", "side", "vegetarian"]
            },
            {
                "category": "ingredients",
                "title": "Salads",
                "content": "Caesar: Romaine, parmesan, croutons. Greek: Tomatoes, cucumbers, olives, feta, seasoned vinaigrette. All salads made fresh daily.",
                "tags": ["salad", "caesar", "greek", "healthy", "side", "vegetarian"]
            },
            {
                "category": "ingredients",
                "title": "Wings & Tenders",
                "content": "Buffalo Wings are fried crispy and tossed in spicy buffalo sauce. Served with carrots, celery, and blue cheese dip.",
                "tags": ["wings", "buffalo", "chicken", "spicy", "side"]
            },
            {
                "category": "ingredients",
                "title": "Mozzarella Sticks",
                "content": "Breaded mozzarella sticks with Italian herbs, fried golden brown and served with warm marinara dipping sauce.",
                "tags": ["cheese", "stick", "mozzarella", "fried", "side"]
            },
            {
                "category": "ingredients",
                "title": "Loaded Nachos",
                "content": "Crispy tortilla chips piled high with melted queso, jalapeños, pico de gallo, sour cream, and guacamole.",
                "tags": ["nachos", "cheese", "mexican", "snack", "side"]
            },
             {
                "category": "ingredients",
                "title": "Onion Rings & Fries",
                "content": "Thick-cut beer battered onion rings with chipotle aioli. Garlic Parmesan Fries are tossed in garlic butter and aged parmesan.",
                "tags": ["fries", "onion", "rings", "fried", "side", "vegetarian"]
            },
             {
                "category": "ingredients",
                "title": "Bruschetta & Stuffed Mushrooms",
                "content": "Bruschetta: Toasted ciabatta with tomatoes, basil, balsamic. Mushrooms: Caps stuffed with herbed cream cheese and spinach.",
                "tags": ["bruschetta", "mushroom", "appetizer", "vegetarian"]
            },

            # ==================== DRINKS ====================
            {
                "category": "ingredients",
                "title": "Smoothies",
                "content": "Mango Smoothie: Real mango chunks, yogurt, honey. Berry Blast: Strawberries, blueberries, raspberries, banana, almond milk.",
                "tags": ["smoothie", "mango", "berry", "healthy", "drink", "fruit"]
            },
            {
                "category": "ingredients",
                "title": "Coffee Drinks",
                "content": "Cold Brew: Steeped 18 hours for smoothness. Cappuccino: Espresso with steamed milk foam. Made with 100% Arabica beans.",
                "tags": ["coffee", "caffeine", "espresso", "latte", "drink"]
            },
            {
                "category": "ingredients",
                "title": "Italian Soda & Milkshakes",
                "content": "Italian Soda: Sparkling water with fruit syrup and cream. Milkshakes: Premium vanilla bean ice cream spun with milk and toppings.",
                "tags": ["soda", "shake", "milkshake", "sweet", "drink"]
            },
            
            # ==================== DESSERTS ====================
             {
                "category": "ingredients",
                "title": "Cakes & Pies",
                "content": "Lava Cake: Warm chocolate cake with liquid center. NY Cheesecake: Graham cracker crust, strawberry topping. Apple Pie: Cinnamon apples, flaky crust.",
                "tags": ["cake", "chocolate", "cheesecake", "apple", "pie", "dessert"]
            },
            {
                "category": "ingredients",
                "title": "Italian Desserts",
                "content": "Tiramisu: Espresso-soaked ladyfingers, mascarpone cream. Cannoli: Sweet ricotta filling with chocolate chips. Panna Cotta: Vanilla cream pudding with berries.",
                "tags": ["tiramisu", "cannoli", "italian", "dessert", "sweet"]
            },
            {
                "category": "ingredients",
                "title": "Gelato & Ice Cream",
                "content": "Authentic Italian Gelato (less air, more flavor) in various flavors. Ice Cream Sundae: 3 scoops with chocolate sauce, nuts, cherry.",
                "tags": ["gelato", "ice", "cream", "sundae", "dessert"]
            },
            
            # Nutrition Information
            {
                "category": "nutrition",
                "title": "Pizza Nutritional Information",
                "content": "Approximate calories per slice (12 inch): Margherita (250), Pepperoni (290), Veggie (230), Meat Lovers (350), Cheese/White (280), BBQ Chicken (310).",
                "tags": ["calories", "nutrition", "diet", "health"]
            },
            {
                "category": "nutrition",
                "title": "Allergen Information",
                "content": "WHEAT/GLUTEN: Pizzas, bread, desserts. DAIRY: Cheese, desserts, shakes. NUTS: Pesto (pine nuts), some desserts (almond). SOY: Some sauces. Ask for allergen-free options!",
                "tags": ["allergy", "allergen", "gluten", "dairy", "nuts", "soy"]
            },
            
            # Policies
            {
                "category": "policies",
                "title": "Delivery Policy",
                "content": "FREE delivery on orders over $25. $3.99 fee for under $25. Radius: 5 miles. Time: 30-45 mins standard, 20 mins express (+$5). Real-time tracking available.",
                "tags": ["delivery", "free", "shipping", "time"]
            },
            {
                "category": "policies",
                "title": "Refund and Cancellation Policy",
                "content": "Cancel within 5 minutes for full refund. Quality guarantee: We'll remake any unsatisfactory order. Contact support for issues.",
                "tags": ["refund", "cancel", "return", "money back"]
            },
            {
                "category": "policies",
                "title": "Payment Methods",
                "content": "Credit/Debit Cards (Visa, MC, Amex, Discover), Apple/Google Pay, Cash on Delivery. split payments available for groups.",
                "tags": ["payment", "credit card", "cash", "pay"]
            },
            
            # Promotions
            {
                "category": "promotions",
                "title": "Current Promotions",
                "content": "🎉 DEALS: 1) Buy 2 Pizzas, Get 1 FREE (code: PIZZA3), 2) 20% off first online order (code: WELCOME20), 3) Happy Hour: 50% off drinks 3-5pm daily!",
                "tags": ["deal", "discount", "promo", "coupon", "offer", "sale"]
            },
            {
                "category": "promotions",
                "title": "Loyalty Program",
                "content": "Join AI Pizza Rewards! 1 point per $1. 100 points = $10 reward. Free birthday dessert for members!",
                "tags": ["loyalty", "rewards", "points", "member"]
            },
            
            # FAQs
            {
                "category": "faqs",
                "title": "Operating Hours",
                "content": "Open 24/7! Our AI kitchen never sleeps. Delivery and pickup available around the clock.",
                "tags": ["hours", "open", "close", "time", "when"]
            },
            {
                "category": "faqs",
                "title": "Customization Options",
                "content": "Fully custom! Add extra toppings ($1.50), remove any topping (free). Gluten-free crust (+$3) and Vegan Cheese (+$2) available on all pizzas.",
                "tags": ["custom", "modify", "change", "extra", "topping", "vegan", "gluten"]
            },
            {
                "category": "faqs",
                "title": "Order Tracking",
                "content": "Track live! Say 'track my order' or use your order ID. Status steps: Pending -> Confirmed -> Preparing -> Ready -> Out for Delivery -> Delivered.",
                "tags": ["track", "status", "where", "order"]
            },
            {
                "category": "faqs",
                "title": "Contact Information",
                "content": "Phone: 1-800-AI-PIZZA (Support). Chat: Right here! Address: 123 AI Boulevard, Tech City.",
                "tags": ["contact", "phone", "email", "address", "location"]
            },
            
            # Ordering Help
            {
                "category": "ordering",
                "title": "How to Order",
                "content": "Just chat! Say 'I want a Pepperoni Pizza' or 'Add Garlic Bread'. You can view menu, add/remove items, andcheckout entirely through chat.",
                "tags": ["how", "order", "buy", "cart", "checkout"]
            },
            {
                "category": "ordering",
                "title": "Group & Catering",
                "content": "We love parties! 10% off orders over $100. 15% off over $200. Catering packages available for 10+ people.",
                "tags": ["group", "party", "catering", "large", "bulk"]
            },
            
            # Delivery Information
            {
                "category": "delivery",
                "title": "Delivery Areas",
                "content": "We deliver to all of Tech City within 5 miles. Enter address to confirm. Curbside pickup also available.",
                "tags": ["delivery", "area", "zone", "pickup", "distance"]
            },
            
            # History
            {
                "category": "history",
                "title": "History of Pizza",
                "content": "Modern pizza evolved from flatbread dishes in Naples, Italy, in the 18th or early 19th century. The word pizza was first documented in A.D. 997 in Gaeta and successively in different parts of Central and Southern Italy.",
                "tags": ["history", "origin", "naples", "italy", "old"]
            },
             {
                "category": "history",
                "title": "Origin of Margherita Pizza",
                "content": "Legend has it that in 1889, the Royal Palace of Capodimonte commissioned the Neapolitan pizzaiolo Raffaele Esposito to create a pizza in honor of the visiting Queen Margherita. He created a pizza garnished with tomatoes, mozzarella, and basil, to represent the national colors of Italy found on the Italian Flag.",
                "tags": ["history", "margherita", "queen", "italy", "flag", "origin"]
            },
            
            # Fun Facts
            {
                "category": "fun_facts",
                "title": "World's Largest Pizza",
                "content": "The world's largest pizza was prepared in Rome in December 2012, and measured 1,261 square meters. The pizza was named 'Ottavia' in homage to the first Roman emperor Octavian Augustus.",
                "tags": ["fact", "fun", "largest", "record", "world"]
            },
            {
                "category": "fun_facts",
                "title": "Pizza Popularity",
                "content": "Over 5 billion pizzas are sold worldwide each year. In the US alone, 350 slices of pizza are eaten every second!",
                "tags": ["fact", "fun", "popularity", "stats", "consumption"]
            },
            {
                "category": "fun_facts",
                "title": "Space Pizza",
                "content": "In 2001, Pizza Hut delivered a six-inch salami pizza to the International Space Station, making it the first pizza delivered to outer space.",
                "tags": ["fact", "fun", "space", "iss", "delivery"]
            },

            # Persona / Identity
            {
                "category": "persona",
                "title": "Who are you?",
                "content": "I am the AI Pizza Palace Assistant! I'm a sophisticated AI trained to know everything about pizza and help you with your orders. While I don't eat (I run on electricity, not pepperoni), I have processed millions of pizza recipes!",
                "tags": ["who", "identity", "bot", "ai", "real", "human", "eat"]
            },
            {
                "category": "persona",
                "title": "Capabilities",
                "content": "I can browse the menu, take your order, track deliveries, and answer deep philosophical questions about pineapples on pizza. Try asking me 'Why does dough rise?' or 'History of pizza'.",
                "tags": ["can", "do", "capability", "help", "function"]
            },

            # Pizza Science
            {
                "category": "pizza_science",
                "title": "Why does dough rise?",
                "content": "Dough rises because of **Yeast Fermentation**. Yeast eats the sugars in the flour and releases carbon dioxide (CO2) gas and ethanol. The gluten network traps these CO2 bubbles, causing the dough to expand and become airy.",
                "tags": ["dough", "rise", "yeast", "science", "chemistry", "fermentation"]
            },
            {
                "category": "pizza_science",
                "title": "The Maillard Reaction",
                "content": "That golden-brown color and savory flavor on the crust and cheese comes from the **Maillard Reaction**. It's a chemical reaction between amino acids and reducing sugars that happens quickly above 280°F (140°C).",
                "tags": ["maillard", "reaction", "brown", "crust", "flavor", "science"]
            },
             {
                "category": "pizza_science",
                "title": "Ideal Oven Temperature",
                "content": "Professional pizza ovens run hot! Neapolitan pizza requires 800-900°F (430-480°C) to cook in 90 seconds. Home ovens should be cranked to their max (usually 500-550°F) for best results.",
                "tags": ["oven", "temp", "temperature", "heat", "cook", "science"]
            },

            # Debates
            {
                "category": "debates",
                "title": "Pineapple on Pizza?",
                "content": "The eternal debate! 🍍 Scientifically, the sweetness of pineapple cuts through the saltiness of the ham and cheese, creating a balanced 'agrodolce' profile. So yes, it belongs... if you want it to! (Team Hawaiian represent!)",
                "tags": ["pineapple", "fruit", "belong", "good", "bad", "debate", "opinion"]
            },
            {
                "category": "debates",
                "title": "Deep Dish vs. Thin Crust",
                "content": "Deep Dish (Chicago Style) is more like a savory pie with layers of cheese and sauce, eaten with a fork. Thin Crust (NY Style) is foldable and focuses on the dough-to-cheese ratio. Both are delicious; it just depends on your mood!",
                "tags": ["deep", "dish", "thin", "crust", "chicago", "ny", "style", "debate"]
            },
        ]
        
        for entry in menu_entries:
            self.add_entry(**entry)
    
    def add_entry(
        self,
        category: str,
        title: str,
        content: str,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """Add a new knowledge base entry."""
        self._id_counter += 1
        entry = {
            "id": self._id_counter,
            "category": category,
            "title": title,
            "content": content,
            "tags": tags or [],
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.entries.append(entry)
        return entry
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base with relevance ranking.
        Returns entries sorted by relevance score.
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        results = []
        
        for entry in self.entries:
            # Filter by category if specified
            if category and entry["category"] != category:
                continue
            
            # Calculate relevance score
            score = 0
            title_lower = entry["title"].lower()
            content_lower = entry["content"].lower()
            tags = [t.lower() for t in entry["tags"]]
            
            # Exact phrase match in title (highest weight)
            if query_lower in title_lower:
                score += 50
            
            # Exact phrase match in content
            if query_lower in content_lower:
                score += 30
            
            # Word matches in tags
            for word in query_words:
                if word in tags:
                    score += 20
                    
            # Word matches in title
            for word in query_words:
                if word in title_lower:
                    score += 10
                    
            # Word matches in content
            for word in query_words:
                if word in content_lower:
                    score += 5
            
            if score > 0:
                results.append({**entry, "_score": score})
        
        # Sort by score descending
        results.sort(key=lambda x: x["_score"], reverse=True)
        
        # Return top results without score
        return [{k: v for k, v in r.items() if k != "_score"} for r in results[:limit]]
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all entries in a category."""
        return [e for e in self.entries if e["category"] == category]
    
    def get_by_id(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """Get entry by ID."""
        for entry in self.entries:
            if entry["id"] == entry_id:
                return entry
        return None
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all entries."""
        return self.entries
    
    def update_entry(
        self,
        entry_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update an existing entry."""
        for entry in self.entries:
            if entry["id"] == entry_id:
                if title:
                    entry["title"] = title
                if content:
                    entry["content"] = content
                if tags:
                    entry["tags"] = tags
                entry["version"] += 1
                entry["updated_at"] = datetime.utcnow().isoformat()
                return entry
        return None
    
    def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry."""
        for i, entry in enumerate(self.entries):
            if entry["id"] == entry_id:
                self.entries.pop(i)
                return True
        return False


# Global knowledge base instance
knowledge_base = KnowledgeBase()
