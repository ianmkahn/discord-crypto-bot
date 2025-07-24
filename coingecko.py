import requests

def get_price_and_ath(token_id, currency='usd'):
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}?localization=false"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Invalid token")
    data = response.json()
    current_price = data["market_data"]["current_price"][currency]
    ath_price = data["market_data"]["ath"][currency]
    return current_price, ath_price
