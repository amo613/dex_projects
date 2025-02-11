from nicegui import ui
from datetime import datetime

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
                {'name': 'mint', 'label': 'Mint', 'field': 'mint'},
                {'name': 'image', 'label': 'Image', 'field': 'image',
                 'template': "<img :src='row.image' class='w-16 h-16' />"},
                {'name': 'created', 'label': 'Created', 'field': 'created'},
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
            row_key='mint',
            pagination={'rowsPerPage': 10}
        ).classes('w-full')

        self.table_filtered = ui.table(
            columns=[
                {'name': 'mint', 'label': 'Mint', 'field': 'mint'},
                {'name': 'image', 'label': 'Image', 'field': 'image',
                 'template': "<img :src='row.image' class='w-16 h-16' />"},
                {'name': 'created', 'label': 'Created', 'field': 'created'},
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
            row_key='mint',
            pagination={'rowsPerPage': 10}
        ).classes('w-full')

        # Neuer Bereich für Top 20 Holder
        with ui.card().classes("q-pa-md"):
            ui.label("Top 20 Holder").classes("text-xl")
            self.mint_input = ui.input(
                label="Token Mint Address",
                placeholder="z.B. 7xKXtg2CWgdmZQ6A54NDq8V5FZRjhzp9V5QD5VyZq...",
                validation={'Invalid length': lambda v: len(v) >= 32}
            ).classes("w-full")
            ui.button("Show Top Holders", on_click=self.show_top_holders)
        self.table_holders = ui.table(
            columns=[
                {'name': 'address', 'label': 'Address', 'field': 'address'},
                {'name': 'percentage', 'label': 'Anteil', 'field': 'percentage'},
                {'name': 'role', 'label': 'Rolle', 'field': 'role'}
            ],
            rows=[],
            row_key='address'
        ).classes("w-full")

        ui.timer(10, self.update_all_table)

    def update_all_table(self):
        new_rows = []
        for mint, data in self.viewmodel.tokens.items():
            token_mint = data.get('mint', 'N/A')
            token_name = data.get('name', 'N/A')
            token_symbol = data.get('symbol', 'N/A')
            token_image = data.get('image_uri', 'N/A')
            created_ts = data.get('created_timestamp')
            if created_ts:
                created_date = datetime.fromtimestamp(created_ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
            else:
                created_date = "N/A"

            pair_data = data.get('pair', {})
            pair_stats = data.get('pairStats', {})

            try:
                market_cap = float(pair_data.get('pairMarketcapUsd', 0))
                price = float(pair_data.get('pairPrice1Usd', 0))
            except Exception:
                market_cap = price = 0.0

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

            try:
                fdv = float(pair_data.get('fdv', 0))
            except Exception:
                fdv = 0.0

            formatted_market_cap = f"${market_cap:,.2f}" if market_cap else "N/A"
            formatted_price = f"${price:,.8f}" if price else "N/A"
            formatted_change_5min = f"{change_5min:.2f}%" if change_5min else "0.00%"
            formatted_change_1h = f"{change_1h:.2f}%" if change_1h else "0.00%"
            formatted_change_6h = f"{change_6h:.2f}%" if change_6h else "0.00%"
            formatted_change_24h = f"{change_24h:.2f}%" if change_24h else "0.00%"
            formatted_migration_progress = f"{migration_progress:.2f}%" if migration_progress else "N/A"
            formatted_fdv = f"${fdv:,.2f}" if fdv else "N/A"

            new_rows.append({
                'mint': token_mint,
                'image': token_image,
                'created': created_date,
                'symbol': token_symbol,
                'name': token_name,
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

    async def show_top_holders(self):
        mint_address = self.mint_input.value.strip()
        if not mint_address:
            ui.notify("Bitte Mint-Adresse eingeben", color="negative")
            return
        if len(mint_address) < 32:
            ui.notify("Ungültige Mint-Adresse (zu kurz)", color="negative")
            return

        try:
            await self.viewmodel.load_top_holders(mint_address)
            self.update_top_holders_table()
            ui.notify(f"Top Holder für {mint_address[:6]}... geladen", color="positive")
        except Exception as e:
            ui.notify(f"Fehler: {str(e)}", color="negative")

    def update_top_holders_table(self):
        rows = []
        vm = self.viewmodel  
        
        for holder in vm.top_holders:
            address = holder["address"]
            role = ""
            
            # Rollenüberprüfung
            if address == vm.selected_token_creator:
                role = "👑 Dev"
            elif address == vm.bonding_curve:
                role = "📈 Bonding Curve"
            elif address == vm.associated_bonding_curve:
                role = "🔗 Associated Curve"
            
            rows.append({
                "address": address,
                "percentage": holder["percentage"],
                "role": role  
            })
        
        self.table_holders.columns = [
            {'name': 'address', 'label': 'Address', 'field': 'address'},
            {'name': 'percentage', 'label': 'Anteil', 'field': 'percentage'},
            {'name': 'role', 'label': 'Rolle', 'field': 'role'}
        ]
        
        self.table_holders.rows = rows
        self.table_holders.update()

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
            token_mint = data.get('mint', 'N/A')
            token_name = data.get('name', 'N/A')
            token_symbol = data.get('symbol', 'N/A')
            token_image = data.get('image_uri', 'N/A')
            created_ts = data.get('created_timestamp')
            if created_ts:
                created_date = datetime.fromtimestamp(created_ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
            else:
                created_date = "N/A"

            try:
                pair_data = data.get('pair', {})
                pair_stats = data.get('pairStats', {})
                market_cap = float(pair_data.get('pairMarketcapUsd', 0))
                price = float(pair_data.get('pairPrice1Usd', 0))
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

            try:
                fdv = float(pair_data.get('fdv', 0))
            except Exception:
                fdv = 0.0

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
                'mint': token_mint,
                'image': token_image,
                'created': created_date,
                'symbol': token_symbol,
                'name': token_name,
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