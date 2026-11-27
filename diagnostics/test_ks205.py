"""Read-only authenticated discovery and update; no credentials saved."""
import argparse
import asyncio
import getpass
import ipaddress
from importlib.metadata import version
from kasa import Discover


async def probe(host, username, password):
    device = None
    try:
        device = await Discover.discover_single(
            host, username=username, password=password, discovery_timeout=8, timeout=8)
        if device is None:
            print("Discovery returned no device.")
            return 2
        await device.update()
        print("SUCCESS: authenticated discovery and read-only update.")
        print("Model:", device.model)
        print("Switch state:", device.is_on)
        return 0
    except Exception as exc:
        print("Probe failed:", type(exc).__name__)
        return 1
    finally:
        if device is not None:
            try:
                await device.protocol.close()
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=ipaddress.ip_address)
    args = parser.parse_args()
    print("python-kasa:", version("python-kasa"))
    username = input("TP-Link account email: ").strip()
    password = getpass.getpass("TP-Link account password: ")
    if not username or not password:
        return 2
    return asyncio.run(probe(str(args.host), username, password))


if __name__ == "__main__":
    raise SystemExit(main())
