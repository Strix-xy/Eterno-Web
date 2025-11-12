document.addEventListener("DOMContentLoaded", function() {
  if (document.getElementById("cartCount")) {
    updateCartCount();
  }
});

async function updateCartCount() {
  try {
    const response = await fetch("/cart/count");
    const data = await response.json();
    const countEl = document.getElementById("cartCount");
    if (countEl && data.count > 0) {
      countEl.textContent = data.count;
      countEl.style.display = "flex";
    } else if (countEl) {
      countEl.style.display = "none";
    }
  } catch (error) {
  }
}

function confirmLogout() {
  if (confirm("Are you sure you want to logout?")) {
    const logoutLink = document.querySelector("#logoutUrl");
    const logoutUrl = logoutLink ? logoutLink.dataset.url : window.logoutUrl || "/logout";
    window.location.href = logoutUrl;
  }
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  const newTheme = currentTheme === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
  updateThemeButton(newTheme);
}

function updateThemeButton(theme) {
  const icon = document.getElementById("themeIcon");
  if (icon) {
    if (theme === "light") {
      icon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
    } else {
      icon.innerHTML = '<circle cx="12" cy="12" r="5"/><path d="M12 1v3m0 16v3M5.64 5.64l2.12 2.12m8.48 8.48l2.12 2.12M1 12h3m16 0h3M5.64 18.36l2.12-2.12m8.48-8.48l2.12-2.12"/>';
    }
  }
}

window.addEventListener("DOMContentLoaded", function () {
  const savedTheme = localStorage.getItem("theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeButton(savedTheme);
});

async function updateQuantity(cartId, change) {
  try {
    const response = await fetch(`/cart/update/${cartId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ change: change }),
    });

    const data = await response.json();

    if (data.success) {
      location.reload();
    } else {
      alert("Error: " + data.error);
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

async function removeItem(cartId) {
  if (!confirm("Remove this item from cart?")) {
    return;
  }

  try {
    const response = await fetch(`/cart/remove/${cartId}`, {
      method: "DELETE",
    });

    const data = await response.json();

    if (data.success) {
      location.reload();
    } else {
      alert("Error: " + data.error);
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

window.voucherApplied = false;
window.baseSubtotal = 0;

function showPaymentDetails() {
  const paymentMethod = document.querySelector('input[name="payment"]:checked');
  if (!paymentMethod) return;
  
  const paymentValue = paymentMethod.value;
  const deliveryAddressInput = document.getElementById("deliveryAddress");
  if (deliveryAddressInput) {
    deliveryAddressInput.required = true;
  }
  const paymentDetails = document.getElementById("paymentDetails");
  if (paymentDetails) paymentDetails.style.display = "block";
  const codDetails = document.getElementById("codDetails");
  const gcashDetails = document.getElementById("gcashDetails");
  const cardDetails = document.getElementById("cardDetails");
  const paypalDetails = document.getElementById("paypalDetails");
  const deliveryDetails = document.getElementById("deliveryDetails");
  if (deliveryDetails) deliveryDetails.classList.add("show");

  if (codDetails) codDetails.classList.remove("show");
  if (gcashDetails) gcashDetails.classList.remove("show");
  if (cardDetails) cardDetails.classList.remove("show");
  if (paypalDetails) paypalDetails.classList.remove("show");
  if (paymentValue === "cod") {
    if (paymentDetails) paymentDetails.style.display = "block";
    if (codDetails) codDetails.classList.add("show");
  } else if (paymentValue === "gcash") {
    if (paymentDetails) paymentDetails.style.display = "block";
    if (gcashDetails) gcashDetails.classList.add("show");
    const gcashNumberInput = document.getElementById("gcashNumber");
    const gcashAccountNameInput = document.getElementById("gcashAccountName");
    if (gcashNumberInput) gcashNumberInput.required = true;
    if (gcashAccountNameInput) gcashAccountNameInput.required = true;
  } else if (paymentValue === "credit_card") {
    if (paymentDetails) paymentDetails.style.display = "block";
    if (cardDetails) cardDetails.classList.add("show");
    const cardNumber = document.getElementById("cardNumber");
    const cardExpiry = document.getElementById("cardExpiry");
    const cardCVV = document.getElementById("cardCVV");
    if (cardNumber) cardNumber.required = true;
    if (cardExpiry) cardExpiry.required = true;
    if (cardCVV) cardCVV.required = true;
  } else if (paymentValue === "paypal") {
    if (paymentDetails) paymentDetails.style.display = "block";
    if (paypalDetails) paypalDetails.classList.add("show");
    const paypalEmail = document.getElementById("paypalEmail");
    const paypalName = document.getElementById("paypalName");
    if (paypalEmail) paypalEmail.required = true;
    if (paypalName) paypalName.required = true;
  } else {
    if (paymentDetails) paymentDetails.style.display = "none";
  }
}

function applyVoucher() {
  const voucherCode = document.getElementById("voucherCode");
  if (!voucherCode) return;
  
  const code = voucherCode.value.trim();
  if (code) {
    window.voucherApplied = true;
    const voucherAppliedEl = document.getElementById("voucherApplied");
    if (voucherAppliedEl) voucherAppliedEl.style.display = "block";
    updateTotal();
  } else {
    alert("Please enter a voucher code");
  }
}

function removeVoucher() {
  window.voucherApplied = false;
  const voucherAppliedEl = document.getElementById("voucherApplied");
  if (voucherAppliedEl) voucherAppliedEl.style.display = "none";
  const voucherCode = document.getElementById("voucherCode");
  if (voucherCode) voucherCode.value = "";
  updateTotal();
}

function updateTotal() {
  const voucherRow = document.getElementById("voucherDiscountRow");
  const totalEl = document.getElementById("totalDisplay");
  let subtotal = window.baseSubtotal || 0;
  let discount = window.voucherApplied ? 100 : 0;
  let total = subtotal - discount;
  
  if (window.voucherApplied && voucherRow) {
    voucherRow.style.display = "flex";
  } else if (voucherRow) {
    voucherRow.style.display = "none";
  }
  
  if (totalEl) {
    totalEl.textContent = `₱${total.toFixed(2)}`;
  }
}

function checkoutBtnHandler(btn) {
  const paymentMethod = document.querySelector('input[name="payment"]:checked');
  if (!paymentMethod) {
    alert("Please select a payment method");
    return;
  }

  const paymentValue = paymentMethod.value;
  const addressInput = document.getElementById("deliveryAddress");
  if (!addressInput || !addressInput.value.trim()) {
    alert("Please enter your delivery address");
    if (addressInput) {
      addressInput.focus();
    }
    return;
  }

  const deliveryAddress = addressInput.value.trim();
  let paymentDetails = {
    address: deliveryAddress,
    customer_address: deliveryAddress
  };

  if (paymentValue === "gcash") {
    const gcashNumber = document.getElementById("gcashNumber");
    const gcashAccountName = document.getElementById("gcashAccountName");
    if (!gcashNumber || !gcashNumber.value.trim()) {
      alert("Please enter your GCash number");
      return;
    }
    if (!gcashAccountName || !gcashAccountName.value.trim()) {
      alert("Please enter your GCash account name");
      return;
    }
    paymentDetails.gcash_number = gcashNumber.value.trim();
    paymentDetails.gcash_account_name = gcashAccountName.value.trim();
  } else if (paymentValue === "credit_card") {
    const cardType = document.querySelector('input[name="cardType"]:checked');
    const cardNumber = document.getElementById("cardNumber");
    const cardExpiry = document.getElementById("cardExpiry");
    const cardCVV = document.getElementById("cardCVV");
    if (!cardNumber || !cardNumber.value.trim() || !cardExpiry || !cardExpiry.value.trim() || !cardCVV || !cardCVV.value.trim()) {
      alert("Please fill in all card details");
      return;
    }
    paymentDetails.card_type = cardType ? cardType.value : "credit";
    paymentDetails.card_number = cardNumber.value.trim();
    paymentDetails.card_expiry = cardExpiry.value.trim();
    paymentDetails.card_cvv = cardCVV.value.trim();
  } else if (paymentValue === "paypal") {
    const paypalEmail = document.getElementById("paypalEmail");
    const paypalName = document.getElementById("paypalName");
    if (!paypalEmail || !paypalEmail.value.trim() || !paypalName || !paypalName.value.trim()) {
      alert("Please fill in all PayPal details");
      return;
    }
    paymentDetails.paypal_email = paypalEmail.value.trim();
    paymentDetails.paypal_name = paypalName.value.trim();
  }

  // Show confirmation summary
  showConfirmationSummary(paymentValue, paymentDetails);
}

function showConfirmationSummary(paymentMethod, paymentDetails) {
  const subtotal = window.baseSubtotal || 0;
  const discount = window.voucherApplied ? 100 : 0;
  const deliveryFee = 50 + Math.floor(Math.random() * 51); // Random between 50-100
  const total = subtotal - discount + deliveryFee;

  let summary = `ORDER CONFIRMATION\n\n`;
  summary += `Subtotal: ₱${subtotal.toFixed(2)}\n`;
  if (discount > 0) {
    summary += `Voucher Discount: -₱${discount.toFixed(2)}\n`;
  }
  summary += `Delivery Fee: ₱${deliveryFee.toFixed(2)}\n`;
  summary += `Total: ₱${total.toFixed(2)}\n\n`;
  summary += `Payment Method: ${paymentMethod.toUpperCase()}\n`;
  if (paymentDetails.customer_address || paymentDetails.address) {
    summary += `Delivery Address: ${paymentDetails.customer_address || paymentDetails.address}\n`;
  }
  
  if (paymentMethod === "gcash") {
    summary += `GCash Number: ${paymentDetails.gcash_number}\n`;
    summary += `Account Name: ${paymentDetails.gcash_account_name}\n`;
  } else if (paymentMethod === "credit_card") {
    summary += `Card Type: ${paymentDetails.card_type.toUpperCase()}\n`;
    summary += `Card: ****${paymentDetails.card_number.slice(-4)}\n`;
  } else if (paymentMethod === "paypal") {
    summary += `PayPal: ${paymentDetails.paypal_email}\n`;
  }

  if (confirm(summary + "\n\nConfirm order?")) {
    proceedCheckout(paymentMethod, paymentDetails, deliveryFee);
  }
}

async function proceedCheckout(paymentMethod, paymentDetails, deliveryFee) {
  try {
    const subtotal = window.baseSubtotal || 0;
    const discount = window.voucherApplied ? 100 : 0;
    const total = subtotal - discount + deliveryFee;

    const response = await fetch("/checkout", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        payment_method: paymentMethod,
        customer_address: paymentDetails.customer_address || paymentDetails.address || "",
        gcash_number: paymentDetails.gcash_number || "",
        gcash_account_name: paymentDetails.gcash_account_name || "",
        card_type: paymentDetails.card_type || "",
        card_number: paymentDetails.card_number || "",
        card_expiry: paymentDetails.card_expiry || "",
        card_cvv: paymentDetails.card_cvv || "",
        paypal_email: paymentDetails.paypal_email || "",
        paypal_name: paymentDetails.paypal_name || "",
        voucher_applied: window.voucherApplied,
        delivery_fee: deliveryFee,
        total: total,
      }),
    });

    const data = await response.json();

    if (data.success) {
      alert("Order placed successfully! Generating receipt...");
      window.open(`/receipt/${data.order_id}`, "_blank");
      window.location.href = "/shop";
    } else {
      alert("Error: " + data.error);
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

window.addEventListener("load", function() {
  if (document.getElementById("paymentDetails")) {
    showPaymentDetails();
  }
});

document.addEventListener("DOMContentLoaded", function() {
  const filterButtons = document.querySelectorAll(".filter-btn");
  const productCards = document.querySelectorAll(".product-card");

  filterButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const category = btn.dataset.category;

      filterButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      productCards.forEach((card) => {
        if (category === "all" || card.dataset.category === category) {
          card.style.display = "block";
        } else {
          card.style.display = "none";
        }
      });
    });
  });
});
async function addToCartShop(productId) {
  try {
    const response = await fetch("/cart/add", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        product_id: productId,
        quantity: 1,
      }),
    });

    const data = await response.json();

    if (data.success) {
      showNotification("Item added to cart!");
      updateCartCount();
    } else if (response.status === 401) {
      if (
        confirm(
          "Please login to add items to cart. Would you like to go to the login page?"
        )
      ) {
        window.location.href = window.loginUrl || "/login";
      }
    } else {
      alert("Error: " + data.error);
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

function showNotification(message, type = "success") {
  let notification = document.getElementById("notification");
  
  if (!notification) {
    notification = document.createElement("div");
    notification.id = "notification";
    notification.className = "notification";
    document.body.appendChild(notification);
  }
  
  notification.textContent = message;
  notification.className = `notification notification-${type}`;
  notification.classList.add("show");

  setTimeout(() => {
    notification.classList.remove("show");
  }, 3000);
}

let currentFilter = "all";
let allTransactions = [];

async function viewOrders() {
  const modal = document.getElementById("ordersModal");
  const container = document.getElementById("ordersTableContainer");
  
  if (modal) modal.classList.add("active");
  
  try {
    const response = await fetch("/admin/orders?limit=200");
    const data = await response.json();
    if (data.success) {
      allTransactions = data.transactions || [];
      displayOrders(allTransactions);
      
      if (container) {
        const existingMsg = container.querySelector(".orders-info-message");
        if (existingMsg) existingMsg.remove();
        
        const totals = data.totals || {};
        const combinedTotal = totals.combined ?? allTransactions.length;
        const infoMsg = document.createElement("div");
        infoMsg.className = "orders-info-message";
        infoMsg.style.cssText = "text-align: center; padding: 1rem; margin-top: 1rem; color: var(--text-gray); font-size: 0.9rem; border-top: 1px solid var(--border-color);";
        let summaryText = `Showing ${allTransactions.length} recent transactions (Customer: ${totals.customer_orders ?? 0} | POS: ${totals.pos_sales ?? 0} | Combined: ${combinedTotal}).`;
        if (combinedTotal > allTransactions.length) {
          summaryText += " Use filters to narrow down results.";
        }
        infoMsg.textContent = summaryText;
        container.appendChild(infoMsg);
      }
    } else {
      if (container) {
        container.innerHTML = `<p style="text-align: center; padding: 2rem; color: #ff4444;">Error: ${data.error}</p>`;
      } else {
        alert("Error loading orders: " + data.error);
      }
    }
  } catch (error) {
    if (container) {
      container.innerHTML = `<p style="text-align: center; padding: 2rem; color: #ff4444;">Error: ${error.message}</p>`;
    } else {
      alert("Error loading orders: " + error.message);
    }
  }
}

function filterOrders(filter, button) {
  currentFilter = filter;
  document.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.classList.remove("active");
  });
  if (button) {
    button.classList.add("active");
  } else {
    const buttons = document.querySelectorAll(".filter-btn");
    buttons.forEach((btn) => {
      if (btn.textContent.trim().includes(filter.toUpperCase())) {
        btn.classList.add("active");
      }
    });
  }

  let filteredTransactions = allTransactions;
  if (filter === "paid") {
    filteredTransactions = allTransactions.filter((transaction) => {
      const status = (transaction.status || "").toLowerCase();
      if (transaction.record_type === "pos_sale") {
        return true;
      }
      return status === "completed" || status === "paid";
    });
  } else if (filter === "pending") {
    filteredTransactions = allTransactions.filter(
      (transaction) =>
        transaction.record_type === "customer_order" &&
        (transaction.status || "").toLowerCase() === "pending"
    );
  }
  
  displayOrders(filteredTransactions);
}

function displayOrders(transactions) {
  const tbody = document.getElementById("ordersTableBody");
  if (!tbody) return;
  if (!transactions || transactions.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="8" style="text-align: center; padding: 2rem;">No orders found</td></tr>';
    return;
  }

  tbody.innerHTML = transactions
    .map((transaction) => {
      const isPosSale = transaction.record_type === "pos_sale";
      const statusValue = (transaction.status || (isPosSale ? "completed" : "")).toLowerCase();
      const statusClass =
        statusValue === "completed" || statusValue === "paid"
          ? "status-paid"
          : statusValue === "pending"
          ? "status-pending"
          : "";
      const statusLabel = isPosSale
        ? "COMPLETED"
        : (transaction.status || "N/A").toUpperCase();
      const paymentLabel = (transaction.payment_method || (isPosSale ? "cash" : "n/a")).toUpperCase();
      const reference = transaction.reference || `#${transaction.id}`;
      const badgeClass = isPosSale ? "badge-pos" : "badge-customer";
      const badgeLabel = isPosSale ? "POS" : "ONLINE";
      const dateDisplay = transaction.created_at_display || transaction.created_at || "";
      const totalAmount = parseFloat(transaction.total_amount || 0).toFixed(2);
      const customerName = transaction.customer_name || (isPosSale ? "POS Walk-in" : "N/A");
      const changeStatusCell = isPosSale
        ? '<td style="text-align: center; color: var(--text-gray);">—</td>'
        : `<td>
            <select class="status-select" data-order-id="${transaction.id}" onchange="updateOrderStatus(${transaction.id}, this.value)">
              <option value="pending" ${statusValue === "pending" ? "selected" : ""}>PENDING</option>
              <option value="completed" ${statusValue === "completed" || statusValue === "paid" ? "selected" : ""}>COMPLETED</option>
            </select>
          </td>`;
      return `
        <tr>
          <td>
            <span class="transaction-badge ${badgeClass}">${badgeLabel}</span>
            ${reference}
          </td>
          <td>${dateDisplay}</td>
          <td>${customerName}</td>
          <td>₱${totalAmount}</td>
          <td class="${statusClass}">${statusLabel}</td>
          <td>${paymentLabel}</td>
          <td><button class="order-details-btn" onclick="viewOrderDetails(${
            transaction.id
          })">VIEW DETAILS</button></td>
          ${changeStatusCell}
        </tr>
      `;
    })
    .join("");
}

async function viewOrderDetails(orderId) {
  try {
    const response = await fetch(`/admin/orders/${orderId}`);
    const data = await response.json();
    if (data.success) {
      displayTransactionDetails(data.transaction, data.record_type);
      const modal = document.getElementById("orderDetailsModal");
      if (modal) modal.classList.add("active");
    } else {
      alert("Error loading order details: " + data.error);
    }
  } catch (error) {
    alert("Error loading order details: " + error.message);
  }
}

function displayTransactionDetails(transaction, recordType) {
  if (!transaction) return;
  const container = document.getElementById("orderDetailsContent");
  if (!container) return;

  const isPosSale = recordType === "pos_sale" || transaction.record_type === "pos_sale";
  const items = Array.isArray(transaction.items) ? transaction.items : [];
  const dateDisplay = transaction.created_at_display || transaction.created_at || "";
  const statusValue = (transaction.status || (isPosSale ? "completed" : "")).toUpperCase();
  const statusClass =
    statusValue === "COMPLETED" || statusValue === "PAID"
      ? "status-paid"
      : statusValue === "PENDING"
      ? "status-pending"
      : "";
  const paymentMethod = (transaction.payment_method || (isPosSale ? "cash" : "n/a")).toUpperCase();
  const subtotal = parseFloat(transaction.subtotal || 0);
  const shippingFee = parseFloat(transaction.shipping_fee || 0);
  const discountAmount = parseFloat(transaction.discount_amount || 0);
  const discountLabel = transaction.discount_type
    ? transaction.discount_type.toUpperCase()
    : "DISCOUNT";
  const total = parseFloat(transaction.total_amount || 0);
  const processedBy = transaction.processed_by || (isPosSale ? "Admin" : "Online Checkout");
  const reference = transaction.reference || `#${transaction.id}`;
  const customerName = transaction.customer_name || (isPosSale ? "POS Walk-in" : "N/A");
  const customerEmail = transaction.customer_email || "";
  const customerAddress = transaction.customer_address || "";
  
  const itemRows =
    items && items.length
      ? items
          .map((item) => {
            const name = item.product_name || item.name || "Item";
            const quantity = parseFloat(item.quantity || 0);
            const price = parseFloat(item.price || 0);
            const lineTotal = price * quantity;
            return `
              <tr style="border-bottom: 1px solid var(--border-color);">
                <td style="padding: 0.5rem;">${name}</td>
                <td style="padding: 0.5rem; text-align: right;">${quantity}</td>
                <td style="padding: 0.5rem; text-align: right;">₱${price.toFixed(2)}</td>
                <td style="padding: 0.5rem; text-align: right;">₱${lineTotal.toFixed(2)}</td>
              </tr>
            `;
          })
          .join("")
      : `<tr><td colspan="4" style="padding: 1rem; text-align: center; color: var(--text-gray);">No items recorded.</td></tr>`;
  
  const discountRow =
    discountAmount > 0
      ? `<p style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
          <span>Discount (${discountLabel}):</span>
          <span>-₱${discountAmount.toFixed(2)}</span>
        </p>`
      : "";
  
  const shippingRow = !isPosSale
    ? `<p style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span>Shipping Fee:</span>
        <span>₱${shippingFee.toFixed(2)}</span>
      </p>`
    : "";
  
  const customerDetails = isPosSale
    ? `<p><strong>Customer:</strong> POS Walk-in</p>`
    : `
        <p><strong>Customer:</strong> ${customerName}</p>
        ${customerEmail ? `<p><strong>Email:</strong> ${customerEmail}</p>` : ""}
        ${customerAddress ? `<p><strong>Address:</strong> ${customerAddress}</p>` : ""}
      `;
  
  const content = `
      <div class="transaction-receipt-block">
        <div style="margin-bottom: 1.5rem;">
          <h3 style="font-family: 'Cinzel', serif; letter-spacing: 2px; margin-bottom: 0.75rem;">${isPosSale ? "POS SALE" : "CUSTOMER ORDER"}</h3>
          <p><strong>Reference:</strong> ${reference}</p>
          <p><strong>Date & Time:</strong> ${dateDisplay}</p>
          <p><strong>Payment Method:</strong> ${paymentMethod}</p>
          <p><strong>Status:</strong> <span class="${statusClass}">${statusValue}</span></p>
          <p><strong>Processed By:</strong> ${processedBy}</p>
        </div>
        <div style="margin-bottom: 1.5rem;">
          <h4 style="font-family: 'Cinzel', serif; letter-spacing: 2px; margin-bottom: 0.75rem;">CUSTOMER DETAILS</h4>
          ${customerDetails}
        </div>
        <div style="margin-bottom: 1.5rem;">
          <h4 style="font-family: 'Cinzel', serif; letter-spacing: 2px; margin-bottom: 0.75rem;">ITEMS</h4>
          <table style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 1px solid var(--border-color);">
                <th style="padding: 0.5rem; text-align: left;">Product</th>
                <th style="padding: 0.5rem; text-align: right;">Qty</th>
                <th style="padding: 0.5rem; text-align: right;">Price</th>
                <th style="padding: 0.5rem; text-align: right;">Total</th>
              </tr>
            </thead>
            <tbody>
              ${itemRows}
            </tbody>
          </table>
        </div>
        <div style="border-top: 2px solid var(--border-color); padding-top: 1rem;">
          <p style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>Subtotal:</span>
            <span>₱${subtotal.toFixed(2)}</span>
          </p>
          ${discountRow}
          ${shippingRow}
          <p style="display: flex; justify-content: space-between; font-size: 1.2rem; font-weight: bold; margin-top: 1rem;">
            <span>Total:</span>
            <span>₱${total.toFixed(2)}</span>
          </p>
        </div>
      </div>
    `;
  
  container.innerHTML = content;
}

function closeOrdersModal() {
  const modal = document.getElementById("ordersModal");
  if (modal) modal.classList.remove("active");
}

function closeOrderDetailsModal() {
  const modal = document.getElementById("orderDetailsModal");
  if (modal) modal.classList.remove("active");
}

// Close modals when clicking outside
document.addEventListener("DOMContentLoaded", function() {
  const ordersModal = document.getElementById("ordersModal");
  if (ordersModal) {
    ordersModal.addEventListener("click", (e) => {
      if (e.target.id === "ordersModal") {
        closeOrdersModal();
      }
    });
  }

  const orderDetailsModal = document.getElementById("orderDetailsModal");
  if (orderDetailsModal) {
    orderDetailsModal.addEventListener("click", (e) => {
      if (e.target.id === "orderDetailsModal") {
        closeOrderDetailsModal();
      }
    });
  }
});

async function viewProducts() {
  const modal = document.getElementById("productsModal");
  const container = document.getElementById("productsListContainer");
  
  if (modal) modal.classList.add("active");
  
  try {
    const response = await fetch("/admin/products/list");
    const data = await response.json();
    if (data.success) {
      displayProducts(data.products);
    } else {
      if (container) {
        container.innerHTML = `<p style="text-align: center; padding: 2rem; color: #ff4444;">Error: ${data.error}</p>`;
      } else {
        alert("Error loading products: " + data.error);
      }
    }
  } catch (error) {
    if (container) {
      container.innerHTML = `<p style="text-align: center; padding: 2rem; color: #ff4444;">Error: ${error.message}</p>`;
    } else {
      alert("Error loading products: " + error.message);
    }
  }
}

function displayProducts(products) {
  const container = document.getElementById("productsListContainer");
  if (!container) return;
  if (!products || products.length === 0) {
    container.innerHTML =
      '<p style="text-align: center; padding: 2rem;">No products found</p>';
    return;
  }

  container.innerHTML = `
      <table class="orders-table">
        <thead>
          <tr>
            <th>Image</th>
            <th>Product Name</th>
            <th>Category</th>
            <th>Price</th>
            <th>Stock</th>
          </tr>
        </thead>
        <tbody>
          ${products
            .map(
              (product) => `
            <tr>
              <td>
                ${
                  product.image_url
                    ? `<img src="${product.image_url}" alt="${product.name}" class="product-item-image" />`
                    : `<div class="product-item-placeholder">E</div>`
                }
              </td>
              <td>${product.name}</td>
              <td>${product.category || "Uncategorized"}</td>
              <td>₱${parseFloat(product.price).toFixed(2)}</td>
              <td class="${
                product.stock === 0
                  ? "stock-out"
                  : product.stock < 10
                  ? "stock-low"
                  : ""
              }">${product.stock}</td>
            </tr>
          `
            )
            .join("")}
        </tbody>
      </table>
    `;
}

function closeProductsModal() {
  const modal = document.getElementById("productsModal");
  if (modal) modal.classList.remove("active");
}

// Revenue Modal Functions
async function viewRevenue() {
  const modal = document.getElementById("revenueModal");
  const container = document.getElementById("revenueContent");
  
  if (modal) modal.classList.add("active");
  
  try {
    const response = await fetch("/admin/revenue");
    const data = await response.json();
    if (data.success) {
      displayRevenue(data.revenue);
    } else {
      if (container) {
        container.innerHTML = `<p style="text-align: center; padding: 2rem; color: #ff4444;">Error: ${data.error}</p>`;
      } else {
        alert("Error loading revenue: " + data.error);
      }
    }
  } catch (error) {
    if (container) {
      container.innerHTML = `<p style="text-align: center; padding: 2rem; color: #ff4444;">Error: ${error.message}</p>`;
    } else {
      alert("Error loading revenue: " + error.message);
    }
  }
}

function displayRevenue(revenue) {
  const container = document.getElementById("revenueContent");
  if (!container || !revenue) return;
  container.innerHTML = `
      <div class="revenue-layout">
        <div class="report-controls">
          <h3 class="report-controls-title">Report Actions</h3>
          <div class="report-buttons">
            <button class="btn report-btn" onclick="resetReports('weekly')">Reset Weekly</button>
            <button class="btn report-btn" onclick="resetReports('monthly')">Reset Monthly</button>
            <button class="btn report-btn" onclick="resetReports('yearly')">Reset Yearly</button>
          </div>
          <div class="report-buttons">
            <button class="btn report-btn" onclick="downloadReport('weekly')">Download Weekly PDF</button>
            <button class="btn report-btn" onclick="downloadReport('monthly')">Download Monthly PDF</button>
            <button class="btn report-btn" onclick="downloadReport('yearly')">Download Yearly PDF</button>
          </div>
          <div id="reportCheckpoints" class="report-checkpoints">
            <p style="color: var(--text-gray);">Loading report status...</p>
          </div>
        </div>
        <div class="revenue-breakdown">
          <div class="revenue-item">
            <div class="revenue-item-header">
              <h3 style="font-family: 'Cinzel', serif; letter-spacing: 2px;">Total Revenue</h3>
              <div class="revenue-amount">₱${parseFloat(revenue.total).toFixed(
                2
              )}</div>
            </div>
          </div>
          <div class="revenue-item">
            <div class="revenue-item-header">
              <h3 style="font-family: 'Cinzel', serif; letter-spacing: 2px;">From Orders</h3>
              <div class="revenue-amount">₱${parseFloat(
                revenue.from_orders
              ).toFixed(2)}</div>
            </div>
            <p style="color: var(--text-gray); margin-top: 0.5rem;">Total: ${
              revenue.orders_count
            } orders</p>
          </div>
          <div class="revenue-item">
            <div class="revenue-item-header">
              <h3 style="font-family: 'Cinzel', serif; letter-spacing: 2px;">From POS Sales</h3>
              <div class="revenue-amount">₱${parseFloat(revenue.from_pos).toFixed(
                2
              )}</div>
            </div>
            <p style="color: var(--text-gray); margin-top: 0.5rem;">Total: ${
              revenue.pos_count
            } sales</p>
          </div>
          <div class="revenue-item">
            <div class="revenue-item-header">
              <h3 style="font-family: 'Cinzel', serif; letter-spacing: 2px;">Average Order Value</h3>
              <div class="revenue-amount">₱${parseFloat(
                revenue.avg_order_value
              ).toFixed(2)}</div>
            </div>
          </div>
        </div>
      </div>
    `;
  loadReportCheckpoints();
}

async function loadReportCheckpoints() {
  const container = document.getElementById("reportCheckpoints");
  if (!container) return;
  
  try {
    const response = await fetch("/admin/reports/checkpoints");
    const data = await response.json();
    if (data.success) {
      renderReportCheckpoints(data.checkpoints || {});
    } else {
      container.innerHTML = `<p style="color: #ff7373;">${data.error || "Unable to load report status."}</p>`;
    }
  } catch (error) {
    container.innerHTML = `<p style="color: #ff7373;">${error.message}</p>`;
  }
}

function renderReportCheckpoints(checkpoints) {
  const container = document.getElementById("reportCheckpoints");
  if (!container) return;
  
  const periods = [
    { key: "weekly", label: "Weekly" },
    { key: "monthly", label: "Monthly" },
    { key: "yearly", label: "Yearly" },
  ];
  
  const items = periods
    .map(({ key, label }) => {
      const entry = checkpoints[key];
      const displayValue = entry ? entry.last_reset_at_display : "Not reset yet";
      return `
        <div class="report-checkpoint-item">
          <span class="report-checkpoint-label">${label} reset:</span>
          <span class="report-checkpoint-value">${displayValue}</span>
        </div>
      `;
    })
    .join("");
  
  container.innerHTML = items;
}

async function resetReports(period) {
  const periodLabel = period.charAt(0).toUpperCase() + period.slice(1);
  if (
    !confirm(
      `Reset ${periodLabel} sales reports? This will update the baseline timestamp for ${periodLabel.toLowerCase()} reporting.`
    )
  ) {
    return;
  }
  
  try {
    const response = await fetch("/admin/reports/reset", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ period }),
    });
    
    const data = await response.json();
    
    if (data.success) {
      showNotification(data.message || `${periodLabel} reports reset.`);
      loadReportCheckpoints();
    } else {
      showNotification(data.error || "Failed to reset reports.", "error");
    }
  } catch (error) {
    showNotification(error.message, "error");
  }
}

function downloadReport(period) {
  const url = `/admin/reports/pdf?period=${encodeURIComponent(period)}`;
  window.open(url, "_blank");
}

function closeRevenueModal() {
  const modal = document.getElementById("revenueModal");
  if (modal) modal.classList.remove("active");
}

// Update Order Status
async function updateOrderStatus(orderId, newStatus) {
  const targetOrder = allTransactions.find(
    (transaction) =>
      transaction.id === orderId &&
      transaction.record_type === "customer_order"
  );
  if (!targetOrder) {
    showNotification("Only customer orders can be updated.", "error");
    return;
  }
  if (
    !confirm(`Change order #${orderId} status to ${newStatus.toUpperCase()}?`)
  ) {
    // Reload to reset the select
    try {
      const response = await fetch("/admin/orders");
      const data = await response.json();
      if (data.success) {
        allTransactions = data.transactions || [];
        filterOrders(currentFilter, null);
      }
    } catch (error) {
      // Silently fail - user cancelled anyway
    }
    return;
  }

  try {
    const response = await fetch(`/admin/orders/${orderId}/status`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ status: newStatus }),
    });

    const data = await response.json();

    if (data.success) {
      const orderIndex = allTransactions.findIndex(
        (transaction) =>
          transaction.id === orderId &&
          transaction.record_type === "customer_order"
      );
      if (orderIndex !== -1) {
        allTransactions[orderIndex].status = newStatus;
      }
      filterOrders(currentFilter, null);
      showNotification("Order status updated successfully!");
    } else {
      showNotification("Error: " + data.error, "error");
      try {
        const response = await fetch("/admin/orders");
        const data = await response.json();
        if (data.success) {
          allTransactions = data.transactions || [];
          filterOrders(currentFilter, null);
        }
      } catch (error) {
      }
    }
  } catch (error) {
    showNotification("Error: " + error.message, "error");
    try {
      const response = await fetch("/admin/orders");
      const data = await response.json();
      if (data.success) {
        allTransactions = data.transactions || [];
        filterOrders(currentFilter, null);
      }
    } catch (err) {
    }
  }
}

document.addEventListener("DOMContentLoaded", function() {
  const productsModal = document.getElementById("productsModal");
  if (productsModal) {
    productsModal.addEventListener("click", (e) => {
      if (e.target.id === "productsModal") {
        closeProductsModal();
      }
    });
  }

  const revenueModal = document.getElementById("revenueModal");
  if (revenueModal) {
    revenueModal.addEventListener("click", (e) => {
      if (e.target.id === "revenueModal") {
        closeRevenueModal();
      }
    });
  }
});

function updateImagePreview(url) {
  const previewDiv = document.getElementById("imagePreview");
  const previewImg = document.getElementById("previewImg");

  if (url && url.trim() !== "") {
    if (previewImg) {
      previewImg.src = url;
      previewImg.onerror = function() {
        if (previewDiv) previewDiv.style.display = "none";
      };
      previewImg.onload = function() {
        if (previewDiv) previewDiv.style.display = "block";
      };
    }
  } else {
    if (previewDiv) previewDiv.style.display = "none";
  }
}

function handleImageUpload(input) {
  const file = input.files[0];
  if (file) {
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      input.value = '';
      return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
      const previewDiv = document.getElementById("imagePreview");
      const previewImg = document.getElementById("previewImg");
      if (previewImg) {
        previewImg.src = e.target.result;
      }
      if (previewDiv) {
        previewDiv.style.display = "block";
      }

      const urlInput = document.getElementById("productImage");
      if (urlInput) urlInput.value = "";
    };
    reader.readAsDataURL(file);
  }
}

function openEditModal(productId) {
  const productsDataById = window.productsDataById || {};
  
  const product = productsDataById[productId];
  if (!product) {
    alert("Product data not found");
    return;
  }

  window.isEditMode = true;
  const modalTitle = document.getElementById("modalTitle");
  if (modalTitle) modalTitle.textContent = "EDIT PRODUCT";
  
  const { id, name, description, price, stock, category, image_url } = product;
  const productIdInput = document.getElementById("productId");
  const productName = document.getElementById("productName");
  const productDescription = document.getElementById("productDescription");
  const productPrice = document.getElementById("productPrice");
  const productStock = document.getElementById("productStock");
  const productCategory = document.getElementById("productCategory");
  const productImage = document.getElementById("productImage");
  const productImageFile = document.getElementById("productImageFile");
  
  if (productIdInput) productIdInput.value = id || "";
  if (productName) productName.value = name || "";
  if (productDescription) productDescription.value = description || "";
  if (productPrice) productPrice.value = price || 0;
  if (productStock) productStock.value = stock || 0;
  if (productCategory) productCategory.value = category || "";
  if (productImage) productImage.value = image_url || "";
  if (productImageFile) productImageFile.value = "";
  
  updateImagePreview(image_url || "");
  
  const modal = document.getElementById("productModal");
  if (modal) modal.classList.add("active");
}

function openAddModal() {
  window.isEditMode = false;
  const modalTitle = document.getElementById("modalTitle");
  if (modalTitle) modalTitle.textContent = "ADD PRODUCT";
  
  const form = document.getElementById("productForm");
  if (form) form.reset();
  
  const productId = document.getElementById("productId");
  if (productId) productId.value = "";
  
  const productImageFile = document.getElementById("productImageFile");
  if (productImageFile) productImageFile.value = "";
  
  const imagePreview = document.getElementById("imagePreview");
  if (imagePreview) imagePreview.style.display = "none";
  
  const modal = document.getElementById("productModal");
  if (modal) modal.classList.add("active");
}

function closeModal() {
  const modal = document.getElementById("productModal");
  if (modal) modal.classList.remove("active");
}

document.addEventListener("DOMContentLoaded", function() {
  const productForm = document.getElementById("productForm");
  if (productForm) {
    productForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const imageFileInput = document.getElementById("productImageFile");
      const imageUrlInput = document.getElementById("productImage");
      
      const imageFile = imageFileInput ? imageFileInput.files[0] : null;
      const imageUrl = imageUrlInput ? imageUrlInput.value.trim() : "";

      let finalImageUrl = imageUrl;
      if (imageFile) {
        try {
          const formData = new FormData();
          formData.append('image', imageFile);

          const uploadResponse = await fetch('/admin/products/upload-image', {
            method: 'POST',
            body: formData
          });

          const uploadData = await uploadResponse.json();
          if (uploadData.success) {
            finalImageUrl = uploadData.image_url;
          } else {
            alert('Error uploading image: ' + uploadData.error);
            return;
          }
        } catch (error) {
          alert('Error uploading image: ' + error.message);
          return;
        }
      }

      const productName = document.getElementById("productName");
      const productDescription = document.getElementById("productDescription");
      const productPrice = document.getElementById("productPrice");
      const productStock = document.getElementById("productStock");
      const productCategory = document.getElementById("productCategory");

      const productData = {
        name: productName ? productName.value : "",
        description: productDescription ? productDescription.value : "",
        price: productPrice ? productPrice.value : "",
        stock: productStock ? productStock.value : "",
        category: productCategory ? productCategory.value : "",
        image_url: finalImageUrl,
      };

      try {
        let response;

        if (window.isEditMode) {
          const productId = document.getElementById("productId");
          const id = productId ? productId.value : "";
          response = await fetch(`/admin/products/update/${id}`, {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(productData),
          });
        } else {
          response = await fetch("/admin/products/add", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(productData),
          });
        }

        const data = await response.json();

        if (data.success) {
          alert(
            window.isEditMode
              ? "Product updated successfully!"
              : "Product added successfully!"
          );
          closeModal();
          location.reload();
        } else {
          alert("Error: " + data.error);
        }
      } catch (error) {
        alert("Error: " + error.message);
      }
    });
  }
});

async function deleteProduct(productId) {
  if (
    !confirm(
      "Are you sure you want to delete this product? This action cannot be undone."
    )
  ) {
    return;
  }

  try {
    const response = await fetch(`/admin/products/delete/${productId}`, {
      method: "DELETE",
    });

    const data = await response.json();

    if (data.success) {
      alert("Product deleted successfully!");
      location.reload();
    } else {
      alert("Error: " + data.error);
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

// Close modal when clicking outside
document.addEventListener("DOMContentLoaded", function() {
  const productModal = document.getElementById("productModal");
  if (productModal) {
    productModal.addEventListener("click", (e) => {
      if (e.target.id === "productModal") {
        closeModal();
      }
    });
  }
});

async function viewProductOrders(productId) {
  try {
    const response = await fetch(`/admin/products/${productId}/orders`);
    const data = await response.json();
    if (data.success) {
      const orderIds = data.order_ids;
      if (orderIds.length === 0) {
        alert("This product has not been ordered yet.");
      } else {
        const orderList = orderIds.map(id => `#${id}`).join(", ");
        alert(`Order IDs containing this product:\n${orderList}`);
      }
    } else {
      alert("Error: " + data.error);
    }
  } catch (error) {
    alert("Error: " + error.message);
  }
}

// ============================================
// ADMIN POS JAVASCRIPT
// ============================================

// POS cart and discount variables
window.posCart = [];
window.posCurrentDiscount = { type: null, amount: 0 };

// POS addToCart function (different signature from shop page)
function addToPosCart(productId, productName, productPrice, stock) {
  const existingItem = window.posCart.find((item) => item.product_id === productId);

  if (existingItem) {
    if (existingItem.quantity < stock) {
      existingItem.quantity++;
    } else {
      alert("Cannot add more. Stock limit reached.");
      return;
    }
  } else {
    window.posCart.push({
      product_id: productId,
      name: productName,
      price: productPrice,
      quantity: 1,
      stock: stock,
    });
  }

  renderPosCart();
}

async function addToCart(productId, productName, productPrice, stock) {
  if (arguments.length === 4 && productName !== undefined) {
    addToPosCart(productId, productName, productPrice, stock);
    return;
  }
  
  await addToCartShop(productId);
}

function updatePosQuantity(productId, change) {
  const item = window.posCart.find((item) => item.product_id === productId);
  if (item) {
    const newQty = item.quantity + change;
    if (newQty > 0 && newQty <= item.stock) {
      item.quantity = newQty;
      renderPosCart();
    } else if (newQty <= 0) {
      removeFromPosCart(productId);
    } else {
      alert("Cannot exceed available stock.");
    }
  }
}

function removeFromPosCart(productId) {
  window.posCart = window.posCart.filter((item) => item.product_id !== productId);
  renderPosCart();
}

function clearCart() {
  const cartItemsDiv = document.getElementById("cartItems");
  if (!cartItemsDiv) {
    return;
  }
  
  if (confirm("Clear all items from cart?")) {
    window.posCart = [];
    renderPosCart();
  }
}

function renderPosCart() {
  const cartItemsDiv = document.getElementById("cartItems");
  const totalAmountSpan = document.getElementById("totalAmount");
  const subtotalAmountSpan = document.getElementById("subtotalAmount");
  const discountRow = document.getElementById("discountRow");
  const discountAmountSpan = document.getElementById("discountAmount");

  if (!cartItemsDiv || !totalAmountSpan || !subtotalAmountSpan) return;

  if (window.posCart.length === 0) {
    cartItemsDiv.innerHTML = '<div class="pos-empty-cart">No items added</div>';
    totalAmountSpan.textContent = "₱0.00";
    subtotalAmountSpan.textContent = "₱0.00";
    if (discountRow) discountRow.style.display = "none";
    window.posCurrentDiscount = { type: null, amount: 0 };
    return;
  }

  let html = "";
  let subtotal = 0;

  window.posCart.forEach((item) => {
    const itemTotal = item.price * item.quantity;
    subtotal += itemTotal;

    html += `
                <div class="pos-cart-item">
                    <div class="pos-cart-item-info">
                        <div class="pos-cart-item-name">${item.name}</div>
                        <div class="pos-cart-item-price">₱${item.price.toFixed(
                          2
                        )} each</div>
                    </div>
                    <div class="pos-cart-item-controls">
                        <div class="pos-qty-control">
                            <button class="pos-qty-btn" onclick="updatePosQuantity(${
                              item.product_id
                            }, -1)">-</button>
                            <span class="pos-qty-display">${
                              item.quantity
                            }</span>
                            <button class="pos-qty-btn" onclick="updatePosQuantity(${
                              item.product_id
                            }, 1)">+</button>
                        </div>
                        <div>₱${itemTotal.toFixed(2)}</div>
                        <div class="pos-remove-btn" onclick="removeFromPosCart(${
                          item.product_id
                        })">✕</div>
                    </div>
                </div>
            `;
  });

  cartItemsDiv.innerHTML = html;
  subtotalAmountSpan.textContent = `₱${subtotal.toFixed(2)}`;

  let total = subtotal - window.posCurrentDiscount.amount;
  if (total < 0) total = 0;

  if (window.posCurrentDiscount.amount > 0) {
    if (discountRow) discountRow.style.display = "flex";
    if (discountAmountSpan) discountAmountSpan.textContent = `-₱${window.posCurrentDiscount.amount.toFixed(2)}`;
  } else {
    if (discountRow) discountRow.style.display = "none";
  }

  totalAmountSpan.textContent = `₱${total.toFixed(2)}`;
}

function applyDiscount(type) {
  const subtotal = window.posCart.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );
  let discountAmount = 0;

  if (type === "pwd" || type === "senior") {
    discountAmount = subtotal * 0.2; // 20% discount
  } else if (type === "voucher") {
    discountAmount = 100; // Fixed ₱100 discount
  }

  window.posCurrentDiscount = { type: type, amount: discountAmount };
  renderPosCart();
}

function removeDiscount() {
  window.posCurrentDiscount = { type: null, amount: 0 };
  renderPosCart();
}

async function completeSale() {
  if (window.posCart.length === 0) {
    alert("Cart is empty!");
    return;
  }

  const subtotal = window.posCart.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );
  const total = subtotal - window.posCurrentDiscount.amount;

  try {
    const response = await fetch("/admin/sales/create", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        items: window.posCart,
        payment_method: "cash",
        discount_type: window.posCurrentDiscount.type || "none",
      }),
    });

    const data = await response.json();

    if (data.success) {
      const singaporeTime = new Intl.DateTimeFormat("en-SG", {
        dateStyle: "medium",
        timeStyle: "medium",
        timeZone: "Asia/Singapore",
      }).format(new Date());
      alert(`Sale completed successfully!\nSingapore Time: ${singaporeTime}\nGenerating receipt...`);
      window.open(`/admin/receipt/${data.sale_id}`, "_blank");
      window.posCart = [];
      window.posCurrentDiscount = { type: null, amount: 0 };
      renderPosCart();
      location.reload(); // Reload to update stock numbers
    } else {
      alert("Error: " + data.error);
    }
  } catch (error) {
    alert("Error completing sale: " + error.message);
  }
}

