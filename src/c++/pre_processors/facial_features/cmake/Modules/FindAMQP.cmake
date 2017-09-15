# Find the Rabbitmq C library

SET(_AMQP_REQUIRED_VARS  AMQP_INCLUDE_DIR AMQP_LIBRARY )

# Find the include directories
FIND_PATH(AMQP_INCLUDE_DIR
	NAMES amqpcpp.h
    HINTS ${AMQP_DIR}/include
)

FIND_LIBRARY(AMQP_LIBRARY
	NAMES libamqpcpp
    HINTS ${AMQP_DIR}/lib
)

SET(AMQP_PROCESS_INCLUDES AMQP_INCLUDE_DIR)
SET(AMQP_PROCESS_LIBS AMQP_LIBRARY)

include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(AMQP DEFAULT_MSG ${_AMQP_REQUIRED_VARS})