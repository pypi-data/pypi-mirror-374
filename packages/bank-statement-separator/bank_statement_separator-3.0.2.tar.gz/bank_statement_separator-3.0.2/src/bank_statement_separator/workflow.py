"""LangGraph workflow definition for bank statement separation."""

from typing import Dict, Any, List, Optional, TypedDict
from dataclasses import dataclass
from langgraph.graph import StateGraph, END
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """State structure for the bank statement separation workflow."""

    # Input data
    input_file_path: str
    output_directory: str

    # Processing state
    pdf_document: Optional[Dict[str, Any]]  # PDFDocument as dict
    text_chunks: Optional[List[str]]
    detected_boundaries: Optional[List[Dict[str, Any]]]  # Statement boundaries
    extracted_metadata: Optional[List[Dict[str, Any]]]  # Account numbers, periods, etc.
    generated_files: Optional[List[str]]  # Output file paths
    processed_input_file: Optional[str]  # Path to moved input file
    paperless_upload_results: Optional[Dict[str, Any]]  # Paperless-ngx upload results

    # Workflow control
    current_step: str
    error_message: Optional[str]
    processing_complete: bool

    # Metrics and logging
    total_pages: int
    total_statements_found: int
    processing_time_seconds: Optional[float]
    confidence_scores: Optional[List[float]]
    validation_results: Optional[Dict[str, Any]]  # Output validation results
    skipped_fragments: Optional[int]  # Number of fragments skipped
    skipped_pages: Optional[int]  # Number of pages in skipped fragments


@dataclass
class StatementBoundary:
    """Represents a detected statement boundary."""

    start_page: int
    end_page: int
    confidence: float
    statement_type: Optional[str] = None
    account_number: Optional[str] = None
    statement_period: Optional[str] = None
    bank_name: Optional[str] = None


class BankStatementWorkflow:
    """LangGraph workflow for bank statement separation."""

    def __init__(self, config: Any):
        """
        Initialize workflow with configuration.

        Args:
            config: Application configuration object
        """
        self.config = config

        # Initialize error handler
        from .utils.error_handler import ErrorHandler

        self.error_handler = ErrorHandler(config)

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""

        # Create the graph
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("pdf_ingestion", self._pdf_ingestion_node)
        workflow.add_node("document_analysis", self._document_analysis_node)
        workflow.add_node("statement_detection", self._statement_detection_node)
        workflow.add_node("metadata_extraction", self._metadata_extraction_node)
        workflow.add_node("pdf_generation", self._pdf_generation_node)
        workflow.add_node("file_organization", self._file_organization_node)
        workflow.add_node("output_validation", self._output_validation_node)
        workflow.add_node("paperless_upload", self._paperless_upload_node)
        workflow.add_node("error_handler", self._error_handler_node)

        # Define the workflow flow
        workflow.set_entry_point("pdf_ingestion")

        # NOTE: Using ONLY conditional edges to avoid concurrent state updates
        # Regular edges are removed to prevent conflicts with error handling

        # Error handling - all nodes can transition to error handler
        workflow.add_conditional_edges(
            "pdf_ingestion",
            self._should_handle_error,
            {"continue": "document_analysis", "error": "error_handler"},
        )

        workflow.add_conditional_edges(
            "document_analysis",
            self._should_handle_error,
            {"continue": "statement_detection", "error": "error_handler"},
        )

        workflow.add_conditional_edges(
            "statement_detection",
            self._should_handle_error,
            {"continue": "metadata_extraction", "error": "error_handler"},
        )

        workflow.add_conditional_edges(
            "metadata_extraction",
            self._should_handle_error,
            {"continue": "pdf_generation", "error": "error_handler"},
        )

        workflow.add_conditional_edges(
            "pdf_generation",
            self._should_handle_error,
            {"continue": "file_organization", "error": "error_handler"},
        )

        workflow.add_conditional_edges(
            "file_organization",
            self._should_handle_error,
            {"continue": "output_validation", "error": "error_handler"},
        )

        workflow.add_conditional_edges(
            "output_validation",
            self._should_handle_error,
            {"continue": "paperless_upload", "error": "error_handler"},
        )

        workflow.add_conditional_edges(
            "paperless_upload",
            self._should_handle_error,
            {"continue": END, "error": "error_handler"},
        )

        workflow.add_edge("error_handler", END)

        return workflow.compile()

    def _should_handle_error(self, state: WorkflowState) -> str:
        """Determine if workflow should handle an error."""
        if state.get("error_message"):
            return "error"
        return "continue"

    def _pdf_ingestion_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 1: PDF Ingestion - Load and validate input PDF file.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        logger.info(f"Starting PDF ingestion for: {state['input_file_path']}")

        try:
            # Pre-processing document validation
            validation_result = self.error_handler.validate_document_format(
                state["input_file_path"]
            )

            if not validation_result["is_valid"]:
                error_msg = f"Document format validation failed: {'; '.join(validation_result['errors'])}"
                logger.error(error_msg)

                # Quarantine invalid document if configured
                if self.config.auto_quarantine_critical_failures:
                    quarantine_path = self.error_handler.move_to_quarantine(
                        state["input_file_path"], error_msg, state
                    )
                    state["quarantine_path"] = quarantine_path

                state["error_message"] = error_msg
                state["current_step"] = "pdf_ingestion_format_error"
                return state

            # Log validation warnings if any
            if validation_result["warnings"]:
                logger.warning(
                    f"Document validation warnings: {'; '.join(validation_result['warnings'])}"
                )
                state["document_validation_warnings"] = validation_result["warnings"]

            from .utils.pdf_processor import PDFProcessor

            # Initialize PDF processor with config limits
            processor = PDFProcessor(
                max_file_size_mb=self.config.max_file_size_mb,
                max_pages=self.config.max_total_pages,
            )

            # Extract text from PDF
            pdf_document = processor.extract_text_from_pdf(state["input_file_path"])

            # Update state
            state["pdf_document"] = {
                "file_path": pdf_document.file_path,
                "total_pages": pdf_document.total_pages,
                "pages": [
                    {
                        "page_number": page.page_number,
                        "text": page.text,
                        "bbox": page.bbox,
                        "word_count": page.word_count,
                    }
                    for page in pdf_document.pages
                ],
                "metadata": pdf_document.metadata,
                "file_size_mb": pdf_document.file_size_mb,
                "total_words": pdf_document.total_words,
            }

            state["total_pages"] = pdf_document.total_pages
            state["current_step"] = "pdf_ingestion_complete"

            logger.info(
                f"PDF ingestion complete: {pdf_document.total_pages} pages, {pdf_document.total_words} words"
            )

        except Exception as e:
            logger.error(f"PDF ingestion failed: {e}")
            state["error_message"] = f"PDF ingestion failed: {str(e)}"
            state["current_step"] = "pdf_ingestion_error"

        return state

    def _document_analysis_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 2: Document Analysis - Extract text and analyze document structure.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        logger.info("Starting document analysis")

        try:
            pdf_doc = state["pdf_document"]

            # Create text chunks for processing
            chunks = []
            current_chunk = ""
            chunk_size = self.config.chunk_size
            overlap = self.config.chunk_overlap

            for page in pdf_doc["pages"]:
                page_text = page["text"]

                # Add page text to current chunk
                if len(current_chunk) + len(page_text) < chunk_size:
                    current_chunk += (
                        f"\n--- PAGE {page['page_number']} ---\n{page_text}"
                    )
                else:
                    # Save current chunk and start new one
                    if current_chunk:
                        chunks.append(current_chunk.strip())

                    # Start new chunk with overlap from previous chunk
                    if overlap > 0 and current_chunk:
                        overlap_text = current_chunk[-overlap:]
                        current_chunk = f"{overlap_text}\n--- PAGE {page['page_number']} ---\n{page_text}"
                    else:
                        current_chunk = (
                            f"--- PAGE {page['page_number']} ---\n{page_text}"
                        )

            # Add final chunk
            if current_chunk:
                chunks.append(current_chunk.strip())

            state["text_chunks"] = chunks
            state["current_step"] = "document_analysis_complete"

            logger.info(
                f"Document analysis complete: created {len(chunks)} text chunks"
            )

        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            state["error_message"] = f"Document analysis failed: {str(e)}"
            state["current_step"] = "document_analysis_error"

        return state

    def _statement_detection_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 3: Statement Detection - Identify individual statement boundaries.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        logger.info("Starting statement detection")

        try:
            from .nodes.llm_analyzer import LLMAnalyzer

            text_chunks = state["text_chunks"]
            total_pages = state["total_pages"]

            # Try LLM-based boundary detection first
            try:
                logger.info("Attempting LLM-based boundary detection")
                analyzer = LLMAnalyzer(self.config)

                llm_result = analyzer.detect_statement_boundaries(
                    text_chunks, total_pages
                )

                # Convert LLM result to our format
                boundaries = []
                for i, boundary in enumerate(llm_result.boundaries):
                    boundaries.append(
                        {
                            "start_page": boundary.start_page,
                            "end_page": boundary.end_page,
                            "confidence": boundary.confidence,
                            "statement_type": "monthly_statement",
                            "account_number": None,  # Will be extracted in metadata step
                            "statement_period": None,  # Will be extracted in metadata step
                            "bank_name": None,  # Will be extracted in metadata step
                            "reasoning": boundary.reasoning,
                        }
                    )

                logger.info(
                    f"LLM boundary detection successful: found {len(boundaries)} statements"
                )

            except Exception as llm_error:
                logger.warning(
                    f"LLM boundary detection failed: {llm_error}, falling back to pattern matching"
                )

                # Fallback to simple heuristic
                estimated_pages_per_statement = min(20, max(5, total_pages // 3))
                boundaries = []
                current_page = 1
                statement_count = 0

                while current_page <= total_pages:
                    end_page = min(
                        current_page + estimated_pages_per_statement - 1, total_pages
                    )

                    boundary = {
                        "start_page": current_page,
                        "end_page": end_page,
                        "confidence": 0.5,  # Lower confidence for fallback
                        "statement_type": "monthly_statement",
                        "account_number": None,
                        "statement_period": None,
                        "bank_name": None,
                        "reasoning": "Fallback page-based segmentation",
                    }

                    boundaries.append(boundary)
                    current_page = end_page + 1
                    statement_count += 1

            state["detected_boundaries"] = boundaries
            state["total_statements_found"] = len(boundaries)
            state["current_step"] = "statement_detection_complete"

            logger.info(
                f"Statement detection complete: found {len(boundaries)} statements"
            )

        except Exception as e:
            logger.error(f"Statement detection failed: {e}")
            state["error_message"] = f"Statement detection failed: {str(e)}"
            state["current_step"] = "statement_detection_error"

        return state

    def _metadata_extraction_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 4: Metadata Extraction - Parse account numbers and statement periods.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        logger.info("Starting metadata extraction")

        try:
            from .nodes.llm_analyzer import LLMAnalyzer

            boundaries = state["detected_boundaries"]
            pdf_doc = state["pdf_document"]
            extracted_metadata = []

            # Initialize LLM analyzer for metadata extraction
            try:
                analyzer = LLMAnalyzer(self.config)
            except Exception as analyzer_error:
                logger.warning(f"Failed to initialize LLM analyzer: {analyzer_error}")
                analyzer = None

            for i, boundary in enumerate(boundaries):
                # Extract text from ALL pages of the statement for comprehensive analysis
                statement_text = ""
                for page in pdf_doc["pages"]:
                    if (
                        boundary["start_page"]
                        <= page["page_number"]
                        <= boundary["end_page"]
                    ):
                        statement_text += page["text"] + "\n"

                # Try LLM-based metadata extraction
                if analyzer:
                    try:
                        logger.debug(
                            f"Extracting metadata for statement {i + 1} using LLM"
                        )
                        llm_metadata = analyzer.extract_metadata(
                            statement_text, boundary["start_page"], boundary["end_page"]
                        )

                        account_number = llm_metadata.account_number
                        # Use the statement_period directly, or construct from start/end dates if available
                        if llm_metadata.statement_period:
                            statement_period = llm_metadata.statement_period
                        elif llm_metadata.start_date and llm_metadata.end_date:
                            statement_period = (
                                f"{llm_metadata.start_date}_{llm_metadata.end_date}"
                            )
                        else:
                            statement_period = None
                        bank_name = llm_metadata.bank_name
                        confidence = llm_metadata.confidence

                        logger.debug(
                            f"LLM metadata extraction successful for statement {i + 1}"
                        )

                    except Exception as llm_error:
                        error_msg = str(llm_error) if llm_error else "Unknown error"
                        logger.warning(
                            f"LLM metadata extraction failed for statement {i + 1}: {error_msg}"
                        )
                        # Fallback to placeholder values
                        account_number = f"ACCT{i + 1:04d}"
                        statement_period = f"2024-{i + 1:02d}"
                        bank_name = "Unknown Bank"
                        confidence = 0.3
                else:
                    # Fallback when analyzer not available
                    account_number = f"ACCT{i + 1:04d}"
                    statement_period = f"2024-{i + 1:02d}"
                    bank_name = "Unknown Bank"
                    confidence = 0.3

                # Create updated boundary for filename generation
                updated_boundary = {
                    **boundary,
                    "account_number": account_number,
                    "statement_period": statement_period,
                    "bank_name": bank_name,
                }

                metadata = {
                    "statement_index": i,
                    "account_number": account_number,
                    "statement_period": statement_period,
                    "bank_name": bank_name,
                    "start_page": boundary["start_page"],
                    "end_page": boundary["end_page"],
                    "confidence": confidence,
                    "filename": self._generate_filename(updated_boundary),
                    "text_preview": statement_text[:500] + "..."
                    if len(statement_text) > 500
                    else statement_text,
                }

                extracted_metadata.append(metadata)

            state["extracted_metadata"] = extracted_metadata
            state["current_step"] = "metadata_extraction_complete"

            logger.info(
                f"Metadata extraction complete: processed {len(extracted_metadata)} statements"
            )

        except Exception as e:
            error_msg = str(e) if e else "Unknown error"
            logger.error(f"Metadata extraction failed: {error_msg}")
            state["error_message"] = f"Metadata extraction failed: {error_msg}"
            state["current_step"] = "metadata_extraction_error"

        return state

    def _pdf_generation_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 5: PDF Generation - Create separate PDF files for each statement.
        Now includes filtering of low-confidence fragments.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        logger.info("Starting PDF generation")

        try:
            from .utils.pdf_processor import PDFProcessor

            processor = PDFProcessor()
            extracted_metadata = state["extracted_metadata"]
            input_file = state["input_file_path"]
            output_dir = state["output_directory"]

            # Ensure output directory exists
            from pathlib import Path

            Path(output_dir).mkdir(parents=True, exist_ok=True)

            generated_files = []
            skipped_fragments = 0
            skipped_pages = 0

            for metadata in extracted_metadata:
                # Check confidence level - skip very low confidence fragments
                confidence = metadata.get("confidence", 0.5)

                if confidence < 0.3:  # Very low confidence threshold
                    page_count = metadata["end_page"] - metadata["start_page"] + 1
                    logger.warning(
                        f"Skipping fragment with confidence {confidence}: pages {metadata['start_page']}-{metadata['end_page']} ({page_count} pages)"
                    )
                    skipped_fragments += 1
                    skipped_pages += page_count
                    continue

                output_filename = metadata["filename"]
                output_path = f"{output_dir}/{output_filename}"

                # Extract page range to new PDF
                success = processor.extract_page_range(
                    input_file,
                    metadata["start_page"],
                    metadata["end_page"],
                    output_path,
                )

                if success:
                    generated_files.append(output_path)
                    logger.info(
                        f"Generated: {output_filename} (confidence: {confidence})"
                    )
                else:
                    logger.warning(f"Failed to generate: {output_filename}")

            state["generated_files"] = generated_files
            state["current_step"] = "pdf_generation_complete"

            # Track skipped fragments for validation
            state["skipped_fragments"] = skipped_fragments
            state["skipped_pages"] = skipped_pages

            # Update total_statements_found to reflect actual generated files after filtering
            state["total_statements_found"] = len(generated_files)

            if skipped_fragments > 0:
                logger.info(
                    f"PDF generation complete: created {len(generated_files)} files, skipped {skipped_fragments} fragments ({skipped_pages} pages)"
                )
            else:
                logger.info(
                    f"PDF generation complete: created {len(generated_files)} files"
                )

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            state["error_message"] = f"PDF generation failed: {str(e)}"
            state["current_step"] = "pdf_generation_error"

        return state

    def _file_organization_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 6: File Organization - Apply naming conventions and organize output.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        logger.info("Starting file organization")

        try:
            generated_files = state["generated_files"]

            # Files are already organized by the PDF generation step
            # This step could add additional organization like subdirectories by bank or date

            state["processing_complete"] = True
            state["current_step"] = "file_organization_complete"

            logger.info(
                f"File organization complete: {len(generated_files)} files ready"
            )

        except Exception as e:
            logger.error(f"File organization failed: {e}")
            state["error_message"] = f"File organization failed: {str(e)}"
            state["current_step"] = "file_organization_error"

        return state

    def _output_validation_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 7: Output Validation - Validate output files against original input.

        Performs comprehensive validation to ensure data integrity:
        1. File count validation (all statements accounted for)
        2. Page count validation (total pages match original)
        3. File size validation (approximate content preservation)
        4. Content sampling validation (spot checks)

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state with validation results
        """
        logger.info("Starting output validation")

        try:
            input_file_path = state["input_file_path"]
            generated_files = state["generated_files"]
            original_total_pages = state["total_pages"]
            skipped_pages = state.get("skipped_pages", 0)

            validation_results = self._validate_output_integrity(
                input_file_path, generated_files, original_total_pages, skipped_pages
            )

            if not validation_results["is_valid"]:
                # Use enhanced validation error handling
                return self.error_handler.handle_validation_failure(
                    state, validation_results
                )

            # Add validation results to state
            state["validation_results"] = validation_results

            # Move input file to processed directory if validation passed
            processed_file_path = self._move_to_processed_directory(input_file_path)
            state["processed_input_file"] = processed_file_path

            state["current_step"] = "output_validation_complete"

            logger.info(f"Output validation passed: {validation_results['summary']}")
            if processed_file_path:
                logger.info(
                    f"Input file moved to processed directory: {processed_file_path}"
                )

        except Exception as e:
            error_msg = f"Output validation failed with exception: {str(e)}"
            logger.error(error_msg)
            state["error_message"] = error_msg
            state["current_step"] = "output_validation_error"

        return state

    def _move_to_processed_directory(self, input_file_path: str) -> Optional[str]:
        """
        Move input file to processed directory.

        If processed_input_dir is configured, uses that directory.
        Otherwise, creates a 'processed' subdirectory in the same directory as the input file.

        Args:
            input_file_path: Path to the original input file

        Returns:
            Path to moved file if successful, None if failed
        """
        try:
            input_path = Path(input_file_path)

            # Determine processed directory
            if self.config.processed_input_dir:
                processed_dir = Path(self.config.processed_input_dir)
                logger.debug(f"Using configured processed directory: {processed_dir}")
            else:
                # Create processed subdirectory next to input file
                processed_dir = input_path.parent / "processed"
                logger.debug(f"Using default processed directory: {processed_dir}")

            # Create processed directory if it doesn't exist
            processed_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename if file already exists
            destination_path = processed_dir / input_path.name
            counter = 1
            while destination_path.exists():
                name_parts = input_path.stem, counter, input_path.suffix
                destination_path = (
                    processed_dir
                    / f"{name_parts[0]}_processed_{name_parts[1]}{name_parts[2]}"
                )
                counter += 1

            # Move the file
            shutil.move(str(input_path), str(destination_path))
            logger.info(f"Moved processed input file to: {destination_path}")

            return str(destination_path)

        except Exception as e:
            logger.warning(f"Failed to move input file to processed directory: {e}")
            return None

    def _validate_output_integrity(
        self,
        input_file_path: str,
        generated_files: List[str],
        original_total_pages: int,
        skipped_pages: int = 0,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive validation of output files against original input.
        Now accounts for skipped fragment pages.

        Args:
            input_file_path: Path to original input file
            generated_files: List of generated output file paths
            original_total_pages: Total pages in original file
            skipped_pages: Number of pages skipped due to low confidence fragments

        Returns:
            Dict containing validation results and details
        """
        import os
        import fitz

        validation_results = {
            "is_valid": True,
            "error_details": [],
            "summary": "",
            "checks": {
                "file_count": {"status": "unknown", "details": ""},
                "page_count": {"status": "unknown", "details": ""},
                "file_size": {"status": "unknown", "details": ""},
                "content_sampling": {"status": "unknown", "details": ""},
            },
        }

        try:
            # 1. File existence validation
            missing_files = [f for f in generated_files if not os.path.exists(f)]
            if missing_files:
                validation_results["is_valid"] = False
                validation_results["error_details"].append(
                    f"Missing output files: {missing_files}"
                )
                validation_results["checks"]["file_count"]["status"] = "failed"
                validation_results["checks"]["file_count"]["details"] = (
                    f"Missing {len(missing_files)} files"
                )
                return validation_results

            validation_results["checks"]["file_count"]["status"] = "passed"
            validation_results["checks"]["file_count"]["details"] = (
                f"All {len(generated_files)} files exist"
            )

            # 2. Page count validation
            total_output_pages = 0
            page_distribution = []

            for output_file in generated_files:
                try:
                    doc = fitz.open(output_file)
                    page_count = len(doc)
                    total_output_pages += page_count
                    page_distribution.append(
                        f"{os.path.basename(output_file)}: {page_count} pages"
                    )
                    doc.close()
                except Exception as e:
                    validation_results["is_valid"] = False
                    validation_results["error_details"].append(
                        f"Failed to read {output_file}: {str(e)}"
                    )
                    validation_results["checks"]["page_count"]["status"] = "failed"
                    return validation_results

            # Account for skipped fragment pages
            expected_pages = original_total_pages - skipped_pages

            if total_output_pages != expected_pages:
                validation_results["is_valid"] = False
                validation_results["error_details"].append(
                    f"Page count mismatch: expected={expected_pages} (original={original_total_pages}, skipped={skipped_pages}), output={total_output_pages}"
                )
                validation_results["checks"]["page_count"]["status"] = "failed"
                validation_results["checks"]["page_count"]["details"] = (
                    f"Expected {expected_pages}, got {total_output_pages}"
                )
            else:
                validation_results["checks"]["page_count"]["status"] = "passed"
                if skipped_pages > 0:
                    validation_results["checks"]["page_count"]["details"] = (
                        f"Page count matches: {total_output_pages} pages (skipped {skipped_pages} fragment pages)"
                    )
                else:
                    validation_results["checks"]["page_count"]["details"] = (
                        f"Page count matches: {total_output_pages} pages"
                    )

            # 3. File size validation (approximate - should be within reasonable range)
            original_size = os.path.getsize(input_file_path)
            total_output_size = sum(os.path.getsize(f) for f in generated_files)
            size_ratio = total_output_size / original_size if original_size > 0 else 0

            # Adjust tolerance if fragments were skipped
            min_ratio = (
                0.85 if skipped_pages == 0 else max(0.5, 0.85 - (skipped_pages * 0.05))
            )
            max_ratio = 1.15

            # Allow more variance when fragments are skipped
            if size_ratio < min_ratio or size_ratio > max_ratio:
                validation_results["is_valid"] = False
                validation_results["error_details"].append(
                    f"File size mismatch: original={original_size:,} bytes, output={total_output_size:,} bytes (ratio: {size_ratio:.2f})"
                )
                validation_results["checks"]["file_size"]["status"] = "failed"
                validation_results["checks"]["file_size"]["details"] = (
                    f"Size ratio {size_ratio:.2f} outside acceptable range ({min_ratio:.2f}-{max_ratio:.2f})"
                )
            else:
                validation_results["checks"]["file_size"]["status"] = "passed"
                validation_results["checks"]["file_size"]["details"] = (
                    f"Size ratio {size_ratio:.2f} within acceptable range"
                )

            # 4. Content sampling validation - check that key content exists
            original_doc = fitz.open(input_file_path)
            original_sample_content = []

            # Sample content from first, middle, and last pages of original
            sample_pages = [0, len(original_doc) // 2, len(original_doc) - 1]
            for page_num in sample_pages:
                if page_num < len(original_doc):
                    page_text = original_doc[page_num].get_text()
                    # Extract key identifiers (account numbers, dates, bank names) - more specific patterns
                    import re

                    # Focus on longer numbers (account/card numbers), bank names, and key terms
                    key_phrases = re.findall(
                        r"\b\d{8,}\b|BusinessChoice|Westpac|Statement|Account|Card\s+Number|Facility",
                        page_text,
                        re.IGNORECASE,
                    )
                    original_sample_content.extend(
                        key_phrases[:3]
                    )  # Top 3 key phrases per page

            original_doc.close()

            # Check if sample content appears in output files
            output_sample_content = []
            for output_file in generated_files:
                doc = fitz.open(output_file)
                for page_num in range(
                    min(2, len(doc))
                ):  # Check first 2 pages of each file
                    page_text = doc[page_num].get_text()
                    import re

                    # Use same pattern as original sampling
                    key_phrases = re.findall(
                        r"\b\d{8,}\b|BusinessChoice|Westpac|Statement|Account|Card\s+Number|Facility",
                        page_text,
                        re.IGNORECASE,
                    )
                    output_sample_content.extend(key_phrases)
                doc.close()

            # Check overlap of key content
            original_unique = set(original_sample_content)
            output_unique = set(output_sample_content)
            content_overlap = (
                len(original_unique.intersection(output_unique)) / len(original_unique)
                if original_unique
                else 1
            )

            if (
                content_overlap < 0.7
            ):  # At least 70% of key content should be preserved (adjusted for PDF processing)
                validation_results["is_valid"] = False
                validation_results["error_details"].append(
                    f"Content sampling validation failed: only {content_overlap:.1%} of key content found in outputs"
                )
                validation_results["checks"]["content_sampling"]["status"] = "failed"
                validation_results["checks"]["content_sampling"]["details"] = (
                    f"Only {content_overlap:.1%} key content overlap"
                )
            else:
                validation_results["checks"]["content_sampling"]["status"] = "passed"
                validation_results["checks"]["content_sampling"]["details"] = (
                    f"{content_overlap:.1%} key content overlap"
                )

            # Build summary
            passed_checks = sum(
                1
                for check in validation_results["checks"].values()
                if check["status"] == "passed"
            )
            total_checks = len(validation_results["checks"])

            if validation_results["is_valid"]:
                validation_results["summary"] = (
                    f"All {total_checks} validation checks passed ({len(generated_files)} files, {total_output_pages} pages)"
                )
            else:
                validation_results["summary"] = (
                    f"{passed_checks}/{total_checks} checks passed, {len(validation_results['error_details'])} errors found"
                )

        except Exception as e:
            validation_results["is_valid"] = False
            validation_results["error_details"].append(
                f"Validation exception: {str(e)}"
            )
            validation_results["summary"] = (
                f"Validation failed with exception: {str(e)}"
            )

        return validation_results

    def _paperless_upload_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 8: Paperless Upload - Upload generated statements to paperless-ngx if enabled.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state with upload results
        """
        logger.info("Starting paperless upload")

        upload_results = {
            "enabled": False,
            "success": True,
            "uploads": [],
            "errors": [],
            "summary": "Paperless integration disabled",
        }

        try:
            from .utils.paperless_client import PaperlessClient

            # Initialize paperless client
            paperless_client = PaperlessClient(self.config)

            # Check if paperless integration is enabled
            if not paperless_client.is_enabled():
                logger.info("Paperless integration disabled, skipping upload")
                upload_results["summary"] = "Paperless integration disabled"
                state["paperless_upload_results"] = upload_results
                state["current_step"] = "paperless_upload_skipped"
                return state

            upload_results["enabled"] = True

            # Test connection first
            try:
                paperless_client.test_connection()
                logger.info("Paperless connection test successful")
            except Exception as conn_error:
                error_msg = f"Paperless connection test failed: {conn_error}"
                logger.error(error_msg)
                upload_results["success"] = False
                upload_results["errors"].append(error_msg)
                upload_results["summary"] = "Connection test failed"
                state["paperless_upload_results"] = upload_results
                state["current_step"] = "paperless_upload_connection_error"
                return state

            # Get generated files and metadata
            generated_files = state["generated_files"] or []

            if not generated_files:
                logger.warning("No generated files to upload to paperless")
                upload_results["summary"] = "No files to upload"
                state["paperless_upload_results"] = upload_results
                state["current_step"] = "paperless_upload_no_files"
                return state

            # Upload each generated file
            successful_uploads = []
            failed_uploads = []

            for i, file_path in enumerate(generated_files):
                try:
                    # Use the exact filename (without extension) as the title to maintain perfect consistency
                    file_name = Path(
                        file_path
                    ).stem  # Gets filename without .pdf extension
                    title = file_name  # Use exact filename: "westpac-2440-2023-01-31"

                    # Upload the file
                    upload_result = paperless_client.upload_document(
                        file_path=Path(file_path),
                        title=title,
                        tags=self.config.paperless_tags,
                        correspondent=self.config.paperless_correspondent,
                        document_type=self.config.paperless_document_type,
                        storage_path=self.config.paperless_storage_path,
                    )

                    successful_uploads.append(upload_result)
                    logger.info(f"Successfully uploaded: {Path(file_path).name}")

                except Exception as upload_error:
                    error_info = {"file_path": file_path, "error": str(upload_error)}
                    failed_uploads.append(error_info)
                    logger.error(
                        f"Failed to upload {Path(file_path).name}: {upload_error}"
                    )

            # Update results
            upload_results["uploads"] = successful_uploads
            upload_results["errors"] = failed_uploads
            upload_results["success"] = len(failed_uploads) == 0

            # Create summary
            if upload_results["success"]:
                upload_results["summary"] = (
                    f"Successfully uploaded {len(successful_uploads)} files to paperless-ngx"
                )
            else:
                upload_results["summary"] = (
                    f"Uploaded {len(successful_uploads)}/{len(generated_files)} files, {len(failed_uploads)} errors"
                )

            state["paperless_upload_results"] = upload_results
            state["current_step"] = "paperless_upload_complete"

            logger.info(f"Paperless upload complete: {upload_results['summary']}")

        except Exception as e:
            error_msg = f"Paperless upload failed with exception: {str(e)}"
            logger.error(error_msg)
            upload_results["success"] = False
            upload_results["errors"].append(error_msg)
            upload_results["summary"] = f"Upload failed: {str(e)}"
            state["paperless_upload_results"] = upload_results
            state["error_message"] = error_msg
            state["current_step"] = "paperless_upload_error"

        return state

    def _error_handler_node(self, state: WorkflowState) -> WorkflowState:
        """Error handling node for workflow failures."""
        logger.error(
            f"Workflow error in step '{state['current_step']}': {state['error_message']}"
        )

        state["processing_complete"] = False
        state["current_step"] = "error_handled"

        return state

    def _generate_filename(self, boundary: Dict[str, Any]) -> str:
        """Generate filename based on extracted metadata using PRD specification.

        Format: <bank>-<last4digits>-<statement_date>.pdf
        """
        # Extract and normalize components
        bank = self._normalize_bank_name(boundary.get("bank_name", ""))
        last4digits = self._extract_last4_digits(boundary.get("account_number", ""))

        # Handle both legacy and new date field names
        statement_period = boundary.get("statement_period_end", "") or boundary.get(
            "statement_period", ""
        )
        statement_date = self._format_statement_date(statement_period)

        filename = f"{bank}-{last4digits}-{statement_date}.pdf"

        # Handle potential filename collisions by adding page numbers
        if statement_date == "unknown-date" and last4digits == "0000":
            start_page = boundary.get("start_page", 1)
            filename = f"{bank}-{last4digits}-{statement_date}-p{start_page}.pdf"

        # Ensure filename is not too long
        if len(filename) > self.config.max_filename_length:
            # Truncate bank name if needed, keeping other components intact
            max_bank_length = self.config.max_filename_length - len(
                f"-{last4digits}-{statement_date}.pdf"
            )
            bank = bank[:max_bank_length] if max_bank_length > 0 else "unk"
            filename = f"{bank}-{last4digits}-{statement_date}.pdf"

        return filename

    def _normalize_bank_name(self, bank_name: str) -> str:
        """Normalize bank name per PRD specification.

        Returns lowercase, no spaces, max 10 chars.
        Fallback: 'unknown' if empty or invalid.
        """
        if not bank_name or not isinstance(bank_name, str):
            return "unknown"

        # Normalize: lowercase, remove spaces and special chars
        normalized = (
            bank_name.lower().replace(" ", "").replace("-", "").replace("_", "")
        )

        # Remove common words to shorten
        normalized = (
            normalized.replace("banking", "")
            .replace("corporation", "")
            .replace("bank", "")
        )

        # Truncate to max 10 chars
        normalized = normalized[:10] if normalized else "unknown"

        return normalized or "unknown"

    def _extract_last4_digits(self, account_number: str) -> str:
        """Extract last 4 digits from account number.

        Fallback: '0000' if no digits found.
        """
        if not account_number or not isinstance(account_number, str):
            return "0000"

        # Extract only digits from the account number
        digits = "".join(char for char in account_number if char.isdigit())

        # Return last 4 digits, or '0000' if insufficient
        return digits[-4:] if len(digits) >= 4 else "0000"

    def _format_statement_date(self, statement_period: str) -> str:
        """Format statement period to extract end date in YYYY-MM-DD format.

        Handles formats like:
        - '2015-04-22_2015-05-21' -> '2015-05-21' (end date)
        - '2015-05-21' -> '2015-05-21' (already correct)
        - '01 January 2023 to 31 January 2023' -> '2023-01-31' (end date)
        - 'Unknown' -> 'unknown-date'

        Fallback: 'unknown-date' if invalid or empty.
        """
        if not statement_period or not isinstance(statement_period, str):
            return "unknown-date"

        # Handle range format like '2015-04-22_2015-05-21' (extract end date)
        if "_" in statement_period:
            parts = statement_period.split("_")
            if len(parts) == 2:
                end_date = parts[1].strip()
                if len(end_date) == 10 and end_date.count("-") == 2:
                    return end_date

        # Handle single YYYY-MM-DD format (already correct)
        if len(statement_period) == 10 and statement_period.count("-") == 2:
            return statement_period

        # Handle natural language date ranges like "01 January 2023 to 31 January 2023"
        try:
            import re

            # Look for "to" pattern to extract end date
            if " to " in statement_period.lower():
                parts = statement_period.split(" to ")
                if len(parts) == 2:
                    end_date_str = parts[1].strip()
                else:
                    end_date_str = statement_period
            else:
                end_date_str = statement_period

            # Month name mapping
            month_names = {
                "january": "01",
                "february": "02",
                "march": "03",
                "april": "04",
                "may": "05",
                "june": "06",
                "july": "07",
                "august": "08",
                "september": "09",
                "october": "10",
                "november": "11",
                "december": "12",
            }

            # Try to parse "DD Month YYYY" format
            date_pattern = r"(\d{1,2})\s+(\w+)\s+(\d{4})"
            match = re.search(date_pattern, end_date_str.lower())

            if match:
                day, month_name, year = match.groups()
                month_num = month_names.get(month_name.lower())
                if month_num:
                    formatted_date = f"{year}-{month_num}-{day.zfill(2)}"
                    return formatted_date

        except (ImportError, ValueError, AttributeError):
            pass

        # Handle 'Unknown' or other invalid formats
        return "unknown-date"

    def run(self, input_file_path: str, output_directory: str) -> Dict[str, Any]:
        """
        Run the complete workflow.

        Args:
            input_file_path: Path to input PDF file
            output_directory: Directory for output files

        Returns:
            dict: Workflow results
        """
        initial_state = WorkflowState(
            input_file_path=input_file_path,
            output_directory=output_directory,
            pdf_document=None,
            text_chunks=None,
            detected_boundaries=None,
            extracted_metadata=None,
            generated_files=None,
            processed_input_file=None,
            paperless_upload_results=None,
            current_step="initializing",
            error_message=None,
            processing_complete=False,
            total_pages=0,
            total_statements_found=0,
            processing_time_seconds=None,
            confidence_scores=None,
            validation_results=None,
        )

        logger.info(f"Starting workflow for: {input_file_path}")

        try:
            # Run the workflow
            result = self.graph.invoke(initial_state)

            logger.info(f"Workflow completed with status: {result['current_step']}")
            return result

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                **initial_state,
                "error_message": f"Workflow execution failed: {str(e)}",
                "current_step": "workflow_error",
                "processing_complete": False,
            }
