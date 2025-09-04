#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# ------------------------------------------------------------------------------
#  Copyright  2020. NAVER Corp.                                                -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#   http://www.apache.org/licenses/LICENSE-2.0        _pinpointPy                         -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------

# Created by eeliu at 11/10/20
from pinpointPy import Defines, pinpoint, get_logger
import os


def generateNextSid():
    return pinpoint.gen_sid()


def generatePinpointHeader(host, headers, traceId=-1):
    headers[Defines.PP_HEADER_PINPOINT_SAMPLED] = Defines.PP_SAMPLED
    headers[Defines.PP_HEADER_PINPOINT_PAPPTYPE] = pinpoint.get_context(
        Defines.PP_SERVER_TYPE, traceId)
    headers[Defines.PP_HEADER_PINPOINT_PAPPNAME] = pinpoint.get_context(
        Defines.PP_APP_NAME, traceId)
    headers['Pinpoint-Flags'] = "0"
    headers[Defines.PP_HEADER_PINPOINT_HOST] = host
    headers[Defines.PP_HEADER_PINPOINT_TRACEID] = pinpoint.get_context(
        Defines.PP_TRANSCATION_ID, traceId)
    headers[Defines.PP_HEADER_PINPOINT_PSPANID] = pinpoint.get_context(
        Defines.PP_SPAN_ID, traceId)
    nextSeqId = pinpoint.gen_sid()
    pinpoint.add_context(Defines.PP_NEXT_SPAN_ID, nextSeqId, traceId)
    headers[Defines.PP_HEADER_PINPOINT_SPANID] = nextSeqId
    
    # Add canary tag propagation
    canary_tag = pinpoint.get_context('canary_tag', traceId)
    if canary_tag:
        headers[Defines.PP_HEADER_CANARY_TAG] = canary_tag
    
    # Debug printing for outgoing request headers
    debug_enabled = os.environ.get('PINPOINT_DEBUG_HEADERS', 'false').lower() == 'true'
    if debug_enabled:
        print(f"[PINPOINT-OUTBOUND] 📤 Outgoing Request Headers:")
        print(f"  🏠 Host: {host}")
        print(f"  🔗 TraceID: {headers.get(Defines.PP_HEADER_PINPOINT_TRACEID)}")
        print(f"  🎯 SpanID: {headers.get(Defines.PP_HEADER_PINPOINT_SPANID)}")
        print(f"  ⬆️ Parent SpanID: {headers.get(Defines.PP_HEADER_PINPOINT_PSPANID)}")
        print(f"  🏷️ CanaryTag: {canary_tag if canary_tag else 'None'}")
        print(f"  📱 App: {headers.get(Defines.PP_HEADER_PINPOINT_PAPPNAME)}")
        print(f"  🔄 TraceContext: {traceId}")
        print(f"  📋 All Headers: {dict(headers)}")
        print("=" * 60)
    
    get_logger().debug(f'append PinpointHeader header:{headers}')


def startPinpointByEnviron(environ, trace_id: int):
    pinpoint.add_trace_header(
        Defines.PP_APP_NAME, pinpoint.app_name(), trace_id)
    pinpoint.add_context(Defines.PP_APP_NAME, pinpoint.app_name(), trace_id)
    pinpoint.add_trace_header(Defines.PP_APP_ID, pinpoint.app_id(), trace_id)
    
    # Debug printing for incoming WSGI environment
    debug_enabled = os.environ.get('PINPOINT_DEBUG_HEADERS', 'false').lower() == 'true'
    path, remote_addr, host = environ['PATH_INFO'], environ['REMOTE_ADDR'], environ['HTTP_HOST']
    
    if debug_enabled:
        print(f"[PINPOINT-WSGI-INBOUND] 📨 WSGI Environment Headers:")
        print(f"  🌐 Path: {path}")
        print(f"  🏠 Remote: {remote_addr} -> Host: {host}")
        
        # Print all Pinpoint related environ variables
        pinpoint_environ = {}
        for env_name in [
            Defines.PP_HTTP_PINPOINT_TRACEID, Defines.PP_HEADER_PINPOINT_TRACEID,
            Defines.PP_HTTP_PINPOINT_SPANID, Defines.PP_HEADER_PINPOINT_SPANID,
            Defines.PP_HTTP_PINPOINT_PSPANID, Defines.PP_HEADER_PINPOINT_PSPANID,
            Defines.PP_HTTP_PINPOINT_PAPPNAME, Defines.PP_HEADER_PINPOINT_PAPPNAME,
            Defines.PP_HTTP_PINPOINT_PAPPTYPE, Defines.PP_HEADER_PINPOINT_PAPPTYPE,
            Defines.PP_HTTP_PINPOINT_HOST, Defines.PP_HEADER_PINPOINT_HOST,
            Defines.PP_HTTP_CANARY_TAG, Defines.PP_HEADER_CANARY_TAG,
            Defines.PP_HTTP_PINPOINT_SAMPLED, Defines.PP_HEADER_PINPOINT_SAMPLED
        ]:
            if env_name in environ:
                pinpoint_environ[env_name] = environ[env_name]
        
        if pinpoint_environ:
            print(f"  📋 Pinpoint Environment Found:")
            for name, value in pinpoint_environ.items():
                icon = "🏷️" if "CANARY" in name else "🔍"
                print(f"    {icon} {name}: {value}")
        else:
            print(f"  ❌ No Pinpoint environ found - starting new trace")
        print()
    
    ###############################################################
    pinpoint.add_trace_header(
        Defines.PP_INTERCEPTOR_NAME, 'WSGI handle', trace_id)

    pinpoint.add_trace_header(Defines.PP_REQ_URI, path, trace_id)
    pinpoint.add_trace_header(Defines.PP_REQ_CLIENT, remote_addr, trace_id)
    pinpoint.add_trace_header(Defines.PP_REQ_SERVER, host, trace_id)
    pinpoint.add_trace_header(Defines.PP_SERVER_TYPE, Defines.PYTHON, trace_id)
    pinpoint.add_context(Defines.PP_SERVER_TYPE, Defines.PYTHON, trace_id)
    # nginx add http
    if Defines.PP_HTTP_PINPOINT_PSPANID in environ:
        pinpoint.add_trace_header(
            Defines.PP_PARENT_SPAN_ID, environ[Defines.PP_HTTP_PINPOINT_PSPANID], trace_id)

    if Defines.PP_HTTP_PINPOINT_SPANID in environ:
        sid = environ[Defines.PP_HTTP_PINPOINT_SPANID]
    elif Defines.PP_HEADER_PINPOINT_SPANID in environ:
        sid = environ[Defines.PP_HEADER_PINPOINT_SPANID]
    else:
        sid = pinpoint.gen_sid()

    if Defines.PP_HTTP_PINPOINT_TRACEID in environ:
        tid = environ[Defines.PP_HTTP_PINPOINT_TRACEID]
    elif Defines.PP_HEADER_PINPOINT_TRACEID in environ:
        tid = environ[Defines.PP_HEADER_PINPOINT_TRACEID]
    else:
        tid = pinpoint.gen_tid()

    if Defines.PP_HTTP_PINPOINT_PAPPNAME in environ:
        pname = environ[Defines.PP_HTTP_PINPOINT_PAPPNAME]
        pinpoint.add_context(Defines.PP_PARENT_NAME, pname, trace_id)
        pinpoint.add_trace_header(Defines.PP_PARENT_NAME, pname, trace_id)

    if Defines.PP_HTTP_PINPOINT_PAPPTYPE in environ:
        ptype = environ[Defines.PP_HTTP_PINPOINT_PAPPTYPE]
        pinpoint.add_context(Defines.PP_PARENT_TYPE, ptype, trace_id)
        pinpoint.add_trace_header(Defines.PP_PARENT_TYPE, ptype, trace_id)

    if Defines.PP_HTTP_PINPOINT_HOST in environ:
        Ah = environ[Defines.PP_HTTP_PINPOINT_HOST]
        pinpoint.add_context(Defines.PP_PARENT_HOST, Ah, trace_id)
        pinpoint.add_trace_header(Defines.PP_PARENT_HOST, Ah, trace_id)

    # Handle canary tag - HTTP format
    if Defines.PP_HTTP_CANARY_TAG in environ:
        canary_tag = environ[Defines.PP_HTTP_CANARY_TAG]
        pinpoint.add_context('canary_tag', canary_tag, trace_id)
        pinpoint.add_trace_header('canary_tag', canary_tag, trace_id)

    # Not nginx, no http
    if Defines.PP_HEADER_PINPOINT_PSPANID in environ:
        pinpoint.add_trace_header(
            Defines.PP_PARENT_SPAN_ID, environ[Defines.PP_HEADER_PINPOINT_PSPANID], trace_id)

    if Defines.PP_HEADER_PINPOINT_PAPPNAME in environ:
        pname = environ[Defines.PP_HEADER_PINPOINT_PAPPNAME]
        pinpoint.add_context(Defines.PP_PARENT_NAME, pname, trace_id)
        pinpoint.add_trace_header(Defines.PP_PARENT_NAME, pname, trace_id)

    if Defines.PP_HEADER_PINPOINT_PAPPTYPE in environ:
        ptype = environ[Defines.PP_HEADER_PINPOINT_PAPPTYPE]
        pinpoint.add_context(Defines.PP_PARENT_TYPE, ptype, trace_id)
        pinpoint.add_trace_header(Defines.PP_PARENT_TYPE, ptype, trace_id)

    if Defines.PP_HEADER_PINPOINT_HOST in environ:
        Ah = environ[Defines.PP_HEADER_PINPOINT_HOST]
        pinpoint.add_context(Defines.PP_PARENT_HOST, Ah, trace_id)
        pinpoint.add_trace_header(Defines.PP_PARENT_HOST, Ah, trace_id)

    # Handle canary tag - direct header format
    if Defines.PP_HEADER_CANARY_TAG in environ:
        canary_tag = environ[Defines.PP_HEADER_CANARY_TAG]
        pinpoint.add_context('canary_tag', canary_tag, trace_id)
        pinpoint.add_trace_header('canary_tag', canary_tag, trace_id)

    if Defines.PP_NGINX_PROXY in environ:
        pinpoint.add_trace_header(
            Defines.PP_NGINX_PROXY, environ[Defines.PP_NGINX_PROXY], trace_id)

    if Defines.PP_APACHE_PROXY in environ:
        pinpoint.add_trace_header(
            Defines.PP_APACHE_PROXY, environ[Defines.PP_APACHE_PROXY], trace_id)

    pinpoint.add_context(Defines.PP_HEADER_PINPOINT_SAMPLED, "s1", trace_id)
    if (Defines.PP_HTTP_PINPOINT_SAMPLED in environ and environ[
            Defines.PP_HTTP_PINPOINT_SAMPLED] == Defines.PP_NOT_SAMPLED) or pinpoint.check_trace_limit():
        pinpoint.drop_trace(trace_id)
        pinpoint.add_context(
            Defines.PP_HEADER_PINPOINT_SAMPLED, "s0", trace_id)

    pinpoint.add_trace_header(Defines.PP_TRANSCATION_ID, tid, trace_id)
    pinpoint.add_context(Defines.PP_TRANSCATION_ID, tid, trace_id)

    pinpoint.add_trace_header(Defines.PP_SPAN_ID, sid, trace_id)
    pinpoint.add_context(Defines.PP_SPAN_ID, sid, trace_id)
    
    # Debug printing for generated trace info
    if debug_enabled:
        canary_tag = pinpoint.get_context('canary_tag', trace_id)
        print(f"[PINPOINT-WSGI-INBOUND] 🆔 Generated Trace Info:")
        print(f"  🔗 TraceID: {tid}")
        print(f"  🎯 SpanID: {sid}")
        print(f"  🏷️ CanaryTag: {canary_tag if canary_tag else 'None'}")
        print(f"  📱 AppName: {pinpoint.app_name()}")
        print(f"  🔄 TraceContext: {trace_id}")
        print("=" * 60)


def endPinpointByEnviron(ret, trace_id: int):
    # for future use
    pass
