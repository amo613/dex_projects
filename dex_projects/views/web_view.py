from nicegui import ui

class DexWebView:
    def __init__(self, viewmodel):
        self.viewmodel = viewmodel
        self.setup_ui()

    def setup_ui(self):
        with ui.header().classes('justify-between'):
            ui.label('Dex Dashboard').classes('text-2xl')

        self.table = ui.table(
            columns=[
                {'name': 'symbol', 'label': 'Symbol', 'field': 'symbol'},
                {'name': 'name', 'label': 'Token Name', 'field': 'name'},
                {'name': 'market_cap', 'label': 'Market Cap (USD)', 'field': 'market_cap'},
                {'name': 'price', 'label': 'Price (USD)', 'field': 'price'},
                {'name': 'change_24h', 'label': 'Change 24h (%)', 'field': 'change_24h'},
            ],
            rows=[],
            row_key='symbol',
            pagination={'rowsPerPage': 10}
        ).classes('w-full')

        ui.timer(10, self.update_table)

    def update_table(self):
        new_rows = []

        for mint, data in self.viewmodel.tokens.items():
            pair_data = data.get('pair', {})
            pair_stats = data.get('pairStats', {}).get('twentyFourHour', {})

            symbol = pair_data.get('token1Symbol', 'N/A')
            name = pair_data.get('token1Name', 'N/A')
            market_cap = float(pair_data.get('pairMarketcapUsd', 0))
            price = float(pair_data.get('pairPrice1Usd', 0))
            change_24h = float(pair_stats.get('diff', 0))

            formatted_market_cap = f"${market_cap:,.2f}" if market_cap else "N/A"
            formatted_price = f"${price:,.8f}" if price else "N/A"
            formatted_change_24h = f"{change_24h:.2f}%" if change_24h else "0.00%"

            new_rows.append({
                'symbol': symbol,
                'name': name,
                'market_cap': formatted_market_cap,
                'price': formatted_price,
                'change_24h': formatted_change_24h,
            })

        self.table.rows = new_rows
        self.table.update()
