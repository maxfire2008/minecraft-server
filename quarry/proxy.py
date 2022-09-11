import twisted.internet
import quarry.net.proxy
import pickle

chunk_data = []

class ExampleBridge(quarry.net.proxy.Bridge):
    def packet_downstream_time_update(self, buff):
        content = buff.read()
        self.downstream.send_packet("time_update", content)
    def packet_upstream_player_position(self, buff):
        content = buff.read()
        self.upstream.send_packet("player_position", content)
    def packet_upstream_player_look(self, buff):
        content = buff.read()
        self.upstream.send_packet("player_look", content)
    def packet_upstream_player_position_and_look(self, buff):
        content = buff.read()
        self.upstream.send_packet("player_position_and_look", content)
    def packet_downstream_block_change(self, buff):
        content = buff.read()
        print(content)
        self.downstream.send_packet("block_change", content)
    def packet_upstream_chat_message(self, buff):
        buff.save()
        chat_message = buff.unpack_string()
        print(f" >> {chat_message}")
        
        self.downstream.send_packet("block_change", b'\x00\x007\xff\xff\xf3\xc0GO')

        buff.restore()
        self.upstream.send_packet("chat_message", buff.read())
    def packet_downstream_join_game(self, buff):
        content = buff.read()
        print(content)
        self.downstream.send_packet("join_game", content)
    def packet_downstream_chunk_data(self, buff):
        content = buff.read()
        chunk_data.append(content)
        pickle.dump(chunk_data, open("chunk_data.pickle", "wb"))
        self.downstream.send_packet("chunk_data", content)
    def packet_unhandled(self, buff, direction, name):
        print(f"[*][{direction}] {name}")
        return super().packet_unhandled(buff, direction, name)


factory = quarry.net.proxy.DownstreamFactory()
factory.bridge_class = ExampleBridge
factory.connect_host = "127.0.0.1"
factory.connect_port = 25565
factory.listen("127.0.0.1", 25566)
twisted.internet.reactor.run()