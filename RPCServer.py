import pynng
import asyncio

from jsonrpc import JSONRPCResponseManager, Dispatcher

class RPCServer:
	def __init__(self, address):
		self.address = address
		self.dispatcher = Dispatcher()

	def register_function(self, function = None, name = None):
		return self.dispatcher.add_method(function, name)

	async def response(self, sock, msg):
		content = msg.bytes.decode()
		
		response = JSONRPCResponseManager.handle(
			content, self.dispatcher)

		if response is None: return

		await sock.asend(response.json.encode())

	async def start(self):
		ssock = pynng.Rep0()
		ssock.listen(self.address)
		while True:
			sock = ssock.new_context()
			msg = await sock.arecv_msg()
			asyncio.create_task(self.response(sock, msg))

	def serve_forever(self):
		asyncio.run(self.start())

if __name__ == "__main__":
	server = RPCServer("tcp://0.0.0.0:8080")

	import datetime
	# @server.register_function
	def today():
		ret = datetime.datetime.today().ctime()
		print("call today: ", ret)
		return ret

	server.register_function(today, "today")
	server.serve_forever()
