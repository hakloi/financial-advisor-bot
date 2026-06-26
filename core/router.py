from services.finance import get_stock_info


def route(user_input: str, lang: str):

    text = user_input.lower()


    if "акции" in text or "stock" in text:

        return handle_stocks(lang)


    if "вклад" in text or "deposit" in text:

        return handle_deposits(lang)


    return fallback(lang)



def handle_stocks(lang):

    ticker = "AAPL"  

    data = get_stock_info(ticker)

    if lang == "English":
        response = (
            f"📊 Stock: {ticker}\n"
            f"Price: {data['last_price']:.2f}\n"
            f"Volatility: {data['volatility']:.2f}"
        )
    else:
        response = (
            f"📊 Акции: {ticker}\n"
            f"Цена: {data['last_price']:.2f}\n"
            f"Волатильность: {data['volatility']:.2f}"
        )

    return {
        "type": "stocks",
        "response": response
    }


def handle_deposits(lang):

    if lang == "English":
        return {
            "type": "deposits",
            "response": "💰 Deposit comparison module coming soon"
        }

    return {
        "type": "deposits",
        "response": "💰 Модуль вкладов скоро будет добавлен"
    }


def fallback(lang):

    if lang == "English":
        return {
            "type": "chat",
            "response": "I can help with stocks or deposits"
        }

    return {
        "type": "chat",
        "response": "Я могу помочь с акциями или вкладами"
    }