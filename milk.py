import requests
import time
import json

# Configuration
PRODUCT_ID = "52262769"  # TCIN for Horizon Organic Whole High Vitamin D Milk 1gal
STORE_ID = "1426"       # Target store ID for San Jose - Capitol
API_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"
DISCORD_WEBHOOK_URL = ""
CHECK_INTERVAL = 3600  # Check every hour (in seconds)

API_URL = "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_v1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124",
    "Accept": "application/json"
}

def check_stock():
    """Check if the product is available for in-store pickup."""
    params = {
        "key": API_KEY,
        "tcin": PRODUCT_ID,
        "store_id": STORE_ID,
        "zip": "95116",  # San Jose ZIP code for reference
        "state": "CA",
        "required_store_id": STORE_ID,
        "is_bot": "false"
    }
    
    try:
        response = requests.get(API_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        # Extract in-store availability status
        fulfillment = data.get("data", {}).get("product", {}).get("fulfillment", {})
        store_options = fulfillment.get("store_options", [])
        
        if not store_options:
            print("No store options available.")
            return False
        
        in_store_status = store_options[0].get("in_store_only", {}).get("availability_status", "UNKNOWN")
        print(f"In-Store Availability: {in_store_status}")
        return in_store_status == "IN_STOCK"
    
    except requests.RequestException as e:
        print(f"Request Error: {e}")
        return False
    except (KeyError, IndexError) as e:
        print(f"Parsing Error: {e}")
        return False

def send_discord_alert():
    """Send a Discord notification when the product is back in stock."""
    payload = {
        "content": f"Horizon Organic Whole Milk (1gal) is back in stock at Target San Jose - Capitol for in-store pickup!\nhttps://www.target.com/p/horizon-organic-whole-high-vitamin-d-milk-1gal/-/A-{PRODUCT_ID}"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Discord alert sent successfully.")
    except requests.RequestException as e:
        print(f"Error sending Discord alert: {e}")

def main():
    """Main loop to monitor stock and send notifications."""
    print("Starting milk stock monitor for Horizon Organic Whole Milk (1gal)...")
    was_out_of_stock = True  # Track previous stock status
    
    while True:
        try:
            in_stock = check_stock()
            
            if in_stock and was_out_of_stock:
                print("Milk is back in stock for in-store pickup!")
                send_discord_alert()
                was_out_of_stock = False
            elif not in_stock:
                print("Milk is still out of stock for in-store pickup.")
                was_out_of_stock = True
            else:
                print("Milk remains in stock for in-store pickup.")
            
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            time.sleep(CHECK_INTERVAL)  # Wait before retrying

if __name__ == "__main__":
    main()
