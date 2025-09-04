import io

# FN from https://stackoverflow.com/questions/6657820/how-to-convert-an-iterable-to-a-stream/20260030#20260030
def iter_to_stream(iter, bufferSize=io.DEFAULT_BUFFER_SIZE):
    class IterStream(io.RawIOBase):
        def __init__(self):
            self.leftover = None
        def readable(self):
            return True
        def readinto(self, b):
            try:
                l = len(b)
                chunk = self.leftover or next(iter)
                output, self.leftover = chunk[:l], chunk[l:]
                b[:len(output)] = output
                return len(output)
            except StopIteration:
                return 0
    return io.BufferedReader(IterStream(), buffer_size=bufferSize)
