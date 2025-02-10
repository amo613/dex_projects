from nicegui import ui

class DexWebView:
    def __init__(self, viewmodel):
        self.viewmodel = viewmodel
        self.setup_ui()

    def setup_ui(self):
        with ui.header().classes('justify-between'):
            ui.label('Dex Dashboard').classes('text-2xl')

        with ui.card().classes('q-pa-md'):
            with ui.row():
                self.min_market_cap_input = ui.input(
                    label='Min Market Cap (USD)',
                    placeholder='z.B. 1000000'
                ).props('type=number')
                self.max_market_cap_input = ui.input(
                    label='Max Market Cap (USD)',
                    placeholder='z.B. 5000000'
                ).props('type=number')
                self.min_change_24h_input = ui.input(
                    label='Min Price Change 24h (%)',
                    placeholder='z.B. 1'
                ).props('type=number')
                self.max_change_24h_input = ui.input(
                    label='Max Price Change 24h (%)',
                    placeholder='z.B. 10'
                ).props('type=number')
                self.min_change_5min_input = ui.input(
                    label='Min Price Change 5min (%)',
                    placeholder='z.B. 0.5'
                ).props('type=number')
                self.max_change_5min_input = ui.input(
                    label='Max Price Change 5min (%)',
                    placeholder='z.B. 5'
                ).props('type=number')
                self.min_change_1h_input = ui.input(
                    label='Min Price Change 1h (%)',
                    placeholder='z.B. 1'
                ).props('type=number')
                self.max_change_1h_input = ui.input(
                    label='Max Price Change 1h (%)',
                    placeholder='z.B. 10'
                ).props('type=number')
                self.min_change_6h_input = ui.input(
                    label='Min Price Change 6h (%)',
                    placeholder='z.B. 2'
                ).props('type=number')
                self.max_change_6h_input = ui.input(
                    label='Max Price Change 6h (%)',
                    placeholder='z.B. 15'
                ).props('type=number')
                # Filter für Migration Progress und FDV
                self.min_migration_input = ui.input(
                    label='Min Migration Progress (%)',
                    placeholder='z.B. 50'
                ).props('type=number')
                self.max_migration_input = ui.input(
                    label='Max Migration Progress (%)',
                    placeholder='z.B. 100'
                ).props('type=number')
                self.min_fdv_input = ui.input(
                    label='Min FDV (USD)',
                    placeholder='z.B. 100000'
                ).props('type=number')
                self.max_fdv_input = ui.input(
                    label='Max FDV (USD)',
                    placeholder='z.B. 500000'
                ).props('type=number')
                ui.button('Filter anwenden', on_click=self.apply_filters)

        self.table_all = ui.table(
            columns=[
                {'name': 'symbol', 'label': 'Symbol', 'field': 'symbol'},
                {'name': 'name', 'label': 'Token Name', 'field': 'name'},
                {'name': 'market_cap', 'label': 'Market Cap (USD)', 'field': 'market_cap'},
                {'name': 'price', 'label': 'Price (USD)', 'field': 'price'},
                {'name': 'change_5min', 'label': 'Change 5min (%)', 'field': 'change_5min'},
                {'name': 'change_1h', 'label': 'Change 1h (%)', 'field': 'change_1h'},
                {'name': 'change_6h', 'label': 'Change 6h (%)', 'field': 'change_6h'},
                {'name': 'change_24h', 'label': 'Change 24h (%)', 'field': 'change_24h'},
                {'name': 'migration_progress', 'label': 'Migration Progress (%)', 'field': 'migration_progress'},
                {'name': 'fdv', 'label': 'FDV (USD)', 'field': 'fdv'},
            ],
            rows=[],
            row_key='symbol',
            pagination={'rowsPerPage': 10}
        ).classes('w-full')

        self.table_filtered = ui.table(
            columns=[
                {'name': 'symbol', 'label': 'Symbol', 'field': 'symbol'},
                {'name': 'name', 'label': 'Token Name', 'field': 'name'},
                {'name': 'market_cap', 'label': 'Market Cap (USD)', 'field': 'market_cap'},
                {'name': 'price', 'label': 'Price (USD)', 'field': 'price'},
                {'name': 'change_5min', 'label': 'Change 5min (%)', 'field': 'change_5min'},
                {'name': 'change_1h', 'label': 'Change 1h (%)', 'field': 'change_1h'},
                {'name': 'change_6h', 'label': 'Change 6h (%)', 'field': 'change_6h'},
                {'name': 'change_24h', 'label': 'Change 24h (%)', 'field': 'change_24h'},
                {'name': 'migration_progress', 'label': 'Migration Progress (%)', 'field': 'migration_progress'},
                {'name': 'fdv', 'label': 'FDV (USD)', 'field': 'fdv'},
            ],
            rows=[],
            row_key='symbol',
            pagination={'rowsPerPage': 10}
        ).classes('w-full')

        # Aktualisierung der "Alle Tokens"-Tabelle alle 3 Sekunden
        ui.timer(3, self.update_all_table)

    def update_all_table(self):
        new_rows = []
        for mint, data in self.viewmodel.tokens.items():
            pair_data = data.get('pair', {})
            pair_stats = data.get('pairStats', {})

            try:
                symbol = pair_data.get('token1Symbol', 'N/A')
                name = pair_data.get('token1Name', 'N/A')
                market_cap = float(pair_data.get('pairMarketcapUsd', 0))
                price = float(pair_data.get('pairPrice1Usd', 0))
                fdv = float(pair_data.get('fdv', 0))
            except Exception:
                symbol = 'N/A'
                name = 'N/A'
                market_cap = price = fdv = 0.0

            try:
                five_min_stats = pair_stats.get('fiveMin', {})
                one_hour_stats = pair_stats.get('oneHour', {})
                six_hour_stats = pair_stats.get('sixHour', {})
                twenty_four_stats = pair_stats.get('twentyFourHour', {})
                change_5min = float(five_min_stats.get('diff', 0))
                change_1h = float(one_hour_stats.get('diff', 0))
                change_6h = float(six_hour_stats.get('diff', 0))
                change_24h = float(twenty_four_stats.get('diff', 0))
            except Exception:
                change_5min = change_1h = change_6h = change_24h = 0.0

            try:
                migration_progress = float(data.get('migrationProgress', 0))
            except Exception:
                migration_progress = 0.0

            formatted_market_cap = f"${market_cap:,.2f}" if market_cap else "N/A"
            formatted_price = f"${price:,.8f}" if price else "N/A"
            formatted_change_5min = f"{change_5min:.2f}%" if change_5min else "0.00%"
            formatted_change_1h = f"{change_1h:.2f}%" if change_1h else "0.00%"
            formatted_change_6h = f"{change_6h:.2f}%" if change_6h else "0.00%"
            formatted_change_24h = f"{change_24h:.2f}%" if change_24h else "0.00%"
            formatted_migration_progress = f"{migration_progress:.2f}%" if migration_progress else "N/A"
            formatted_fdv = f"${fdv:,.2f}" if fdv else "N/A"

            new_rows.append({
                'symbol': symbol,
                'name': name,
                'market_cap': formatted_market_cap,
                'price': formatted_price,
                'change_5min': formatted_change_5min,
                'change_1h': formatted_change_1h,
                'change_6h': formatted_change_6h,
                'change_24h': formatted_change_24h,
                'migration_progress': formatted_migration_progress,
                'fdv': formatted_fdv,
            })
        self.table_all.rows = new_rows
        self.table_all.update()

    def apply_filters(self):
        try:
            min_market_cap = float(self.min_market_cap_input.value) if self.min_market_cap_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Min Market Cap eingeben.', color='negative')
            return
        try:
            max_market_cap = float(self.max_market_cap_input.value) if self.max_market_cap_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Max Market Cap eingeben.', color='negative')
            return
        try:
            min_change_24h = float(self.min_change_24h_input.value) if self.min_change_24h_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Min Price Change 24h eingeben.', color='negative')
            return
        try:
            max_change_24h = float(self.max_change_24h_input.value) if self.max_change_24h_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Max Price Change 24h eingeben.', color='negative')
            return
        try:
            min_change_5min = float(self.min_change_5min_input.value) if self.min_change_5min_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Min Price Change 5min eingeben.', color='negative')
            return
        try:
            max_change_5min = float(self.max_change_5min_input.value) if self.max_change_5min_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Max Price Change 5min eingeben.', color='negative')
            return
        try:
            min_change_1h = float(self.min_change_1h_input.value) if self.min_change_1h_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Min Price Change 1h eingeben.', color='negative')
            return
        try:
            max_change_1h = float(self.max_change_1h_input.value) if self.max_change_1h_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Max Price Change 1h eingeben.', color='negative')
            return
        try:
            min_change_6h = float(self.min_change_6h_input.value) if self.min_change_6h_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Min Price Change 6h eingeben.', color='negative')
            return
        try:
            max_change_6h = float(self.max_change_6h_input.value) if self.max_change_6h_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Max Price Change 6h eingeben.', color='negative')
            return
        try:
            min_migration = float(self.min_migration_input.value) if self.min_migration_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Min Migration Progress eingeben.', color='negative')
            return
        try:
            max_migration = float(self.max_migration_input.value) if self.max_migration_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Max Migration Progress eingeben.', color='negative')
            return
        try:
            min_fdv = float(self.min_fdv_input.value) if self.min_fdv_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Min FDV eingeben.', color='negative')
            return
        try:
            max_fdv = float(self.max_fdv_input.value) if self.max_fdv_input.value.strip() != '' else None
        except ValueError:
            ui.notify('Bitte nur Zahlen für Max FDV eingeben.', color='negative')
            return

        filtered_rows = []
        for mint, data in self.viewmodel.tokens.items():
            pair_data = data.get('pair', {})
            pair_stats = data.get('pairStats', {})

            try:
                symbol = pair_data.get('token1Symbol', 'N/A')
                name = pair_data.get('token1Name', 'N/A')
                market_cap = float(pair_data.get('pairMarketcapUsd', 0))
                price = float(pair_data.get('pairPrice1Usd', 0))
                fdv = float(pair_data.get('fdv', 0))
            except Exception:
                continue

            try:
                five_min_stats = pair_stats.get('fiveMin', {})
                one_hour_stats = pair_stats.get('oneHour', {})
                six_hour_stats = pair_stats.get('sixHour', {})
                twenty_four_stats = pair_stats.get('twentyFourHour', {})
                change_5min = float(five_min_stats.get('diff', 0))
                change_1h = float(one_hour_stats.get('diff', 0))
                change_6h = float(six_hour_stats.get('diff', 0))
                change_24h = float(twenty_four_stats.get('diff', 0))
            except Exception:
                change_5min = change_1h = change_6h = change_24h = 0.0

            try:
                migration_progress = float(data.get('migrationProgress', 0))
            except Exception:
                migration_progress = 0.0

            if min_market_cap is not None and market_cap < min_market_cap:
                continue
            if max_market_cap is not None and market_cap > max_market_cap:
                continue
            if min_change_24h is not None and change_24h < min_change_24h:
                continue
            if max_change_24h is not None and change_24h > max_change_24h:
                continue
            if min_change_5min is not None and change_5min < min_change_5min:
                continue
            if max_change_5min is not None and change_5min > max_change_5min:
                continue
            if min_change_1h is not None and change_1h < min_change_1h:
                continue
            if max_change_1h is not None and change_1h > max_change_1h:
                continue
            if min_change_6h is not None and change_6h < min_change_6h:
                continue
            if max_change_6h is not None and change_6h > max_change_6h:
                continue
            if min_migration is not None and migration_progress < min_migration:
                continue
            if max_migration is not None and migration_progress > max_migration:
                continue
            if min_fdv is not None and fdv < min_fdv:
                continue
            if max_fdv is not None and fdv > max_fdv:
                continue

            formatted_market_cap = f"${market_cap:,.2f}" if market_cap else "N/A"
            formatted_price = f"${price:,.8f}" if price else "N/A"
            formatted_change_5min = f"{change_5min:.2f}%" if change_5min else "0.00%"
            formatted_change_1h = f"{change_1h:.2f}%" if change_1h else "0.00%"
            formatted_change_6h = f"{change_6h:.2f}%" if change_6h else "0.00%"
            formatted_change_24h = f"{change_24h:.2f}%" if change_24h else "0.00%"
            formatted_migration_progress = f"{migration_progress:.2f}%" if migration_progress else "N/A"
            formatted_fdv = f"${fdv:,.2f}" if fdv else "N/A"

            filtered_rows.append({
                'symbol': symbol,
                'name': name,
                'market_cap': formatted_market_cap,
                'price': formatted_price,
                'change_5min': formatted_change_5min,
                'change_1h': formatted_change_1h,
                'change_6h': formatted_change_6h,
                'change_24h': formatted_change_24h,
                'migration_progress': formatted_migration_progress,
                'fdv': formatted_fdv,
            })
        self.table_filtered.rows = filtered_rows
        self.table_filtered.update()
        ui.notify(f'Filter angewendet: {len(filtered_rows)} Token gefunden.', color='positive')
