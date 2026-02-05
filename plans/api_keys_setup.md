# API Keys Setup Guide

## Required API Keys

### 1. OpenAI API Key (Required)

The StockBot uses OpenAI's GPT models for AI-powered trading decisions and market analysis.

#### How to Get OpenAI API Key:

1. **Create OpenAI Account**
   - Go to [https://platform.openai.com](https://platform.openai.com)
   - Sign up for an account or log in if you already have one

2. **Navigate to API Keys**
   - Click on your profile in the top-right corner
   - Select "View API keys" or go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

3. **Create New API Key**
   - Click "Create new secret key"
   - Give it a descriptive name like "StockBot Trading"
   - Copy the key immediately (you won't be able to see it again)

4. **Add Billing Information**
   - Go to [https://platform.openai.com/account/billing](https://platform.openai.com/account/billing)
   - Add a payment method
   - Set up usage limits to control costs (recommended: $10-20/month for testing)

#### Cost Estimation:
- GPT-4 API calls: ~$0.03 per 1K tokens
- Expected daily usage: 10-50 API calls
- Estimated monthly cost: $5-15 for moderate usage

### 2. Stock Data APIs (Optional Upgrades)

Currently using Yahoo Finance (free), but here are paid alternatives for better data:

#### Alpha Vantage (Optional)
- **Free Tier**: 5 API calls per minute, 500 calls per day
- **Paid Plans**: Starting at $49.99/month
- **Setup**: [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)

#### Polygon.io (Optional)
- **Free Tier**: 5 API calls per minute
- **Paid Plans**: Starting at $29/month
- **Setup**: [https://polygon.io/](https://polygon.io/)

## Environment Variables Setup

### Backend (.env file)

Create a `.env` file in the backend directory with the following variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Stock Data APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
POLYGON_API_KEY=your_polygon_key_here

# Database
DATABASE_URL=sqlite:///./stockbot.db

# Security
SECRET_KEY=your_secret_key_for_jwt_tokens

# Bot Configuration
INITIAL_BALANCE=20.00
DEFAULT_MAX_DAILY_TRADES=5
DEFAULT_RISK_TOLERANCE=MEDIUM

# Trading Hours (EST)
TRADING_START_HOUR=9
TRADING_START_MINUTE=30
TRADING_END_HOUR=16
TRADING_END_MINUTE=0
```

### Frontend (.env file)

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## Security Best Practices

### 1. Environment Variables
- Never commit `.env` files to version control
- Add `.env` to your `.gitignore` file
- Use different keys for development and production

### 2. API Key Protection
- Store keys in environment variables only
- Use key rotation regularly (monthly recommended)
- Monitor API usage for unusual activity
- Set up usage alerts and limits

### 3. Production Deployment
- Use secure secret management (AWS Secrets Manager, Azure Key Vault, etc.)
- Enable HTTPS for all API communications
- Implement rate limiting to prevent abuse
- Use API key restrictions when available

## Testing Your Setup

### 1. OpenAI API Test
```python
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello, this is a test."}],
        max_tokens=10
    )
    print("OpenAI API: ✅ Working")
except Exception as e:
    print(f"OpenAI API: ❌ Error - {e}")
```

### 2. Yahoo Finance Test
```python
import yfinance as yf

try:
    stock = yf.Ticker("AAPL")
    info = stock.info
    print(f"Yahoo Finance: ✅ Working - AAPL price: ${info.get('currentPrice', 'N/A')}")
except Exception as e:
    print(f"Yahoo Finance: ❌ Error - {e}")
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Invalid**
   - Verify the key is copied correctly (no extra spaces)
   - Check if billing is set up on your OpenAI account
   - Ensure you have sufficient credits

2. **Rate Limiting**
   - OpenAI: 3 requests per minute on free tier
   - Implement exponential backoff in your code
   - Consider upgrading to paid tier for higher limits

3. **Yahoo Finance Blocking**
   - Add delays between requests (1-2 seconds)
   - Use different user agents
   - Consider upgrading to paid stock data service

### Environment Setup Verification

Run this script to verify all your environment variables are set correctly:

```python
import os

required_vars = [
    "OPENAI_API_KEY",
    "DATABASE_URL",
    "SECRET_KEY",
    "INITIAL_BALANCE"
]

optional_vars = [
    "ALPHA_VANTAGE_API_KEY",
    "POLYGON_API_KEY"
]

print("=== Required Environment Variables ===")
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: Set (length: {len(value)})")
    else:
        print(f"❌ {var}: Not set")

print("\n=== Optional Environment Variables ===")
for var in optional_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: Set (length: {len(value)})")
    else:
        print(f"⚠️  {var}: Not set (using free alternatives)")
```

## Next Steps

1. Set up your OpenAI API key first (required for AI functionality)
2. Test the API connection using the provided test scripts
3. Start with Yahoo Finance for stock data (free)
4. Consider upgrading to paid stock data APIs later for better reliability
5. Monitor your API usage and costs regularly

## Support

If you encounter issues:
- Check the troubleshooting section above
- Verify your environment variables are set correctly
- Test API connections individually
- Review API documentation for any changes
- Check your account billing and usage limits