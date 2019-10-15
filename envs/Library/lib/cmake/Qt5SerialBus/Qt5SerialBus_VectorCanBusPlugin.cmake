
add_library(Qt5::VectorCanBusPlugin MODULE IMPORTED)

_populate_SerialBus_plugin_properties(VectorCanBusPlugin RELEASE "canbus/qtvectorcanbus.dll")

list(APPEND Qt5SerialBus_PLUGINS Qt5::VectorCanBusPlugin)
