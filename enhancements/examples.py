# -*- coding: utf-8 -*-

import binascii
from enhancements.modules import Module


class ExampleModule(Module):

    def execute(self, data):
        pass


class HexDump(ExampleModule):

    @classmethod
    def parser_arguments(cls):
        cls.PARSER.add_argument(
            '--hexwidth',
            dest='hexwidth',
            type=int,
            default=16,
            help='width of the hexdump in chars'
        )

    def execute(self, data):
        result = []

        if isinstance(data, str):
            data = bytes(data, 'UTF-8')

        for i in range(0, len(data), self.args.hexwidth):
            s = data[i:i + self.args.hexwidth]
            hexa = list(map(''.join, zip(*[iter(binascii.hexlify(s).decode('utf-8'))] * 2)))
            while self.args.hexwidth - len(hexa) > 0:
                hexa.append(' ' * 2)
            text = ''.join([chr(x) if 0x20 <= x < 0x7F else '.' for x in s])
            addr = '%04X:    %s    %s' % (i, " ".join(hexa), text)
            result.append(addr)

        print('\n'.join(result))
        return data
