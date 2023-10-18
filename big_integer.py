class BigInteger:
    _block_length = 8

    def __init__(self, number: str):
        self._number = []
        while number:
            self._number.append(int(number[-self._block_length:], 16))
            number = number[:-self._block_length]
        self._number.reverse()

    def __str__(self):
        to_print = []
        for block in map(lambda i: hex(i)[2:], self._number):
            to_print.append(block if not to_print else '0' * (8 - len(block)) + block)
        return ''.join(to_print)

    def __xor__(self, other):
        return BigInteger(''.join(self._go_throw_blocks(other, 'xor')))

    def __or__(self, other):
        return BigInteger(''.join(self._go_throw_blocks(other, 'or')))

    def __and__(self, other):
        return BigInteger(''.join(self._go_throw_blocks(other, 'and')))

    def __rshift__(self, other):
        if other >= len(self.get_blocks()) * 8:
            return BigInteger('0')
        return BigInteger(self._from_blocks_to_hex_str(self.get_blocks[other // 8:]))

    def __lshift__(self, other):
        shifted_blocks = [0] * (other // 8)
        return BigInteger(self._from_blocks_to_hex_str(shifted_blocks + self.get_blocks()))

    def __add__(self, other):
        result = []
        temp_self = self.get_blocks()
        temp_other = other.get_blocks()
        diff = len(temp_other) - len(temp_self)
        if diff > 0:
            temp_self = [0] * diff + temp_self
        if diff < 0:
            temp_other = [0] * -diff + temp_other
        add_to_next_block = 0
        for i in range(-1, -len(temp_self) - 1, -1):
            new_block = temp_self[i] + temp_other[i] + add_to_next_block
            if new_block > 0xffffffff:
                add_to_next_block = int(hex(new_block)[2:][:-8], 16)
                new_block = int(hex(new_block)[2:][-8:], 16)
            else:
                add_to_next_block = 0
            result.append(new_block)

        result.reverse()

        return BigInteger(self._from_blocks_to_hex_str(result))

    def __sub__(self, other):
        result = []
        temp_self = self.get_blocks()
        temp_other = other.get_blocks()
        diff = len(temp_other) - len(temp_self)
        if diff > 0:
            temp_self = [0] * diff + temp_self
        if diff < 0:
            temp_other = [0] * -diff + temp_other
        sub_from_next_block = 0
        for i in range(-1, -len(temp_self) - 1, -1):
            new_block = temp_self[i] - temp_other[i] - sub_from_next_block
            if new_block < 0:
                sub_from_next_block = -new_block // 0x100000000 + 1
                new_block = new_block + sub_from_next_block * 0x100000000
            else:
                sub_from_next_block = 0
            result.append(new_block)

        result.reverse()

        return BigInteger(self._from_blocks_to_hex_str(result))

    def __mul__(self, other):
        if len(self.get_blocks()) == 1 or len(other.get_blocks()) == 1:
            return self.get_blocks()[0] * other.get_blocks()[0]

        n = max(len(self.get_blocks()), len(other.get_blocks()))
        m = n // 2

        a = BigInteger(''.join(map(lambda i: hex(i)[2:], self.get_blocks()[:m])))
        b = BigInteger(''.join(map(lambda i: hex(i)[2:], self.get_blocks()[m:])))
        c = BigInteger(''.join(map(lambda i: hex(i)[2:], other.get_blocks()[:m])))
        d = BigInteger(''.join(map(lambda i: hex(i)[2:], other.get_blocks()[m:])))

        ac = a * c
        bd = b * d
        product = (a + b) * (c + d) - ac - bd

        result = (ac << (2 * m * 8)) + (product << (m * 8)) + bd

        return result

    def __truediv__(self, other):
        quotient = BigInteger(0)
        remainder = BigInteger(str(self))
        divisor_int = int(other)

        while int(remainder) >= divisor_int:
            factor = 1
            temp_other = other
            while int(remainder) >= int(temp_other):
                temp_other <<= 1
                factor <<= 1
            temp_other >>= 1
            factor >>= 1

            remainder -= temp_other
            quotient += factor

        return quotient

    def __invert__(self):
        new_number = []
        for block in self._number:
            bin_block = bin(block)[2:]
            new_block = ''
            for bit in bin_block:
                new_block += '1' if bit == '0' else '0'
            new_number.append(int(new_block, 2))
        return BigInteger(''.join(map(lambda i: hex(i)[2:], new_number)))

    def __eq__(self, other):
        return str(self) == str(other)

    def get_blocks(self):
        return self._number

    @staticmethod
    def _from_blocks_to_hex_str(blocks):
        temp = map(lambda i: hex(i)[2:], blocks)
        return ''.join(map(lambda block: '0' * (8 - len(block)) + block, temp))

    def _go_throw_blocks(self, other, operand:str):
        result = []
        temp_self = self.get_blocks()
        temp_other = other.get_blocks()
        diff = len(temp_other) - len(temp_self)
        if diff > 0:
            temp_self = [0] * diff + temp_self
        if diff < 0:
            temp_other = [0] * -diff + temp_other
        for i in range(len(temp_self)):
            if operand == 'xor':
                result.append(hex(temp_self[i] ^ temp_other[i])[2:])
            elif operand == 'or':
                result.append(hex(temp_self[i] | temp_other[i])[2:])
            elif operand == 'and':
                result.append(hex(temp_self[i] & temp_other[i])[2:])
            elif operand == 'shiftR':
                result.append(hex(temp_self[i] >> temp_other[i])[2:])
            elif operand == 'shiftL':
                result.append(hex(temp_self[i] << temp_other[i])[2:])

        return result


if __name__ == '__main__':
    a = BigInteger('e035c6cfa42609b998b883bc1699df885cef74e2b2cc372eb8fa7e7')
    b = BigInteger('5072f028943e0fd5fab3273782de14b1011741bd0c5cd6ba6474330')
    result = BigInteger('b04736e73018066c620ba48b9447cb395df8355fbe90e194dc8e4d7')
    print((a ^ b) == result)
    print(~BigInteger('5'))
    a = BigInteger('36f028580bb02cc8272a9a020f4200e346e276ae664e45ee80745574e2f5ab80')
    b = BigInteger('70983d692f648185febe6d6fa607630ae68649f7e6fc45b94680096c06e4fadb')
    result = BigInteger('a78865c13b14ae4e25e90771b54963ee2d68c0a64d4a8ba7c6f45ee0e9daa65b')
    print((a + b) == result)
    a = BigInteger('33ced2c76b26cae94e162c4c0d2c0ff7c13094b0185a3c122e732d5ba77efebc')
    b = BigInteger('22e962951cb6cd2ce279ab0e2095825c141d48ef3ca9dabf253e38760b57fe03')
    result = BigInteger('10e570324e6ffdbc6b9c813dec968d9bad134bc0dbb061530934f4e59c2700b9')
    print((a - b) == result)
    a = BigInteger('7d7deab2affa38154326e96d350deee1')
    b = BigInteger('97f92a75b3faf8939e8e98b96476fd22')
    result = BigInteger('4a7f69b908e167eb0dc9af7bbaa5456039c38359e4de4f169ca10c44d0a416e2')
    print((a * b) == result)
