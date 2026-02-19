// Auto-dismiss alerts after 4 seconds
document.querySelectorAll('.alert-dismissible').forEach(alert => {
  setTimeout(() => {
    const bsAlert = new bootstrap.Alert(alert);
    if (bsAlert) bsAlert.close();
  }, 4000);
});

// Quantity input validation in cart
document.querySelectorAll('.qty-input').forEach(input => {
  input.addEventListener('change', function() {
    const min = parseInt(this.min) || 1;
    const max = parseInt(this.max) || 9999;
    let val = parseInt(this.value) || min;
    this.value = Math.min(Math.max(val, min), max);
  });
});

// Product image error fallback
document.querySelectorAll('img[data-fallback]').forEach(img => {
  img.addEventListener('error', function() {
    this.src = this.dataset.fallback;
  });
});

// Confirm delete actions
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', function(e) {
    if (!confirm(this.dataset.confirm)) e.preventDefault();
  });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
  });
});
```

---

## `.env.example`
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///data/farmers_marketplace.db

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-app-password

STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...