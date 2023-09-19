import socket
from threading import Thread
import time
from typing import List, Tuple
import io
import re
import asyncio
from datetime import datetime, timedelta

#https://www.quantstart.com/articles/Downloading-Historical-Intraday-US-Equities-From-DTN-IQFeed-with-Python/

ENDMSG_PATTERN = re.compile(r"!ENDMSG!")

async def connect_to_socket(host: str, port: int) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    reader, writer = await asyncio.open_connection(host, port)
    writer.write(bytes("S,SET PROTOCOL 6.2\n", "utf-8"))
    await writer.drain()
    print("Connection established!")
    return reader, writer

def close_socket(writer: asyncio.StreamWriter) -> None:
    writer.close()
    print("Connection closed")

async def send_message_to_socket(writer: asyncio.StreamWriter, message: str) -> None:
    writer.write(bytes(message, "utf-8"))
    await writer.drain()
    print("Message sent...")

async def receive_data(reader: asyncio.StreamReader) -> str:
    buffer_pieces = []
    while True:
        data = await reader.read(4096)
        buffer_pieces.append(data.decode('utf-8'))
        if ENDMSG_PATTERN.search(buffer_pieces[-1]):  # Check with precompiled regex
            break
    buffer = ''.join(buffer_pieces)[:-12]  # -12 to remove the '!ENDMSG!'
    print("Data received...")
    return buffer

def data_to_csv(data: str, sym: str, start_date: str, end_date: str, interval: str) -> None:
    with open(f"{sym}_{start_date}_{end_date}_{interval}.csv", "w", buffering=8192) as f:  # Buffered writing
        f.write(data)

def clean_data(data: str) -> str:
    """
    Does basic string operations to make the data more readable
    :param data: Data string
    :return: Cleared data
    """
    return data.replace("\r", "").replace(",\n", "\n").strip()

def calculate_latency(time_str: str, packet_timestamp: datetime) -> float:
    # Parse the time from the data string
    reported_time = datetime.strptime(time_str, '%H:%M:%S.%f')
    adjusted_reported_time = reported_time + timedelta(hours=5)
    
    # Convert reported time to a full datetime object for today's date
    adjusted_datetime = datetime.combine(datetime.today(), adjusted_reported_time.time())
    
    # Calculate latency
    latency_timedelta = adjusted_datetime - packet_timestamp
    
    # Convert latency to seconds as a float
    latency_seconds = latency_timedelta.total_seconds()
    return latency_seconds

latency_data = []

def parse_data(row: str, packet_timestamp: datetime):
    """
    Parses a row of data into relevant data types.
    :param row: A string of comma-separated values.
    :return: A list containing data in their relevant data types.
    """
    items = row.split(",")
    
    # Define the data types for each column. This is based on the given examples.
    # Modify this as needed.
    data_types = [
        str,   # Q
        str,   # AAPL
        float, # 177.8700
        int,   # 7
        str,   # 17:29:56.581896
        int,   # 24
        int,   # 67071270
        float, # 177.8800
        int,   # 300
        float, # 177.9200
        int,   # 1000
        str, # 176.4800
        str, # 179.3800
        str, # 176.1700
        str, # 175.0100
        str,   # ba
        str    # 8717
    ]
    
    parsed_data = [data_type(item) for data_type, item in zip(data_types, items)]
    latency = calculate_latency(parsed_data[4], packet_timestamp)
    if latency > 0:
        latency_data.append((packet_timestamp, latency))
        if len(latency_data) > 10000:
            latency_data.pop(0)
    else:
        pass #this is usually a duplicate ID getting sent again for the same bar data that's already been received, but the time on that bar data's receival is now old.

    return parsed_data

async def establish_live_feed(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, ticker_name: str) -> None:
    writer.write(bytes(f"S,TIMESTAMPSOFF\n", "utf-8"))
    await writer.drain()
    writer.write(bytes(f"w{ticker_name}\n", "utf-8"))
    await writer.drain()
    
    buffer = ""

    while True:
        raw_data = await reader.read(4096)
        
        # Capture the exact time the packet was received
        packet_timestamp = datetime.now()

        buffer += raw_data.decode("utf-8")

        while "\n" in buffer:
            row, buffer = buffer.split("\n", 1)
            row = row.replace("\r", "").strip()

            if row and row[0] == "Q":
                print(parse_data(row, packet_timestamp))
            else:
                print(row)

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns
import warnings

latency_data = []  # This should be updated in real-time with your data

def live_plot():
    fig, (ax, ax_hist, ax_vol) = plt.subplots(1, 3, figsize=(15, 5), gridspec_kw={'width_ratios': [4, 1, 2]})

    # Set background colors and grid lines
    for axis in [ax, ax_hist, ax_vol]:
        axis.set_facecolor('#f4f4f4')
        axis.grid(True, linestyle="--", linewidth=0.5)

    # Placeholder for scatter points
    scatter = ax.scatter([], [], color='blue', s=5, alpha=0.5)
    
    # For latency volatility
    line, = ax_vol.plot([], [], color="purple", lw=2)
    
    # Format the x-axis to handle datetime values
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    def init():
        return scatter, line

    def update(num):
        if len(latency_data) == 0:
            return scatter, line

        xdata = [mdates.date2num(item[0]) for item in latency_data]
        ydata = [item[1] for item in latency_data]

        scatter.set_offsets(np.c_[xdata, ydata])  # Update scatter points

        with warnings.catch_warnings():
            # Suppress specific warnings
            warnings.simplefilter("ignore", category=UserWarning)
            
            # KDE for histogram with custom bandwidth
            ax_hist.cla()
            sns.kdeplot(y=ydata, ax=ax_hist, fill=True, color='gray', bw=0.01, warn_singular=False)

            # Latency volatility (rolling standard deviation)
            window = max(10, len(ydata)//5)  # Use 20% of data, at least 10 points
            y_vol = np.sqrt(np.convolve(np.power(np.diff(ydata, prepend=ydata[0]), 2), np.ones(window)/window, mode='valid'))
            x_vol = xdata[:len(y_vol)]
            line.set_data(x_vol, y_vol)

        # Set x and y limits dynamically
        y_min = min(ydata)
        y_max = max(ydata)
        ax.set_xlim(min(xdata), max(xdata))
        ax.set_ylim(y_min, y_max)
        ax_hist.set_ylim(y_min, y_max)
        ax_vol.set_xlim(min(xdata), max(xdata))
        ax_vol.set_ylim(0, max(y_vol) * 1.1)  # Ensure positive values and a little headroom

        fig.autofmt_xdate()  # Make space for and rotate the x-axis tick labels

        return scatter, line

    # Axis labels and titles
    ax.set_xlabel('Time')
    ax.set_ylabel('Latency (seconds)')
    ax.set_title('Latency over Time')
    ax_vol.set_xlabel('Time')
    ax_vol.set_ylabel('Latency Volatility')
    ax_vol.set_title('Volatility of Latency')

    ani = FuncAnimation(fig, update, frames=range(100), init_func=init, repeat=True)
    plt.tight_layout()
    plt.show()