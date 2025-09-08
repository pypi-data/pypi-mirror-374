"""
MarkItDown Handler for MCP Server
Handles document conversion to markdown format - supports both single file and batch directory conversion
Enhanced with filtering, recursive scanning, and custom output directory
"""
import os
from typing import List, Dict, Any, Set
from pathlib import Path
from lgedv.modules.config import setup_logging
from urllib.parse import urlparse



logger = setup_logging()

class MarkItDownHandler:
    """Handler for document conversion using markitdown"""
    
    def __init__(self):
        self.supported_schemes = ['http:', 'https:', 'file:', 'data:']
        self.supported_extensions = {
            '.pdf', '.docx', '.doc', '.pptx', '.ppt', 
            '.xlsx', '.xls', '.rtf', '.odt', '.odp', '.ods'
        }
        
    async def handle_convert_markitdown(self, arguments: Dict[str, Any]) -> List[Dict]:
        """
        Convert document(s) to markdown using markitdown
        Supports both single URI and directory batch conversion with advanced options
        
        Args:
            arguments: Dict containing either:
                - 'uri': Single file URI
                - 'dir': Directory path for batch conversion
                - 'file': Single file path with 'output' directory
                - 'ext': Comma-separated extensions to filter (e.g., "pdf,docx")
                - 'recursive': Boolean to scan subdirectories
                - 'output': Custom output directory path
            
        Returns:
            List[Dict]: Conversion results
        """
        try:
            # Nếu có uri và output (và có thể có name)
            if 'uri' in arguments and 'output' in arguments:
                result = await self.convert_uri_to_output(
                    uri=arguments['uri'],
                    output_dir=arguments['output'],
                    name=arguments.get('name')
                )
                return [result]            
            
            # Nếu là batch directory
            if 'dir' in arguments:
                return await self._handle_directory_conversion(
                    dir_path=arguments['dir'],
                    extensions_filter=arguments.get('ext'),
                    recursive=arguments.get('recursive', False),
                    output_dir=arguments.get('output')
                )
            
            # Single file conversion (existing logic)
            uri = arguments.get('uri')
            if not uri:
                return [{"error": "Either 'uri', 'dir', or 'file' parameter is required"}]
            
            return await self._convert_single_file(uri)
                
        except Exception as e:
            logger.error(f"Error in convert_markitdown: {e}")
            return [{"error": f"Conversion failed: {str(e)}"}]
    
    def _parse_extensions_filter(self, ext_param: str) -> Set[str]:
        """
        Parse extension filter parameter
        
        Args:
            ext_param: Comma-separated extensions (e.g., "pdf,docx,pptx")
            
        Returns:
            Set[str]: Normalized extensions with dots (e.g., {'.pdf', '.docx', '.pptx'})
        """
        if not ext_param:
            return self.supported_extensions
        
        extensions = set()
        for ext in ext_param.split(','):
            ext = ext.strip().lower()
            if not ext.startswith('.'):
                ext = '.' + ext
            if ext in self.supported_extensions:
                extensions.add(ext)
            else:
                logger.warning(f"Unsupported extension: {ext}")
        
        return extensions if extensions else self.supported_extensions
    
    def _find_supported_files(self, dir_path: str, extensions: Set[str], recursive: bool) -> List[Path]:
        """
        Find all supported files in directory
        """
        supported_files = []
        logger.info(f"DEBUG: dir_path={dir_path}, extensions={extensions}, recursive={recursive}")

        if recursive:
            for ext in extensions:
                pattern = f"**/*{ext}"
                logger.info(f"DEBUG: Searching with pattern: {pattern}")
                found = list(Path(dir_path).glob(pattern))
                logger.info(f"DEBUG: Found {len(found)} files for {ext}: {[str(f) for f in found]}")
                supported_files.extend(found)
        else:
            for file_path in Path(dir_path).iterdir():
                if file_path.is_file() and file_path.suffix.lower() in extensions:
                    supported_files.append(file_path)
            logger.info(f"DEBUG: Non-recursive found: {[str(f) for f in supported_files]}")

        logger.info(f"DEBUG: Total supported_files: {len(supported_files)}")
        return sorted(supported_files)
    
    async def _handle_directory_conversion(self, dir_path: str, extensions_filter: str = None, 
                                         recursive: bool = False, output_dir: str = None) -> List[Dict]:
        """
        Convert all supported documents in a directory to markdown files with advanced options
        
        Args:
            dir_path: Path to directory containing documents
            extensions_filter: Comma-separated extensions to filter
            recursive: Whether to scan subdirectories recursively
            output_dir: Custom output directory (if None, output to same directory as input)
            
        Returns:
            List[Dict]: Batch conversion results
        """
        try:
            if not os.path.exists(dir_path):
                return [{"error": f"Directory does not exist: {dir_path}"}]
            
            if not os.path.isdir(dir_path):
                return [{"error": f"Path is not a directory: {dir_path}"}]
            
            # Import markitdown
            try:
                from markitdown import MarkItDown
            except ImportError:
                return [{"error": "markitdown library not installed. Run: pip install markitdown[all]"}]
            
            # Parse extensions filter
            allowed_extensions = self._parse_extensions_filter(extensions_filter)
            logger.info(f"Filtering by extensions: {sorted(allowed_extensions)}")
            
            # Validate and create output directory if specified
            if output_dir:
                output_dir = os.path.abspath(output_dir)
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Output directory: {output_dir}")
            
            md_converter = MarkItDown()
            results = []
            converted_count = 0
            error_count = 0
            
            # Find all supported files
            supported_files = self._find_supported_files(dir_path, allowed_extensions, recursive)
            
            if not supported_files:
                return [{
                    "success": True,
                    "message": f"No supported document files found in {dir_path}",
                    "search_config": {
                        "recursive": recursive,
                        "extensions": sorted(allowed_extensions),
                        "output_dir": output_dir
                    },
                    "converted_count": 0,
                    "error_count": 0
                }]
            
            logger.info(f"Found {len(supported_files)} files (recursive={recursive})")
            
            # Convert each file
            for file_path in supported_files:
                try:
                    # Determine output path
                    if output_dir:
                        # Preserve relative directory structure in output
                        rel_path = os.path.relpath(file_path, dir_path)
                        output_file_path = Path(output_dir) / Path(rel_path).with_suffix('.md')
                        # Create subdirectories if needed
                        output_file_path.parent.mkdir(parents=True, exist_ok=True)
                    else:
                        # Output to same directory as input
                        output_file_path = file_path.with_suffix('.md')
                    
                    logger.info(f"Converting: {file_path} -> {output_file_path}")
                    result = md_converter.convert(str(file_path))
                    
                    if result and hasattr(result, 'text_content'):
                        # Write markdown content to file
                        with open(output_file_path, 'w', encoding='utf-8') as f:
                            f.write(result.text_content)
                        
                        converted_count += 1
                        results.append({
                            "success": True,
                            "input_file": str(file_path),
                            "output_file": str(output_file_path),
                            "relative_path": os.path.relpath(str(file_path), dir_path),
                            "content_length": len(result.text_content),
                            "message": f"Converted {file_path.name} -> {output_file_path.name}"
                        })
                        
                    else:
                        error_count += 1
                        results.append({
                            "success": False,
                            "input_file": str(file_path),
                            "relative_path": os.path.relpath(str(file_path), dir_path),
                            "error": "No content returned from conversion"
                        })
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error converting {file_path}: {e}")
                    results.append({
                        "success": False,
                        "input_file": str(file_path),
                        "relative_path": os.path.relpath(str(file_path), dir_path),
                        "error": str(e)
                    })
            
            # Add comprehensive summary
            summary = {
                "success": True,
                "batch_conversion": True,
                "directory": dir_path,
                "search_config": {
                    "recursive": recursive,
                    "extensions": sorted(allowed_extensions),
                    "output_dir": output_dir
                },
                "total_files_found": len(supported_files),
                "converted_count": converted_count,
                "error_count": error_count,
                "results": results,
                "message": f"Batch conversion completed: {converted_count} successful, {error_count} errors"
            }
            
            return [summary]
            
        except Exception as e:
            logger.error(f"Error in directory conversion: {e}")
            return [{"error": f"Directory conversion failed: {str(e)}"}]
    
    async def _convert_single_file(self, uri: str) -> List[Dict]:
        """
        Convert single file (existing logic)
        
        Args:
            uri: File URI to convert
            
        Returns:
            List[Dict]: Single file conversion result
        """
        # Validate URI scheme
        if not any(uri.startswith(scheme) for scheme in self.supported_schemes):
            return [{"error": f"Unsupported URI scheme. Supported: {', '.join(self.supported_schemes)}"}]
        
        # Import markitdown
        try:
            from markitdown import MarkItDown
        except ImportError:
            return [{"error": "markitdown library not installed. Run: pip install markitdown[all]"}]
        
        # Convert document
        md = MarkItDown()
        result = md.convert(uri)
        
        if result and hasattr(result, 'text_content'):
            markdown_content = result.text_content
            
            # Extract metadata if available
            metadata = {}
            if hasattr(result, 'title') and result.title:
                metadata['title'] = result.title
            if hasattr(result, 'source') and result.source:
                metadata['source'] = result.source
            
            return [{
                "success": True,
                "uri": uri,
                "markdown_content": markdown_content,
                "metadata": metadata,
                "content_length": len(markdown_content),
                "message": f"Successfully converted document from {uri}"
            }]
        else:
            return [{"error": "Failed to convert document - no content returned"}]

    
    async def convert_uri_to_output(self, uri: str, output_dir: str, name: str = None) -> dict:
        """
        Convert a URI (http/https/file/data) to markdown and save to output directory.
        Args:
            uri: Document URI (http/https/file/data)
            output_dir: Directory to save markdown file
            name: Optional file name for markdown output
        Returns:
            dict: Conversion result
        """
        # Validate URI scheme
        if not any(uri.startswith(scheme) for scheme in self.supported_schemes):
            return {"error": f"Unsupported URI scheme. Supported: {', '.join(self.supported_schemes)}"}
        
        try:
            from markitdown import MarkItDown
        except ImportError:
            return {"error": "markitdown library not installed. Run: pip install markitdown[all]"}
        
        md = MarkItDown()
        result = md.convert(uri)
        
        if result and hasattr(result, 'text_content'):
            # Xác định tên file markdown
            if name:
                file_name = name if name.endswith('.md') else name + '.md'
            else:
                parsed = urlparse(uri)
                path_parts = Path(parsed.path).parts
                if path_parts:
                    if path_parts[-1] == "index.html" and len(path_parts) > 1:
                        file_name = f"{path_parts[-2]}_index.md"
                    else:
                        file_name = Path(path_parts[-1]).with_suffix('.md').name
                else:
                    file_name = "output.md"
            
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / file_name
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
            
            return {
                "success": True,
                "uri": uri,
                "output_file": str(output_file),
                "content_length": len(result.text_content),
                "message": f"Successfully converted and saved to {output_file}"
            }
        else:
            return {"error": "Failed to convert document - no content returned"}
    
# Global instance
markitdown_handler = MarkItDownHandler()