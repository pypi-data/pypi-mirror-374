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
        """
        Simplified bulk upsert that leverages DRF's internal field conversion.

        Instead of manually converting fields, we use DRF's save() method to handle
        all the complex field conversion, then extract the model data for bulk operations.
        """
        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model

        print(
            f"BulkOperationsMixin._handle_array_upsert_direct() - Processing {len(data_list)} items",
            file=sys.stderr,
        )

        instances_to_upsert = []
        errors = []

        for index, item_data in enumerate(data_list):
            try:
                # Create serializer with the original data
                serializer = serializer_class(data=item_data)

                if serializer.is_valid():
                    # Use DRF's save() method to handle all field conversion
                    # This leverages DRF's existing logic for SlugRelatedField, etc.
                    temp_instance = serializer.save()

                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Created temp instance {index}: {temp_instance}",
                        file=sys.stderr,
                    )

                    # Extract the model data from the instance
                    model_data = {}
                    for field in model_class._meta.fields:
                        if field.name != "id":  # Skip auto-generated ID
                            value = getattr(temp_instance, field.name)
                            if value is not None:
                                model_data[field.name] = value

                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Extracted model data {index}: {model_data}",
                        file=sys.stderr,
                    )

                    # Delete the temporary instance since we just needed it for field conversion
                    temp_instance.delete()

                    # Create a new instance with the extracted data for bulk operations
                    new_instance = model_class(**model_data)
                    instances_to_upsert.append(new_instance)

                else:
                    print(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Validation failed for item {index}: {serializer.errors}",
                        file=sys.stderr,
                    )
                    errors.append(
                        {
                            "index": index,
                            "error": f"Validation failed: {serializer.errors}",
                            "data": item_data,
                        }
                    )

            except Exception as e:
                print(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Error processing item {index}: {e}",
                    file=sys.stderr,
                )
                errors.append(
                    {
                        "index": index,
                        "error": f"Processing error: {str(e)}",
                        "data": item_data,
                    }
                )

        # Return errors if any
        if errors:
            print(
                f"BulkOperationsMixin._handle_array_upsert_direct() - Returning {len(errors)} errors",
                file=sys.stderr,
            )
            return Response(
                {"errors": errors, "error_count": len(errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Now perform the bulk upsert with the properly converted instances
        if instances_to_upsert:
            try:
                print(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Performing bulk upsert with {len(instances_to_upsert)} instances",
                    file=sys.stderr,
                )

                # Use bulk_create with update_conflicts for upsert behavior
                upserted_instances = model_class.objects.bulk_create(
                    instances_to_upsert,
                    update_conflicts=True,
                    update_fields=update_fields or [],
                    unique_fields=unique_fields,
                    batch_size=1000,
                )

                print(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Successfully upserted {len(upserted_instances)} instances",
                    file=sys.stderr,
                )

                # Get all affected instances
                all_instances = []
                if upserted_instances:
                    upserted_ids = [
                        instance.id
                        for instance in upserted_instances
                        if hasattr(instance, "id") and instance.id
                    ]
                    if upserted_ids:
                        all_instances = list(
                            model_class.objects.filter(id__in=upserted_ids)
                        )

                if all_instances:
                    serializer = serializer_class(all_instances, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response([], status=status.HTTP_200_OK)

            except Exception as e:
                print(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Bulk upsert failed: {e}",
                    file=sys.stderr,
                )
                return Response(
                    {"error": "Bulk upsert failed", "details": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            print(
                "BulkOperationsMixin._handle_array_upsert_direct() - No instances to upsert",
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

        unique_fields_set = set(unique_fields)
        return list(all_fields - unique_fields_set)

    def _infer_update_fields(self, data_list, unique_fields):
        """Auto-infer update fields from data payload."""
        if not data_list:
            return []

        all_fields = set()
        for item in data_list:
            if isinstance(item, dict):
                all_fields.update(item.keys())

        unique_fields_set = set(unique_fields)
        return list(all_fields - unique_fields_set)


# Legacy aliases for backwards compatibility
OperationsMixin = BulkOperationsMixin  # Backward compatibility alias
