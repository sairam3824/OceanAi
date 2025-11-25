# Product Specifications

## E-Commerce Checkout System

### Overview
The checkout system allows customers to complete their purchases by providing shipping, payment, and discount information.

### Features

#### 1. Customer Information
- Email address (required)
- Phone number (optional)
- Email validation must check for valid format
- Phone number accepts US format

#### 2. Shipping Address
- First name and last name (required)
- Street address (required)
- City (required)
- State selection from dropdown (required)
- ZIP code (required, 5 digits)
- Address validation ensures all required fields are filled

#### 3. Payment Processing
- Accepts major credit cards (Visa, MasterCard, American Express)
- Card number validation (16 digits)
- Expiry date in MM/YY format
- CVV (3-4 digits)
- Name on card must match billing information

#### 4. Discount Codes
The system supports the following discount codes:

- **SAVE10**: 10% off entire order
- **SAVE15**: 15% off entire order
- **SAVE20**: 20% off entire order
- **FREESHIP**: Free shipping (saves $10)
- **WELCOME**: $5 off for new customers

Discount code rules:
- Only one discount code can be applied per order
- Discount codes are case-insensitive
- Invalid codes show error message: "Invalid discount code"
- Valid codes show success message: "Discount applied successfully"
- Discount is applied to subtotal before tax calculation

#### 5. Order Calculation
- Subtotal: Sum of all items in cart
- Discount: Applied based on discount code
- Tax: 8% of (Subtotal - Discount)
- Total: Subtotal - Discount + Tax

#### 6. Order Submission
- All required fields must be filled
- Payment information must be valid
- On successful submission:
  - Display order confirmation
  - Show order ID
  - Hide checkout form
- On error:
  - Display error message
  - Keep form visible for correction

### Validation Rules

#### Email Validation
- Must contain @ symbol
- Must have domain extension
- Example: user@example.com

#### Phone Validation
- Optional field
- Format: (XXX) XXX-XXXX or XXX-XXX-XXXX

#### ZIP Code Validation
- Must be 5 digits
- Example: 12345

#### Card Number Validation
- Must be 16 digits
- No spaces or dashes
- Example: 1234567890123456

#### Expiry Date Validation
- Format: MM/YY
- Month must be 01-12
- Year must be current year or future

#### CVV Validation
- 3 digits for Visa/MasterCard
- 4 digits for American Express

### Error Messages
- "Email is required"
- "Invalid email format"
- "First name is required"
- "Last name is required"
- "Address is required"
- "City is required"
- "State is required"
- "ZIP code must be 5 digits"
- "Card number is required"
- "Invalid card number"
- "Expiry date is required"
- "Invalid expiry date format"
- "CVV is required"
- "Invalid CVV"

### Success Messages
- "Discount applied successfully"
- "Order placed successfully"
- "Thank you for your order"
