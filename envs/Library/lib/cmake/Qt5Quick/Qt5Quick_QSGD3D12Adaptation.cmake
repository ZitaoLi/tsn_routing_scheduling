
add_library(Qt5::QSGD3D12Adaptation MODULE IMPORTED)

_populate_Quick_plugin_properties(QSGD3D12Adaptation RELEASE "scenegraph/qsgd3d12backend.dll")

list(APPEND Qt5Quick_PLUGINS Qt5::QSGD3D12Adaptation)
