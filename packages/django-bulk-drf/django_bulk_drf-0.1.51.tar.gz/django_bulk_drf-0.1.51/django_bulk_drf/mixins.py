"""
Operation mixins for DRF ViewSets.

Provides a unified mixin that enhances standard ViewSet endpoints with efficient
synchronous bulk operations using query parameters.
"""

import sys

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

# Optional OpenAPI schema support
try:
    from drf_spectacular.types import OpenApiTypes
    from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema

    SPECTACULAR_AVAILABLE = True
except ImportError:
    SPECTACULAR_AVAILABLE = False

    # Create dummy decorator if drf-spectacular is not available
    def extend_schema(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    # Create dummy classes for OpenAPI types
    class OpenApiParameter:
        QUERY = "query"

        def __init__(self, name, type, location, description, examples=None):
            pass

    class OpenApiExample:
        def __init__(self, name, value, description=None):
            pass

    class OpenApiTypes:
        STR = "string"
        INT = "integer"


from django_bulk_drf.processing import (
    async_create_task,
    async_get_task,
    async_upsert_task,
)


class BulkOperationsMixin:
    """
    Unified mixin providing synchronous bulk operations with intelligent routing.

    Simple routing strategy:
    - Single instances (dict): Direct database operations (no Celery overhead)
    - Arrays (list): Celery workers for heavy lifting (triggers fire in workers)

    Enhanced endpoints:
    - GET    /api/model/?ids=1                    # Direct single get
    - GET    /api/model/?ids=1,2,3               # Celery multi-get
    - POST   /api/model/?unique_fields=...       # Smart upsert routing
    - PATCH  /api/model/?unique_fields=...      # Smart upsert routing
    - PUT    /api/model/?unique_fields=...      # Smart upsert routing

    Relies on DRF's built-in payload size limits for request validation.
    Maintains synchronous API behavior while optimizing performance and resource usage.
    Database triggers fire in the appropriate execution context based on payload type.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        """Handle array data for serializers with upsert context."""
        try:
            data = kwargs.get("data", None)
            if data is not None and isinstance(data, list):
                kwargs["many"] = True

            serializer = super().get_serializer(*args, **kwargs)

            # Note: Upsert validation bypass is now handled directly in _handle_array_upsert_direct()
            # for individual serializers to ensure proper handling of uniqueness constraints

            return serializer
        except Exception:
            raise

    # =============================================================================
    # Enhanced Standard ViewSet Methods (Sync Operations)
    # =============================================================================

    def list(self, request, *args, **kwargs):
        """
        Enhanced list endpoint that supports multi-get via ?ids= parameter.

        - GET /api/model/                    # Standard list
        - GET /api/model/?ids=1,2,3          # Sync multi-get (small datasets)
        """
        ids_param = request.query_params.get("ids")
        if ids_param:
            return self._sync_multi_get(request, ids_param)

        # Standard list behavior
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Enhanced create endpoint that supports bulk operations.

        - POST /api/model/                                    # Standard single create (dict data)
        - POST /api/model/                                    # Bulk create (array data, uses Celery)
        - POST /api/model/?unique_fields=field1,field2       # Bulk upsert (array data, uses Celery)
        """
        unique_fields_param = request.query_params.get("unique_fields")
        print(
            f"BulkOperationsMixin.create() - unique_fields_param: {unique_fields_param}, data_type: {type(request.data)}, is_list: {isinstance(request.data, list)}",
            file=sys.stderr,
        )

        if isinstance(request.data, list):
            # Array data - route based on unique_fields presence
            if unique_fields_param:
                print(
                    f"BulkOperationsMixin.create() - Routing to bulk upsert with unique_fields: {unique_fields_param}",
                    file=sys.stderr,
                )
                return self._sync_upsert(request, unique_fields_param)
            else:
                print(
                    "BulkOperationsMixin.create() - Routing to bulk create (no unique_fields)",
                    file=sys.stderr,
                )
                return self._handle_bulk_create(request)

        print(
            "BulkOperationsMixin.create() - Using standard single create behavior",
            file=sys.stderr,
        )
        # Standard single create behavior
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Enhanced update endpoint that supports sync upsert via query params.

        - PUT /api/model/{id}/                               # Standard single update
        - PUT /api/model/?unique_fields=field1,field2       # Sync upsert (array data)
        """
        unique_fields_param = request.query_params.get("unique_fields")
        if unique_fields_param and isinstance(request.data, list):
            return self._sync_upsert(request, unique_fields_param)

        # Standard single update behavior
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Enhanced partial update endpoint that supports sync upsert via query params.

        - PATCH /api/model/{id}/                             # Standard single partial update
        - PATCH /api/model/?unique_fields=field1,field2     # Sync upsert (array data)
        """
        unique_fields_param = request.query_params.get("unique_fields")
        if unique_fields_param and isinstance(request.data, list):
            return self._sync_upsert(request, unique_fields_param)

        # Standard single partial update behavior
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="unique_fields",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Comma-separated unique field names for upsert mode",
                examples=[OpenApiExample("Fields", value="account_number,email")],
            ),
            OpenApiParameter(
                name="update_fields",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Comma-separated field names to update (optional, auto-inferred if not provided)",
                examples=[OpenApiExample("Fields", value="business,status")],
            ),
            OpenApiParameter(
                name="max_items",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Maximum items for sync processing (default: 50)",
                examples=[OpenApiExample("Max Items", value=50)],
            ),
            OpenApiParameter(
                name="partial_success",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Allow partial success (default: false). Set to 'true' to allow some records to succeed while others fail.",
                examples=[OpenApiExample("Partial Success", value="true")],
            ),
            OpenApiParameter(
                name="include_results",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="If 'false', skips serializing response results to improve performance (default: true)",
                examples=[OpenApiExample("Include Results", value="false")],
            ),
            OpenApiParameter(
                name="db_batch_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Optional database batch_size for bulk_create (default: ORM default)",
                examples=[OpenApiExample("DB Batch Size", value=2000)],
            ),
        ],
        request={
            "application/json": {
                "type": "array",
                "description": "Array of objects to upsert",
            }
        },
        responses={
            200: {
                "description": "Upsert completed successfully - returns updated/created objects",
                "oneOf": [
                    {"type": "object", "description": "Single object response"},
                    {"type": "array", "description": "Multiple objects response"},
                ],
            },
            207: {
                "description": "Partial success - some records succeeded, others failed",
                "type": "object",
                "properties": {
                    "success": {
                        "type": "array",
                        "description": "Successfully processed records",
                    },
                    "errors": {
                        "type": "array",
                        "description": "Failed records with error details",
                    },
                    "summary": {"type": "object", "description": "Operation summary"},
                },
            },
            400: {"description": "Bad request - missing parameters or invalid data"},
        },
        description="Upsert multiple instances synchronously. Creates new records or updates existing ones based on unique fields. Defaults to all-or-nothing behavior unless partial_success=true.",
        summary="Sync upsert (PATCH)",
    )
    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH requests on list endpoint for sync upsert.

        DRF doesn't handle PATCH on list endpoints by default, so we add this method
        to support: PATCH /api/model/?unique_fields=field1,field2
        """
        unique_fields_param = request.query_params.get("unique_fields")
        preparsed_list = request.data

        if unique_fields_param and isinstance(preparsed_list, list):
            return self._sync_upsert(
                request, unique_fields_param, preparsed_data=preparsed_list
            )

        # If no unique_fields or not array data, this is invalid
        return Response(
            {
                "error": "PATCH on list endpoint requires 'unique_fields' parameter and array data"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="unique_fields",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Comma-separated unique field names for upsert mode",
                examples=[OpenApiExample("Fields", value="account_number,email")],
            ),
            OpenApiParameter(
                name="update_fields",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Comma-separated field names to update (optional, auto-inferred if not provided)",
                examples=[OpenApiExample("Fields", value="business,status")],
            ),
            OpenApiParameter(
                name="max_items",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Maximum items for sync processing (default: 50)",
                examples=[OpenApiExample("Max Items", value=50)],
            ),
            OpenApiParameter(
                name="partial_success",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Allow partial success (default: false). Set to 'true' to allow some records to succeed while others fail.",
                examples=[OpenApiExample("Partial Success", value="true")],
            ),
            OpenApiParameter(
                name="include_results",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="If 'false', skips serializing response results to improve performance (default: true)",
                examples=[OpenApiExample("Include Results", value="false")],
            ),
            OpenApiParameter(
                name="db_batch_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Optional database batch_size for bulk_create (default: ORM default)",
                examples=[OpenApiExample("DB Batch Size", value=2000)],
            ),
        ],
        request={
            "application/json": {
                "type": "array",
                "description": "Array of objects to upsert",
            }
        },
        responses={
            200: {
                "description": "Upsert completed successfully - returns updated/created objects",
                "oneOf": [
                    {"type": "object", "description": "Single object response"},
                    {"type": "array", "description": "Multiple objects response"},
                ],
            },
            207: {
                "description": "Partial success - some records succeeded, others failed",
                "type": "object",
                "properties": {
                    "success": {
                        "type": "array",
                        "description": "Successfully processed records",
                    },
                    "errors": {
                        "type": "array",
                        "description": "Failed records with error details",
                    },
                    "summary": {"type": "object", "description": "Operation summary"},
                },
            },
            400: {"description": "Bad request - missing parameters or invalid data"},
        },
        description="Upsert multiple instances synchronously. Creates new records or updates existing ones based on unique fields. Defaults to all-or-nothing behavior unless partial_success=true.",
        summary="Sync upsert (PUT)",
    )
    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests on list endpoint for sync upsert.

        DRF doesn't handle PUT on list endpoints by default, so we add this method
        to support: PUT /api/model/?unique_fields=field1,field2
        """
        unique_fields_param = request.query_params.get("unique_fields")
        if unique_fields_param and isinstance(request.data, list):
            return self._sync_upsert(request, unique_fields_param)

        # If no unique_fields or not array data, this is invalid
        return Response(
            {
                "error": "PUT on list endpoint requires 'unique_fields' parameter and array data"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # =============================================================================
    # Sync Operation Implementations
    # =============================================================================

    def _sync_multi_get(self, request, ids_param):
        """Handle sync multi-get - direct for single items, Celery for arrays."""
        try:
            ids_list = [int(id_str.strip()) for id_str in ids_param.split(",")]
        except ValueError:
            return Response(
                {"error": "Invalid ID format. Use comma-separated integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Simple routing: single item direct, arrays via Celery
        if len(ids_list) == 1:
            # Single item - direct database call
            return self._handle_single_get(ids_list[0])
        else:
            # Multiple items - use Celery workers
            return self._handle_array_get(request, ids_list)

    def _handle_single_get(self, item_id):
        """Handle single item retrieval directly without Celery overhead."""
        try:
            queryset = self.get_queryset().filter(id=item_id)
            instance = queryset.first()

            if instance:
                serializer = self.get_serializer(instance)
                return Response(
                    {
                        "count": 1,
                        "results": [serializer.data],
                        "is_sync": True,
                        "operation_type": "direct_get",
                    }
                )
            else:
                return Response(
                    {"error": f"Item with id {item_id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return Response(
                {"error": f"Direct get failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_array_get(self, request, ids_list):
        """Handle array retrieval using Celery workers."""
        # Use Celery worker for multiple items
        model_class = self.get_queryset().model
        model_class_path = f"{model_class.__module__}.{model_class.__name__}"
        serializer_class = self.get_serializer_class()
        serializer_class_path = (
            f"{serializer_class.__module__}.{serializer_class.__name__}"
        )

        query_data = {"ids": ids_list}
        user_id = request.user.id if request.user.is_authenticated else None

        # Start Celery task with optimized settings
        task = async_get_task.delay(
            model_class_path, serializer_class_path, query_data, user_id
        )

        # Wait for task completion with fixed timeout
        try:
            # Wait for the task to complete (synchronous behavior)
            task_result = task.get(timeout=180)  # 3 minute timeout for get operations

            if task_result.get("success", False):
                return Response(
                    {
                        "count": task_result.get("count", 0),
                        "results": task_result.get("results", []),
                        "is_sync": True,
                        "task_id": task.id,
                        "operation_type": "sync_get_via_worker",
                    }
                )
            else:
                return Response(
                    {"error": f"Worker task failed: {task_result.get('error')}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Exception as e:
            return Response(
                {"error": f"Task execution failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _sync_upsert(self, request, unique_fields_param, preparsed_data=None):
        """Handle sync upsert operations - direct for single items, Celery for arrays."""
        print(
            f"BulkOperationsMixin._sync_upsert() - Called with unique_fields_param: {unique_fields_param}",
            file=sys.stderr,
        )

        # Parse parameters
        unique_fields = [f.strip() for f in unique_fields_param.split(",") if f.strip()]
        print(
            f"BulkOperationsMixin._sync_upsert() - Parsed unique_fields: {unique_fields}",
            file=sys.stderr,
        )

        update_fields_param = request.query_params.get("update_fields")
        update_fields = None
        if update_fields_param:
            update_fields = [
                f.strip() for f in update_fields_param.split(",") if f.strip()
            ]
        print(
            f"BulkOperationsMixin._sync_upsert() - Parsed update_fields: {update_fields}",
            file=sys.stderr,
        )

        # Use pre-parsed data from caller if available
        data_payload = preparsed_data if preparsed_data is not None else request.data
        print(
            f"BulkOperationsMixin._sync_upsert() - Data payload type: {type(data_payload)}, is_list: {isinstance(data_payload, list)}",
            file=sys.stderr,
        )

        if isinstance(data_payload, list):
            print(
                f"BulkOperationsMixin._sync_upsert() - Array with {len(data_payload)} items",
                file=sys.stderr,
            )

        # Simple routing: dict direct, list via Celery
        if isinstance(data_payload, dict):
            print(
                "BulkOperationsMixin._sync_upsert() - Routing to single upsert",
                file=sys.stderr,
            )
            # Single instance - direct database operations
            return self._handle_single_upsert(
                request, unique_fields, update_fields, data_payload
            )
        elif isinstance(data_payload, list):
            print(
                "BulkOperationsMixin._sync_upsert() - Routing to array upsert (Celery)",
                file=sys.stderr,
            )
            # Array - use Celery workers for heavy operations
            return self._handle_array_upsert(
                request, unique_fields, update_fields, data_payload
            )
        else:
            print(
                f"BulkOperationsMixin._sync_upsert() - Invalid data type: {type(data_payload)}",
                file=sys.stderr,
            )
            return Response(
                {"error": "Expected dict or array data for upsert operations."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _handle_single_upsert(self, request, unique_fields, update_fields, data_dict):
        """Handle single instance upsert directly without Celery overhead."""
        print(
            f"BulkOperationsMixin._handle_single_upsert() - Processing single item: {data_dict}",
            file=sys.stderr,
        )

        if not unique_fields:
            print(
                "BulkOperationsMixin._handle_single_upsert() - ERROR: No unique_fields provided",
                file=sys.stderr,
            )
            return Response(
                {"error": "unique_fields parameter is required for upsert operations"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Auto-infer update_fields if not provided
        if not update_fields:
            update_fields = self._infer_update_fields([data_dict], unique_fields)
            print(
                f"BulkOperationsMixin._handle_single_upsert() - Auto-inferred update_fields: {update_fields}",
                file=sys.stderr,
            )

        # Use direct database operations for single instance
        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model
        print(
            f"BulkOperationsMixin._handle_single_upsert() - Using model: {model_class.__name__}",
            file=sys.stderr,
        )

        try:
            # Try to find existing instance
            unique_filter = {}
            for field in unique_fields:
                if field in data_dict:
                    unique_filter[field] = data_dict[field]

            print(
                f"BulkOperationsMixin._handle_single_upsert() - Unique filter: {unique_filter}",
                file=sys.stderr,
            )

            existing_instance = None
            if unique_filter:
                existing_instance = model_class.objects.filter(**unique_filter).first()
                print(
                    f"BulkOperationsMixin._handle_single_upsert() - Existing instance found: {existing_instance is not None}",
                    file=sys.stderr,
                )

            if existing_instance:
                print(
                    f"BulkOperationsMixin._handle_single_upsert() - Updating existing instance ID: {existing_instance.id}",
                    file=sys.stderr,
                )
                # Update existing instance
                if update_fields:
                    update_data = {
                        k: v for k, v in data_dict.items() if k in update_fields
                    }
                else:
                    update_data = {
                        k: v for k, v in data_dict.items() if k not in unique_fields
                    }

                print(
                    f"BulkOperationsMixin._handle_single_upsert() - Update data: {update_data}",
                    file=sys.stderr,
                )

                for field, value in update_data.items():
                    setattr(existing_instance, field, value)
                existing_instance.save()

                serializer = serializer_class(existing_instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print(
                    "BulkOperationsMixin._handle_single_upsert() - Creating new instance",
                    file=sys.stderr,
                )
                # Create new instance
                serializer = serializer_class(data=data_dict)
                if serializer.is_valid():
                    instance = serializer.save()
                    print(
                        f"BulkOperationsMixin._handle_single_upsert() - Created instance ID: {instance.id}",
                        file=sys.stderr,
                    )
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    print(
                        f"BulkOperationsMixin._handle_single_upsert() - Validation failed: {serializer.errors}",
                        file=sys.stderr,
                    )
                    return Response(
                        {
                            "error": "Validation failed",
                            "errors": [
                                {
                                    "index": 0,
                                    "error": str(serializer.errors),
                                    "data": data_dict,
                                }
                            ],
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except Exception as e:
            print(
                f"BulkOperationsMixin._handle_single_upsert() - ERROR: {str(e)}",
                file=sys.stderr,
            )
            return Response(
                {"error": f"Direct upsert failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_bulk_create(self, request):
        """Handle bulk create operations using Celery workers."""
        data_list = request.data
        print(
            f"BulkOperationsMixin._handle_bulk_create() - Processing bulk create with {len(data_list)} items",
            file=sys.stderr,
        )

        # Use Celery worker for bulk create
        serializer_class = self.get_serializer_class()
        serializer_class_path = (
            f"{serializer_class.__module__}.{serializer_class.__name__}"
        )
        user_id = request.user.id if request.user.is_authenticated else None

        # Start Celery bulk create task
        print(
            "BulkOperationsMixin._handle_bulk_create() - Dispatching bulk create to Celery",
            file=sys.stderr,
        )
        task = async_create_task.delay(serializer_class_path, data_list, user_id)
        print(
            f"BulkOperationsMixin._handle_bulk_create() - Task dispatched with ID: {task.id}",
            file=sys.stderr,
        )

        # Wait for task completion
        try:
            print(
                "BulkOperationsMixin._handle_bulk_create() - Waiting for task completion (300s timeout)...",
                file=sys.stderr,
            )
            # Wait for the task to complete (synchronous behavior)
            task_result = task.get(
                timeout=300
            )  # 5 minute timeout for bulk create operations
            print(
                "BulkOperationsMixin._handle_bulk_create() - Task completed successfully",
                file=sys.stderr,
            )
            print(
                f"BulkOperationsMixin._handle_bulk_create() - Result: success_count={task_result.get('success_count', 0)}, error_count={task_result.get('error_count', 0)}",
                file=sys.stderr,
            )

            # Check for errors first
            errors = task_result.get("errors", [])
            if errors:
                print(
                    f"BulkOperationsMixin._handle_bulk_create() - Returning errors: {errors}",
                    file=sys.stderr,
                )
                return Response(
                    {
                        "errors": errors,
                        "error_count": task_result.get("error_count", 0),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Return successful result in standard DRF format
            serializer_class = self.get_serializer_class()
            model_class = serializer_class.Meta.model

            # Get the created instances
            created_ids = task_result.get("created_ids", [])
            if created_ids:
                created_instances = list(model_class.objects.filter(id__in=created_ids))
                serializer = serializer_class(created_instances, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # No instances were created successfully
                print(
                    "BulkOperationsMixin._handle_bulk_create() - No instances created and no errors",
                    file=sys.stderr,
                )
                return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            print(
                f"BulkOperationsMixin._handle_bulk_create() - ERROR: Task execution failed: {str(e)}",
                file=sys.stderr,
            )
            return Response(
                {"error": f"Bulk create task execution failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_array_upsert(self, request, unique_fields, update_fields, data_list):
        """Handle array upsert using Celery workers."""
        print(
            f"BulkOperationsMixin._handle_array_upsert() - Processing array with {len(data_list)} items",
            file=sys.stderr,
        )

        # TEMPORARY DEBUGGING: Bypass Celery for direct debugging
        # Set to True to debug validation issues without Celery overhead
        DEBUG_BYPASS_CELERY = True  # Set to False to use Celery again

        if DEBUG_BYPASS_CELERY:
            print(
                "BulkOperationsMixin._handle_array_upsert() - DEBUG MODE: Bypassing Celery for direct execution",
                file=sys.stderr,
            )
            return self._handle_array_upsert_direct(
                request, unique_fields, update_fields, data_list
            )

        if not unique_fields:
            print(
                "BulkOperationsMixin._handle_array_upsert() - ERROR: No unique_fields provided",
                file=sys.stderr,
            )
            return Response(
                {"error": "unique_fields parameter is required for upsert operations"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Auto-infer update_fields if not provided
        if not update_fields:
            update_fields = self._infer_update_fields(data_list, unique_fields)
            print(
                f"BulkOperationsMixin._handle_array_upsert() - Auto-inferred update_fields: {update_fields}",
                file=sys.stderr,
            )

        # Use Celery worker for array operations
        serializer_class = self.get_serializer_class()
        serializer_class_path = (
            f"{serializer_class.__module__}.{serializer_class.__name__}"
        )
        print(
            f"BulkOperationsMixin._handle_array_upsert() - Using serializer: {serializer_class_path}",
            file=sys.stderr,
        )

        user_id = request.user.id if request.user.is_authenticated else None
        print(
            f"BulkOperationsMixin._handle_array_upsert() - User ID: {user_id}",
            file=sys.stderr,
        )

        # Start Celery upsert task with optimized settings
        print(
            "BulkOperationsMixin._handle_array_upsert() - Dispatching Celery task...",
            file=sys.stderr,
        )

        # Pass upsert context to skip uniqueness validation
        upsert_context = {
            "skip_uniqueness_validation": True,
            "unique_fields": unique_fields,
        }

        task = async_upsert_task.delay(
            serializer_class_path,
            data_list,
            unique_fields,
            update_fields,
            user_id,
            upsert_context,
        )
        print(
            f"BulkOperationsMixin._handle_array_upsert() - Task dispatched with ID: {task.id}",
            file=sys.stderr,
        )

        # Wait for task completion with fixed timeout
        try:
            print(
                "BulkOperationsMixin._handle_array_upsert() - Waiting for task completion (300s timeout)...",
                file=sys.stderr,
            )
            # Wait for the task to complete (synchronous behavior)
            task_result = task.get(
                timeout=300
            )  # 5 minute timeout for upsert operations
            print(
                "BulkOperationsMixin._handle_array_upsert() - Task completed successfully",
                file=sys.stderr,
            )
            print(
                f"BulkOperationsMixin._handle_array_upsert() - Result: success_count={task_result.get('success_count', 0)}, error_count={task_result.get('error_count', 0)}",
                file=sys.stderr,
            )

            # Check for errors first
            errors = task_result.get("errors", [])
            if errors:
                print(
                    f"BulkOperationsMixin._handle_array_upsert() - Returning errors: {errors}",
                    file=sys.stderr,
                )
                return Response(
                    {
                        "errors": errors,
                        "error_count": task_result.get("error_count", 0),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Return successful result in standard DRF format
            serializer_class = self.get_serializer_class()
            model_class = serializer_class.Meta.model

            # Get all affected instances (created and updated)
            created_ids = task_result.get("created_ids", [])
            updated_ids = task_result.get("updated_ids", [])
            all_ids = created_ids + updated_ids

            if all_ids:
                affected_instances = list(model_class.objects.filter(id__in=all_ids))
                serializer = serializer_class(affected_instances, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # No instances were affected and no errors
                print(
                    "BulkOperationsMixin._handle_array_upsert() - No instances affected and no errors",
                    file=sys.stderr,
                )
                return Response([], status=status.HTTP_200_OK)

        except Exception as e:
            print(
                f"BulkOperationsMixin._handle_array_upsert() - ERROR: Task execution failed: {str(e)}",
                file=sys.stderr,
            )
            return Response(
                {"error": f"Upsert task execution failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_array_upsert_direct(
        self, request, unique_fields, update_fields, data_list
    ):
        """Direct upsert implementation for debugging - bypasses Celery."""
        print(
            f"BulkOperationsMixin._handle_array_upsert_direct() - Starting direct upsert with {len(data_list)} items",
            file=sys.stderr,
        )
        print(
            f"BulkOperationsMixin._handle_array_upsert_direct() - Unique fields: {unique_fields}",
            file=sys.stderr,
        )
        print(
            f"BulkOperationsMixin._handle_array_upsert_direct() - Update fields: {update_fields}",
            file=sys.stderr,
        )

        if not unique_fields:
            print(
                "BulkOperationsMixin._handle_array_upsert_direct() - ERROR: No unique_fields provided",
                file=sys.stderr,
            )
            return Response(
                {"error": "unique_fields parameter is required for upsert operations"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Auto-infer update_fields if not provided
        if not update_fields:
            update_fields = self._infer_update_fields(data_list, unique_fields)
            print(
                f"BulkOperationsMixin._handle_array_upsert_direct() - Auto-inferred update_fields: {update_fields}",
                file=sys.stderr,
            )

        # Get serializer and model classes
        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model
        print(
            f"BulkOperationsMixin._handle_array_upsert_direct() - Using model: {model_class.__name__}",
            file=sys.stderr,
        )

        success_count = 0
        error_count = 0
        errors = []
        created_instances = []
        updated_instances = []

        # PHASE 1: Bulk validation only (NO DATABASE QUERIES!)
        instances_to_upsert = []
        validated_items = []

        print(
            f"BulkOperationsMixin._handle_array_upsert_direct() - PHASE 1: Validating {len(data_list)} items (no DB queries)",
            file=sys.stderr,
        )

        for index, item_data in enumerate(data_list):
            print(
                f"BulkOperationsMixin._handle_array_upsert_direct() - Processing item {index}: {item_data}",
                file=sys.stderr,
            )

            try:
                # Create serializer with upsert validation bypass
                print(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Creating upsert-aware serializer for item {index}",
                    file=sys.stderr,
                )

                # Create a custom serializer class that bypasses model validation for upsert
                class UpsertSerializer(serializer_class):
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, **kwargs)
                        # Remove all uniqueness-related validators from serializer level
                        original_validators = self.validators[:]
                        self.validators = [
                            v
                            for v in self.validators
                            if not self._is_uniqueness_validator(v, unique_fields)
                        ]
                        print(
                            f"BulkOperationsMixin._handle_array_upsert_direct() - Filtered {len(original_validators)} -> {len(self.validators)} validators for uniqueness bypass",
                            file=sys.stderr,
                        )

                        # Store original field types before overriding for later reference
                        self._original_field_types = {}

                        # Debug: Print field types for unique fields and override problematic fields
                        for field_name in unique_fields:
                            if field_name in self.fields:
                                field = self.fields[field_name]
                                field_type_name = type(field).__name__

                                # Store the original field type before overriding
                                self._original_field_types[field_name] = field_type_name

                                print(
                                    f"BulkOperationsMixin._handle_array_upsert_direct() - Field '{field_name}' type: {field_type_name}",
                                    file=sys.stderr,
                                )

                                # If the field is a PrimaryKeyRelatedField or similar foreign key field,
                                # we need to override it for upsert operations
                                # This handles cases where fields are incorrectly configured as foreign keys
                                if (
                                    hasattr(field, "queryset")
                                    or "RelatedField" in field_type_name
                                ):
                                    from rest_framework import serializers

                                    # Determine the appropriate field type based on the related field type
                                    if "SlugRelatedField" in field_type_name:
                                        # SlugRelatedField should be overridden to CharField
                                        self.fields[field_name] = (
                                            serializers.CharField()
                                        )
                                        print(
                                            f"BulkOperationsMixin._handle_array_upsert_direct() - Overriding field '{field_name}' from {field_type_name} to CharField for upsert",
                                            file=sys.stderr,
                                        )
                                    else:
                                        # Other related fields should be overridden to IntegerField
                                        self.fields[field_name] = (
                                            serializers.IntegerField()
                                        )
                                        print(
                                            f"BulkOperationsMixin._handle_array_upsert_direct() - Overriding field '{field_name}' from {field_type_name} to IntegerField for upsert",
                                            file=sys.stderr,
                                        )
                                else:
                                    print(
                                        f"BulkOperationsMixin._handle_array_upsert_direct() - Field '{field_name}' not overridden (type: {field_type_name}, has_queryset: {hasattr(field, 'queryset')})",
                                        file=sys.stderr,
                                    )

                        # Also remove uniqueness validators from individual fields and override validation
                        for field_name, field in self.fields.items():
                            if field_name in unique_fields:
                                # Remove validators
                                if hasattr(field, "validators"):
                                    original_field_validators = field.validators[:]
                                    field.validators = [
                                        v
                                        for v in field.validators
                                        if not self._is_field_uniqueness_validator(
                                            v, field_name
                                        )
                                    ]
                                    if len(original_field_validators) != len(
                                        field.validators
                                    ):
                                        print(
                                            f"BulkOperationsMixin._handle_array_upsert_direct() - Removed {len(original_field_validators) - len(field.validators)} uniqueness validators from field '{field_name}'",
                                            file=sys.stderr,
                                        )

                                # Override field validation to bypass uniqueness checks
                                original_run_validation = field.run_validation

                                def bypass_uniqueness_validation(data):
                                    try:
                                        return original_run_validation(data)
                                    except Exception as e:
                                        # If it's a uniqueness error or a "does not exist" error for unique fields, suppress it
                                        error_str = str(e).lower()
                                        if (
                                            "unique" in error_str
                                            and "already exists" in error_str
                                        ) or ("does not exist" in error_str):
                                            print(
                                                f"BulkOperationsMixin._handle_array_upsert_direct() - Suppressing validation error for field '{field_name}': {e}",
                                                file=sys.stderr,
                                            )
                                            # Return the data as-is for upsert processing
                                            return data
                                        else:
                                            # Re-raise non-uniqueness errors
                                            raise e

                                field.run_validation = bypass_uniqueness_validation

                    def _is_uniqueness_validator(self, validator, unique_fields):
                        """Check if validator is related to uniqueness constraints."""
                        # Check for UniqueTogetherValidator
                        if hasattr(validator, "fields") and hasattr(
                            validator, "queryset"
                        ):
                            validator_fields = getattr(validator, "fields", [])
                            return any(
                                field in unique_fields for field in validator_fields
                            )

                        # Check for UniqueValidator (field-level uniqueness)
                        if hasattr(validator, "queryset") and hasattr(
                            validator, "field_name"
                        ):
                            return validator.field_name in unique_fields

                        # Check for UniqueValidator by class name
                        validator_class_name = validator.__class__.__name__
                        if validator_class_name == "UniqueValidator":
                            # For UniqueValidator, we need to check if it's validating one of our unique fields
                            # This is a bit tricky since we don't have direct access to the field name
                            # We'll be more permissive and assume it could be a uniqueness validator
                            return True

                        return False

                    def _is_field_uniqueness_validator(self, validator, field_name):
                        """Check if a field validator is a uniqueness validator for the specified field."""
                        validator_class_name = validator.__class__.__name__

                        # Check for UniqueValidator
                        if validator_class_name == "UniqueValidator":
                            return True

                        # Check for other uniqueness-related validators
                        if hasattr(validator, "queryset") and hasattr(
                            validator, "field_name"
                        ):
                            return validator.field_name == field_name

                        return False

                    def is_valid(self, raise_exception=False):
                        # Call parent validation but skip model-level validation
                        result = super().is_valid(raise_exception=raise_exception)

                        # If validation failed due to uniqueness, clear those errors
                        if not result and "non_field_errors" in self.errors:
                            filtered_errors = []
                            for error in self.errors["non_field_errors"]:
                                error_str = str(error).lower()
                                if (
                                    "unique" in error_str
                                    and "must make a unique set" in error_str
                                ):
                                    print(
                                        f"BulkOperationsMixin._handle_array_upsert_direct() - Suppressing uniqueness error: {error}",
                                        file=sys.stderr,
                                    )
                                    continue
                                filtered_errors.append(error)

                            if filtered_errors:
                                self.errors["non_field_errors"] = filtered_errors
                            else:
                                del self.errors["non_field_errors"]

                            # Recalculate validation result
                            result = not bool(self.errors)

                        return result

                serializer = UpsertSerializer(data=item_data)
                print(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Created upsert serializer for item {index}",
                    file=sys.stderr,
                )

                if serializer.is_valid():
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Serializer validation passed for item {index}",
                        file=sys.stderr,
                    )
                    validated_data = serializer.validated_data

                    # DEBUG: Let's see what to_internal_value returns vs validated_data
                    internal_data = serializer.to_internal_value(item_data)
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - DEBUG: to_internal_value: {internal_data}",
                        file=sys.stderr,
                    )
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - DEBUG: validated_data: {validated_data}",
                        file=sys.stderr,
                    )

                    # Create model instance for bulk operation
                    # Handle foreign key fields properly by converting integer IDs to _id fields
                    model_data = {}
                    for field_name, value in validated_data.items():
                        print(
                            f"BulkOperationsMixin._handle_array_upsert_direct() - Processing field '{field_name}' with value: {value} (type: {type(value)})",
                            file=sys.stderr,
                        )
                        # Check if this is a foreign key field that was overridden
                        if hasattr(model_class, field_name):
                            field = model_class._meta.get_field(field_name)
                            print(
                                f"BulkOperationsMixin._handle_array_upsert_direct() - Field '{field_name}' is a model field: {type(field).__name__}",
                                file=sys.stderr,
                            )
                            if hasattr(field, "related_model") and field.related_model:
                                # Check if this field was originally a SlugRelatedField in the serializer
                                # Use the stored original field type instead of the overridden field
                                original_field_type = getattr(
                                    serializer, "_original_field_types", {}
                                ).get(field_name, "")
                                is_slug_related = (
                                    "SlugRelatedField" in original_field_type
                                )
                                print(
                                    f"BulkOperationsMixin._handle_array_upsert_direct() - DEBUG: Field '{field_name}' original type: {original_field_type}, was originally SlugRelatedField: {is_slug_related}",
                                    file=sys.stderr,
                                )
                                # This is a foreign key field
                                if is_slug_related:
                                    # For SlugRelatedField, we need to look up the actual integer ID
                                    # The value is a string (like "Disbursement") but we need the integer ID
                                    related_model = field.related_model

                                    # Get the original SlugRelatedField to access its slug_field attribute
                                    # We need to get it from the original serializer class, not the overridden one
                                    original_serializer_class = serializer_class
                                    original_field = original_serializer_class().fields[
                                        field_name
                                    ]
                                    slug_field_name = original_field.slug_field

                                    print(
                                        f"BulkOperationsMixin._handle_array_upsert_direct() - DEBUG: SlugRelatedField '{field_name}' slug_field: {slug_field_name}, value: {value}",
                                        file=sys.stderr,
                                    )

                                    try:
                                        # Look up the related object by the slug field
                                        lookup_kwargs = {slug_field_name: value}
                                        related_obj = related_model.objects.get(
                                            **lookup_kwargs
                                        )
                                        actual_value = related_obj.pk
                                        print(
                                            f"BulkOperationsMixin._handle_array_upsert_direct() - DEBUG: Found related object: {related_obj}, PK: {actual_value}",
                                            file=sys.stderr,
                                        )

                                        # Use _id suffix for SlugRelatedField (it's still a foreign key with integer PK)
                                        model_data[f"{field_name}_id"] = actual_value
                                        print(
                                            f"BulkOperationsMixin._handle_array_upsert_direct() - Using SlugRelatedField lookup for field '{field_name}': {value} -> {actual_value}",
                                            file=sys.stderr,
                                        )
                                    except related_model.DoesNotExist:
                                        print(
                                            f"BulkOperationsMixin._handle_array_upsert_direct() - ERROR: Related object not found for {field_name}={value}",
                                            file=sys.stderr,
                                        )
                                        raise ValueError(
                                            f"Related object not found for {field_name}={value}"
                                        )
                                else:
                                    # Regular foreign key field (PrimaryKeyRelatedField, etc.)
                                    # Extract the actual ID from the model instance if it's a model instance
                                    if hasattr(value, "pk"):
                                        # It's a model instance, extract the primary key
                                        actual_value = value.pk
                                    elif hasattr(value, "id"):
                                        # It's a model instance, extract the id
                                        actual_value = value.id
                                    else:
                                        # It's already an ID value (could be string or int)
                                        actual_value = value

                                    # For regular foreign keys, always use _id suffix
                                    model_data[f"{field_name}_id"] = actual_value
                                    print(
                                        f"BulkOperationsMixin._handle_array_upsert_direct() - Using regular FK for field '{field_name}': {actual_value}",
                                        file=sys.stderr,
                                    )
                            else:
                                # Handle special field types that need conversion
                                if hasattr(field, "to_python"):
                                    # Use Django field's to_python method for proper type conversion
                                    try:
                                        converted_value = field.to_python(value)
                                        model_data[field_name] = converted_value
                                        print(
                                            f"BulkOperationsMixin._handle_array_upsert_direct() - Converted field '{field_name}' using to_python: {value} -> {converted_value} (type: {type(converted_value)})",
                                            file=sys.stderr,
                                        )
                                    except Exception as e:
                                        print(
                                            f"BulkOperationsMixin._handle_array_upsert_direct() - Failed to convert field '{field_name}' using to_python: {e}, using original value",
                                            file=sys.stderr,
                                        )
                                        model_data[field_name] = value
                                else:
                                    model_data[field_name] = value
                        else:
                            model_data[field_name] = value

                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Model data for instantiation: {model_data}",
                        file=sys.stderr,
                    )
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Original validated_data: {validated_data}",
                        file=sys.stderr,
                    )
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Model data keys: {list(model_data.keys())}",
                        file=sys.stderr,
                    )
                    instance = model_class(**model_data)

                    # Ensure foreign key fields are properly set for bulk-hooks framework
                    # This is handled by the model_data mapping above, no need to clear fields

                    instances_to_upsert.append(instance)
                    validated_items.append((index, item_data, validated_data))

                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Queued for bulk upsert: {validated_data}",
                        file=sys.stderr,
                    )

                    # Check database constraints (only once)
                    if index == 0:
                        print(
                            "BulkOperationsMixin._handle_array_upsert_direct() - Checking model meta constraints...",
                            file=sys.stderr,
                        )
                        if hasattr(model_class._meta, "constraints"):
                            for constraint in model_class._meta.constraints:
                                print(
                                    f"BulkOperationsMixin._handle_array_upsert_direct() - Model constraint: {constraint}",
                                    file=sys.stderr,
                                )

                        # Check unique_together
                        if (
                            hasattr(model_class._meta, "unique_together")
                            and model_class._meta.unique_together
                        ):
                            print(
                                f"BulkOperationsMixin._handle_array_upsert_direct() - Model unique_together: {model_class._meta.unique_together}",
                                file=sys.stderr,
                            )

                else:
                    # Enhanced error logging with detailed debugging info
                    error_msg = (
                        f"Serializer validation failed: {str(serializer.errors)}"
                    )
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - ERROR at index {index}: {error_msg}",
                        file=sys.stderr,
                    )
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Detailed errors: {serializer.errors}",
                        file=sys.stderr,
                    )
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Input data: {item_data}",
                        file=sys.stderr,
                    )

                    # Try to understand what validation failed
                    if "non_field_errors" in serializer.errors:
                        print(
                            f"BulkOperationsMixin._handle_array_upsert_direct() - Non-field errors: {serializer.errors['non_field_errors']}",
                            file=sys.stderr,
                        )
                        for error in serializer.errors["non_field_errors"]:
                            print(
                                f"BulkOperationsMixin._handle_array_upsert_direct() - Error code: {error.code}, message: {error}",
                                file=sys.stderr,
                            )

                    # Check field-specific errors
                    if "financial_provider" in serializer.errors:
                        print(
                            f"BulkOperationsMixin._handle_array_upsert_direct() - Financial provider field error: {serializer.errors['financial_provider']}",
                            file=sys.stderr,
                        )
                        print(
                            f"BulkOperationsMixin._handle_array_upsert_direct() - This might be SlugRelatedField validation failing",
                            file=sys.stderr,
                        )

                    if "account_number" in serializer.errors:
                        print(
                            f"BulkOperationsMixin._handle_array_upsert_direct() - Account number field error: {serializer.errors['account_number']}",
                            file=sys.stderr,
                        )

                    errors.append(
                        {"index": index, "error": error_msg, "data": item_data}
                    )
                    error_count += 1

            except Exception as e:
                error_msg = f"Direct upsert failed: {str(e)}"
                print(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - EXCEPTION at index {index}: {error_msg}",
                    file=sys.stderr,
                )
                import traceback

                print(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Exception stack trace:\n{traceback.format_exc()}",
                    file=sys.stderr,
                )

                errors.append({"index": index, "error": error_msg, "data": item_data})
                error_count += 1

        # PHASE 2: TRUE BULK UPSERT (NO INDIVIDUAL QUERIES!)
        print(
            "BulkOperationsMixin._handle_array_upsert_direct() - PHASE 2: TRUE bulk upsert",
            file=sys.stderr,
        )
        print(
            f"BulkOperationsMixin._handle_array_upsert_direct() - Instances to upsert: {len(instances_to_upsert)}",
            file=sys.stderr,
        )

        if instances_to_upsert:
            try:
                # Determine update fields for bulk_create with update_conflicts
                if update_fields:
                    fields_to_update = update_fields
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Using specified update_fields: {fields_to_update}",
                        file=sys.stderr,
                    )
                else:
                    # Auto-determine update fields (all non-unique fields, excluding auto-set fields)
                    if instances_to_upsert:
                        sample_instance = instances_to_upsert[0]
                        fields_to_update = [
                            field.name
                            for field in sample_instance._meta.fields
                            if field.name not in unique_fields
                            and not field.primary_key
                            and not getattr(field, "auto_now", False)
                            and not getattr(field, "auto_now_add", False)
                        ]
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Auto-determined update_fields: {fields_to_update}",
                        file=sys.stderr,
                    )

                print(
                    "BulkOperationsMixin._handle_array_upsert_direct() - Executing bulk_create with update_conflicts",
                    file=sys.stderr,
                )
                print(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - unique_fields: {unique_fields}",
                    file=sys.stderr,
                )
                print(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - update_fields: {fields_to_update}",
                    file=sys.stderr,
                )

                # DEBUG: Show what instances are being passed to bulk_create
                print(
                    "BulkOperationsMixin._handle_array_upsert_direct() - DEBUG: Instances being passed to bulk_create:",
                    file=sys.stderr,
                )
                for i, instance in enumerate(instances_to_upsert):
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Instance {i}: {instance.__dict__}",
                        file=sys.stderr,
                    )
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Instance {i} model: {instance._meta.label}",
                        file=sys.stderr,
                    )

                with transaction.atomic():
                    # TRUE BULK UPSERT: Single database operation handles both create and update
                    print(
                        "BulkOperationsMixin._handle_array_upsert_direct() - DEBUG: Calling bulk_create with:",
                        file=sys.stderr,
                    )
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() -   instances: {len(instances_to_upsert)} items",
                        file=sys.stderr,
                    )
                    print(
                        "BulkOperationsMixin._handle_array_upsert_direct() -   update_conflicts: True",
                        file=sys.stderr,
                    )
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() -   update_fields: {fields_to_update}",
                        file=sys.stderr,
                    )
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() -   unique_fields: {unique_fields}",
                        file=sys.stderr,
                    )
                    print(
                        "BulkOperationsMixin._handle_array_upsert_direct() -   batch_size: 1000",
                        file=sys.stderr,
                    )

                    upserted_instances = model_class.objects.bulk_create(
                        instances_to_upsert,
                        update_conflicts=True,
                        update_fields=fields_to_update,
                        unique_fields=unique_fields,
                        batch_size=1000,
                    )

                    success_count += len(upserted_instances)
                    created_instances.extend(upserted_instances)
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - BULK UPSERT COMPLETED: {len(upserted_instances)} instances processed",
                        file=sys.stderr,
                    )

                    # Since bulk_create with update_conflicts returns all instances,
                    # we can't distinguish created vs updated without additional queries
                    # But that's okay - the upsert worked!

            except Exception as bulk_error:
                print(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - BULK UPSERT FAILED: {bulk_error}",
                    file=sys.stderr,
                )
                import traceback

                print(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Bulk upsert stack trace:\n{traceback.format_exc()}",
                    file=sys.stderr,
                )

                # Check if it's a unique constraint error
                error_str = str(bulk_error).lower()
                if "unique" in error_str or "constraint" in error_str:
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - UNIQUE CONSTRAINT ERROR detected",
                        file=sys.stderr,
                    )
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - This usually means the unique constraint isn't properly configured",
                        file=sys.stderr,
                    )

                errors.append(
                    {
                        "index": 0,
                        "error": f"Bulk upsert failed: {bulk_error}",
                        "data": None,
                    }
                )
                error_count += 1

        # Prepare response
        print(
            f"BulkOperationsMixin._handle_array_upsert_direct() - Completed: success={success_count}, errors={error_count}",
            file=sys.stderr,
        )

        if error_count > 0:
            print(
                f"BulkOperationsMixin._handle_array_upsert_direct() - Returning errors: {errors}",
                file=sys.stderr,
            )
            return Response(
                {"errors": errors, "error_count": error_count},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Return successful results
        all_instances = created_instances + updated_instances
        if all_instances:
            print(
                f"BulkOperationsMixin._handle_array_upsert_direct() - Returning {len(all_instances)} instances",
                file=sys.stderr,
            )
            serializer = serializer_class(all_instances, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print(
                "BulkOperationsMixin._handle_array_upsert_direct() - No instances processed",
                file=sys.stderr,
            )
            return Response([], status=status.HTTP_200_OK)

    def _infer_update_fields(self, data_list, unique_fields):
        """Auto-infer update fields from data payload."""
        if not data_list:
            return []

        all_fields = set()
        for item in data_list:
            if isinstance(item, dict):
                all_fields.update(item.keys())

        update_fields = list(all_fields - set(unique_fields))
        update_fields.sort()
        return update_fields

    # =============================================================================
    # End of BulkOperationsMixin
    # =============================================================================


# Legacy aliases for backwards compatibility
OperationsMixin = BulkOperationsMixin  # Backward compatibility alias
