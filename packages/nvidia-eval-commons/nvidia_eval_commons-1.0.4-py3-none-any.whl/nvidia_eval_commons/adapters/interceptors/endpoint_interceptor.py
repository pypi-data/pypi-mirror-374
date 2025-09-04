# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Endpoint interceptor that makes actual requests to the upstream API."""

from typing import final

import requests

from nvidia_eval_commons.adapters.decorators import register_for_adapter
from nvidia_eval_commons.adapters.types import (
    AdapterGlobalContext,
    AdapterRequest,
    AdapterResponse,
    RequestToResponseInterceptor,
)
from nvidia_eval_commons.logging import BaseLoggingParams, get_logger


@register_for_adapter(
    name="endpoint",
    description="Makes the actual request to the upstream API",
)
@final
class EndpointInterceptor(RequestToResponseInterceptor):
    """Makes the actual request to the upstream API."""

    class Params(BaseLoggingParams):
        """Configuration parameters for endpoint interceptor."""

        pass

    def __init__(self, params: Params):
        """
        Initialize the endpoint interceptor.

        Args:
            params: Configuration parameters
        """
        # Get logger for this interceptor with interceptor context
        self.logger = get_logger(self.__class__.__name__)

        self.logger.info("Endpoint interceptor initialized")

    def intercept_request(
        self, ar: AdapterRequest, context: AdapterGlobalContext
    ) -> AdapterResponse:
        """Make the actual request to the upstream API.

        Args:
            ar: The adapter request
            context: Global context containing server-level configuration

        Returns:
            AdapterResponse with the response from the upstream API
        """
        self.logger.debug(
            "Making request to upstream API",
            method=ar.r.method,
            url=context.url,
            headers_count=len(ar.r.headers),
            has_json=ar.r.json is not None,
        )

        # This is a final interceptor, we'll need the flask_request and api
        resp = AdapterResponse(
            r=requests.request(
                method=ar.r.method,
                url=context.url,
                headers={k: v for k, v in ar.r.headers if k.lower() != "host"},
                json=ar.r.json,
                cookies=ar.r.cookies,
                allow_redirects=False,
            ),
            rctx=ar.rctx,
        )

        self.logger.debug(
            "Upstream API request completed",
            status_code=resp.r.status_code,
            reason=resp.r.reason,
            response_headers_count=len(resp.r.headers),
            response_content_length=len(resp.r.content) if resp.r.content else 0,
        )

        return resp
