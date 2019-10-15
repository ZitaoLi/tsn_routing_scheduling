
add_library(Qt5::QQmlNativeDebugServiceFactory MODULE IMPORTED)

_populate_Qml_plugin_properties(QQmlNativeDebugServiceFactory RELEASE "qmltooling/qmldbg_nativedebugger.dll")

list(APPEND Qt5Qml_PLUGINS Qt5::QQmlNativeDebugServiceFactory)
