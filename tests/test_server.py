import asyncio
import pytest

from omni.server import start_server

# Import the server's start_server function from the main server file
# from server import start_server  # Use this if the server code is in another file

HOST = "127.0.0.1"  # Localhost for testing
PORT = 3000  # The same port as the server


# Test fixture to start and stop the server for testing
@pytest.fixture
async def server():
    # Setup: start the server
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Let the server start up

    yield  # This is where the test will execute

    # Teardown: stop the server
    server_task.cancel()  # Stop the server task after the test


# Test case to simulate a client sending data to the server
@pytest.mark.asyncio
async def test_tracker_data(server):
    # Connect to the server as a client
    reader, writer = await asyncio.open_connection(HOST, PORT)

    # Simulate the tracker sending some data (as bytes)
    tracker_data = b"\x00\x01\x02\x03\x04\x05"  # Example binary data from the tracker
    writer.write(tracker_data)
    await writer.drain()  # Ensure data is sent

    # Receive the ACK from the server
    ack = await reader.read(1)  # Expect the ACK byte to be received
    assert ack == b"\x01", "Server did not send correct ACK"

    # Close the connection
    writer.close()
    await writer.wait_closed()


@pytest.mark.asyncio
async def test_multiple_clients(server):
    async def send_data(client_id):
        reader, writer = await asyncio.open_connection(HOST, PORT)
        tracker_data = f"\x00{client_id}".encode()  # Unique data for each client
        writer.write(tracker_data)
        await writer.drain()
        ack = await reader.read(1)
        assert ack == b"\x01", f"Client {client_id} did not receive correct ACK"
        writer.close()
        await writer.wait_closed()

    # Simulate multiple clients sending data
    await asyncio.gather(*(send_data(i) for i in range(10)))
