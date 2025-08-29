"""
Ghidra Decompilation Service

This service provides binary decompilation functionality using Ghidra headless analyzer.
"""

import os
import subprocess
import tempfile
import asyncio
import shutil
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import aiofiles
from middleware.error_handler import GhidraErrorHandler

logger = logging.getLogger(__name__)

class GhidraDecompiler:
    """
    Ghidra headless decompilation service.
    
    Handles binary file decompilation using Ghidra's headless analyzer,
    providing both assembly and decompiled C code output.
    """
    
    def __init__(self):
        self.ghidra_install_dir = os.getenv('GHIDRA_INSTALL_DIR', '/opt/ghidra')
        self.java_home = os.getenv('JAVA_HOME', '/usr/lib/jvm/java-17-openjdk-amd64')
        self.temp_dir = Path('/tmp/ghidra_projects')
        self.temp_dir.mkdir(exist_ok=True)
        
        # Validate Ghidra installation
        self.analyze_headless_path = Path(self.ghidra_install_dir) / 'support' / 'analyzeHeadless'
        if not self.analyze_headless_path.exists():
            logger.error(f"Ghidra analyzeHeadless not found at {self.analyze_headless_path}")
            raise RuntimeError("Ghidra installation not found or incomplete")
    
    async def decompile_binary(self, binary_path: str, filename: str) -> Dict:
        """
        Decompile a binary file using Ghidra headless analyzer.
        
        Args:
            binary_path: Path to the binary file
            filename: Original filename for context
            
        Returns:
            Dictionary containing decompilation results:
            - success: Boolean indicating success/failure
            - assembly_code: Raw assembly disassembly
            - decompiled_code: High-level C decompilation
            - metadata: Additional information about the binary
            - error: Error message if decompilation failed
        """
        project_name = f"temp_project_{os.getpid()}"
        project_dir = self.temp_dir / project_name
        
        try:
            # Create temporary project directory
            project_dir.mkdir(exist_ok=True)
            
            # Create Ghidra script for decompilation
            script_path = await self._create_decompile_script(project_dir)
            
            # Run Ghidra headless analyzer
            success, output, error = await self._run_ghidra_analysis(
                project_dir, project_name, binary_path, script_path
            )
            
            if not success:
                return {
                    'success': False,
                    'error': f"Ghidra analysis failed: {error}",
                    'assembly_code': '',
                    'decompiled_code': '',
                    'metadata': {}
                }
            
            # Parse results
            results = await self._parse_results(project_dir, filename)
            results['success'] = True
            
            return results
            
        except Exception as e:
            logger.error(f"Decompilation error: {str(e)}")
            error_response = GhidraErrorHandler.handle_ghidra_error(e, "Binary decompilation")
            error_response.update({
                'assembly_code': '',
                'decompiled_code': '',
                'metadata': {}
            })
            return error_response
        finally:
            # Cleanup temporary files
            if project_dir.exists():
                shutil.rmtree(project_dir, ignore_errors=True)
    
    async def _create_decompile_script(self, project_dir: Path) -> Path:
        """Create a Ghidra script for decompilation."""
        script_content = '''
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import java.io.FileWriter;
import java.io.IOException;

public class DecompileAll extends GhidraScript {
    
    @Override
    public void run() throws Exception {
        
        // Output files
        FileWriter asmWriter = new FileWriter("assembly_output.txt");
        FileWriter decWriter = new FileWriter("decompiled_output.txt");
        FileWriter metaWriter = new FileWriter("metadata_output.txt");
        
        try {
            Program program = currentProgram;
            
            // Write metadata
            metaWriter.write("Program: " + program.getName() + "\\n");
            metaWriter.write("Language: " + program.getLanguage().getLanguageID() + "\\n");
            metaWriter.write("Compiler: " + program.getCompilerSpec().getCompilerSpecID() + "\\n");
            metaWriter.write("Architecture: " + program.getLanguage().getProcessor() + "\\n");
            metaWriter.write("Address Size: " + program.getAddressFactory().getDefaultAddressSpace().getSize() + "\\n");
            
            // Get listing for assembly output
            Listing listing = program.getListing();
            
            // Initialize decompiler
            DecompInterface decompiler = new DecompInterface();
            decompiler.openProgram(program);
            
            // Process all functions
            FunctionManager functionManager = program.getFunctionManager();
            for (Function function : functionManager.getFunctions(true)) {
                
                Address entryPoint = function.getEntryPoint();
                String functionName = function.getName();
                
                asmWriter.write("\\n=== Function: " + functionName + " ===\\n");
                decWriter.write("\\n=== Function: " + functionName + " ===\\n");
                
                // Get assembly listing for function
                AddressSetView body = function.getBody();
                for (Address addr : body.getAddresses(true)) {
                    CodeUnit codeUnit = listing.getCodeUnitAt(addr);
                    if (codeUnit != null) {
                        asmWriter.write(addr + ": " + codeUnit.toString() + "\\n");
                    }
                }
                
                // Decompile function
                try {
                    DecompileResults results = decompiler.decompileFunction(function, 30, monitor);
                    if (results.isValid()) {
                        decWriter.write(results.getDecompiledFunction().getC() + "\\n\\n");
                    } else {
                        decWriter.write("// Decompilation failed: " + results.getErrorMessage() + "\\n\\n");
                    }
                } catch (Exception e) {
                    decWriter.write("// Decompilation error: " + e.getMessage() + "\\n\\n");
                }
            }
            
            // Process remaining instructions not in functions
            AddressSetView definedData = listing.getDefinedData(true);
            if (!definedData.isEmpty()) {
                asmWriter.write("\\n=== Data Definitions ===\\n");
                for (Address addr : definedData.getAddresses(true)) {
                    Data data = listing.getDataAt(addr);
                    if (data != null) {
                        asmWriter.write(addr + ": " + data.toString() + "\\n");
                    }
                }
            }
            
            println("Decompilation completed successfully");
            
        } finally {
            asmWriter.close();
            decWriter.close();
            metaWriter.close();
        }
    }
}
'''
        
        script_path = project_dir / "DecompileAll.java"
        async with aiofiles.open(script_path, 'w') as f:
            await f.write(script_content)
        
        return script_path
    
    async def _run_ghidra_analysis(self, project_dir: Path, project_name: str, 
                                 binary_path: str, script_path: Path) -> Tuple[bool, str, str]:
        """Run Ghidra headless analysis."""
        
        cmd = [
            str(self.analyze_headless_path),
            str(project_dir),
            project_name,
            '-import', binary_path,
            '-postScript', str(script_path),
            '-deleteProject'  # Clean up automatically
        ]
        
        # Set environment variables
        env = os.environ.copy()
        env['JAVA_HOME'] = self.java_home
        env['PATH'] = f"{self.java_home}/bin:{env.get('PATH', '')}"
        
        try:
            # Run with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=project_dir
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5 minutes
                return_code = process.returncode
                
                stdout_str = stdout.decode('utf-8', errors='replace')
                stderr_str = stderr.decode('utf-8', errors='replace')
                
                success = return_code == 0
                
                logger.info(f"Ghidra analysis completed with code {return_code}")
                if not success:
                    logger.error(f"Ghidra stderr: {stderr_str}")
                
                return success, stdout_str, stderr_str
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return False, "", "Analysis timed out after 5 minutes"
                
        except Exception as e:
            logger.error(f"Failed to run Ghidra analysis: {str(e)}")
            return False, "", str(e)
    
    async def _parse_results(self, project_dir: Path, filename: str) -> Dict:
        """Parse Ghidra analysis results."""
        results = {
            'assembly_code': '',
            'decompiled_code': '',
            'metadata': {'filename': filename}
        }
        
        try:
            # Read assembly output
            asm_file = project_dir / 'assembly_output.txt'
            if asm_file.exists():
                async with aiofiles.open(asm_file, 'r', errors='replace') as f:
                    results['assembly_code'] = await f.read()
            
            # Read decompiled output
            dec_file = project_dir / 'decompiled_output.txt'
            if dec_file.exists():
                async with aiofiles.open(dec_file, 'r', errors='replace') as f:
                    results['decompiled_code'] = await f.read()
            
            # Read metadata
            meta_file = project_dir / 'metadata_output.txt'
            if meta_file.exists():
                async with aiofiles.open(meta_file, 'r', errors='replace') as f:
                    metadata_content = await f.read()
                    # Parse metadata content
                    for line in metadata_content.strip().split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            results['metadata'][key.strip().lower().replace(' ', '_')] = value.strip()
            
        except Exception as e:
            logger.error(f"Error parsing results: {str(e)}")
            results['metadata']['parse_error'] = str(e)
        
        return results

    def validate_binary_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate if the file is a supported binary format.
        
        Args:
            file_path: Path to the binary file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not os.path.exists(file_path):
                return False, "File does not exist"
            
            if os.path.getsize(file_path) == 0:
                return False, "File is empty"
            
            if os.path.getsize(file_path) > 100 * 1024 * 1024:  # 100MB limit
                return False, "File too large (max 100MB)"
            
            # Check file magic numbers for common binary formats
            with open(file_path, 'rb') as f:
                magic = f.read(16)
            
            # Common binary format magic numbers
            binary_magics = [
                b'\x7fELF',  # ELF
                b'MZ',       # PE/DOS
                b'\xfe\xed\xfa',  # Mach-O (32-bit)
                b'\xfe\xed\xfa\xce',  # Mach-O (64-bit)
                b'\xcf\xfa\xed\xfe',  # Mach-O (reverse)
                b'\xca\xfe\xba\xbe',  # Universal binary
            ]
            
            is_binary = any(magic.startswith(sig) for sig in binary_magics)
            
            if not is_binary:
                # Allow files without clear magic signatures (some embedded binaries)
                # but warn about potential issues
                return True, "File format not clearly identified, proceeding with caution"
            
            return True, "Valid binary file"
            
        except Exception as e:
            return False, f"Error validating file: {str(e)}"