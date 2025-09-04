# Implementation Plan

Production-ready PyPI package for natural language image augmentation via MCP protocol. Focus on easy installation (`uv add albumentations-mcp`) and seamless MCP client integration (`uvx albumentations-mcp`).

## 🎉 PROJECT STATUS: BETA v0.1.0b3 - PUBLISHED ON PYPI

**✅ CORE FUNCTIONALITY COMPLETE**

- 7 MCP Tools implemented and working (augment_image, list_available_transforms, validate_prompt, set_default_seed, list_available_presets, load_image_for_processing, get_pipeline_status)
- 3 MCP Prompts implemented (compose_preset, explain_effects, augmentation_parser)
- Complete 7-stage hook system (all hooks active and integrated)
- Natural language parser with 20+ transform mappings
- Reproducible seeding system with global and per-transform seeds
- Preset pipelines (segmentation, portrait, lowlight)
- CLI demo with full functionality
- File path, base64, and session input modes
- Comprehensive testing (383/394 tests passing - 97% pass rate)
- PyPI package published and available (v0.1.0b3)
- Production logging and error handling
- Complete documentation and API reference

**🔧 REMAINING ISSUES TO FIX**

- 11 test failures related to file path processing and resource cleanup
- Some edge cases in utility functions
- MCP client timeout optimization needed
- Minor preset parameter handling improvements

**🚀 BETA v0.2 ROADMAP - PERFORMANCE & RELIABILITY**

- Fix remaining test failures for 100% pass rate
- MCP client timeout optimization
- Individual hook toggles via environment variables
- Batch processing capabilities
- Performance optimizations for large images
- Enhanced error handling and debugging

**📊 CURRENT METRICS**

- **Test Coverage**: 97% (383/394 tests passing)
- **Code Quality**: Black formatted, Ruff linted, MyPy validated
- **Package Status**: Published on PyPI (v0.1.0b3)
- **Documentation**: Comprehensive README and API docs

## Task List - Current Status

### ✅ COMPLETED FEATURES (Beta v0.1.0b3)

All major functionality is implemented and working:

- **7 MCP Tools**: augment_image, list_available_transforms, validate_prompt, set_default_seed, list_available_presets, load_image_for_processing, get_pipeline_status
- **3 MCP Prompts**: compose_preset, explain_effects, augmentation_parser
- **Complete Hook System**: All 7 stages implemented and active (pre_mcp, post_mcp, pre_transform, post_transform, post_transform_verify, pre_save, post_save)
- **Natural Language Parser**: 20+ transform mappings with parameter extraction
- **Seeding System**: Global and per-transform reproducible results
- **Preset System**: segmentation, portrait, lowlight presets
- **Multi-Input Support**: File path, base64, and session modes
- **CLI Demo**: Full command-line interface
- **PyPI Package**: Published as v0.1.0b3
- **Comprehensive Documentation**: README, API docs, examples

### 🔧 REMAINING ISSUES TO FIX

Based on current test results (383/394 tests passing), the following issues need to be addressed:

- [ ] 24. Fix remaining test failures (11 failing tests)

  - [ ] 24.1 Fix file path processing edge cases

    - Debug and fix file path validation issues in test_integration_verification.py
    - Fix image format handling for all supported formats (PNG, JPEG, WEBP, TIFF)
    - Resolve output file generation issues for different image sizes
    - _Requirements: 1.2, 7.1, 7.2_

  - [ ] 24.2 Fix resource cleanup and session management

    - Fix temporary file cleanup logic in post_save hook
    - Resolve session directory structure validation issues
    - Fix resource cleanup test assertions
    - _Requirements: 13.1, 13.2, 13.3_

  - [ ] 24.3 Fix utility function edge cases

    - Fix filename sanitization for empty strings and special cases
    - Resolve filename validation for names starting with numbers
    - Fix security validation error handling
    - _Requirements: 7.1, 7.2_

  - [ ] 24.4 Fix hook system edge cases

    - Debug pre_save hook filename sanitization logic
    - Fix hook validation warnings and error handling
    - Resolve image processing pipeline integration issues
    - _Requirements: 3.3, 3.4, 3.7, 3.8_

### 🚀 BETA v0.2 ROADMAP - PERFORMANCE & RELIABILITY

- [ ] 25. Performance optimizations

  - [ ] 25.1 MCP client timeout optimization

    - Optimize processing pipeline to stay under 30-second client timeouts
    - Implement progress callbacks for long-running operations
    - Add processing time monitoring and optimization
    - _Requirements: 7.1, 7.2_

  - [ ] 25.2 Memory usage optimization

    - Optimize large image processing to reduce memory footprint
    - Implement streaming processing for very large images
    - Add memory usage monitoring and cleanup
    - _Requirements: 7.1, 7.2_

- [ ] 26. Enhanced configuration management

  - [ ] 26.1 Environment-based hook toggles

    - Add ENABLE_VISION_VERIFICATION environment variable
    - Implement individual hook enable/disable flags
    - Add runtime configuration for hook behavior
    - _Requirements: 3.1, 3.2, 3.9_

  - [ ] 26.2 Advanced configuration options

    - Add OUTPUT_DIR customization
    - Implement LOG_LEVEL configuration
    - Add DEFAULT_SEED for reproducible testing
    - Add PRESET_DIR for custom preset locations
    - _Requirements: 5.1, 5.2, 8.6_

- [ ] 27. Batch processing capabilities

  - [ ] 27.1 Implement batch_augment_images tool

    - Create new MCP tool for processing multiple images
    - Add batch processing with progress tracking
    - Implement efficient resource management for batches
    - _Requirements: 1.1, 1.2, 7.1, 7.2_

  - [ ] 27.2 Batch optimization features

    - Add parallel processing for independent transforms
    - Implement batch size optimization based on available memory
    - Add batch progress reporting and cancellation
    - _Requirements: 7.1, 7.2_

### 📚 COMPLETED TASKS (For Reference)

- [x] 1. Set up FastMCP server

  - Initialize project with `uv init` and create virtual environment
  - Install dependencies: `uv add mcp albumentations pillow`
  - Create `main.py` with FastMCP import and basic structure
  - Set up project structure: `src/`, `tests/`
  - Create `pyproject.toml` with minimal dependencies (handled by uv)
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 2. Create image handling utilities

  - Write Base64 ↔ PIL Image conversion functions
  - Add basic image format validation
  - Create simple error handling for invalid images
  - Write unit tests for image conversion
  - _Requirements: 1.2, 7.1, 7.2_

- [x] 3. Build natural language parser

  - Create simple prompt parser using string matching
  - Map phrases to Albumentations transforms ("blur" → Blur)
  - Add parameter extraction with defaults
  - Handle basic errors and provide suggestions
  - _Requirements: 1.1, 1.4, 7.3_

- [x] 4. Restructure for PyPI distribution

  - Restructure to `src/albumentations_mcp/` package layout
  - Create `__init__.py` with package exports and version info
  - Create `__main__.py` entry point for `uvx albumentations-mcp`
  - Move existing files to proper package structure with relative imports
  - Update `pyproject.toml` with proper package metadata and entry points
  - Test package installation and CLI command functionality
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 11.1, 11.2, 11.3, 11.4_

- [x] 5. Implement MCP tools with @mcp.tool() decorators

  - [x] 5.1 Create augment_image tool

    - Use `@mcp.tool()` decorator in `server.py`
    - Accept `image_b64: str` and `prompt: str`
    - Parse prompt → create Albumentations pipeline → apply
    - Return augmented image as Base64 string
    - _Requirements: 1.1, 1.2, 1.3, 7.1, 7.2, 7.5_

  - [x] 5.2 Add list_available_transforms tool

    - Use `@mcp.tool()` decorator
    - Return list of transforms with descriptions
    - Include parameter ranges and examples
    - _Requirements: 2.1, 2.2_

  - [x] 5.3 Create validate_prompt tool

    - Use `@mcp.tool()` decorator
    - Parse prompt and return what would be applied
    - Show parameters and warnings
    - _Requirements: 1.4, 2.1, 2.2_

  - [x] 5.4 Add get_pipeline_status tool

    - Use `@mcp.tool()` decorator
    - Return current pipeline status and registered hooks
    - Show hook system information for debugging
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

  - [x] 5.5 Add set_default_seed tool

    - Use `@mcp.tool()` decorator
    - Set default seed for consistent reproducibility across all augment_image calls
    - Support clearing default seed by passing None
    - _Requirements: 7.1, 7.2, 7.5_

  - [x] 5.6 Add list_available_presets tool

    - Use `@mcp.tool()` decorator
    - Return list of available preset configurations
    - Include preset descriptions and use cases
    - _Requirements: 1.1, 1.4, 2.1, 2.2_

  - [x] 5.7 Add load_image_for_processing tool
    - Use `@mcp.tool()` decorator
    - Load image from URL, file path, or base64 and save for processing
    - Generate session ID and create proper directory structure
    - Support multiple input formats with automatic detection
    - _Requirements: 1.2, 7.1, 7.2_

- [x] 6. Create hook system framework

  - [x] 6.1 Implement hook registry and base classes

    - Create HookRegistry class for managing hooks
    - Define BaseHook abstract class and HookContext/HookResult data structures
    - Implement hook stage enumeration (8 stages)
    - Add hook execution framework with error handling
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

  - [x] 6.2 Implement basic hooks
    - Create pre_mcp hook for input sanitization and preprocessing
    - Create post_mcp hook for JSON spec logging and validation
    - Register hooks in pipeline initialization
    - _Requirements: 3.1, 3.2_

- [x] 7. Create image processor and pipeline orchestration

  - [x] 7.1 Implement image processor

    - Create ImageProcessor class with Albumentations integration
    - Add transform pipeline creation and execution
    - Implement parameter validation and error recovery
    - Add processing result metadata and timing
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 7.2 Create pipeline orchestration
    - Implement AugmentationPipeline class with hook integration
    - Add parse_prompt_with_hooks function for complete workflow
    - Integrate hook execution at appropriate stages
    - Add pipeline status reporting
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

- [x] 8. Complete remaining hook implementations

  - [x] 8.1 Implement pre_transform hook

    - Create hook for image and configuration validation before processing
    - Validate image format, size, and quality
    - Validate transform parameters and provide warnings
    - _Requirements: 3.3, 7.1, 7.2_

  - [x] 8.2 Implement post_transform hook

    - Create hook for metadata attachment after processing
    - Add processing statistics and quality metrics
    - Generate transformation summary and timing data
    - _Requirements: 3.4, 5.1, 5.2, 5.3_

  - [x] 8.3 Implement pre_save hook

    - Create hook for filename modification and versioning
    - Generate unique filenames with timestamps
    - Create output directory structure
    - _Requirements: 3.7, 5.4, 10.1, 10.2_

  - [x] 8.4 Implement post_save hook

    - Create hook for follow-up actions and cleanup
    - Log completion status and file locations
    - Clean up temporary files and resources
    - _Requirements: 3.8, 5.5, 10.3, 10.4, 10.5, 10.6_

  - [x] 8.5 **CODE QUALITY CHECKPOINT: Hook System Review**
    - Review all hook implementations for code duplication and complexity
    - Ensure each hook function is under 20 lines and single-purpose
    - Refactor common patterns into shared utilities
    - Verify consistent error handling across all hooks
    - Check for circular dependencies and unnecessary coupling
    - _Requirements: 4.1, 4.2_

- [x] 9. Add LLM-based visual verification system

  - [x] 9.1 Create image file output system

    - Create utility functions to save images to temporary files
    - Generate unique filenames with timestamps for original and augmented images
    - Add file cleanup utilities for temporary image files
    - Create verification report templates that reference saved image files
    - _Requirements: 8.1, 8.2, 8.6_

  - [x] 9.2 Implement post_transform_verify hook
    - Create hook that saves both original and augmented images to files
    - Generate visual_eval.md report with image file paths and verification prompts
    - Include structured questions for the LLM to evaluate transformation success
    - Add confidence scoring framework (1-5) and change description templates
    - Make verification optional and non-blocking (graceful failure on file I/O errors)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 10. Add reproducibility and seeding support

  - [x] 10.1 Implement seeding infrastructure

    - Add seed parameter to augment_image MCP tool (optional)
    - Create seed management utilities for consistent random state
    - Set numpy.random.seed and random.seed before transform application
    - Add seed to processing metadata and logs for debugging
    - _Requirements: 7.1, 7.2, 7.5_

  - [x] 10.2 Enhance transform reproducibility
    - Ensure Albumentations transforms use consistent random state
    - Add seed validation and range checking (0 to 2^32-1)
    - Document seeding behavior in tool descriptions
    - Add seed to verification reports for debugging
    - _Requirements: 1.1, 1.2, 7.1, 7.2_

- [x] 11. Complete hook system testing

  - [x] 11.1 Test individual hook implementations

    - Write unit tests for pre_transform hook (image/config validation)
    - Write unit tests for post_transform hook (metadata generation)
    - Write unit tests for post_transform_verify hook (visual verification)
    - Write unit tests for pre_save hook (filename/directory management)
    - Write unit tests for post_save hook (cleanup and completion)
    - Test hook error handling and graceful failure modes
    - _Requirements: 3.3, 3.4, 3.5, 3.7, 3.8, 8.1, 8.2_

  - [x] 11.2 Test hook system integration
    - Test complete hook pipeline execution (all 8 stages)
    - Test hook failure recovery and pipeline continuation
    - Test hook context passing and metadata accumulation
    - Test hook registry management and dynamic registration
    - Verify hook execution order and dependencies
    - _Requirements: 3.1, 3.2, 3.9_

- [x] 12. Robust Error Handling & Edge Cases

  - [x] 12.1 Input validation edge cases

    - Invalid/corrupted Base64 images
    - Extremely large images (memory limits)
    - Unsupported image formats
    - Malformed natural language prompts
    - _Requirements: 7.1, 7.2, 7.4_

  - [x] 12.2 Transform failure recovery
    - Parameter out of range handling
    - Albumentations library errors
    - Memory exhaustion during processing
    - Graceful degradation strategies
    - _Requirements: 7.4, 7.5_

- [x] 13. Add CLI demo and development tools

  - [x] 13.1 Create CLI demo interface

    - Add `python -m albumentations_mcp.demo` command
    - Support `--image examples/cat.jpg --prompt "add blur"`
    - Add `--seed` parameter for reproducible demos
    - Create example images and demo scripts
    - _Requirements: 1.1, 1.2, 2.1, 2.2_

  - [x] 13.2 Add preset pipeline support
    - Create preset configurations: "segmentation", "portrait", "lowlight"
    - Add `--preset` parameter to CLI and MCP tools
    - Define YAML/JSON preset format
    - Include preset documentation and examples
    - _Requirements: 1.1, 1.4, 2.1, 2.2_

- [x] 14. Code Review and Quality Improvements

  - [x] 14.1 Fix Kiro IDE hooks (if possible)

    - Investigate why `.kiro/hooks/*.kiro.hook` files are not executing
    - Test hook trigger conditions and syntax
    - Try alternative hook configurations or formats
    - Document findings - this may be an IDE setup issue that cannot be resolved
    - Create manual quality checklist as fallback if hooks cannot be fixed

  - [x] 14.2 Code duplication analysis

    - Search for repeated code patterns across all modules
    - Identify common utility functions that could be extracted
    - Look for similar validation logic, error handling patterns, logging calls
    - Create `src/albumentations_mcp/utils.py` if significant duplication found
    - Focus on: image validation, parameter sanitization, error formatting, file operations
    - _Requirements: 4.1, 4.2_

  - [x] 14.3 Function complexity review

    - Identify functions with high cyclomatic complexity (>10)
    - Break down large functions into smaller, focused utilities
    - Look for functions doing multiple responsibilities
    - Extract complex conditional logic into helper functions
    - Focus on: parser.py, processor.py, validation.py, hooks modules
    - _Requirements: 4.1, 4.2_

  - [x] 14.4 Error handling consistency

    - Review exception handling patterns across modules
    - Standardize error message formats and logging levels
    - Ensure proper exception chaining with `raise ... from e`
    - Add missing error context and recovery information
    - Focus on: graceful degradation, user-friendly error messages
    - _Requirements: 7.4, 7.5_

  - [x] 14.5 Type hints and documentation review

    - Update to modern Python type hints (dict vs Dict, list vs List)
    - Ensure all public functions have proper docstrings
    - Add missing type hints for complex return types
    - Review and improve existing docstring quality
    - Focus on: API clarity, parameter descriptions, return value documentation
    - _Requirements: 4.1, 4.2_

  - [x] 14.6 Performance and memory optimization

    - Identify potential memory leaks or inefficient operations
    - Review large data structure handling (images, transform lists)
    - Look for unnecessary object creation or copying
    - Optimize hot paths in image processing pipeline
    - Focus on: image processing, hook execution, file I/O operations
    - _Requirements: 7.1, 7.2_

  - [x] 14.7 Security and input validation review

    - Review all user input validation and sanitization
    - Check for potential injection vulnerabilities
    - Ensure safe file path handling and temporary file cleanup
    - Review regex patterns for ReDoS vulnerabilities
    - Focus on: Base64 handling, file operations, parameter validation
    - _Requirements: 7.1, 7.2_

  - [x] 14.8 Testing gaps analysis
    - Identify untested or under-tested code paths
    - Add tests for edge cases and error conditions
    - Improve test coverage for new preset and CLI functionality
    - Add integration tests for complete workflows
    - Focus on: preset system, CLI demo, error recovery, hook integration
    - _Requirements: 4.1, 4.2_

- [x] 15. Prepare for PyPI publishing

  - [x] 15.1 Create comprehensive documentation

    - Write detailed README.md with installation and usage examples
    - Add API documentation with examples for all MCP tools
    - Create preset and CLI usage guides
    - Document seeding and reproducibility features
    - Add MCP client setup guides with screenshots
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [x] 15.2 Finalize package distribution
    - Add MIT LICENSE file
    - Test package build with `uv build`
    - Test local installation and verify all entry points work
    - Validate `uvx albumentations-mcp` command functionality
    - Create GitHub repository with proper CI/CD setup
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 11.1, 11.2, 11.3, 11.4_

- [x] 16. Fix remaining test failures

  - [x] 16.1 Fix image utils test expectations

    - Update test expectations for enhanced error message formats
    - Fix large image validation test to expect security validation errors
    - _Requirements: 7.1, 7.2_

  - [x] 16.2 Fix hook system validation warnings

    - Debug hook validation logic for image size, blur, rotation, and probability warnings
    - Verify hook validation thresholds are correct
    - Update hook exception handling tests for improved error recovery
    - _Requirements: 3.3, 3.4, 3.5_

  - [x] 16.3 Fix recovery system data types

    - Fix recovery system to return correct data types instead of tuples
    - Debug progressive fallback recovery logic
    - Update mock setups for new memory recovery manager integration
    - _Requirements: 7.4, 7.5_

  - [x] 16.4 Fix validation edge cases
    - Debug punctuation ratio calculation in validation
    - Verify file path generation behavior (relative vs absolute paths)
    - Fix memory limit exceeded test mock setup
    - _Requirements: 7.3, 7.4_

- [x] 17. Implement MCP prompts and resources

  - [x] 17.1 Add MCP prompt templates

    - Create @mcp.prompt() decorators for structured prompt templates
    - Implement `compose_preset(base, tweak_note?, format=json)` prompt that returns a policy skeleton based on presets with optional tweaks
    - Add `explain_effects(pipeline_json, image_context?)` prompt for plain-English critique/summary of any pipeline
    - Implement augmentation_parser prompt for natural language parsing
    - Add vision_verification prompt for image comparison analysis
    - Add error_handler prompt for user-friendly error messages
    - _Requirements: 1.1, 1.4, 8.1, 8.2, 9.1, 9.2_

  - [x] 17.2 Add MCP resources
    - Add @mcp.resource() for `transforms_guide` - JSON of supported transforms, defaults, and parameter ranges (auto-generated from the parser)
    - Add @mcp.resource() for `policy_presets` - JSON of built-in presets: segmentation, portrait, lowlight
    - Add resource for available transforms with examples
    - Create resource for preset pipelines and best practices
    - Add resource for troubleshooting common issues
    - _Requirements: 2.1, 2.2, 11.1, 11.2_

- [x] 19. Implement comprehensive testing and quality tools

  - [x] 19.1 Expand test coverage for remaining components

    - Write unit tests for verification system
    - Add integration tests for complete MCP tool workflows
    - Create tests for CLI demo and preset functionality
    - Add performance and memory usage tests
    - _Requirements: 4.1, 4.2_

  - [x] 19.2 Set up quality assurance automation
    - Configure pre-commit hooks with black, ruff, and mypy
    - Set up pytest with coverage reporting
    - Add type checking and linting to CI pipeline
    - Create quality gates for code commits
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 23. Fix Claude base64 conversion crash issue

  - [x] 23.1 Modify augment_image tool signature

    - Change signature from `augment_image(image_b64: str, prompt: str, ...)` to `augment_image(image_path: str, prompt: str, output_dir: str = None, ...)`
    - Update tool description and parameter documentation
    - Add file path validation and existence checking
    - Maintain backward compatibility by detecting input type (base64 vs file path)
    - _Requirements: 1.1, 1.2, 7.1, 7.2_

  - [x] 23.2 Update internal processing pipeline

    - Modify image loading to work with file paths using existing conversion functions
    - Update hook system to handle file path inputs
    - Ensure all existing augmentation pipeline and hooks remain intact
    - Add proper error handling for file access issues
    - _Requirements: 7.1, 7.2, 3.1, 3.2_

  - [x] 23.3 Implement dual input mode support

    - Add input type detection (base64 string vs file path)
    - Maintain full backward compatibility for direct API usage
    - Support both `image_b64` and `image_path` parameters with automatic detection
    - Add validation for both input types
    - _Requirements: 1.1, 1.2, 7.1, 7.2_

  - [x] 23.4 Update output handling

    - Change return format from base64 data to success message with output file path
    - Add `output_dir` parameter for specifying where to save results
    - Create default output directory structure if not specified
    - Include metadata about saved files in response
    - _Requirements: 5.4, 10.1, 10.2_

  - [x] 23.5 Comprehensive testing and validation

    - Update all existing tests to cover both file path and base64 input modes
    - Add new tests specifically for file path processing
    - Test error handling for missing files, invalid paths, permission issues
    - Verify all MCP tools still work correctly after changes
    - Run complete test suite: `uv run pytest -v`
    - _Requirements: 4.1, 4.2_

  - [x] 23.6 Documentation and resource cleanup

    - Update README.md with new file path usage examples
    - Update MCP tool descriptions and parameter documentation
    - Add examples showing both base64 and file path usage
    - Document output directory structure and file naming conventions
    - Add resource cleanup procedures for temporary files
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [x] 23.7 Integration testing and verification
    - Test with actual MCP clients to verify Claude integration works
    - Verify file path mode prevents base64 conversion crashes
    - Test with various image sizes and formats
    - Ensure all existing functionality (presets, seeding, hooks) works with file paths
    - Validate resource cleanup after processing
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

### 🚀 FUTURE ROADMAP - ADVANCED FEATURES (v0.3+)

- [ ] 28. GPU acceleration and advanced processing

  - [ ] 28.1 GPU/CUDA support

    - Add CUDA detection and device management
    - Implement GPU-accelerated Albumentations transforms
    - Add GPU memory management and fallback to CPU
    - _Requirements: 7.1, 7.2_

  - [ ] 28.2 Classification consistency checking
    - Implement post_transform_classify hook (8th hook)
    - Add support for MobileNet and CNN explainer models
    - Create classification drift detection and reporting
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [ ] 29. Advanced user features

  - [ ] 29.1 Custom preset system

    - Allow users to create and save custom presets
    - Add preset sharing and import/export functionality
    - Implement preset validation and testing
    - _Requirements: 1.1, 1.4, 2.1, 2.2_

  - [ ] 29.2 Advanced analytics and monitoring
    - Add detailed performance metrics and profiling
    - Implement quality assessment and drift detection
    - Create comprehensive reporting and visualization
    - _Requirements: 8.1, 8.2, 9.1, 9.2_

## PyPI Package Structure

```
albumentations-mcp/                    # Project root
├── pyproject.toml                     # Package metadata & dependencies
├── README.md                          # Documentation
├── LICENSE                            # MIT license
├── src/                              # Source code directory
│   └── albumentations_mcp/           # Your package
│       ├── __init__.py               # Package initialization
│       ├── __main__.py               # Entry point for uvx
│       ├── server.py                 # Main MCP server & tools
│       ├── parser.py                 # Natural language parsing
│       ├── image_utils.py            # Image processing utilities
│       ├── processor.py              # Image processing logic
│       ├── hooks/                    # Hook system (Python files)
│       │   ├── __init__.py           # Hook registry
│       │   ├── vision_verify.py     # Vision verification hook
│       │   ├── classification.py    # Classification hook
│       │   └── metadata_logger.py   # Metadata logging hook
│       ├── prompts/                  # MCP prompt templates
│       │   ├── __init__.py           # Prompt registry
│       │   ├── augmentation_parser.py    # Natural language parsing prompts
│       │   ├── vision_verification.py   # Image comparison prompts
│       │   ├── classification_reasoning.py  # Consistency analysis prompts
│       │   └── error_handler.py     # User-friendly error prompts
│       └── resources/                # MCP resources (optional)
│           ├── __init__.py           # Resource registry
│           ├── transforms_guide.py  # Available transforms documentation
│           ├── best_practices.py    # Augmentation best practices
│           └── troubleshooting.py   # Common issues and solutions
└── tests/                            # Test files
    ├── test_server.py
    ├── test_hooks.py
    └── fixtures/
        └── sample_images/
```

## Entry Point Structure

**`src/albumentations_mcp/__main__.py`** (for `uvx albumentations-mcp`):

```python
#!/usr/bin/env python3
"""CLI entry point for albumentations-mcp server."""

import sys
from .server import main

if __name__ == "__main__":
    sys.exit(main())
```

**`src/albumentations_mcp/server.py`** (main MCP server):

```python
from mcp.server.fastmcp import FastMCP
from .parser import parse_prompt
from .image_utils import base64_to_pil, pil_to_base64
from .hooks import HookRegistry

mcp = FastMCP("albumentations-mcp")
hook_registry = HookRegistry()

@mcp.tool()
def augment_image(image_b64: str, prompt: str) -> str:
    """Apply image augmentations based on natural language prompt."""
    # Implementation with hook integration
    pass

@mcp.prompt()
def augmentation_parser(user_prompt: str, available_transforms: list) -> str:
    """Parse natural language into Albumentations transforms."""
    # Return structured prompt template for parsing
    pass

@mcp.resource()
def transforms_guide() -> str:
    """Available transforms documentation with examples."""
    # Return comprehensive transform documentation
    pass

def main():
    """Main entry point for the MCP server."""
    mcp.run("stdio")

if __name__ == "__main__":
    main()
```

**`pyproject.toml`** configuration:

```toml
[project.scripts]
albumentations-mcp = "albumentations_mcp.__main__:main"

[project.entry-points."console_scripts"]
albumentations-mcp = "albumentations_mcp.__main__:main"
```

This structure enables:

- `uv add albumentations-mcp` (PyPI installation)
- `uvx albumentations-mcp` (direct execution)
- Proper Python package imports and distribution
- Full MCP protocol support with tools, prompts, and resources

## 🔮 BETA v0.2 TASKS - ADVANCED FEATURES

### Hook System Enhancement

- [ ] **Hook Toggle System**

  - Add environment variables for individual hook control (ENABLE_PRE_TRANSFORM, ENABLE_POST_SAVE, etc.)
  - Implement hook registry filtering based on environment settings
  - Add runtime hook enable/disable via MCP tool
  - Update documentation with hook configuration examples

- [ ] **Complete 8-Stage Hook System**

  - [ ] Implement pre_transform hook (image validation, size checks)
  - [ ] Implement post_transform hook (metadata generation)
  - [ ] Implement post_transform_classify hook (classification consistency)
  - [ ] Implement pre_save hook (file management, versioning)
  - [ ] Implement post_save hook (cleanup, completion logging)
  - [ ] Register all hooks in pipeline with proper error handling

- [ ] **Custom Hook Framework**
  - Add hook development documentation
  - Create hook template generator
  - Implement hook priority system
  - Add hook dependency management

### Advanced Features

- [ ] **User-Defined Presets**

  - Allow users to create custom preset configurations
  - Add preset validation and error handling
  - Implement preset sharing/export functionality

- [ ] **Batch Processing**

  - Add batch_augment_images MCP tool
  - Implement efficient memory management for multiple images
  - Add progress tracking and cancellation support

- [ ] **Performance Optimizations**
  - Implement image caching for repeated operations
  - Add async processing for independent transforms
  - Optimize memory usage for large images

### Developer Experience

- [ ] **Enhanced CLI**

  - Add interactive mode for testing transforms
  - Implement batch processing via CLI
  - Add preset management commands

- [ ] **Advanced Debugging**
  - Add hook execution tracing
  - Implement performance profiling tools
  - Add visual diff tools for before/after comparison

## 🔧 BETA v0.2 - ENHANCED IMAGE HANDLING

- [x] 24. Implement automatic image size handling and comprehensive temp cleanup

  **Problem**: Current PreTransformHook only warns about oversized images but doesn't fix them, causing pipeline failures. PostSaveHook only cleans temp files matching session_id patterns, leaving orphaned files from pasted images.

  **Solution**: Enhance PreTransformHook to auto-resize oversized images and improve PostSaveHook to comprehensively clean all temporary files within proper session directory structure.

  - [x] 24.1 Enhance PreTransformHook with auto-resize capability

    - Add automatic downscaling in PreTransformHook when image exceeds MAX_IMAGE_SIZE (default: 4096px largest dimension)
    - Preserve aspect ratio using LANCZOS filter for high-quality downscaling
    - Save resized copy to `session_dir/tmp/` directory following proper session structure
    - Log comprehensive metadata: original_dimensions, resized_dimensions, resize_applied=True, resize_reason
    - Add STRICT_MODE environment variable: when true, reject oversized images with error instead of resizing
    - Make MAX_IMAGE_SIZE configurable via environment variable
    - Add hard checks for MAX_PIXELS_IN (e.g., 16_000_000) and MAX_BYTES_IN (e.g., 50_000_000) in addition to MAX_IMAGE_SIZE (max side).
    - Normalize EXIF orientation and convert to RGB BEFORE measuring/resizing.
    - Preserve source format on save (JPEG→JPEG with quality=85/optimize; PNG→PNG; WEBP→WEBP lossless when supported). Avoid forcing PNG.
    - Log: resize_applied, original_wxh, original_bytes, resized_wxh, resized_bytes, reason, limits.

    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_

  - [x] 24.2 Fix session directory structure for temporary files

    - Ensure all temporary files from URLs/pasted images are saved in correct session directory format
    - Update file saving logic to use `outputs/YYYYMMDD_HHMMSS_sessionID/tmp/` structure
    - Modify URL/paste image handling to follow proper session directory conventions
    - Add validation to ensure temp files are created in session-specific directories
    - Route ALL derived temps (pasted/url downloads, EXIF-fix copies, resized copies) into session_dir/tmp/.
    - Maintain context.temp_paths: list[str] of every temp created during the run.
    - Guard against path traversal and symlinks: reject absolute outside session_dir and any '..' segments or symlinked inputs.

    - _Requirements: 13.1, 13.2_

  - [x] 24.3 Enhance PostSaveHook comprehensive temp cleanup

    - Extend `_cleanup_temporary_resources` to track all temp files/directories created during processing
    - Remove dependency on session_id pattern matching for cleanup
    - Implement comprehensive cleanup that handles all temporary files regardless of naming pattern
    - Confine cleanup operations to session-specific temp directories only
    - Add detailed logging of cleanup results including files removed, directories removed, and warnings
    - Ensure `session_dir/tmp/` is empty or removed after processing
    - Never touch user original files during cleanup
    - Cleanup uses ONLY context.temp_paths (do not glob by session_id).
    - Delete files/dirs listed; then remove session_dir/tmp/ if empty.
    - Never touch user originals or any path outside session_dir.
    - Log counts: files_removed, dirs_removed, warnings.
    - _Requirements: 13.3, 13.4, 13.5, 13.6, 13.7, 13.8_

  - [x] 24.4 Add comprehensive testing for image size handling

    - Add test: oversized image (>4096px) automatically resizes and augmentation continues
    - Add test: STRICT_MODE=true rejects oversized image with clear error message
    - Add test: resized image maintains aspect ratio and uses proper temp directory
    - Add test: original input files are preserved and never modified
    - Add test: MAX_IMAGE_SIZE configuration works correctly
    - Oversize by pixels (e.g., 9000×2000) and by bytes (high-quality JPEG).
    - EXIF-rotated portrait → verify orientation corrected, aspect preserved.
    - WEBP input preserved as WEBP (when resized).
    - Corrupted image raises clean error.
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_

  - [x] 24.5 Add comprehensive testing for temp cleanup

    - Add test: pasted image temp files are cleaned after processing
    - Add test: URL-loaded image temp files are cleaned after processing
    - Add test: session_dir/tmp/ is empty or removed after processing
    - Add test: user original files are never touched during cleanup
    - Add test: cleanup works regardless of temp file naming patterns
    - Add test: cleanup logs provide detailed information about removed files
    - Pasted image temp + resized temp → both removed; session_dir/tmp/ gone or empty.
    - Concurrent sessions: ensure each session cleans only its own tmp/.
    - Symlink input: rejected; no cleanup outside session tree.
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8_

  - [x] 24.6 Environment variable configuration

    - Add STRICT_MODE environment variable (default: false)
    - Add MAX_IMAGE_SIZE environment variable (default: 4096)
    - Add documentation for new environment variables
    - Add validation for environment variable values
    - _Requirements: 12.5, 12.6, 12.7_

  **Acceptance Criteria**:

  - Large internet images (>10MB, >8K pixels) automatically resize, process successfully, and leave no orphaned temp folders
  - STRICT_MODE correctly rejects oversized images with helpful error messages
  - After processing, `session_dir/tmp/` directory is empty or removed
  - All temporary files follow proper session directory structure
  - User original files are never modified or deleted
  - Comprehensive logging provides visibility into resize and cleanup operations
  - Logs include: resize_applied, original_wxh, original_bytes, resized_wxh, resized_bytes, reason, limits.
  - Non-whitelisted formats rejected with explicit hint.
  - No path outside session_dir is ever deleted; originals never modified.

## Summary

This task list reflects the current state of the albumentations-mcp project, which is already in **Beta v0.1.0b3** and published on PyPI. The project has achieved significant milestones:

### ✅ Current Status

- **Core Functionality**: Complete and working (7 MCP tools, 3 MCP prompts)
- **Hook System**: All 7 stages implemented and active
- **Test Coverage**: 97% (383/394 tests passing)
- **PyPI Package**: Published and available for installation
- **Documentation**: Comprehensive README and API documentation

### 🔧 Immediate Priorities

1. **Fix Test Failures**: Address the remaining 11 test failures to achieve 100% pass rate
2. **Performance Optimization**: Optimize processing pipeline for MCP client timeout requirements
3. **Resource Management**: Improve temporary file cleanup and session management

### 🚀 Next Release (v0.2)

- Enhanced configuration management with environment variables
- Batch processing capabilities
- Performance optimizations for large images
- Individual hook toggles

The project demonstrates production-ready system design with comprehensive MCP protocol compliance, extensible hook architecture, and robust error handling. The focus now shifts from initial development to refinement and advanced features.

**For developers**: The spec is complete and ready for task execution. Open the tasks.md file and click "Start task" next to any remaining task items to begin implementation.
