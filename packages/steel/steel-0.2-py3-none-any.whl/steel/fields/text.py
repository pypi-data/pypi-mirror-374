from io import BufferedIOBase

from .base import ConfigurationError, Field, Option, ValidationError


class EncodedString(Field[str]):
    encoding: Option[str]

    def __init__(self, *, encoding: str = "utf8"):
        self.encoding = encoding

    def validate(self, value: str) -> None:
        try:
            value.encode(self.encoding)
        except UnicodeEncodeError as e:
            raise ValidationError(f"{value} could be encoded: {e.reason}")

    def unpack(self, value: bytes) -> str:
        return value.decode(self.encoding)

    def pack(self, value: str) -> bytes:
        return value.encode(self.encoding)


class FixedLengthString(EncodedString):
    size: int
    padding: Option[bytes]

    def __init__(self, *, size: int, encoding: str = "utf8", padding: bytes = b"\x00"):
        super().__init__(encoding=encoding)
        if len(padding) > 1:
            raise ConfigurationError(
                f"String padding may only contain one byte; got {len(padding)}"
            )
        self.size = size
        self.padding = padding

    def read(self, buffer: BufferedIOBase) -> tuple[str, int]:
        # Even though this matches the behavior of ExplicitlySizedField,
        # it's useful to define it here, to easily contrast it with the
        # other fields below.
        encoded = buffer.read(self.size)
        return self.unpack(encoded), len(encoded)


class LenghIndexedString(EncodedString):
    # The byte-length of this string is stored in the data buffer itself,
    # so the size attribute defers to another configured Field type that can
    # return an int type.
    size_field: Field[int]

    def __init__(self, *, size: Field[int], encoding: str = "utf8"):
        super().__init__(encoding=encoding)
        self.size_field = size

    def read(self, buffer: BufferedIOBase) -> tuple[str, int]:
        # It would be easier to access the size field as `self.size`, but
        # when accessed as an attribute, its type hint also includes `int` as
        # a valid type, which doesn't have the necessary `read()` method.
        # Accessing it via the instance dictionary bypasses the descriptor
        # that adds the `int` return type. But the values in `self.__dict__`
        # are typed as `Any`, so this provides an explicit hint about what
        # type of object that's expected here.
        size_field: Field[int] = self.__dict__["size_field"]

        size, size_len = size_field.read(buffer)
        # raise RuntimeError(size)
        encoded = buffer.read(size)
        # raise RuntimeError(len(encoded))
        # print(len(encoded), encoded)
        return self.unpack(encoded), size_len + len(encoded)

    def pack(self, value: str) -> bytes:
        size_field: Field[int] = self.__dict__["size_field"]

        encoded = super().pack(value)
        size = size_field.pack(len(encoded))

        return size + encoded


class TerminatedString(EncodedString):
    size: int
    terminator: Option[bytes]

    def __init__(self, *, encoding: str = "utf8", terminator: bytes = b"\x00"):
        super().__init__(encoding=encoding)
        if len(terminator) > 1:
            raise ConfigurationError(
                f"String terminator may only contain one byte; got {len(terminator)}"
            )
        self.terminator = terminator

    def read(self, buffer: BufferedIOBase) -> tuple[str, int]:
        char = buffer.read(1)
        if char == b"":
            return "", 0

        value = bytearray()
        while char not in (b"", self.terminator):
            value.append(char[0])
            char = buffer.read(1)

        encoded = bytes(value)
        return self.unpack(encoded), len(encoded) + 1

    def pack(self, value: str) -> bytes:
        encoded = super().pack(value)
        return encoded + self.terminator


# Some aliases for convenience
CString = TerminatedString
PascalString = LenghIndexedString
