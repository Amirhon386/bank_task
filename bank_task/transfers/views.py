from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from jsonrpcserver import dispatch
import transfers.rpc  # noqa: F401


@csrf_exempt
@require_POST
def rpc_endpoint(request):
    response = dispatch(request.body.decode())
    return JsonResponse(response, safe=False)