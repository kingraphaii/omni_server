import os
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# As configured in the device settings
HOST = os.environ.get("HOST", "0.0.0.0")  # Listen on all interfaces
PORT = os.environ.get("PORT", 3008)  # Port from device settings


async def handle_client(reader, writer):
    # Get the client address for logging
    client_address = writer.get_extra_info("peername")
    logger.info(f"Connection from {client_address}")

    while True:
        # Asynchronously receive data from the tracker
        data: bytes = await reader.read(1024)
        if not data:
            logger.info(f"Connection closed by {client_address}")
            break

        # Process the received data
        logger.info(f"Received data from {client_address}: {data.hex()}")

        # Send TCP/IP ACK back to the tracker
        ack: bytes = b"\x01"  # Example TCP/IP ACK
        writer.write(ack)
        await writer.drain()  # Ensure the data is sent before moving on

    # Close the connection
    writer.close()
    await writer.wait_closed()


async def start_server():
    # Create a TCP server using asyncio's start_server method
    server: asyncio.Server = await asyncio.start_server(handle_client, HOST, PORT)

    # Get the server details for logging
    address = server.sockets[0].getsockname()
    logger.info(f"Server listening on {address}")

    # Serve clients indefinitely
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    # Run the asyncio event loop to start the server
    asyncio.run(start_server())
