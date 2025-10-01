"""
Trading Agent Dashboard
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import json
import time
from datetime import datetime
from config import Config
from recall_api import RecallAPI
from portfolio_manager import PortfolioManager
from trading_strategy import TradingStrategy

app = Flask(__name__)
CORS(app)

# Global instances
api = RecallAPI()
portfolio_manager = PortfolioManager()
strategy = TradingStrategy()

# Trade history storage (in production, use a database)
trade_history = []
active_trades = []

# Mock portfolio data (in production, this would come from a database)
mock_portfolio = {
    'total_value': 10000.0,
    'available_balance': 10000.0,  # Başlangıçta sadece USDC/USDT bakiye
    'positions': [],  # Token pozisyonları
    'current_prices': {}
}

# Custom tokens list (in production, this would come from a database)
custom_tokens = []

# Live trading status
is_live_trading = False

def update_portfolio_after_trade(amount, from_token, to_token):
    """Update mock portfolio after a trade"""
    try:
        # Simulate trade impact on portfolio
        trade_amount = float(amount)
        
        # Reduce available balance by trade amount
        mock_portfolio['available_balance'] = max(0, mock_portfolio['available_balance'] - trade_amount)
        
        # Add token position (simplified - just add the amount as token value)
        # In real scenario, you'd calculate based on exchange rate
        token_position = {
            'token_address': to_token,
            'amount': trade_amount,
            'value_usd': trade_amount,  # Simplified: 1:1 ratio
            'timestamp': datetime.now().isoformat()
        }
        
        # Check if we already have this token position
        existing_position = None
        for i, pos in enumerate(mock_portfolio['positions']):
            if pos['token_address'] == to_token:
                existing_position = i
                break
        
        if existing_position is not None:
            # Update existing position
            mock_portfolio['positions'][existing_position]['amount'] += trade_amount
            mock_portfolio['positions'][existing_position]['value_usd'] += trade_amount
        else:
            # Add new position
            mock_portfolio['positions'].append(token_position)
        
        # Portfolio value stays the same (just reallocation from cash to tokens)
        # Total value = available_balance + sum of all token positions
        total_token_value = sum(pos['value_usd'] for pos in mock_portfolio['positions'])
        mock_portfolio['total_value'] = mock_portfolio['available_balance'] + total_token_value
        
        print(f"Portfolio updated after trade: {amount} {from_token} -> {to_token}")
        print(f"New balance: {mock_portfolio['available_balance']}, Token positions: {len(mock_portfolio['positions'])}, Total: {mock_portfolio['total_value']}")
        
    except Exception as e:
        print(f"Error updating portfolio: {e}")

@app.route('/')
def index():
    """Splash screen page"""
    return render_template('splash.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """Get API status"""
    try:
        health = api.health_check()
        portfolio = api.get_portfolio()
        
        status = {
            'api_connected': 'error' not in health,
            'portfolio_connected': 'error' not in portfolio,
            'environment': Config.ENVIRONMENT,
            'base_url': Config.get_base_url(),
            'has_api_key': bool(Config.get_api_key()),
            'live_trading_ready': is_live_trading and bool(Config.get_api_key()),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio')
def get_portfolio():
    """Get portfolio information"""
    try:
        # Try to get portfolio from API first
        portfolio = api.get_portfolio()
        
        # If API fails, use mock data
        if 'error' in portfolio:
            print(f"Portfolio API error: {portfolio['error']}")
            # Use global mock portfolio data
            portfolio_data = mock_portfolio.copy()
        else:
            # Use real API data
            portfolio_data = portfolio
        
        # Get current prices for all tokens
        prices = {}
        for pair in Config.TRADING_PAIRS:
            try:
                price_data = api.get_price_data(pair['to'])
                if price_data and 'price' in price_data:
                    prices[pair['symbol']] = float(price_data['price'])
                else:
                    prices[pair['symbol']] = 1.0  # Default price
            except Exception as e:
                print(f"Error getting price for {pair['symbol']}: {e}")
                prices[pair['symbol']] = 1.0  # Default price
        
        portfolio_data['current_prices'] = prices
        return jsonify(portfolio_data)
        
    except Exception as e:
        print(f"Portfolio endpoint error: {e}")
        # Return mock data on any error
        return jsonify({
            'total_value': mock_portfolio['total_value'],
            'available_balance': mock_portfolio['available_balance'],
            'positions': mock_portfolio['positions'],
            'current_prices': {pair['symbol']: 1.0 for pair in Config.TRADING_PAIRS},
            'error': str(e)
        })

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    """Execute a manual trade"""
    try:
        data = request.json
        print(f"Received trade data: {data}")  # Debug log
        
        # Handle both camelCase and snake_case field names
        from_token = data.get('from_token') or data.get('fromToken')
        to_token = data.get('to_token') or data.get('toToken')
        amount = data.get('amount')
        reason = data.get('reason', 'Manual trade')
        
        print(f"Parsed fields - from: {from_token}, to: {to_token}, amount: {amount}")  # Debug log
        
        if not all([from_token, to_token, amount]):
            return jsonify({'error': f'Missing required fields. Got: from_token={from_token}, to_token={to_token}, amount={amount}'}), 400
        
        # Check if live trading is enabled
        if is_live_trading:
            print("LIVE TRADING MODE: Executing real trade!")
            # Try to execute real trade
            try:
                result = api.execute_trade(from_token, to_token, str(amount), reason)
                
                if 'error' not in result:
                    # Real trade successful
                    trade_record = {
                        'id': len(trade_history) + 1,
                        'timestamp': datetime.now().isoformat(),
                        'from_token': from_token,
                        'to_token': to_token,
                        'amount': amount,
                        'reason': reason + ' (LIVE)',
                        'status': 'success',
                        'result': result
                    }
                    trade_history.append(trade_record)
                    
                    # Update portfolio after successful trade
                    update_portfolio_after_trade(amount, from_token, to_token)
                    
                    return jsonify({
                        'success': True,
                        'trade_id': trade_record['id'],
                        'result': result,
                        'live_trading': True
                    })
                else:
                    print(f"Real trade failed: {result['error']}")
                    return jsonify({
                        'success': False,
                        'error': f"Live trade failed: {result['error']}",
                        'live_trading': True
                    }), 400
                    
            except Exception as api_error:
                print(f"Live API trade error: {api_error}")
                return jsonify({
                    'success': False,
                    'error': f"Live trading error: {str(api_error)}",
                    'live_trading': True
                }), 500
        else:
            print("MOCK MODE: Executing mock trade")
            # Mock trade for testing
            mock_result = {
                'success': True,
                'message': f'Mock trade: {amount} {from_token} -> {to_token}',
                'transaction_hash': f'mock_{int(time.time())}',
                'mock': True
            }
            
            trade_record = {
                'id': len(trade_history) + 1,
                'timestamp': datetime.now().isoformat(),
                'from_token': from_token,
                'to_token': to_token,
                'amount': amount,
                'reason': reason + ' (Mock)',
                'status': 'success',
                'result': mock_result
            }
            trade_history.append(trade_record)
            
            # Update portfolio after mock trade
            update_portfolio_after_trade(amount, from_token, to_token)
            
            return jsonify({
                'success': True,
                'trade_id': trade_record['id'],
                'result': mock_result,
                'live_trading': False
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades')
def get_trades():
    """Get trade history"""
    return jsonify({
        'trades': trade_history,
        'active_trades': active_trades
    })

@app.route('/api/tokens')
def get_tokens():
    """Get available tokens"""
    tokens = []
    for pair in Config.TRADING_PAIRS:
        try:
            price_data = api.get_price_data(pair['to'])
            if price_data and 'price' in price_data:
                tokens.append({
                    'symbol': pair['symbol'],
                    'address': pair['to'],
                    'price': float(price_data['price']),
                    'timestamp': price_data.get('timestamp', '')
                })
            else:
                # Fallback with default price if API fails
                tokens.append({
                    'symbol': pair['symbol'],
                    'address': pair['to'],
                    'price': 1.0,  # Default price
                    'timestamp': ''
                })
        except Exception as e:
            print(f"Error getting price for {pair['symbol']}: {e}")
            # Fallback with default price
            tokens.append({
                'symbol': pair['symbol'],
                'address': pair['to'],
                'price': 1.0,  # Default price
                'timestamp': ''
            })
    
        # Add custom tokens to the list
        for custom_token in custom_tokens:
            try:
                # Try to get price for custom token using a different approach
                # For now, use a mock price based on symbol or set to 0.001 for unknown tokens
                if custom_token['symbol'] in ['PEPE', 'DOGE', 'SHIB']:
                    # Meme coin prices (very low)
                    custom_token['price'] = 0.000001
                elif custom_token['symbol'] in ['BTC', 'ETH']:
                    # Major coins
                    custom_token['price'] = 50000.0 if custom_token['symbol'] == 'BTC' else 3000.0
                elif custom_token['symbol'] in ['AVAX', 'MATIC', 'SOL']:
                    # Popular altcoins with realistic prices
                    if custom_token['symbol'] == 'AVAX':
                        custom_token['price'] = 29.82
                    elif custom_token['symbol'] == 'MATIC':
                        custom_token['price'] = 0.23
                    elif custom_token['symbol'] == 'SOL':
                        custom_token['price'] = 217.07
                else:
                    # Unknown tokens - set a default low price
                    custom_token['price'] = 0.001
                
                custom_token['timestamp'] = datetime.now().isoformat()
                print(f"Custom token {custom_token['symbol']} price set to: {custom_token['price']}")
                
            except Exception as e:
                print(f"Error setting price for custom token {custom_token['symbol']}: {e}")
                custom_token['price'] = 0.001  # Default fallback
            
            tokens.append(custom_token)
    
    return jsonify({'tokens': tokens})

@app.route('/api/available-tokens')
def get_available_tokens():
    """Get tokens that user can trade FROM (only tokens they own)"""
    try:
        available_tokens = []
        
        # Always include USDC/USDT as base currency
        available_tokens.append({
            'symbol': 'USDT',
            'address': '0xA0b86a33E6441c8C06DDD1233a8c4b3b8a8b8b8b',  # Mock USDT address
            'price': 1.0,
            'balance': mock_portfolio['available_balance'],
            'type': 'base_currency'
        })
        
        # Add tokens from positions
        for position in mock_portfolio['positions']:
            # Find token info from all tokens
            token_info = None
            for pair in Config.TRADING_PAIRS:
                if pair['to'] == position['token_address']:
                    token_info = {
                        'symbol': pair['symbol'],
                        'address': pair['to'],
                        'price': 1.0,  # Will be updated
                        'balance': position['amount'],
                        'type': 'position'
                    }
                    break
            
            # Check custom tokens
            if not token_info:
                for custom_token in custom_tokens:
                    if custom_token['address'] == position['token_address']:
                        token_info = {
                            'symbol': custom_token['symbol'],
                            'address': custom_token['address'],
                            'price': custom_token['price'],
                            'balance': position['amount'],
                            'type': 'custom'
                        }
                        break
            
            if token_info:
                available_tokens.append(token_info)
        
        return jsonify({'available_tokens': available_tokens})
        
    except Exception as e:
        print(f"Error getting available tokens: {e}")
        return jsonify({'available_tokens': []})

@app.route('/api/strategy/signal/<symbol>')
def get_strategy_signal(symbol):
    """Get trading signal for a symbol"""
    try:
        signal = strategy.analyze_symbol(symbol, api)
        return jsonify({
            'symbol': symbol,
            'signal': signal.signal.value,
            'confidence': signal.confidence,
            'reason': signal.reason,
            'target_price': signal.target_price,
            'stop_loss': signal.stop_loss
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy/run')
def run_strategy():
    """Run trading strategy once"""
    try:
        portfolio_manager.run_trading_cycle()
        return jsonify({'success': True, 'message': 'Strategy cycle completed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add-token', methods=['POST'])
def add_custom_token():
    """Add a custom token"""
    try:
        data = request.json
        symbol = data.get('symbol', '').upper()
        address = data.get('address', '')
        
        if not symbol or not address:
            return jsonify({'error': 'Symbol ve address gerekli'}), 400
        
        # Check if token already exists
        for token in custom_tokens:
            if token['symbol'] == symbol or token['address'].lower() == address.lower():
                return jsonify({'error': 'Bu token zaten mevcut'}), 400
        
        # Add custom token
        custom_token = {
            'symbol': symbol,
            'address': address,
            'price': 1.0,  # Default price, will be updated by API
            'timestamp': datetime.now().isoformat()
        }
        custom_tokens.append(custom_token)
        
        print(f"Custom token added: {symbol} ({address})")
        
        return jsonify({
            'success': True,
            'message': f'{symbol} token başarıyla eklendi',
            'token': custom_token
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/live-trading', methods=['POST'])
def update_live_trading():
    """Update live trading status"""
    global is_live_trading
    try:
        data = request.json
        is_live_trading = data.get('isLiveTrading', False)
        
        print(f"Live trading status updated: {is_live_trading}")
        
        return jsonify({
            'success': True,
            'isLiveTrading': is_live_trading,
            'message': f'Live trading {"enabled" if is_live_trading else "disabled"}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
