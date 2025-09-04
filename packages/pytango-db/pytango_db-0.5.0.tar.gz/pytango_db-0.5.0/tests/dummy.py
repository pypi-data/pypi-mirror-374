import tango
from tango.server import Device, attribute, command, run


class Dummy(Device):
    def init_device(self):
        self._attr_int_writable = 0
        self.set_state(tango.DevState.RUNNING)

    @attribute(dtype=float, unit="mm")
    def attr_float(self):
        return 17.3

    @attribute(dtype=float, unit="count")
    def attr_int(self):
        return -24

    @attribute(dtype=[float], unit="cm", max_dim_x=3)
    def attr_float_array(self):
        return [1.2, 3.4, 5.6]

    @attribute(dtype=int)
    def attr_int_writable(self):
        return self._attr_int_writable

    @attr_int_writable.write
    def _write(self, value):
        self._attr_int_writable = value

    @command(dtype_in=int, doc_in="in", dtype_out=int, doc_out="out")
    def CommandInt(self, arg):
        return arg


if __name__ == "__main__":
    run((Dummy,))
