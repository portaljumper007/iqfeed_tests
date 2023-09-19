from typing import List
import time
from threading import Thread
import time
from typing import List
import socket
import typer
import asyncio

from iqfeed_utils import (
    connect_to_socket, send_message_to_socket, receive_data, clean_data, data_to_csv,
    close_socket, establish_live_feed, live_plot
    )

app = typer.Typer()

@app.command()

def historical(host: str, port: int, start_date: str, end_date: str, interval: str, tickers: List[str]):
    
    async def download_data_for_ticker(sym):
        reader, writer = await connect_to_socket(host=host, port=port)

        print(f"Downloading symbol: {sym}...")

        message = (
            f"HTT,{sym},{interval},{start_date} 000000,{end_date} 000000\n"
            if interval == "TICK"
            else f"HIT,{sym},{interval},{start_date} 000000,{end_date} 000000\n"
        )

        await send_message_to_socket(writer=writer, message=message)
        startTime = time.perf_counter()
        data = await receive_data(reader=reader)
        duration = time.perf_counter() - startTime
        data = clean_data(data=data)
        print(data.count("\n"), "length", duration, "duration", data.count("\n")/duration, "lines per second")
        data_to_csv(data=data, sym=sym, start_date=start_date, end_date=end_date, interval=interval)
        
        close_socket(writer)

    async def inner_historical():
        # Create tasks for downloading data
        tasks = []
        for sym in tickers:
            task = download_data_for_ticker(sym)
            tasks.append(task)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
    
    # Run the inner asynchronous function
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # For Windows
    asyncio.run(inner_historical())

async def live_coroutine(host: str, port: int, ticker: str):
    reader, writer = await connect_to_socket(host, port)
    await establish_live_feed(reader, writer, ticker)

def async_runner(host,port,ticker):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(live_coroutine(host, port, ticker))

import threading

def live(host: str, port: int, ticker: str):
    async_thread = threading.Thread(target=async_runner, args=(host,port,ticker))
    async_thread.start()

    live_plot()

    async_thread.join() 

if __name__ == "__main__":
    app()
