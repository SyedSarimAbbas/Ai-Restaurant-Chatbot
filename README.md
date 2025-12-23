# 🍕 AI Pizza Palace - Restaurant Chatbot

AI-Operated Restaurant Chatbot System with Knowledge Base integration, modern responsive UI, and full ordering workflow.

## ✨ Features

### 🤖 AI-Powered Chatbot
- **Knowledge Base Integration** - Context-aware responses about ingredients, nutrition, policies, promotions
- **Intent Detection** - Understands greetings, menu queries, orders, tracking, and support requests
- **Order Management** - Add items to cart, confirm orders, track status via chat
- **Smart Suggestions** - Quick-action chips for common queries

### 🍕 Modern Frontend
- **Hero Section** - Stunning pizza shop cover with animated CTAs
- **Card-Based Menu** - High-resolution images with hover effects and animations
- **Dynamic Filtering** - Search and filter by category (Pizza, Sides, Drinks, Dessert)
- **Shopping Cart** - Persistent cart with localStorage, quantity controls, checkout flow
- **Lightbox Gallery** - Click images to view full-size
- **Toast Notifications** - Real-time feedback on actions
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Accessibility** - ARIA labels, keyboard navigation, focus states

### 📊 Admin Dashboard
- **Live Analytics** - Orders today, revenue, pending orders
- **Charts** - Status breakdown, category revenue
- **Order Management** - Update status, track workflow
- **Menu Management** - Add new items

---

## 🚀 Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend runs at: **http://localhost:8000**

### Frontend
Open `frontend/index.html` in your browser, or serve via:
```bash
cd frontend
python -m http.server 3000
```
Then visit: **http://localhost:3000**

---

## 📚 API Endpoints

### Menu
- `GET /menu` - List all menu items (with images)
- `GET /menu?category=Pizza` - Filter by category
- `POST /menu` - Add new item (admin)

### Orders
- `GET /orders` - List all orders
- `POST /orders` - Create new order
- `PUT /orders/{id}/status` - Update order status

### Chat
- `POST /chat` - Send message to AI chatbot

### Knowledge Base
- `GET /kb` - List all KB entries
- `GET /kb/search?q=pepperoni` - Search KB with relevance ranking
- `POST /kb` - Add KB entry

### Analytics
- `GET /analytics/summary` - Dashboard statistics

### Utils
- `POST /seed` - Seed database with sample menu items

---

## 🧠 Knowledge Base

The chatbot includes a rich knowledge base covering:

| Category | Topics |
|----------|--------|
| **Ingredients** | Full ingredient lists for each pizza and item |
| **Nutrition** | Calorie information, allergen warnings |
| **Policies** | Delivery, refunds, cancellation, payments |
| **Promotions** | Current deals, loyalty program |
| **FAQs** | Hours, customization, tracking, contact info |
| **Ordering** | How to order, group/catering orders |
| **Delivery** | Areas, times, express options |

### Example Chat Queries
- "What ingredients are in the pepperoni pizza?"
- "Do you have any promotions?"
- "What are your delivery times?"
- "Are there any allergens in your food?"
- "I want to order a Margherita pizza"

---

## 🛠 Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Python
- **Frontend**: Vanilla HTML/CSS/JS with modern SPA patterns
- **Database**: SQLite
- **Images**: Unsplash CDN (high-resolution, royalty-free)
- **Charts**: Chart.js

---

## 📁 Project Structure

```
├── backend/
│   ├── main.py           # FastAPI app with all endpoints
│   ├── chatbot.py        # AI chatbot with intent detection
│   ├── knowledge_base.py # KB storage and search
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # DB connection
│   └── requirements.txt
├── frontend/
│   ├── index.html        # SPA with hero, menu, dashboard
│   ├── styles.css        # Modern CSS with animations
│   └── app.js            # Dynamic functionality
└── README.md
```

---

## 🎨 Design Highlights

- **Glassmorphism** - Frosted glass cards with backdrop blur
- **Micro-animations** - Hover effects, transitions, loading states
- **Dark Theme** - Easy on the eyes with vibrant accent colors
- **Typography** - Inter + Playfair Display for modern/classic mix

---

## 📝 License

This project uses royalty-free images from [Unsplash](https://unsplash.com).
