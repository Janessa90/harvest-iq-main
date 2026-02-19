PH_REGIONS = [
    'NCR', 'CAR', 'Region I', 'Region II', 'Region III',
    'Region IV-A', 'Region IV-B', 'Region V', 'Region VI',
    'Region VII', 'Region VIII', 'Region IX', 'Region X',
    'Region XI', 'Region XII', 'Region XIII', 'BARMM'
]

PRODUCT_UNITS = ['kg', 'gram', 'piece', 'bundle', 'sack', 'box', 'tray', 'liter', 'dozen']

PAYMENT_METHODS = {
    'cod': 'Cash on Delivery',
    'gcash': 'GCash',
    'maya': 'Maya (PayMaya)',
    'card': 'Credit/Debit Card',
    'bank': 'Bank Transfer',
}

ORDER_STATUSES = [
    'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'
]

DELIVERY_FEE = 50.00  # base delivery fee in PHP
FREE_DELIVERY_THRESHOLD = 500.00