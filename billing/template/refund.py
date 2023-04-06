def html_refund(user_id: str, amount: float) -> str:
    html_buy_return = """
        <html>
            <head>
                <title>Refund page</title>
            </head>
            <body>
                <h1>User %s - Refund %s RUB!</h1>
            </body>
        </html>
        """ % (user_id, amount)
    return html_buy_return
