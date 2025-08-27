"""CLI interface for Fear and Greed Index scraper."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .fngindex import FearAndGreedIndex

app = typer.Typer(
    name="fng-cli",
    help="Fear and Greed Index scraper with CLI interface",
    rich_markup_mode="rich",
)

console = Console()


@app.command()
def scrape(
    start_date: str = typer.Option(
        "2020-09-19",
        "--start-date",
        "-s",
        help="Start date for data collection (YYYY-MM-DD format)",
        show_default=True,
    ),
    end_date: str = typer.Option(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d"),
        callback=lambda x: x or datetime.now().strftime("%Y-%m-%d"),
        help="End date for data collection (YYYY-MM-DD format). Defaults to today.",
        show_default="today",
    ),
    input_csv: Optional[Path] = typer.Option(
        None,
        "--input-csv",
        "-i",
        help="Path to existing CSV file to merge with new data",
        exists=False,  # Allow non-existing files
        file_okay=True,
        dir_okay=False,
    ),
    output_file: Path = typer.Option(
        "fng_data.parquet", "--output", "-o", help="Output file path"
    ),
    format_type: str = typer.Option(
        "parquet",
        "--format",
        "-f",
        help="Output format (parquet or csv)",
        case_sensitive=False,
    ),
    backfill: bool = typer.Option(
        False, "--backfill", "-b", help="Backfill missing values instead of using zeros"
    ),
    show_summary: bool = typer.Option(
        True, "--summary/--no-summary", help="Display data summary after processing"
    ),
) -> None:
    """
    Scrape Fear and Greed Index data from CNN API.

    This command fetches historical Fear and Greed Index data and saves it in the specified format.
    """
    # Validate format
    if format_type.lower() not in ["parquet", "csv"]:
        console.print("[red]Error: Format must be 'parquet' or 'csv'[/red]")
        raise typer.Exit(1)

    # Validate dates
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        if start_dt > end_dt:
            console.print("[red]Error: Start date must be before end date[/red]")
            raise typer.Exit(1)

    except ValueError as e:
        console.print(f"[red]Error: Invalid date format. Use YYYY-MM-DD. {e}[/red]")
        raise typer.Exit(1)

    # Ensure output file has correct extension
    if format_type.lower() == "parquet" and not output_file.suffix == ".parquet":
        output_file = output_file.with_suffix(".parquet")
    elif format_type.lower() == "csv" and not output_file.suffix == ".csv":
        output_file = output_file.with_suffix(".csv")

    try:
        console.print(f"[bold blue]Fear and Greed Index Scraper[/bold blue]")
        console.print(f"Date range: {start_date} to {end_date}")

        if input_csv:
            console.print(f"Input CSV: {input_csv}")

        console.print(f"Output: {output_file} ({format_type.upper()})")
        console.print(f"Backfill: {'Enabled' if backfill else 'Disabled'}")
        console.print()

        # Initialize scraper
        scraper = FearAndGreedIndex(console=console)

        # Process data
        data = scraper.process_data(
            start_date=start_date,
            end_date=end_date,
            csv_file=input_csv,
            backfill=backfill,
        )

        # Save data
        scraper.save_data(data, output_file, format_type)

        # Show summary if requested
        if show_summary:
            console.print()
            scraper.display_summary(data)

        console.print(
            f"\n[bold green]✓ Successfully processed {data.height} records![/bold green]"
        )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def info() -> None:
    """Display information about the Fear and Greed Index."""
    console.print("""
[bold blue]Fear and Greed Index Information[/bold blue]

The Fear and Greed Index is a measure of market sentiment that combines several factors:
- [cyan]Stock Price Momentum[/cyan]: S&P 500 vs 125-day moving average
- [cyan]Stock Price Strength[/cyan]: Stocks hitting 52-week highs vs lows
- [cyan]Stock Price Breadth[/cyan]: Trading volume in advancing vs declining stocks
- [cyan]Put/Call Options[/cyan]: Put/call ratio as fear indicator
- [cyan]Junk Bond Demand[/cyan]: Spread between high-yield and treasury bonds
- [cyan]Market Volatility[/cyan]: VIX compared to 50-day moving average
- [cyan]Safe Haven Demand[/cyan]: Performance difference between stocks and bonds

[bold]Scale:[/bold]
- [green]0-24: Extreme Fear[/green]
- [yellow]25-49: Fear[/yellow] 
- [blue]50-74: Greed[/blue]
- [red]75-100: Extreme Greed[/red]

[italic]Data source: CNN Fear and Greed Index[/italic]
    """)


if __name__ == "__main__":
    app()
