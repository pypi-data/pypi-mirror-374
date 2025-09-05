#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/compatibility.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

py::module init_loader(py::module);
py::module init_abc(py::module);
py::module init_java(py::module);

void init_module(py::module m)
{
    pyext::init_compiler_config(m);
    pyext::check_compatibility(py::module::import("amulet.leveldb"), m);
    pyext::check_compatibility(py::module::import("amulet.utils"), m);
    pyext::check_compatibility(py::module::import("amulet.zlib"), m);
    pyext::check_compatibility(py::module::import("amulet.nbt"), m);
    pyext::check_compatibility(py::module::import("amulet.core"), m);
    pyext::check_compatibility(py::module::import("amulet.game"), m);
    pyext::check_compatibility(py::module::import("amulet.anvil"), m);

    auto abc = init_abc(m);
    m.attr("Level") = abc.attr("Level");

    auto loader = init_loader(m);
    m.attr("get_level") = loader.attr("get_level");
    m.attr("NoValidLevelLoader") = loader.attr("NoValidLevelLoader");

    // from .temporary_level import TemporaryLevel

    // Submodules
    auto java_module = init_java(m);
    // m.attr("JavaLevel") = java_module.attr("JavaLevel");

    // m.attr("BedrockLevel") = py::module::import("amulet.level.bedrock").attr("BedrockLevel");
}

PYBIND11_MODULE(_amulet_level, m)
{
    py::options options;
    options.disable_function_signatures();
    m.def("init", &init_module, py::doc("init(arg0: types.ModuleType) -> None"));
    options.enable_function_signatures();
}
