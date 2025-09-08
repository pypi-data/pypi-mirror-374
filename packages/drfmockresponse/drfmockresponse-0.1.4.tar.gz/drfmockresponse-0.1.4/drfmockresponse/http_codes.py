from collections import OrderedDict

import rest_framework.status as status


class HttpCode(object):
    def __init__(self, code, name):
        self.code = code
        self.name = name


default_http_codes = OrderedDict()
default_http_codes["100"] = HttpCode(status.HTTP_100_CONTINUE, "HTTP_100_CONTINUE")
default_http_codes["101"] = HttpCode(status.HTTP_101_SWITCHING_PROTOCOLS, "HTTP_101_SWITCHING_PROTOCOLS")
default_http_codes["200"] = HttpCode(status.HTTP_200_OK, "HTTP_200_OK")
default_http_codes["201"] = HttpCode(status.HTTP_201_CREATED, "HTTP_201_CREATED")
default_http_codes["202"] = HttpCode(status.HTTP_202_ACCEPTED, "HTTP_202_ACCEPTED")
default_http_codes["203"] = HttpCode(
    status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, "HTTP_203_NON_AUTHORITATIVE_INFORMATION"
)
default_http_codes["204"] = HttpCode(status.HTTP_204_NO_CONTENT, "HTTP_204_NO_CONTENT")
default_http_codes["205"] = HttpCode(status.HTTP_205_RESET_CONTENT, "HTTP_205_RESET_CONTENT")
default_http_codes["206"] = HttpCode(status.HTTP_206_PARTIAL_CONTENT, "HTTP_206_PARTIAL_CONTENT")
default_http_codes["207"] = HttpCode(status.HTTP_207_MULTI_STATUS, "HTTP_207_MULTI_STATUS")
default_http_codes["208"] = HttpCode(status.HTTP_208_ALREADY_REPORTED, "HTTP_208_ALREADY_REPORTED")
default_http_codes["226"] = HttpCode(status.HTTP_226_IM_USED, "HTTP_226_IM_USED")
default_http_codes["300"] = HttpCode(status.HTTP_300_MULTIPLE_CHOICES, "HTTP_300_MULTIPLE_CHOICES")
default_http_codes["301"] = HttpCode(status.HTTP_301_MOVED_PERMANENTLY, "HTTP_301_MOVED_PERMANENTLY")
default_http_codes["302"] = HttpCode(status.HTTP_302_FOUND, "HTTP_302_FOUND")
default_http_codes["303"] = HttpCode(status.HTTP_303_SEE_OTHER, "HTTP_303_SEE_OTHER")
default_http_codes["304"] = HttpCode(status.HTTP_304_NOT_MODIFIED, "HTTP_304_NOT_MODIFIED")
default_http_codes["305"] = HttpCode(status.HTTP_305_USE_PROXY, "HTTP_305_USE_PROXY")
default_http_codes["306"] = HttpCode(status.HTTP_306_RESERVED, "HTTP_306_RESERVED")
default_http_codes["307"] = HttpCode(status.HTTP_307_TEMPORARY_REDIRECT, "HTTP_307_TEMPORARY_REDIRECT")
default_http_codes["308"] = HttpCode(status.HTTP_308_PERMANENT_REDIRECT, "HTTP_308_PERMANENT_REDIRECT")
default_http_codes["400"] = HttpCode(status.HTTP_400_BAD_REQUEST, "HTTP_400_BAD_REQUEST")
default_http_codes["401"] = HttpCode(status.HTTP_401_UNAUTHORIZED, "HTTP_401_UNAUTHORIZED")
default_http_codes["402"] = HttpCode(status.HTTP_402_PAYMENT_REQUIRED, "HTTP_402_PAYMENT_REQUIRED")
default_http_codes["403"] = HttpCode(status.HTTP_403_FORBIDDEN, "HTTP_403_FORBIDDEN")
default_http_codes["404"] = HttpCode(status.HTTP_404_NOT_FOUND, "HTTP_404_NOT_FOUND")
default_http_codes["405"] = HttpCode(status.HTTP_405_METHOD_NOT_ALLOWED, "HTTP_405_METHOD_NOT_ALLOWED")
default_http_codes["406"] = HttpCode(status.HTTP_406_NOT_ACCEPTABLE, "HTTP_406_NOT_ACCEPTABLE")
default_http_codes["407"] = HttpCode(
    status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED, "HTTP_407_PROXY_AUTHENTICATION_REQUIRED"
)
default_http_codes["408"] = HttpCode(status.HTTP_408_REQUEST_TIMEOUT, "HTTP_408_REQUEST_TIMEOUT")
default_http_codes["409"] = HttpCode(status.HTTP_409_CONFLICT, "HTTP_409_CONFLICT")
default_http_codes["410"] = HttpCode(status.HTTP_410_GONE, "HTTP_410_GONE")
default_http_codes["411"] = HttpCode(status.HTTP_411_LENGTH_REQUIRED, "HTTP_411_LENGTH_REQUIRED")
default_http_codes["412"] = HttpCode(status.HTTP_412_PRECONDITION_FAILED, "HTTP_412_PRECONDITION_FAILED")
default_http_codes["413"] = HttpCode(
    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "HTTP_413_REQUEST_ENTITY_TOO_LARGE"
)
default_http_codes["414"] = HttpCode(
    status.HTTP_414_REQUEST_URI_TOO_LONG, "HTTP_414_REQUEST_URI_TOO_LONG"
)
default_http_codes["415"] = HttpCode(
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "HTTP_415_UNSUPPORTED_MEDIA_TYPE"
)
default_http_codes["416"] = HttpCode(
    status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, "HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE"
)
default_http_codes["417"] = HttpCode(status.HTTP_417_EXPECTATION_FAILED, "HTTP_417_EXPECTATION_FAILED")
default_http_codes["418"] = HttpCode(status.HTTP_418_IM_A_TEAPOT, "HTTP_418_IM_A_TEAPOT")
default_http_codes["422"] = HttpCode(
    status.HTTP_422_UNPROCESSABLE_ENTITY, "HTTP_422_UNPROCESSABLE_ENTITY"
)
default_http_codes["423"] = HttpCode(status.HTTP_423_LOCKED, "HTTP_423_LOCKED")
default_http_codes["424"] = HttpCode(status.HTTP_424_FAILED_DEPENDENCY, "HTTP_424_FAILED_DEPENDENCY")
default_http_codes["426"] = HttpCode(status.HTTP_426_UPGRADE_REQUIRED, "HTTP_426_UPGRADE_REQUIRED")
default_http_codes["428"] = HttpCode(
    status.HTTP_428_PRECONDITION_REQUIRED, "HTTP_428_PRECONDITION_REQUIRED"
)
default_http_codes["429"] = HttpCode(status.HTTP_429_TOO_MANY_REQUESTS, "HTTP_429_TOO_MANY_REQUESTS")
default_http_codes["431"] = HttpCode(
    status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE, "HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE"
)
default_http_codes["451"] = HttpCode(
    status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS, "HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS"
)
default_http_codes["500"] = HttpCode(
    status.HTTP_500_INTERNAL_SERVER_ERROR, "HTTP_500_INTERNAL_SERVER_ERROR"
)
default_http_codes["501"] = HttpCode(status.HTTP_501_NOT_IMPLEMENTED, "HTTP_501_NOT_IMPLEMENTED")
default_http_codes["502"] = HttpCode(status.HTTP_502_BAD_GATEWAY, "HTTP_502_BAD_GATEWAY")
default_http_codes["503"] = HttpCode(status.HTTP_503_SERVICE_UNAVAILABLE, "HTTP_503_SERVICE_UNAVAILABLE")
default_http_codes["504"] = HttpCode(status.HTTP_504_GATEWAY_TIMEOUT, "HTTP_504_GATEWAY_TIMEOUT")
default_http_codes["505"] = HttpCode(
    status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED, "HTTP_505_HTTP_VERSION_NOT_SUPPORTED"
)
default_http_codes["506"] = HttpCode(
    status.HTTP_506_VARIANT_ALSO_NEGOTIATES, "HTTP_506_VARIANT_ALSO_NEGOTIATES"
)
default_http_codes["507"] = HttpCode(
    status.HTTP_507_INSUFFICIENT_STORAGE, "HTTP_507_INSUFFICIENT_STORAGE"
)
default_http_codes["508"] = HttpCode(status.HTTP_508_LOOP_DETECTED, "HTTP_508_LOOP_DETECTED")
default_http_codes["509"] = HttpCode(
    status.HTTP_509_BANDWIDTH_LIMIT_EXCEEDED, "HTTP_509_BANDWIDTH_LIMIT_EXCEEDED"
)
default_http_codes["510"] = HttpCode(status.HTTP_510_NOT_EXTENDED, "HTTP_510_NOT_EXTENDED")
default_http_codes["511"] = HttpCode(
    status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED, "HTTP_511_NETWORK_AUTHENTICATION_REQUIRED"
)
