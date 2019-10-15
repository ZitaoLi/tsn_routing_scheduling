
add_library(Qt5::TinyCanBusPlugin MODULE IMPORTED)

_populate_SerialBus_plugin_properties(TinyCanBusPlugin RELEASE "canbus/qttinycanbus.dll")

list(APPEND Qt5SerialBus_PLUGINS Qt5::TinyCanBusPlugin)
