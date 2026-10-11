"""Guard the public RPC stacks against bypassing their Caddy proxy."""

from pathlib import Path
import re
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RPC_COMPOSE_FILES = (
    Path("testnet/rpc/docker-compose.yml"),
    Path("mainnet/rpc/docker-compose.yml"),
)
EXTERNAL_RPC_FLAG = re.compile(r"(?m)^\s+--(?:unsafe-)?rpc-external(?:\s|$)")


class PublicRpcLoopbackTests(unittest.TestCase):
    def test_rpc_nodes_do_not_bind_all_interfaces(self) -> None:
        for relative_path in RPC_COMPOSE_FILES:
            with self.subTest(network=relative_path.parts[0]):
                compose_file = REPOSITORY_ROOT / relative_path
                compose = compose_file.read_text(encoding="utf-8")
                service_start = compose.index("  orbinum-rpc-node:\n")
                service_end = compose.find("\n  caddy:\n", service_start)
                self.assertNotEqual(service_end, -1, "expected a Caddy service")
                rpc_service = compose[service_start:service_end]

                self.assertRegex(rpc_service, r"(?m)^    network_mode: host$")
                self.assertNotRegex(
                    rpc_service,
                    EXTERNAL_RPC_FLAG,
                    "public RPC must stay on loopback so it cannot bypass Caddy",
                )


if __name__ == "__main__":
    unittest.main()
