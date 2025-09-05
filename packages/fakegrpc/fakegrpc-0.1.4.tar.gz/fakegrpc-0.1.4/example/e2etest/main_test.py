import os

import pytest
from dotenv import load_dotenv

from example.fakeservers import warehouse_v1
from fakegrpc.server.e2etest import E2ETestExecutor
from fakegrpc.server.port import find_free_port

# なぜか E2ETestCase._on_pytest で self.xxx_server として初期化すると、テストから参照したとき runtime error になるのでここで初期化
fake_warehouse_server = warehouse_v1.WarehouseServer()
fake_server_port = find_free_port([])
target_server_port = find_free_port([fake_server_port])


@pytest.mark.asyncio
class E2ETestCase:
    @pytest.fixture(scope="session", autouse=True)
    def _on_pytest(self):
        """
        pytest 起動時に実行される generator.
        async にはできないので、並行処理をしたい場合は thread を使用すること。
        """

        print(f"【main_test】: fake_server_port: {fake_server_port}")
        print(f"【main_test】: target_server_port: {target_server_port}")

        load_dotenv(".env.e2e")  # not needed for now
        os.environ["GRPC_SERVER_PORT"] = str(target_server_port)
        os.environ["SHIPPING_SERVICE_ADDR"] = f"localhost:{fake_server_port}"
        os.environ["WAREHOUSE_SERVICE_ADDR"] = f"localhost:{fake_server_port}"

        executor = E2ETestExecutor.start_servers(
            target_server_port,
            "make run",
            fake_server_port,
            [fake_warehouse_server],
            target_server_cwd="example",
        )

        yield

        executor.stop_servers()
