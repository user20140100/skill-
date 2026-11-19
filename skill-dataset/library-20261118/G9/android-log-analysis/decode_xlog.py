#!/usr/bin/env python3
"""
xlog decoder - converts binary .xlog files to readable text logs.
Ported from the original Python 2.7 version to Python 3.
Supports zlib and zstd compressed xlog formats (non-encrypted only).
"""

import sys
import os
import glob
import zlib
import struct
import traceback

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False

MAGIC_NO_COMPRESS_START = 0x03
MAGIC_NO_COMPRESS_START1 = 0x06
MAGIC_NO_COMPRESS_NO_CRYPT_START = 0x08
MAGIC_COMPRESS_START = 0x04
MAGIC_COMPRESS_START1 = 0x05
MAGIC_COMPRESS_START2 = 0x07
MAGIC_COMPRESS_NO_CRYPT_START = 0x09

MAGIC_SYNC_ZSTD_START = 0x0A
MAGIC_SYNC_NO_CRYPT_ZSTD_START = 0x0B
MAGIC_ASYNC_ZSTD_START = 0x0C
MAGIC_ASYNC_NO_CRYPT_ZSTD_START = 0x0D

MAGIC_END = 0x00

ENCRYPTED_MAGICS = {
    MAGIC_NO_COMPRESS_START1,
    MAGIC_COMPRESS_START2,
    MAGIC_SYNC_ZSTD_START,
    MAGIC_ASYNC_ZSTD_START,
}

SHORT_KEY_MAGICS = {
    MAGIC_NO_COMPRESS_START,
    MAGIC_COMPRESS_START,
    MAGIC_COMPRESS_START1,
}

LONG_KEY_MAGICS = {
    MAGIC_COMPRESS_START2,
    MAGIC_NO_COMPRESS_START1,
    MAGIC_NO_COMPRESS_NO_CRYPT_START,
    MAGIC_COMPRESS_NO_CRYPT_START,
    MAGIC_SYNC_ZSTD_START,
    MAGIC_SYNC_NO_CRYPT_ZSTD_START,
    MAGIC_ASYNC_ZSTD_START,
    MAGIC_ASYNC_NO_CRYPT_ZSTD_START,
}

ALL_MAGICS = SHORT_KEY_MAGICS | LONG_KEY_MAGICS

lastseq = 0


def _crypt_key_len(magic):
    if magic in SHORT_KEY_MAGICS:
        return 4
    if magic in LONG_KEY_MAGICS:
        return 64
    return -1


def IsGoodLogBuffer(_buffer, _offset, count):
    if _offset == len(_buffer):
        return (True, '')

    magic_start = _buffer[_offset]
    cklen = _crypt_key_len(magic_start)
    if cklen < 0:
        return (False, '_buffer[%d]:%d != MAGIC_NUM_START' % (_offset, _buffer[_offset]))

    headerLen = 1 + 2 + 1 + 1 + 4 + cklen

    if _offset + headerLen + 1 + 1 > len(_buffer):
        return (False, 'offset:%d > len(buffer):%d' % (_offset, len(_buffer)))

    length = struct.unpack_from("I", _buffer, _offset + headerLen - 4 - cklen)[0]

    if _offset + headerLen + length + 1 > len(_buffer):
        return (False, 'log length:%d, end pos %d > len(buffer):%d' % (
            length, _offset + headerLen + length + 1, len(_buffer)))

    if MAGIC_END != _buffer[_offset + headerLen + length]:
        return (False, 'log length:%d, buffer[%d]:%d != MAGIC_END' % (
            length, _offset + headerLen + length, _buffer[_offset + headerLen + length]))

    if count <= 1:
        return (True, '')
    return IsGoodLogBuffer(_buffer, _offset + headerLen + length + 1, count - 1)


def GetLogStartPos(_buffer, _count):
    offset = 0
    while offset < len(_buffer):
        if _buffer[offset] in ALL_MAGICS:
            if IsGoodLogBuffer(_buffer, offset, _count)[0]:
                return offset
        offset += 1
    return -1


def DecodeBuffer(_buffer, _offset, _outbuffer):
    if _offset >= len(_buffer):
        return -1

    ret = IsGoodLogBuffer(_buffer, _offset, 1)
    if not ret[0]:
        fixpos = GetLogStartPos(_buffer[_offset:], 1)
        if fixpos == -1:
            return -1
        _outbuffer.extend(
            ("[F]decode_xlog.py decode error len=%d, result:%s\n" % (fixpos, ret[1])).encode('utf-8'))
        _offset += fixpos

    magic_start = _buffer[_offset]
    cklen = _crypt_key_len(magic_start)
    if cklen < 0:
        _outbuffer.extend(
            ('in DecodeBuffer _buffer[%d]:%d != MAGIC_NUM_START\n' % (_offset, magic_start)).encode('utf-8'))
        return -1

    headerLen = 1 + 2 + 1 + 1 + 4 + cklen
    length = struct.unpack_from("I", _buffer, _offset + headerLen - 4 - cklen)[0]
    tmpbuffer = bytearray(length)

    seq = struct.unpack_from("H", _buffer, _offset + headerLen - 4 - cklen - 4)[0]
    begin_hour = struct.unpack_from("B", _buffer, _offset + headerLen - 4 - cklen - 2)[0]
    end_hour = struct.unpack_from("B", _buffer, _offset + headerLen - 4 - cklen - 1)[0]

    global lastseq
    if seq != 0 and seq != 1 and lastseq != 0 and seq != (lastseq + 1):
        _outbuffer.extend(
            ("[F]decode_xlog.py log seq:%d-%d is missing\n" % (lastseq + 1, seq - 1)).encode('utf-8'))

    if seq != 0:
        lastseq = seq

    tmpbuffer[:] = _buffer[_offset + headerLen:_offset + headerLen + length]

    try:
        if magic_start in ENCRYPTED_MAGICS:
            _outbuffer.extend(b"[F]decode_xlog.py encrypted xlog, need private key to decode\n")
        elif magic_start in (MAGIC_ASYNC_NO_CRYPT_ZSTD_START, MAGIC_SYNC_NO_CRYPT_ZSTD_START):
            if not HAS_ZSTD:
                _outbuffer.extend(b"[F]decode_xlog.py zstandard not installed, cannot decompress zstd\n")
                return _offset + headerLen + length + 1
            decompressor = zstd.ZstdDecompressor()
            tmpbuffer = decompressor.decompress(bytes(tmpbuffer), max_output_size=10 * 1024 * 1024)
        elif magic_start in (MAGIC_COMPRESS_START, MAGIC_COMPRESS_NO_CRYPT_START):
            decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
            tmpbuffer = decompressor.decompress(bytes(tmpbuffer))
        elif magic_start == MAGIC_COMPRESS_START1:
            decompress_data = bytearray()
            tmp = bytearray(tmpbuffer)
            while len(tmp) > 0:
                single_log_len = struct.unpack_from("H", tmp, 0)[0]
                decompress_data.extend(tmp[2:single_log_len + 2])
                tmp = tmp[single_log_len + 2:]
            decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
            tmpbuffer = decompressor.decompress(bytes(decompress_data))
    except Exception as e:
        traceback.print_exc()
        _outbuffer.extend(("[F]decode_xlog.py decompress err, %s\n" % str(e)).encode('utf-8'))
        return _offset + headerLen + length + 1

    _outbuffer.extend(tmpbuffer)
    return _offset + headerLen + length + 1


def ParseFile(_file, _outfile):
    with open(_file, "rb") as fp:
        _buffer = bytearray(fp.read())

    startpos = GetLogStartPos(_buffer, 2)
    if startpos == -1:
        print("  [SKIP] No valid xlog data found in: %s" % _file)
        return False

    outbuffer = bytearray()
    while True:
        startpos = DecodeBuffer(_buffer, startpos, outbuffer)
        if startpos == -1:
            break

    if len(outbuffer) == 0:
        print("  [SKIP] Decoded output is empty: %s" % _file)
        return False

    with open(_outfile, "wb") as fpout:
        fpout.write(outbuffer)
    print("  [OK] %s -> %s" % (_file, _outfile))
    return True


def main(args):
    global lastseq

    if len(args) == 1:
        if os.path.isdir(args[0]):
            filelist = sorted(glob.glob(os.path.join(args[0], "*.xlog")))
            if not filelist:
                print("No .xlog files found in: %s" % args[0])
                return
            for filepath in filelist:
                lastseq = 0
                ParseFile(filepath, filepath + ".log")
        else:
            ParseFile(args[0], args[0] + ".log")
    elif len(args) == 2:
        ParseFile(args[0], args[1])
    else:
        filelist = sorted(glob.glob("*.xlog"))
        if not filelist:
            print("No .xlog files found in current directory")
            return
        for filepath in filelist:
            lastseq = 0
            ParseFile(filepath, filepath + ".log")


if __name__ == "__main__":
    main(sys.argv[1:])
