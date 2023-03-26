import logging
from datetime import datetime


def html_buy_return(user_id: str, status: str, expired: datetime) -> str:
    html_buy_return = """
        <html>
            <head>
                <title>Return page</title>
            </head>
            <body>
                <h1>User %s - Status %s - Expired %s!</h1>
            </body>
        </html>
        """ % (user_id, status, expired)
    return html_buy_return
