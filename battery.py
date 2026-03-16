# battery.py — Battery level + WiFi status readers
#
# Battery tries these sources in order:
#   1. MAX17048 fuel gauge over I2C (pip install smbus2)
#   2. File-based override: reads integer 0-100 from /tmp/battery_pct
#   3. Pimoroni LiPo SHIM low-battery GPIO pin (binary: ok / critical)
#   4. Returns None (indicator shows "?")
#
# To force a level for testing:  echo 75 > /tmp/battery_pct

import time
import subprocess
import platform

_cache = {"pct": None, "charging": None, "ts": 0}
_wifi_cache = {"connected": False, "ts": 0}
UPDATE_INTERVAL = 30  # seconds between reads


def get_battery():
    """Return (percentage: int|None, charging: bool|None).
    Cached — only reads hardware every UPDATE_INTERVAL seconds."""
    now = time.time()
    if now - _cache["ts"] < UPDATE_INTERVAL:
        return _cache["pct"], _cache["charging"]

    pct, charging = _read_max17048()
    if pct is None:
        pct, charging = _read_file()
    if pct is None:
        pct, charging = _read_lipo_shim_gpio()

    _cache["pct"] = pct
    _cache["charging"] = charging
    _cache["ts"] = now
    return pct, charging


def _read_max17048():
    """Read battery % from MAX17048 fuel gauge (I2C addr 0x36)."""
    try:
        import smbus2
        bus = smbus2.SMBus(1)
        # SOC register 0x04: high byte = whole %, low byte = 1/256 %
        data = bus.read_word_data(0x36, 0x04)
        # smbus returns little-endian; MAX17048 is big-endian
        pct = data & 0xFF  # high byte is actually first
        pct = max(0, min(100, pct))
        bus.close()
        return pct, None  # MAX17048 doesn't report charging status
    except Exception:
        return None, None


def _read_file():
    """Read battery % from /tmp/battery_pct (plain integer 0-100)."""
    try:
        with open("/tmp/battery_pct", "r") as f:
            val = int(f.read().strip())
            return max(0, min(100, val)), None
    except Exception:
        return None, None


def _read_lipo_shim_gpio():
    """Read Pimoroni LiPo SHIM low-battery pin (GPIO 4, active low).
    Returns 10% if low, 50% if ok — rough binary estimate."""
    try:
        # Try gpiod first (Pi 5 compatible), fall back to sysfs
        try:
            import gpiod
            chip = gpiod.Chip("gpiochip4")
            line = chip.get_line(4)
            line.request(consumer="battery", type=gpiod.LINE_REQ_DIR_IN)
            val = line.get_value()
            line.release()
        except Exception:
            # sysfs fallback
            with open("/sys/class/gpio/gpio4/value", "r") as f:
                val = int(f.read().strip())

        # LiPo SHIM: GPIO goes LOW when battery is critically low
        if val == 0:
            return 10, None
        else:
            return 50, None
    except Exception:
        return None, None


# --------------- WiFi status ---------------

def get_wifi_connected():
    """Return True if WiFi is connected, False otherwise.
    Cached — only checks every UPDATE_INTERVAL seconds."""
    now = time.time()
    if now - _wifi_cache["ts"] < UPDATE_INTERVAL:
        return _wifi_cache["connected"]

    connected = _check_wifi()
    _wifi_cache["connected"] = connected
    _wifi_cache["ts"] = now
    return connected


def _check_wifi():
    """Check WiFi connectivity. Works on Linux (Pi) and Windows."""
    try:
        if platform.system() == "Linux":
            # Check wlan0 operstate — fast, no subprocess needed
            try:
                with open("/sys/class/net/wlan0/operstate", "r") as f:
                    return f.read().strip() == "up"
            except Exception:
                pass
            # Fallback: check iwgetid
            result = subprocess.run(
                ["iwgetid", "-r"], capture_output=True, timeout=3)
            return result.returncode == 0 and len(result.stdout.strip()) > 0
        else:
            # Windows fallback — ping localhost as a connectivity hint
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "1000", "8.8.8.8"],
                capture_output=True, timeout=3)
            return result.returncode == 0
    except Exception:
        return False
