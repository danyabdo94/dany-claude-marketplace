"""Build the Chrome clipboard blob that Slack web reads on paste.

Usage: python3 -I slack_pickle.py <texty-json-file> <plain-file> <out-bin-file>

Slack keeps rich text (mentions, bold, links) in a custom `slack/texty`
type, a Quill delta. Chrome stores custom types inside one
`org.chromium.web-custom-data` blob, a Chrome Pickle of UTF-16 pairs.
"""

import json
import struct
import sys


def string16(text):
    data = text.encode('utf-16-le')
    length = struct.pack('<I', len(data) // 2)
    padding = b'\0' * (-len(data) % 4)
    return length + data + padding


def main():
    if len(sys.argv) != 4:
        sys.exit('usage: slack_pickle.py <texty-json-file> <plain-file> <out-bin-file>')

    with open(sys.argv[1], encoding='utf-8') as texty_file:
        texty = json.load(texty_file)
    with open(sys.argv[2], encoding='utf-8') as plain_file:
        plain = plain_file.read()

    texty_text = json.dumps(texty, ensure_ascii=False, separators=(',', ':'))

    payload = struct.pack('<I', 2)
    payload += string16('public.utf8-plain-text')
    payload += string16(plain)
    payload += string16('slack/texty')
    payload += string16(texty_text)

    blob = struct.pack('<I', len(payload)) + payload
    with open(sys.argv[3], 'wb') as out_file:
        out_file.write(blob)


main()
