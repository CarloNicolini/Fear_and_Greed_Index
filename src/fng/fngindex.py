"""Fear and Greed Index scraper with CLI interface."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import polars as pl
import requests
from fake_useragent import UserAgent
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class FearAndGreedIndex:
    """Fear and Greed Index data scraper and processor."""

    BASE_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/"

    def __init__(self, console: Optional[Console] = None):
        """Initialize the scraper with console for output."""
        self.console = console or Console()
        self.ua = UserAgent()

    def get_headers(self) -> dict[str, str]:
        """Generate request headers with random user agent."""
        return {"User-Agent": self.ua.random}

    def fetch_historical_data(self, start_date: str) -> dict:
        """Fetch historical Fear and Greed data from CNN API."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Fetching data from CNN API...", total=1)

            response = requests.get(
                f"{self.BASE_URL}{start_date}", headers=self.get_headers()
            )
            response.raise_for_status()
            progress.advance(task)

        return response.json()

    def load_existing_data(self, csv_file: Path) -> Optional[pl.DataFrame]:
        """Load existing data from CSV file if it exists."""
        if not csv_file.exists():
            self.console.print(f"[yellow]Warning: {csv_file} not found[/yellow]")
            return None

        return pl.read_csv(
            csv_file, try_parse_dates=True, columns=["Date", "Fear Greed"]
        ).with_columns(pl.col("Date").cast(pl.Date))

    def process_data(
        self,
        start_date: str,
        end_date: str,
        csv_file: Optional[Path] = None,
        backfill: bool = False,
    ) -> pl.DataFrame:
        """Process Fear and Greed Index data."""
        # Load existing data if provided
        if csv_file:
            fng_data = self.load_existing_data(csv_file)
        else:
            # Create empty DataFrame with correct schema
            fng_data = pl.DataFrame(
                {"Date": [], "Fear Greed": []},
                schema={"Date": pl.Date, "Fear Greed": pl.Int64},
            )

        # Fetch new data from API
        api_data = self.fetch_historical_data(start_date)
        historical_data = api_data["fear_and_greed_historical"]["data"]

        # Convert API data to DataFrame
        api_records = []
        for record in historical_data:
            timestamp = int(record["x"])
            date = datetime.fromtimestamp(timestamp / 1000).date()
            value = int(record["y"])
            api_records.append({"Date": date, "Fear Greed": value})

        api_df = pl.DataFrame(api_records)

        # Combine existing data with API data
        if fng_data.height > 0:
            # Merge dataframes, API data takes precedence
            combined = fng_data.join(api_df, on="Date", how="outer_coalesce")
        else:
            combined = api_df

        # Create date range and fill missing dates
        date_range = pl.DataFrame().select(
            pl.date_range(
                start=datetime.strptime(start_date, "%Y-%m-%d").date(),
                end=datetime.strptime(end_date, "%Y-%m-%d").date(),
                interval="1d",
            ).alias("Date")
        )

        # Join with date range to ensure all dates are present
        result = date_range.join(combined, on="Date", how="left")

        # Fill missing values
        if backfill:
            result = result.with_columns(
                pl.col("Fear Greed").fill_null(strategy="backward")
            )
        else:
            result = result.with_columns(pl.col("Fear Greed").fill_null(0))

        # Sort by date
        return result.sort("Date")

    def save_data(
        self, data: pl.DataFrame, output_path: Path, format_type: str = "parquet"
    ):
        """Save data in specified format."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(f"Saving data as {format_type}...", total=1)

            if format_type.lower() == "parquet":
                data.write_parquet(output_path)
            elif format_type.lower() == "csv":
                data.write_csv(output_path)
            else:
                raise ValueError(f"Unsupported format: {format_type}")

            progress.advance(task)

        self.console.print(f"[green]✓ Data saved to {output_path}[/green]")

    def display_summary(self, data: pl.DataFrame):
        """Display a summary of the processed data."""
        # Calculate statistics
        total_records = data.height
        date_range = f"{data['Date'].min()} to {data['Date'].max()}"
        avg_fng = data["Fear Greed"].mean()
        min_fng = data["Fear Greed"].min()
        max_fng = data["Fear Greed"].max()
        missing_count = data.filter(pl.col("Fear Greed") == 0).height

        # Create summary table
        table = Table(title="Fear and Greed Index Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Total Records", str(total_records))
        table.add_row("Date Range", date_range)
        table.add_row("Average F&G", f"{avg_fng:.2f}" if avg_fng else "N/A")
        table.add_row("Min F&G", str(min_fng) if min_fng else "N/A")
        table.add_row("Max F&G", str(max_fng) if max_fng else "N/A")
        table.add_row("Missing/Zero Values", str(missing_count))

        self.console.print(table)

        # Show recent data preview
        self.console.print("\n[bold]Recent Data (Last 5 records):[/bold]")
        recent_data = data.tail(5)

        data_table = Table()
        data_table.add_column("Date", style="cyan")
        data_table.add_column("Fear & Greed", style="magenta")

        for row in recent_data.iter_rows(named=True):
            data_table.add_row(str(row["Date"]), str(row["Fear Greed"]))

        self.console.print(data_table)
