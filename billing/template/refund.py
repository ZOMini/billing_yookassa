def html_refund(user_id: str) -> str:
    html_buy_return = """
        <html>
            <head>
                <title>Refund page</title>
            </head>
            <body>
                <h1>User %s - Refund OK!</h1>
            </body>
        </html>
        """ % (user_id)
    return html_buy_return
