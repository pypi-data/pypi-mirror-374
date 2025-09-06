from functools import wraps
from starlette.datastructures import Headers
from Osdental.Models.Response import Response
from Osdental.Models.FakeInfo import FakeInfo
from Osdental.Shared.Enums.GrahpqlOperation import GraphqlOperation
from Osdental.Shared.Enums.Constant import Constant

# Client
def with_grpc_metadata(func):
    """
    Decorator to transform data to bytes and build metadata for gRPC.
    """
    @wraps(func)
    async def wrapper(self, request, headers: Headers, *args, **kwargs):
        # Build metadata from headers
        user_token = headers.get('authorization', '')
        metadata = [
            ('authorization', user_token),
            ('dynamicclientid', headers.get('dynamicClientId') or None),
        ]

        # Add extra metadata if it comes in kwargs
        extra_metadata = kwargs.pop('extra_metadata', None)
        if extra_metadata:
            if isinstance(extra_metadata, dict):
                metadata.extend(extra_metadata.items())
            else:
                metadata.extend(extra_metadata)

        # Call the actual gRPC method passing request and metadata
        res = await func(self, request, metadata, *args, **kwargs)

        # Return a uniform Response
        return Response(status=res.status, message=res.message, data=res.data)

    return wrapper

# Server
def with_grpc_info(operation_name: GraphqlOperation = GraphqlOperation.QUERY):
    """
    Decorator to wrap gRPC methods and build the FakeInfo.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(servicer, request, context):
            metadata_dict = dict(context.invocation_metadata())
            user_token = metadata_dict.get('authorization')
            token_value = user_token.split(' ')[1] if user_token.startswith('Bearer ') else user_token
            context_dict = {
                'user_token': token_value,
                'headers': metadata_dict,
            }
            info = FakeInfo(context_dict, operation_name)

            return await func(servicer, request.data, info)
        return wrapper
    return decorator