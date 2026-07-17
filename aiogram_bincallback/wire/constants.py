from aiogram_bincallback.core.constants import HEADER_BITS
from aiogram_bincallback.core.constants import MAX_CALLBACK_LENGTH

BASE128_ALPHABET = "".join(chr(code) for code in range(128))
BASE128_RADIX = len(BASE128_ALPHABET)
_BITS_PER_BYTE = 8

_COMBINATORIAL_CEILING_BITS: int = (BASE128_RADIX ** MAX_CALLBACK_LENGTH).bit_length() - 1
MAX_TOTAL_BITS: int = (_COMBINATORIAL_CEILING_BITS - 1) // _BITS_PER_BYTE * _BITS_PER_BYTE
MAX_PAYLOAD_BITS: int = MAX_TOTAL_BITS - HEADER_BITS
