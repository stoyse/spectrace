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
import re
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
        self.java_home = os.getenv('JAVA_HOME', self._detect_java_home())
        self.temp_dir = Path('/tmp/ghidra_projects')
        self.temp_dir.mkdir(exist_ok=True)
        
        # Validate Ghidra installation
        self.analyze_headless_path = Path(self.ghidra_install_dir) / 'support' / 'analyzeHeadless'
        if not self.analyze_headless_path.exists():
            logger.error(f"Ghidra analyzeHeadless not found at {self.analyze_headless_path}")
            raise RuntimeError("Ghidra installation not found or incomplete")
        
        # Ensure Ghidra user directory exists
        self._ensure_ghidra_user_directory()
    
    def _detect_java_home(self) -> str:
        """
        Detect Java installation path automatically.
        
        Returns:
            String path to Java home directory
        """
        # Common Java installation paths
        java_paths = [
            '/usr/local/openjdk-17',  # Docker OpenJDK
            '/usr/lib/jvm/java-17-openjdk-amd64',  # Ubuntu/Debian
            '/usr/lib/jvm/java-17-openjdk',  # Generic Linux
            '/usr/lib/jvm/default-java',  # Ubuntu default
            '/opt/java/openjdk',  # Alternative path
            '/System/Library/Frameworks/JavaVM.framework/Home',  # macOS
        ]
        
        # Try to use java command to find JAVA_HOME
        try:
            import subprocess
            result = subprocess.run(['java', '-XshowSettings:properties', '-version'], 
                                  capture_output=True, text=True, stderr=subprocess.STDOUT)
            for line in result.stdout.split('\n'):
                if 'java.home' in line:
                    java_home = line.split('=')[-1].strip()
                    if os.path.exists(java_home):
                        return java_home
        except Exception:
            pass
        
        # Check common paths
        for path in java_paths:
            if os.path.exists(path):
                return path
        
        # Fallback to empty string (will use system PATH)
        logger.warning("Could not detect JAVA_HOME, will rely on system PATH")
        return ""
    
    def _ensure_ghidra_user_directory(self):
        """
        Ensure Ghidra user directory exists with proper permissions.
        """
        try:
            # Get user home directory
            home_dir = Path.home()
            ghidra_user_dir = home_dir / '.ghidra' / '.ghidra_11.0.3_PUBLIC'
            
            # Create directory if it doesn't exist
            ghidra_user_dir.mkdir(parents=True, exist_ok=True)
            
            # Set proper permissions (readable and writable by user)
            os.chmod(ghidra_user_dir, 0o755)
            
            logger.info(f"Ghidra user directory ensured at: {ghidra_user_dir}")
            
        except Exception as e:
            logger.warning(f"Could not create Ghidra user directory: {str(e)}")
            # Don't raise an error, let Ghidra try to create it
    
    def _filter_stderr_output(self, stderr_str: str) -> str:
        """
        Filter out harmless stderr output from Ghidra/Java.
        
        Args:
            stderr_str: Raw stderr output
            
        Returns:
            Filtered stderr output containing only actual errors
        """
        if not stderr_str:
            return ""
        
        # Patterns to ignore (harmless informational output)
        ignore_patterns = [
            r"openjdk version.*",
            r"OpenJDK Runtime Environment.*",
            r"OpenJDK.*Server VM.*",
            r"WARNING:.*sun\.awt\.X11.*",
            r"WARNING:.*headless.*",
            r"INFO:.*",
            r"^$",  # Empty lines
        ]
        
        lines = stderr_str.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line matches any ignore pattern
            should_ignore = False
            for pattern in ignore_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    should_ignore = True
                    break
            
            if not should_ignore:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
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
import ghidra.program.model.symbol.*;
import ghidra.app.services.*;
import ghidra.app.util.importer.*;
import ghidra.app.cmd.function.*;
import ghidra.app.cmd.disassemble.*;
import java.io.FileWriter;
import java.io.IOException;

public class DecompileAll extends GhidraScript {
    
    @Override
    public void run() throws Exception {
        
        println("Starting C decompilation script...");
        
        // Output files - focus on C decompilation only
        FileWriter decWriter = new FileWriter("decompiled_output.txt");
        FileWriter metaWriter = new FileWriter("metadata_output.txt");
        FileWriter summaryWriter = new FileWriter("assembly_output.txt");  // Reuse this for summary
        
        try {
            Program program = currentProgram;
            
            if (program == null) {
                throw new Exception("No program loaded");
            }
            
            println("Program loaded: " + program.getName());
            
            // Write metadata
            metaWriter.write("Program: " + program.getName() + "\\n");
            metaWriter.write("Language: " + program.getLanguage().getLanguageID() + "\\n");
            metaWriter.write("Compiler: " + program.getCompilerSpec().getCompilerSpecID() + "\\n");
            metaWriter.write("Architecture: " + program.getLanguage().getProcessor() + "\\n");
            metaWriter.write("Address Size: " + program.getAddressFactory().getDefaultAddressSpace().getSize() + "\\n");
            
            // Get listing and memory blocks
            Listing listing = program.getListing();
            MemoryBlock[] blocks = program.getMemory().getBlocks();
            
            println("Found " + blocks.length + " memory blocks");
            
            // Force analysis if not already done
            AutoAnalysisManager mgr = AutoAnalysisManager.getAnalysisManager(program);
            if (!mgr.isAnalyzing()) {
                println("Starting auto-analysis...");
                mgr.startAnalysis(monitor);
                mgr.waitForAnalysis(null, monitor);
                println("Auto-analysis completed");
            }
            
            // Get all functions
            FunctionManager functionManager = program.getFunctionManager();
            Function[] functions = new Function[0];
            functions = functionManager.getFunctions(true).toArray(functions);
            
            println("Found " + functions.length + " functions");
            
            // Initialize decompiler
            DecompInterface decompiler = new DecompInterface();
            decompiler.openProgram(program);
            
            int processedFunctions = 0;
            int successfulDecompilations = 0;
            
            // Process all functions - focus on C decompilation only
            for (Function function : functions) {
                String functionName = function.getName();
                Address entryPoint = function.getEntryPoint();
                
                // Skip library functions and thunks to reduce noise
                if (function.isThunk() || function.isExternal()) {
                    continue;
                }
                
                // Decompile function to C
                try {
                    DecompileResults results = decompiler.decompileFunction(function, 60, monitor);
                    if (results.isValid()) {
                        String decompiledCode = results.getDecompiledFunction().getC();
                        if (decompiledCode != null && !decompiledCode.isEmpty()) {
                            decWriter.write("\\n// Function: " + functionName + " at " + entryPoint + "\\n");
                            decWriter.write(decompiledCode + "\\n\\n");
                            successfulDecompilations++;
                        }
                    } else {
                        println("Decompilation failed for " + functionName + ": " + results.getErrorMessage());
                    }
                } catch (Exception e) {
                    println("Decompilation error for " + functionName + ": " + e.getMessage());
                }
                
                processedFunctions++;
                if (processedFunctions % 20 == 0) {
                    println("Processed " + processedFunctions + " functions, " + successfulDecompilations + " successful decompilations...");
                }
            }
            
            // Write summary instead of assembly
            summaryWriter.write("=== Decompilation Summary ===\\n");
            summaryWriter.write("Total functions found: " + functions.length + "\\n");
            summaryWriter.write("Functions processed: " + processedFunctions + "\\n");
            summaryWriter.write("Successful decompilations: " + successfulDecompilations + "\\n");
            summaryWriter.write("Memory blocks: " + blocks.length + "\\n");
            
            // If no functions found, provide basic information
            if (functions.length == 0) {
                println("No functions found in binary");
                summaryWriter.write("\\nNo functions were identified in this binary.\\n");
                summaryWriter.write("This could indicate:\\n");
                summaryWriter.write("- Packed or obfuscated binary\\n");
                summaryWriter.write("- Non-standard binary format\\n");
                summaryWriter.write("- Stripped symbols\\n");
                
                decWriter.write("// No functions could be identified for decompilation\\n");
                decWriter.write("// Binary may be packed, obfuscated, or in non-standard format\\n");
                
                // Just list executable blocks for context
                for (MemoryBlock block : blocks) {
                    if (block.isExecute()) {
                        summaryWriter.write("Executable block: " + block.getName() + 
                                          " (" + block.getStart() + " - " + block.getEnd() + 
                                          ", size: " + block.getSize() + ")\\n");
                    }
                }
            }
            
            println("Decompilation completed successfully - processed " + processedFunctions + " functions");
            
        } finally {
            summaryWriter.close();
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
            '-scriptPath', str(project_dir),
            '-log', str(project_dir / 'ghidra.log'),
            '-deleteProject'  # Clean up automatically
        ]
        
        # Set environment variables
        env = os.environ.copy()
        if self.java_home:
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
                
                # Filter out harmless stderr output (Java version info, warnings)
                filtered_stderr = self._filter_stderr_output(stderr_str)
                
                # Determine success based on return code and actual error content
                # Ghidra sometimes returns non-zero codes even on success due to Java warnings
                success = return_code == 0 or (not filtered_stderr and "Decompilation completed successfully" in stdout_str)
                
                logger.info(f"Ghidra analysis completed with code {return_code}")
                if not success and filtered_stderr:
                    logger.error(f"Ghidra stderr: {filtered_stderr}")
                elif stderr_str and not filtered_stderr:
                    logger.debug(f"Ghidra info output: {stderr_str}")
                
                return success, stdout_str, filtered_stderr
                
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
                    asm_content = await f.read()
                    results['assembly_code'] = asm_content.strip()
                    logger.info(f"Assembly output: {len(asm_content)} characters")
            else:
                logger.warning(f"Assembly output file not found: {asm_file}")
            
            # Read decompiled output
            dec_file = project_dir / 'decompiled_output.txt'
            if dec_file.exists():
                async with aiofiles.open(dec_file, 'r', errors='replace') as f:
                    dec_content = await f.read()
                    results['decompiled_code'] = dec_content.strip()
                    logger.info(f"Decompiled output: {len(dec_content)} characters")
            else:
                logger.warning(f"Decompiled output file not found: {dec_file}")
            
            # Read metadata
            meta_file = project_dir / 'metadata_output.txt'
            if meta_file.exists():
                async with aiofiles.open(meta_file, 'r', errors='replace') as f:
                    metadata_content = await f.read()
                    logger.info(f"Metadata content: {metadata_content[:200]}...")
                    # Parse metadata content
                    for line in metadata_content.strip().split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            results['metadata'][key.strip().lower().replace(' ', '_')] = value.strip()
            else:
                logger.warning(f"Metadata output file not found: {meta_file}")
            
            # Check if we got any meaningful output
            if not results['assembly_code'] and not results['decompiled_code']:
                logger.warning("No assembly or decompiled code generated")
                # List files in project directory for debugging
                try:
                    files = [f.name for f in project_dir.iterdir()]
                    logger.info(f"Files in project directory: {files}")
                except Exception as e:
                    logger.error(f"Could not list project directory: {e}")
            
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