from aiogram_bincallback.core.constants import HEADER_BITS
from aiogram_bincallback.core.constants import MAX_CALLBACK_LENGTH

BASE93_ALPHABET = " !#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"
BASE93_RADIX = len(BASE93_ALPHABET)

MAX_TOTAL_BITS = (BASE93_RADIX ** MAX_CALLBACK_LENGTH).bit_length() - 1
MAX_PAYLOAD_BITS = MAX_TOTAL_BITS - HEADER_BITS
