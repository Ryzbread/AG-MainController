import machine
import time
import network
import socket
import uasyncio as asyncio

# Set up the LED pin
led = machine.Pin('LED', machine.Pin.OUT)

html = """
    <!DOCTYPE html>
    <html>
      <head><title>MicroPython HTTP Server</title></head>
      <body>
        <h1>Hello, MicroPython!</h1>
      </body>
    </html>
    """

# Wi-Fi credentials
WIFI_SSID = "Louis"
WIFI_PASSWORD = "SourCream612$"

def connect_to_wifi():
    print("Connecting")
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            pass
    print('Network config:', wlan.ifconfig())

async def start_http_server(port=80):

    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print('HTTP server started on http://{}:{}'.format(addr[0], port))

    while True:
        cl, addr = s.accept()
        try:
            request = cl.recv(1024).decode()  # Decode the request as a string
            await handle_client(cl, request, addr)
        except Exception as e:
            print(f'Error handling client request: {e}')
        finally:
            cl.close()
        
async def handle_client(cl, request, addr):

    form_data = {}

    # Parse the HTTP request
    headers = request.split('\r\n')
    first_line = headers[0].split(' ')
    method = first_line[0]
    path = first_line[1]

    # Parse POST request
    if method == 'POST' and path == '/post':
        for header in headers:
            if 'Content-Length:' in header:
                content_length_header = header
                content_length = int(content_length_header.split(': ')[1])

            if(('data' in header) and (len(header) == content_length)):
                post_data = header

                # POST request has been validated. Parse the data
                pairs = post_data.split('&')  # Decode the POST data as UTF-8
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        form_data[key] = value

    # Print received connection request for testing
    # print('Client connected from', addr)
    # print("Headers: " + str(headers))
    # print("Method: " + str(method))
    # print("Path: " + str(path))
    # print("CLH: " + str(content_length_header))
    # print("Length: " + str(content_length))
    # print("Form Data: " + str(form_data))
    print("Node: " + str(form_data['node']) + "\tData: " + str(form_data['data']))

    response = html
    cl.send('HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n')
    cl.send(response)

# Blink Onboard LED 0.5hz
async def blink_led():
    while True:
        led.on()
        await asyncio.sleep(1)
        led.off()
        await asyncio.sleep(1)

if __name__ == "__main__":
    connect_to_wifi()

    loop = asyncio.get_event_loop()
    blink_led_task = asyncio.create_task(blink_led())
    http_server_task = asyncio.create_task(start_http_server())
    #loop.create_task(start_http_server())
    #tasks = [blink_led_task, http_server_task]
    #loop.run_until_complete(asyncio.gather(*tasks))
    #loop.run_until_complete(blink_led())
    #loop.run_until_complete(start_http_server())
    while(True):
        loop.run_until_complete(asyncio.gather(blink_led_task, http_server_task))