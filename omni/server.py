import os
import logging
import asyncio
import datetime

log_dir = os.path.join(os.path.dirname(__file__), "..", ".logs")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "server.txt")
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG, INFO, WARNING, ERROR, or CRITICAL
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(),  # Logs to console as well
    ],
)

# As configured in the device settings
HOST = os.environ.get("HOST", "0.0.0.0")  # Listen on all interfaces
PORT = os.environ.get("PORT", 3008)  # Port from device settings


async def handle_client(reader, writer):
    # Get the client address for logging
    client_address = writer.get_extra_info("peername")
    logging.info(f"Connection from {client_address}")

    while True:
        timestamp = datetime.datetime.now().isoformat()
        # Asynchronously receive data from the tracker
        data: bytes = await reader.read(1024)
        if not data:
            logging.info(f"[{timestamp}] Connection closed by {client_address}")
            break

        # Process the received data
        # Start of Selection
        logging.info(f"[{timestamp}] Received data from {client_address}: {data.hex()}")

        # Send TCP/IP ACK back to the tracker
        ack: bytes = b"\x01"  # Example TCP/IP ACK
        writer.write(ack)
        await writer.drain()  # Ensure the data is sent before moving on

    # Close the connection
    writer.close()
    await writer.wait_closed()


async def start_server():
    timestamp = datetime.datetime.now().isoformat()
    # Create a TCP server using asyncio's start_server method
    server: asyncio.Server = await asyncio.start_server(handle_client, HOST, PORT)

    # Get the server details for logging
    address = server.sockets[0].getsockname()
    logging.info(f"[{timestamp}] Server listening on {address}")

    # Serve clients indefinitely
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    # Run the asyncio event loop to start the server
    asyncio.run(start_server())
