from rest_framework import status
from rest_framework.response import Response


class ApiResponse:

    @staticmethod
    def success(
        message="Success",
        data=None,
        status_code=status.HTTP_200_OK
    ):
        return Response(
            {
                "success": True,
                "message": message,
                "data": data
            },
            status=status_code
        )

    @staticmethod
    def error(
        message="Something went wrong",
        errors=None,
        status_code=status.HTTP_400_BAD_REQUEST
    ):
        return Response(
            {
                "success": False,
                "message": message,
                "errors": errors
            },
            status=status_code
        )
