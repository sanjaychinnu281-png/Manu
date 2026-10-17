# message_ids.py
# Maps protocol message IDs to human-readable names.
# Used by classify() in app.py. Extend with any extra IDs you receive.

MESSAGE_ID_TO_NAME = {
    1:   "UDP_HELLO",
    2:   "UDP_ACK",
    3:   "UDP_PING",
    101: "RUDP_ACK",
    103: "SERVER_CLOSE",
    107: "SERVER_END",
    447: "RUDP_JOIN_MATCH",
    448: "RUDP_LOADING",
}
