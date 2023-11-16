import pytest
import dotenv


@pytest.fixture
def env():
    dotenv.load_dotenv()