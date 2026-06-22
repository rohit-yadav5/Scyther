import pytest
from pathlib import Path

from scyther.core.models import SymbolLocation, FileDependency
from scyther.services.code_index_service import CodeIndexService


@pytest.fixture
def temp_project(tmp_path):
    # Setup mock files
    # Python file
    py_file = tmp_path / "app.py"
    py_file.write_text(
        "import helper\n"
        "from core.models import RuntimeContext\n"
        "\n"
        "class AppController:\n"
        "    def run(self):\n"
        "        print(helper.get_message())\n",
        encoding="utf-8"
    )

    helper_file = tmp_path / "helper.py"
    helper_file.write_text(
        "def get_message():\n"
        "    return 'Hello'\n",
        encoding="utf-8"
    )

    core_dir = tmp_path / "core"
    core_dir.mkdir()
    models_file = core_dir / "models.py"
    models_file.write_text(
        "class RuntimeContext:\n"
        "    pass\n",
        encoding="utf-8"
    )

    # JS file
    js_file = tmp_path / "index.js"
    js_file.write_text(
        "import { helper } from './utils/helper';\n"
        "const logger = require('./utils/logger');\n"
        "\n"
        "export class IndexController {\n"
        "    start() {\n"
        "        helper();\n"
        "    }\n"
        "}\n",
        encoding="utf-8"
    )

    utils_dir = tmp_path / "utils"
    utils_dir.mkdir()
    js_helper = utils_dir / "helper.js"
    js_helper.write_text(
        "export function helper() {\n"
        "    console.log('helper');\n"
        "}\n",
        encoding="utf-8"
    )

    js_logger = utils_dir / "logger.js"
    js_logger.write_text(
        "module.exports = function() {};\n",
        encoding="utf-8"
    )

    return tmp_path


def test_find_definitions_python(temp_project):
    service = CodeIndexService(str(temp_project))
    
    # Class lookup
    defs = service.find_definitions("AppController")
    assert len(defs) == 1
    assert defs[0].path == "app.py"
    assert defs[0].line == 4
    assert defs[0].symbol == "AppController"

    # Function lookup
    defs = service.find_definitions("get_message")
    assert len(defs) == 1
    assert defs[0].path == "helper.py"
    assert defs[0].line == 1
    assert defs[0].symbol == "get_message"


def test_find_definitions_javascript(temp_project):
    service = CodeIndexService(str(temp_project))
    
    # Class lookup
    defs = service.find_definitions("IndexController")
    assert len(defs) == 1
    assert defs[0].path == "index.js"
    assert defs[0].line == 4
    assert defs[0].symbol == "IndexController"

    # Function lookup
    defs = service.find_definitions("helper")
    assert len(defs) == 1
    assert defs[0].path == "utils/helper.js"
    assert defs[0].line == 1
    assert defs[0].symbol == "helper"


def test_find_references(temp_project):
    service = CodeIndexService(str(temp_project))
    
    # Find references of "helper" - should find imports/usages but skip definition in utils/helper.js
    refs = service.find_references("helper")
    assert len(refs) > 0
    
    ref_locations = {(r.path, r.line) for r in refs}
    assert "index.js" in {r.path for r in refs}
    assert "app.py" in {r.path for r in refs}
    assert ("utils/helper.js", 1) not in ref_locations  # Excluded definition line
    assert ("utils/helper.js", 2) in ref_locations      # Included reference line


def test_get_dependencies_python(temp_project):
    service = CodeIndexService(str(temp_project))
    
    deps = service.get_dependencies("app.py")
    # app.py has: import helper (resolves helper.py), from core.models (resolves core/models.py)
    assert len(deps) == 2
    targets = {d.target for d in deps}
    assert "helper.py" in targets
    assert "core/models.py" in targets


def test_get_dependencies_javascript(temp_project):
    service = CodeIndexService(str(temp_project))
    
    deps = service.get_dependencies("index.js")
    # index.js imports ./utils/helper and require ./utils/logger
    assert len(deps) == 2
    targets = {d.target for d in deps}
    assert "utils/helper.js" in targets
    assert "utils/logger.js" in targets
