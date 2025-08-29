# Ghidra Integration Feature Plan

## Overview
This document outlines the integration plan for adding Ghidra decompilation capabilities to the Spectrace firmware security analysis platform.

## Current System Understanding
Spectrace is a FastAPI backend with React frontend for firmware vulnerability analysis that currently handles:
- Assembly/C code comparison between versions
- Specification analysis and compliance validation
- Security vulnerability detection (buffer overflows, hardcoded credentials, etc.)

## Integration Strategy

### Architecture Changes

#### 1. Frontend Binary Upload Enhancement
**File**: `dashboard/src/pages/Dashboard.tsx`

Add binary file upload support alongside existing text files:
- Extend `fileAccept` to include binary formats: `.bin`, `.hex`, `.elf`, `.exe`
- Add new state for binary files: `oldBinary`, `newBinary`
- Create "Binary Files" upload section in existing cards
- Support mixed workflow: binaries + specifications

#### 2. New Decompile Endpoint
**File**: `api/routes/code_routes.py`

```python
@router.post("/decompile", response_model=DecompileResponse)
async def decompile_binary(request: DecompileRequest):
    """
    Decompile binary files using Ghidra headless analyzer.
    
    Features:
    - Accept binary file upload (multipart/form-data)
    - Call Ghidra headless analyzer via subprocess
    - Return decompiled assembly/C code
    - Store results temporarily for analysis pipeline
    """
```

#### 3. Enhanced Analyzer Service
**File**: `api/services/ghidra_service.py` (new)

```python
class GhidraDecompiler:
    """
    Ghidra headless execution wrapper
    
    Responsibilities:
    - Ghidra headless execution wrapper
    - Binary format detection (ELF, PE, etc.)
    - Decompilation result parsing
    - Error handling and timeout management
    """
    
    async def decompile_binary(self, binary_path: str) -> str:
        # Execute: ghidra_headless.py project_dir project_name 
        #          -import binary_path -postscript decompile_all.py
```

#### 4. Modified Analysis Workflow

**Current Flow:**
```
Upload Text Files → Compare Code → Analyze
```

**New Flow:**
```
Upload Binary → /decompile → Get Text → Compare Code → Analyze
        OR
Upload Text Files → Compare Code → Analyze (unchanged)
```

## Detailed Implementation Plan

### Phase 1: Backend Infrastructure

1. **Install Ghidra Requirements**
   - Add Ghidra to `requirements.txt`
   - Docker container with Ghidra pre-installed
   - Java runtime dependencies

2. **Create Decompile Endpoint**
   ```python
   # api/routes/code_routes.py
   @router.post("/decompile")
   async def decompile_binary(file: UploadFile = File(...)):
       # Validate binary file
       # Save temporarily 
       # Execute Ghidra headless
       # Parse decompiled output
       # Return assembly/C code text
   ```

3. **Ghidra Service Implementation**
   - Sandboxed execution environment
   - Binary format auto-detection
   - Structured output parsing
   - Error handling for corrupted binaries

### Phase 2: Frontend Integration

1. **Update Dashboard Component**
   - Add binary upload sections
   - Progress indicator for decompilation step
   - Handle mixed binary/text workflows

2. **Modified Analysis Flow**
   ```typescript
   // Check if binary files uploaded
   if (binaryFiles.length > 0) {
       // Step 1: Decompile binaries
       const decompiled = await fetch('/api/v1/decompile', {...});
       // Use decompiled text for code comparison
   }
   // Continue with existing compare-code flow
   ```

## Technical Considerations

### Security & Performance
- **Sandboxed Execution**: Run Ghidra in isolated containers
- **File Size Limits**: Restrict binary uploads (e.g., 50MB max)
- **Timeout Handling**: Decompilation can be slow for large binaries
- **Temp File Cleanup**: Auto-delete uploaded binaries after processing

### Error Handling
- Unsupported binary formats
- Ghidra execution failures
- Malformed/corrupted binaries
- Resource exhaustion

### Schema Updates
```python
# api/schemas.py
class DecompileRequest(BaseModel):
    binary_data: bytes
    filename: str
    architecture: Optional[str] = None

class DecompileResponse(BaseModel):
    success: bool
    decompiled_code: str
    assembly_code: str
    metadata: dict
```

## Integration Points

1. **Dashboard.tsx:154-159** - Update `fileAccept` for binary formats
2. **Dashboard.tsx:41-152** - Modify `analyzeFiles()` function 
3. **code_routes.py:28** - Add decompile route before compare-code
4. **services/** - New `ghidra_service.py` module

## Benefits of This Approach

✅ **Maintains existing workflow** - Text files continue working unchanged  
✅ **Seamless integration** - Binaries become text, then use existing analysis  
✅ **Leverages current security detection** - Same vulnerability patterns apply  
✅ **Progressive enhancement** - Can implement incrementally  

## Implementation Notes

This plan transforms the current text-based firmware analysis into a comprehensive binary analysis platform while preserving all existing functionality. The integration follows the existing patterns in the codebase and maintains the current API structure.

## Ghidra Resources

- **GitHub Repository**: https://github.com/NationalSecurityAgency/ghidra
- **Headless Analyzer**: Use for automated binary processing
- **Supported Formats**: ELF, PE, Mach-O, and many embedded formats
- **Output Formats**: Assembly code, decompiled C, and metadata

## Next Steps

1. Set up Ghidra development environment
2. Create proof-of-concept decompile endpoint
3. Implement frontend binary upload support
4. Test with sample firmware binaries
5. Integrate with existing analysis pipeline
6. Add comprehensive error handling and validation

---

*Created: 2025-08-29*  
*Project: Spectrace - Firmware Security Analysis Platform*