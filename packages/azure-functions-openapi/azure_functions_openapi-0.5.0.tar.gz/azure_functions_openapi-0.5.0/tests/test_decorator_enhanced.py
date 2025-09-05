# tests/test_decorator_enhanced.py

import pytest
from unittest.mock import patch
from pydantic import BaseModel

from azure_functions_openapi.decorator import (
    openapi,
    get_openapi_registry,
    _validate_and_sanitize_route,
    _validate_and_sanitize_operation_id,
    _validate_parameters,
    _validate_tags,
    _validate_models
)
from azure_functions_openapi.errors import ValidationError, OpenAPIError


class SampleModel(BaseModel):
    """Sample Pydantic model for testing."""
    name: str
    age: int


class TestOpenAPIDecoratorEnhanced:
    """Test enhanced OpenAPI decorator functionality."""
    
    def test_openapi_decorator_with_validation_error(self):
        """Test decorator with validation error."""
        with pytest.raises(OpenAPIError):
            @openapi(
                route="<script>alert('xss')</script>",  # Invalid route
                summary="Test"
            )
            def test_func():
                pass
    
    def test_openapi_decorator_with_invalid_operation_id(self):
        """Test decorator with invalid operation ID."""
        # The decorator should sanitize the operation ID instead of raising an error
        @openapi(
            operation_id="<script>alert('xss')</script>",  # Invalid operation ID
            summary="Test"
        )
        def test_func():
            pass
        
        # Verify the operation ID was sanitized
        registry = get_openapi_registry()
        assert "test_func" in registry
        # The operation ID should be sanitized to remove dangerous characters
        assert registry["test_func"]["operation_id"] == "scriptalertxssscript"
    
    def test_openapi_decorator_with_invalid_parameters(self):
        """Test decorator with invalid parameters."""
        with pytest.raises(OpenAPIError):
            @openapi(
                parameters="not_a_list",  # Invalid parameters type
                summary="Test"
            )
            def test_func():
                pass
    
    def test_openapi_decorator_with_invalid_parameter_structure(self):
        """Test decorator with invalid parameter structure."""
        with pytest.raises(OpenAPIError):
            @openapi(
                parameters=[{"name": "test"}],  # Missing required field 'in'
                summary="Test"
            )
            def test_func():
                pass
    
    def test_openapi_decorator_with_invalid_tags(self):
        """Test decorator with invalid tags."""
        with pytest.raises(OpenAPIError):
            @openapi(
                tags="not_a_list",  # Invalid tags type
                summary="Test"
            )
            def test_func():
                pass
    
    def test_openapi_decorator_with_empty_tag(self):
        """Test decorator with empty tag."""
        with pytest.raises(OpenAPIError):
            @openapi(
                tags=["valid_tag", ""],  # Empty tag
                summary="Test"
            )
            def test_func():
                pass
    
    def test_openapi_decorator_with_invalid_request_model(self):
        """Test decorator with invalid request model."""
        with pytest.raises(OpenAPIError):
            @openapi(
                request_model=str,  # Not a BaseModel subclass
                summary="Test"
            )
            def test_func():
                pass
    
    def test_openapi_decorator_with_invalid_response_model(self):
        """Test decorator with invalid response model."""
        with pytest.raises(OpenAPIError):
            @openapi(
                response_model=int,  # Not a BaseModel subclass
                summary="Test"
            )
            def test_func():
                pass
    
    def test_openapi_decorator_success(self):
        """Test successful decorator application."""
        @openapi(
            summary="Test function",
            description="A test function",
            tags=["test"],
            operation_id="test_operation",
            route="/test",
            method="get",
            parameters=[{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            request_model=SampleModel,
            response_model=SampleModel
        )
        def test_func():
            pass
        
        # Verify function is registered
        registry = get_openapi_registry()
        assert "test_func" in registry
        
        metadata = registry["test_func"]
        assert metadata["summary"] == "Test function"
        assert metadata["description"] == "A test function"
        assert metadata["tags"] == ["test"]
        assert metadata["operation_id"] == "test_operation"
        assert metadata["route"] == "/test"
        assert metadata["method"] == "get"
        assert len(metadata["parameters"]) == 1
        assert metadata["request_model"] == SampleModel
        assert metadata["response_model"] == SampleModel


class TestValidationFunctions:
    """Test validation helper functions."""
    
    def test_validate_and_sanitize_route_valid(self):
        """Test route validation with valid route."""
        result = _validate_and_sanitize_route("/api/test", "test_func")
        assert result == "/api/test"
    
    def test_validate_and_sanitize_route_none(self):
        """Test route validation with None route."""
        result = _validate_and_sanitize_route(None, "test_func")
        assert result is None
    
    def test_validate_and_sanitize_route_invalid(self):
        """Test route validation with invalid route."""
        with pytest.raises(ValidationError):
            _validate_and_sanitize_route("<script>alert('xss')</script>", "test_func")
    
    def test_validate_and_sanitize_operation_id_valid(self):
        """Test operation ID validation with valid ID."""
        result = _validate_and_sanitize_operation_id("test_operation", "test_func")
        assert result == "test_operation"
    
    def test_validate_and_sanitize_operation_id_none(self):
        """Test operation ID validation with None ID."""
        result = _validate_and_sanitize_operation_id(None, "test_func")
        assert result is None
    
    def test_validate_and_sanitize_operation_id_invalid(self):
        """Test operation ID validation with invalid ID."""
        # The function should sanitize instead of raising an error
        result = _validate_and_sanitize_operation_id("<script>alert('xss')</script>", "test_func")
        assert result == "scriptalertxssscript"
    
    def test_validate_parameters_valid(self):
        """Test parameter validation with valid parameters."""
        params = [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}]
        result = _validate_parameters(params, "test_func")
        assert result == params
    
    def test_validate_parameters_none(self):
        """Test parameter validation with None parameters."""
        result = _validate_parameters(None, "test_func")
        assert result == []
    
    def test_validate_parameters_invalid_type(self):
        """Test parameter validation with invalid type."""
        with pytest.raises(ValidationError):
            _validate_parameters("not_a_list", "test_func")
    
    def test_validate_parameters_invalid_structure(self):
        """Test parameter validation with invalid structure."""
        with pytest.raises(ValidationError):
            _validate_parameters([{"name": "test"}], "test_func")  # Missing 'in' field
    
    def test_validate_parameters_invalid_item_type(self):
        """Test parameter validation with invalid item type."""
        with pytest.raises(ValidationError):
            _validate_parameters(["not_a_dict"], "test_func")
    
    def test_validate_tags_valid(self):
        """Test tag validation with valid tags."""
        tags = ["tag1", "tag2"]
        result = _validate_tags(tags, "test_func")
        assert result == tags
    
    def test_validate_tags_none(self):
        """Test tag validation with None tags."""
        result = _validate_tags(None, "test_func")
        assert result == ["default"]
    
    def test_validate_tags_invalid_type(self):
        """Test tag validation with invalid type."""
        with pytest.raises(ValidationError):
            _validate_tags("not_a_list", "test_func")
    
    def test_validate_tags_invalid_item_type(self):
        """Test tag validation with invalid item type."""
        with pytest.raises(ValidationError):
            _validate_tags([123], "test_func")
    
    def test_validate_tags_empty_tag(self):
        """Test tag validation with empty tag."""
        with pytest.raises(ValidationError):
            _validate_tags(["valid", ""], "test_func")
    
    def test_validate_tags_whitespace_tag(self):
        """Test tag validation with whitespace-only tag."""
        with pytest.raises(ValidationError):
            _validate_tags(["valid", "   "], "test_func")
    
    def test_validate_models_valid(self):
        """Test model validation with valid models."""
        _validate_models(SampleModel, SampleModel, "test_func")  # Should not raise
    
    def test_validate_models_none(self):
        """Test model validation with None models."""
        _validate_models(None, None, "test_func")  # Should not raise
    
    def test_validate_models_invalid_request_model(self):
        """Test model validation with invalid request model."""
        with pytest.raises(ValidationError):
            _validate_models(str, None, "test_func")
    
    def test_validate_models_invalid_response_model(self):
        """Test model validation with invalid response model."""
        with pytest.raises(ValidationError):
            _validate_models(None, int, "test_func")


class TestOpenAPIDecoratorErrorHandling:
    """Test error handling in OpenAPI decorator."""
    
    @patch('azure_functions_openapi.decorator.logger')
    def test_decorator_error_logging(self, mock_logger):
        """Test that decorator errors are logged."""
        with pytest.raises(OpenAPIError):
            @openapi(
                route="<script>alert('xss')</script>",
                summary="Test"
            )
            def test_func():
                pass
        
        # Should log the error
        mock_logger.error.assert_called()
    
    def test_decorator_exception_conversion(self):
        """Test that exceptions are converted to OpenAPIError."""
        with patch('azure_functions_openapi.decorator._validate_and_sanitize_route') as mock_validate:
            mock_validate.side_effect = Exception("Unexpected error")
            
            with pytest.raises(OpenAPIError) as exc_info:
                @openapi(summary="Test")
                def test_func():
                    pass
            
            assert "Failed to register OpenAPI metadata" in str(exc_info.value)
            assert exc_info.value.details["function_name"] == "test_func"