import twisted.internet
import quarry.net.server
import pickle

chunks = pickle.load(open("chunk_data.pickle", "rb"))

class ExampleServerProtocol(quarry.net.server.ServerProtocol):
    def player_joined(self):
        # Call super. This switches us to "play" mode, marks the player as
        #   in-game, and does some logging.
        quarry.net.server.ServerProtocol.player_joined(self)

        # Send "Join Game" packet
        # self.send_packet("join_game",
        #     self.buff_type.pack("iBqiB",
        #         0,                              # entity id
        #         3,                              # game mode
        #         0,                              # dimension
        #         0,                              # hashed seed
        #         0),                             # max players
        #     self.buff_type.pack_string("flat"), # level type
        #     self.buff_type.pack_varint(32),      # view distance
        #     self.buff_type.pack("??",
        #         False,                          # reduced debug info
        #         True))                          # show respawn screen
        self.send_packet("join_game", b'\x00\x00\x02\xd9\x01\x00\x00\x00\x00\xd4R\xce\xe5{\xf3\x15\xc0\x14\x07default\n\x00\x01')

        # Send "Player Position and Look" packet
        self.send_packet("player_position_and_look",
            self.buff_type.pack("dddff?",
                222,                         # x
                72,                       # y
                -194,                         # z
                0,                         # yaw
                0,                         # pitch
                0b00000),                  # flags
            self.buff_type.pack_varint(0)) # teleport id

        # Start sending "Keep Alive" packets
        self.ticker.add_loop(20, self.update_keep_alive)

        # Announce player joined
        self.factory.send_chat(u"\u00a7e%s has joined." % self.display_name)

    def player_left(self):
        quarry.net.server.ServerProtocol.player_left(self)

        # Announce player left
        self.factory.send_chat(u"\u00a7e%s has left." % self.display_name)

    def update_keep_alive(self):
        # Send a "Keep Alive" packet

        # 1.7.x
        if self.protocol_version <= 338:
            payload =  self.buff_type.pack_varint(0)

        # 1.12.2
        else:
            payload = self.buff_type.pack('Q', 0)

        self.send_packet("keep_alive", payload)

    def packet_chat_message(self, buff):
        # When we receive a chat message from the player, ask the factory
        # to relay it to all connected players
        p_text = buff.unpack_string()
        if p_text == "placegold":
            print("placing gold!")
            self.send_packet("block_change", b'\x00\x007\xff\xff\xf3\xc0GO')
        if p_text == "loadchunk":
            print("loading chunk!")
            for chunk_data in chunks:
                self.send_packet("chunk_data", chunk_data)
        self.factory.send_chat("<%s> %s" % (self.display_name, p_text))

    def packet_received(self, buff, name):
        print("Packet received:", name)
        return super().packet_received(buff, name)

class ExampleServerFactory(quarry.net.server.ServerFactory):
    protocol = ExampleServerProtocol
    def send_chat(self, message):
        for player in self.players:
            player.send_packet("chat_message",player.buff_type.pack_chat(message) + player.buff_type.pack('B', 0) )


factory = ExampleServerFactory()
factory.listen('127.0.0.1', 25566)
twisted.internet.reactor.run()