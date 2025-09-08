import traceback
from io import BytesIO
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.requests import HTTPConnection
from typing import Tuple
from uuid import UUID


def extract_operation_id(request: Request) -> UUID:
    operation_id = request.state.operation_id
    if not isinstance(operation_id, UUID):
        raise TypeError(f"Invalid 'operation_id' type: '{operation_id}'")
    return operation_id


def extract_client_ip(conn: HTTPConnection) -> str:
    """Extract client IP with more robust handling of proxies"""
    # * Check for x-forwarded-for header (common when behind proxy/load balancer)
    x_forwarded_for = conn.headers.get("x-forwarded-for")
    if x_forwarded_for:
        # * The client's IP is the first one in the list
        ips = [ip.strip() for ip in x_forwarded_for.split(",")]
        return ips[0]

    # * Check for x-real-ip header (used by some proxies)
    x_real_ip = conn.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip

    # * Fall back to direct client connection
    return conn.client.host if conn.client else "unknown"


class ResponseBodyExtractor:
    @staticmethod
    async def async_extract(response: Response) -> Tuple[bytes, Response]:
        """
        Extract body from a (possibly streaming) Response.
        Always returns a tuple of (raw_bytes, new_response).
        """
        response_body: bytes = b""

        if hasattr(response, "body_iterator"):  # StreamingResponse
            body_buffer = BytesIO()

            try:
                async for chunk in response.body_iterator:  # type: ignore
                    if isinstance(chunk, str):
                        body_buffer.write(chunk.encode("utf-8"))
                    elif isinstance(chunk, (bytes, memoryview)):
                        body_buffer.write(bytes(chunk))
                    else:
                        body_buffer.write(str(chunk).encode("utf-8"))

                response_body = body_buffer.getvalue()

                new_response = StreamingResponse(
                    iter([response_body]),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                    background=response.background,  # ✅ preserve background tasks
                )

            except Exception as e:
                print(f"Error consuming body iterator: {e}")
                print(traceback.format_exc())
                new_response = Response(
                    content=b"",
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

        else:  # Normal Response
            try:
                response_body = getattr(response, "body", b"") or b""
            except Exception as e:
                print(f"Failed retrieving response body: {e}")
                print(traceback.format_exc())
                response_body = b""

            # No reconstruction needed
            new_response = response

        return response_body, new_response

    @staticmethod
    def sync_extract(response: Response) -> Tuple[bytes, Response]:
        """
        Extract body for non-streaming responses in sync code.
        """
        if hasattr(response, "body_iterator"):
            raise ValueError(
                "Cannot process StreamingResponse synchronously. "
                "Use 'await async_extract()' instead."
            )

        try:
            response_body = getattr(response, "body", b"") or b""
        except Exception as e:
            print(f"Failed retrieving response body: {e}")
            print(traceback.format_exc())
            response_body = b""

        return response_body, response
