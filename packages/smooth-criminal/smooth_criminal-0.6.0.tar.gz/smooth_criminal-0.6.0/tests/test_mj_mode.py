import random
import logging

from smooth_criminal import mj_mode


def test_mj_mode_determinism(caplog):
    random.seed(0)
    caplog.set_level(logging.INFO, logger="SmoothCriminal")

    @mj_mode
    def identidad(x):
        return x

    assert identidad([1, 2]) == [1, 2]
    assert "Jam session" in caplog.text

    caplog.clear()
    random.seed(2)

    @mj_mode
    def identidad2(x):
        return x

    assert identidad2([1, 2]) == [1, 2]
    assert "smooth" in caplog.text
