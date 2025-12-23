// ==================== CONFIG ====================
const API_BASE = 'http://localhost:8000';

// ==================== STATE ====================
let currentView = 'home';
let orders = [];
let menuItems = [];
let analytics = {};
let cart = JSON.parse(localStorage.getItem('pizza_cart')) || [];
let filteredItems = [];

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initEventListeners();
    initCart();
    initChat();
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);

    // Load initial data
    loadMenu();
    loadAnalytics();
    loadOrders();

    updateCartUI();
});

// ==================== NAVIGATION ====================
function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.view;
            switchView(view);
        });
    });

    // Hero buttons
    document.getElementById('hero-order-btn')?.addEventListener('click', () => switchView('menu'));
    document.getElementById('hero-menu-btn')?.addEventListener('click', () => switchView('menu'));
}

function switchView(view) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.view === view);
        if (item.dataset.view === view) {
            item.setAttribute('aria-current', 'page');
        } else {
            item.removeAttribute('aria-current');
        }
    });

    // Update views
    document.querySelectorAll('.view').forEach(v => {
        v.classList.toggle('active', v.id === `${view}-view`);
    });

    currentView = view;

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==================== EVENT LISTENERS ====================
function initEventListeners() {
    // Refresh button
    document.getElementById('refresh-btn')?.addEventListener('click', () => {
        loadAnalytics();
        loadOrders();
        loadMenu();
        showToast('Data refreshed!', 'success');
    });

    // Status filter
    document.getElementById('status-filter')?.addEventListener('change', (e) => {
        renderOrdersTable(orders.filter(o => !e.target.value || o.status === e.target.value));
    });

    // Add menu item modal
    document.getElementById('add-item-btn')?.addEventListener('click', () => {
        document.getElementById('add-item-modal').classList.add('active');
    });

    document.getElementById('modal-close')?.addEventListener('click', () => {
        document.getElementById('add-item-modal').classList.remove('active');
    });

    document.getElementById('add-item-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await addMenuItem();
    });

    // Menu search
    document.getElementById('menu-search')?.addEventListener('input', (e) => {
        filterMenu(e.target.value);
    });

    // Category filter tabs
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.filter-tab').forEach(t => {
                t.classList.remove('active');
                t.setAttribute('aria-selected', 'false');
            });
            tab.classList.add('active');
            tab.setAttribute('aria-selected', 'true');
            filterMenuByCategory(tab.dataset.category);
        });
    });

    // Lightbox
    document.getElementById('lightbox-close')?.addEventListener('click', closeLightbox);
    document.getElementById('lightbox')?.addEventListener('click', (e) => {
        if (e.target.id === 'lightbox') closeLightbox();
    });

    // Checkout modal
    document.getElementById('checkout-btn')?.addEventListener('click', openCheckoutModal);
    document.getElementById('checkout-modal-close')?.addEventListener('click', closeCheckoutModal);
    document.getElementById('checkout-form')?.addEventListener('submit', handleCheckout);

    // Close modals on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeLightbox();
            closeCheckoutModal();
            document.getElementById('add-item-modal')?.classList.remove('active');
        }
    });
}

// ==================== CART ====================
function initCart() {
    // Cart FAB
    document.getElementById('cart-fab')?.addEventListener('click', toggleCart);
    document.getElementById('cart-close')?.addEventListener('click', toggleCart);
}

function toggleCart() {
    const sidebar = document.getElementById('cart-sidebar');
    sidebar.classList.toggle('open');
}

function addToCart(item) {
    const existing = cart.find(c => c.id === item.id);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({
            id: item.id,
            name: item.item,
            price: item.price,
            image: item.image_url,
            quantity: 1
        });
    }
    saveCart();
    updateCartUI();
    showToast(`${item.item} added to cart!`, 'success');

    // Animate FAB
    const fab = document.getElementById('cart-fab');
    fab.style.transform = 'scale(1.2)';
    setTimeout(() => fab.style.transform = '', 200);
}

function updateCartQuantity(itemId, delta) {
    const item = cart.find(c => c.id === itemId);
    if (item) {
        item.quantity += delta;
        if (item.quantity <= 0) {
            cart = cart.filter(c => c.id !== itemId);
        }
        saveCart();
        updateCartUI();
    }
}

function removeFromCart(itemId) {
    cart = cart.filter(c => c.id !== itemId);
    saveCart();
    updateCartUI();
}

function saveCart() {
    localStorage.setItem('pizza_cart', JSON.stringify(cart));
}

function updateCartUI() {
    const cartContainer = document.getElementById('cart-items');
    const cartCount = document.getElementById('cart-count');
    const cartTotal = document.getElementById('cart-total');
    const checkoutBtn = document.getElementById('checkout-btn');

    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    if (cartCount) cartCount.textContent = totalItems;
    if (cartTotal) cartTotal.textContent = `$${totalPrice.toFixed(2)}`;
    if (checkoutBtn) checkoutBtn.disabled = cart.length === 0;

    if (!cartContainer) return;

    if (cart.length === 0) {
        cartContainer.innerHTML = `
            <div class="cart-empty">
                <span class="cart-empty-icon">🛒</span>
                <p>Your cart is empty</p>
                <p class="cart-empty-hint">Add items from the menu</p>
            </div>
        `;
    } else {
        cartContainer.innerHTML = cart.map(item => `
            <div class="cart-item">
                <img src="${item.image || 'https://via.placeholder.com/60'}" alt="${item.name}" class="cart-item-image">
                <div class="cart-item-details">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">$${(item.price * item.quantity).toFixed(2)}</div>
                    <div class="cart-item-quantity">
                        <button class="qty-btn" onclick="updateCartQuantity(${item.id}, -1)" aria-label="Decrease quantity">−</button>
                        <span class="qty-value">${item.quantity}</span>
                        <button class="qty-btn" onclick="updateCartQuantity(${item.id}, 1)" aria-label="Increase quantity">+</button>
                    </div>
                </div>
                <button class="cart-item-remove" onclick="removeFromCart(${item.id})" aria-label="Remove item">🗑️</button>
            </div>
        `).join('');
    }
}

// ==================== CHECKOUT ====================
function openCheckoutModal() {
    if (cart.length === 0) return;

    const modal = document.getElementById('checkout-modal');
    const summary = document.getElementById('checkout-summary');
    const total = document.getElementById('checkout-total');

    summary.innerHTML = cart.map(item => `
        <div class="checkout-item">
            <span>${item.name} × ${item.quantity}</span>
            <span>$${(item.price * item.quantity).toFixed(2)}</span>
        </div>
    `).join('');

    const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    total.textContent = `$${totalPrice.toFixed(2)}`;

    modal.classList.add('active');
}

function closeCheckoutModal() {
    document.getElementById('checkout-modal')?.classList.remove('active');
}

async function handleCheckout(e) {
    e.preventDefault();

    const orderData = {
        customer_name: document.getElementById('customer-name').value,
        customer_phone: document.getElementById('customer-phone').value,
        customer_address: document.getElementById('customer-address').value,
        items: cart.map(item => ({
            menu_item_id: item.id,
            quantity: item.quantity
        }))
    };

    try {
        const result = await fetchAPI('/orders', {
            method: 'POST',
            body: JSON.stringify(orderData)
        });

        if (result) {
            cart = [];
            saveCart();
            updateCartUI();
            closeCheckoutModal();
            toggleCart();
            showToast(`Order #${result.id} placed successfully! 🎉`, 'success');
            loadOrders();
            loadAnalytics();

            // Reset form
            document.getElementById('checkout-form').reset();
        }
    } catch (error) {
        showToast('Failed to place order. Please try again.', 'error');
    }
}

// ==================== CHAT ====================
function initChat() {
    const toggle = document.getElementById('chat-toggle');
    const minimize = document.getElementById('chat-minimize');
    const window = document.getElementById('chat-window');
    const sendBtn = document.getElementById('chat-send-btn');
    const input = document.getElementById('chat-input');

    toggle?.addEventListener('click', () => {
        window.classList.toggle('open');
        toggle.style.display = window.classList.contains('open') ? 'none' : 'flex';
    });

    minimize?.addEventListener('click', () => {
        window.classList.remove('open');
        toggle.style.display = 'flex';
    });

    sendBtn?.addEventListener('click', sendChatMessage);
    input?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });

    // Suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const message = chip.dataset.message;
            document.getElementById('chat-input').value = message;
            sendChatMessage();
        });
    });
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    // Add user message
    addChatMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    showTypingIndicator();

    // Get bot response with artificial delay
    const [result] = await Promise.all([
        fetchAPI('/chat', {
            method: 'POST',
            body: JSON.stringify({ message, user_id: 'web-user' })
        }),
        new Promise(resolve => setTimeout(resolve, 1500)) // 1.5s delay for "thinking"
    ]);

    removeTypingIndicator();

    if (result) {
        addChatMessage(result.response, 'bot');

        // If an order was placed, refresh the dashboard data
        if (result.action === 'confirm_order' && result.data && result.data.order_id) {
            loadOrders();
            loadAnalytics();
        }
    } else {
        addChatMessage('Sorry, I had trouble processing that. Please try again!', 'bot');
    }
}

function showTypingIndicator() {
    const container = document.getElementById('chat-messages');
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    container.appendChild(indicator);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

function addChatMessage(text, sender) {
    const container = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.innerHTML = `<div class="message-content">${formatChatMessage(text)}</div>`;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

// ==================== LIGHTBOX ====================
function openLightbox(imageSrc, caption) {
    const lightbox = document.getElementById('lightbox');
    const img = document.getElementById('lightbox-img');
    const cap = document.getElementById('lightbox-caption');

    img.src = imageSrc;
    img.alt = caption;
    cap.textContent = caption;
    lightbox.classList.add('active');
}

function closeLightbox() {
    document.getElementById('lightbox')?.classList.remove('active');
}

// ==================== TOAST NOTIFICATIONS ====================
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ==================== API CALLS ====================
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`API Error: ${endpoint}`, error);
        return null;
    }
}

async function loadAnalytics() {
    analytics = await fetchAPI('/analytics/summary') || {
        orders_today: 0,
        revenue_today: 0,
        pending_orders: 0,
        status_breakdown: {},
        category_revenue: {}
    };

    const ordersEl = document.getElementById('orders-today');
    const revenueEl = document.getElementById('revenue-today');
    const pendingEl = document.getElementById('pending-orders');

    if (ordersEl) ordersEl.textContent = analytics.orders_today;
    if (revenueEl) revenueEl.textContent = analytics.revenue_today.toFixed(2);
    if (pendingEl) pendingEl.textContent = analytics.pending_orders;

    renderCharts();
}

async function loadOrders() {
    orders = await fetchAPI('/orders') || [];
    renderOrdersTable(orders);
    renderRecentOrders(orders.slice(0, 5));
}

async function loadMenu() {
    menuItems = await fetchAPI('/menu') || [];

    // Seed if empty
    if (menuItems.length === 0) {
        await fetchAPI('/seed', { method: 'POST' });
        menuItems = await fetchAPI('/menu') || [];
    }

    filteredItems = menuItems;
    renderMenuGrid(menuItems);

    // Select popular picks from diverse categories
    const categories = ['Pizza', 'Side', 'Drink', 'Dessert'];
    const featuredItems = [];

    categories.forEach(cat => {
        const catItems = menuItems.filter(item => item.category === cat);
        if (catItems.length > 0) {
            // Pick a random item from each category to show variety
            const randomItem = catItems[Math.floor(Math.random() * catItems.length)];
            featuredItems.push(randomItem);
        }
    });

    renderFeaturedGrid(featuredItems);
}

function filterMenu(searchTerm) {
    const term = searchTerm.toLowerCase();
    filteredItems = menuItems.filter(item =>
        item.item.toLowerCase().includes(term) ||
        item.description?.toLowerCase().includes(term) ||
        item.category.toLowerCase().includes(term)
    );
    renderMenuGrid(filteredItems);
}

function filterMenuByCategory(category) {
    if (category === 'all') {
        filteredItems = menuItems;
    } else {
        filteredItems = menuItems.filter(item => item.category === category);
    }
    renderMenuGrid(filteredItems);
}

async function updateOrderStatus(orderId, status) {
    const result = await fetchAPI(`/orders/${orderId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status })
    });

    if (result) {
        loadOrders();
        loadAnalytics();
        showToast(`Order #${orderId} updated to ${status}`, 'success');
    }
}

async function addMenuItem() {
    const data = {
        item: document.getElementById('item-name').value,
        price: parseFloat(document.getElementById('item-price').value),
        category: document.getElementById('item-category').value,
        description: document.getElementById('item-description').value
    };

    const result = await fetchAPI('/menu', {
        method: 'POST',
        body: JSON.stringify(data)
    });

    if (result) {
        document.getElementById('add-item-modal').classList.remove('active');
        document.getElementById('add-item-form').reset();
        loadMenu();
        showToast('Menu item added!', 'success');
    }
}

// ==================== RENDER FUNCTIONS ====================
function renderCharts() {
    // Status Chart
    const statusCtx = document.getElementById('statusChart')?.getContext('2d');
    if (!statusCtx) return;

    const statusData = analytics.status_breakdown || {};

    if (window.statusChart) window.statusChart.destroy();
    window.statusChart = new Chart(statusCtx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(statusData),
            datasets: [{
                data: Object.values(statusData),
                backgroundColor: [
                    '#fbbf24', // Pending
                    '#4d9fff', // Confirmed
                    '#8b5cf6', // Preparing
                    '#00d98b', // Ready
                    '#00f5a0', // Delivered
                    '#ef4444'  // Cancelled
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#a0a0b0' } }
            }
        }
    });

    // Category Chart
    const categoryCtx = document.getElementById('categoryChart')?.getContext('2d');
    if (!categoryCtx) return;

    const categoryData = analytics.category_revenue || {};

    if (window.categoryChart) window.categoryChart.destroy();
    window.categoryChart = new Chart(categoryCtx, {
        type: 'bar',
        data: {
            labels: Object.keys(categoryData),
            datasets: [{
                label: 'Revenue ($)',
                data: Object.values(categoryData),
                backgroundColor: 'rgba(255, 107, 53, 0.8)',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { ticks: { color: '#a0a0b0' }, grid: { display: false } },
                y: { ticks: { color: '#a0a0b0' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });
}

function renderMenuGrid(items) {
    const grid = document.getElementById('menu-grid');
    if (!grid) return;

    if (items.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 60px; color: var(--text-secondary);">
                <p style="font-size: 48px; margin-bottom: 16px;">🔍</p>
                <p>No items found</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = items.map(item => `
        <div class="menu-card" role="listitem" data-id="${item.id}">
            <div class="menu-card-image">
                <img src="${item.image_url || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400'}" 
                     alt="${item.item}" 
                     loading="lazy"
                     onclick="openLightbox('${item.image_url || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800'}', '${item.item}')">
                <div class="menu-card-overlay"></div>
                <button class="menu-card-view-btn" onclick="openLightbox('${item.image_url || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800'}', '${item.item}')">
                    View Image
                </button>
                <span class="menu-card-category">${item.category}</span>
            </div>
            <div class="menu-card-content">
                <div class="menu-card-header">
                    <span class="menu-card-name">${item.item}</span>
                    <span class="menu-card-price">$${item.price.toFixed(2)}</span>
                </div>
                <p class="menu-card-description">${item.description || 'Delicious and freshly made!'}</p>
                <div class="menu-card-footer">
                    <button class="btn-add-cart" onclick='addToCart(${JSON.stringify(item).replace(/'/g, "\\'")})'>
                        <span>🛒</span> Add to Cart
                    </button>
                    <button class="btn-quick-view" onclick="openLightbox('${item.image_url || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800'}', '${item.item}')" aria-label="Quick view">
                        👁️
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function renderFeaturedGrid(items) {
    const grid = document.getElementById('featured-grid');
    if (!grid) return;

    grid.innerHTML = items.map(item => `
        <div class="menu-card" data-id="${item.id}">
            <div class="menu-card-image">
                <img src="${item.image_url || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400'}" 
                     alt="${item.item}" 
                     loading="lazy">
                <div class="menu-card-overlay"></div>
                <span class="menu-card-category">${item.category}</span>
            </div>
            <div class="menu-card-content">
                <div class="menu-card-header">
                    <span class="menu-card-name">${item.item}</span>
                    <span class="menu-card-price">$${item.price.toFixed(2)}</span>
                </div>
                <p class="menu-card-description">${item.description || 'Delicious and freshly made!'}</p>
                <div class="menu-card-footer">
                    <button class="btn-add-cart" onclick='addToCart(${JSON.stringify(item).replace(/'/g, "\\'")})'>
                        <span>🛒</span> Add to Cart
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function renderOrdersTable(orderList) {
    const tbody = document.getElementById('orders-body');
    if (!tbody) return;

    tbody.innerHTML = orderList.map(order => `
        <tr>
            <td>#${order.id}</td>
            <td>${order.customer_name}</td>
            <td>${order.customer_phone || '-'}</td>
            <td>${order.items?.map(i => i.menu_item?.item || 'Item').join(', ') || '-'}</td>
            <td>$${order.total_amount.toFixed(2)}</td>
            <td><span class="status-badge status-${order.status.toLowerCase()}">${order.status}</span></td>
            <td>${getActionButtons(order)}</td>
        </tr>
    `).join('');
}

function renderRecentOrders(orderList) {
    const tbody = document.getElementById('recent-orders-body');
    if (!tbody) return;

    tbody.innerHTML = orderList.map(order => `
        <tr>
            <td>#${order.id}</td>
            <td>${order.customer_name}</td>
            <td>${order.items?.length || 0} items</td>
            <td>$${order.total_amount.toFixed(2)}</td>
            <td><span class="status-badge status-${order.status.toLowerCase()}">${order.status}</span></td>
            <td>${formatTime(order.created_at)}</td>
        </tr>
    `).join('');
}

function getActionButtons(order) {
    const actions = {
        'Pending': `<button class="action-btn confirm" onclick="updateOrderStatus(${order.id}, 'Confirmed')">Confirm</button>`,
        'Confirmed': `<button class="action-btn prepare" onclick="updateOrderStatus(${order.id}, 'Preparing')">Prepare</button>`,
        'Preparing': `<button class="action-btn ready" onclick="updateOrderStatus(${order.id}, 'Ready')">Ready</button>`,
        'Ready': `<button class="action-btn deliver" onclick="updateOrderStatus(${order.id}, 'Delivered')">Deliver</button>`
    };

    let buttons = actions[order.status] || '';
    if (order.status !== 'Cancelled' && order.status !== 'Delivered') {
        buttons += `<button class="action-btn cancel" onclick="updateOrderStatus(${order.id}, 'Cancelled')">Cancel</button>`;
    }
    return buttons;
}

// ==================== UTILS ====================
function updateCurrentTime() {
    const el = document.getElementById('current-time');
    if (el) {
        const now = new Date();
        el.textContent = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
}

function formatTime(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function formatChatMessage(text) {
    // Convert markdown-like formatting to HTML
    let html = text
        // Escape HTML first (but preserve newlines)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        // Bold: **text**
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        // Italic: _text_
        .replace(/_([^_]+)_/g, '<em>$1</em>')
        // Bullet points
        .replace(/^• /gm, '• ')
        // Convert newlines to <br>
        .replace(/\n/g, '<br>');

    return html;
}

// ==================== GLOBAL FUNCTIONS ====================
// Make functions globally available for inline onclick handlers
window.addToCart = addToCart;
window.updateCartQuantity = updateCartQuantity;
window.removeFromCart = removeFromCart;
window.openLightbox = openLightbox;
window.updateOrderStatus = updateOrderStatus;
