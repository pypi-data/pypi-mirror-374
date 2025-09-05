"""
Main NAV Online Számla API client.

This module provides the main client class for interacting with the NAV Online Számla API.
"""

import gzip
import logging
from datetime import datetime
from typing import List, Optional, Tuple

from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.formats.dataclass.parsers import XmlParser

from .config import (
    ONLINE_SZAMLA_URL,
    MAX_DATE_RANGE_DAYS,
    SOFTWARE_ID,
    SOFTWARE_NAME,
    SOFTWARE_VERSION,
    SOFTWARE_DEV_NAME,
    SOFTWARE_DEV_CONTACT,
    SOFTWARE_DEV_COUNTRY,
    NavEnvironment,
    ENVIRONMENT_URLS,
    get_default_environment,
)
from .models import (
    # Official API types from generated models
    InvoiceDirectionType,
    BasicHeaderType,
    # Additional types from generated models
    InvoiceDetailType,
    DateIntervalParamType,
    MandatoryQueryParamsType,
    InvoiceQueryParamsType,
    CryptoType,
    ManageInvoiceOperationType,
    # Query parameter types
    InvoiceNumberQueryType,
    # Request wrappers (root elements)
    QueryInvoiceDigestRequest,
    QueryInvoiceCheckRequest,
    QueryInvoiceDataRequest,
    QueryInvoiceChainDigestRequest,
    QueryTransactionStatusRequest,
    # Token exchange
    TokenExchangeRequest,
    TokenExchangeResponse,
    # Response wrappers 
    QueryInvoiceDataResponse,
    QueryInvoiceDigestResponse,
    QueryInvoiceCheckResponse,
    QueryInvoiceChainDigestResponse,
    QueryTransactionStatusResponse,
    # Invoice data types
    InvoiceData,
    # Common types
    UserHeaderType,
    SoftwareType,
    SoftwareOperationType,
    # Annulment types
    ManageAnnulmentRequest,
    ManageAnnulmentResponse,
    ManageAnnulmentOperationType,
    AnnulmentOperationType,
    AnnulmentOperationListType,
    # Invoice management types
    ManageInvoiceRequest,
    ManageInvoiceResponse,
    InvoiceOperationType,
    InvoiceOperationListType,
    # Invoice annulment data types
    InvoiceAnnulment,
    InvoiceAnnulmentType,
    AnnulmentCodeType,
)

# Import only essential custom classes
from .models_legacy import (
    NavCredentials,
)
from .exceptions import (
    NavApiException,
    NavValidationException,
    NavXmlParsingException,
    NavInvoiceNotFoundException,
)
from .utils import (
    generate_password_hash,
    generate_custom_id,
    calculate_request_signature,
    calculate_complex_request_signature,
    calculate_electronic_invoice_hash,
    validate_tax_number,
    format_timestamp_for_nav,
    decode_exchange_token,
    encode_annulment_data_to_base64,
    serialize_annulment_data_to_xml,
)
from .http_client import NavHttpClient

logger = logging.getLogger(__name__)


class NavOnlineInvoiceClient:
    """
    Main client for interacting with the NAV Online Számla API.

    This client provides methods for querying invoice data, getting invoice details,
    and managing invoice operations through the NAV API.
    
    Supports both test and production environments for development and deployment.
    """

    def __init__(
        self, 
        credentials: NavCredentials, 
        environment: Optional[NavEnvironment] = None,
        timeout: int = 30
    ):
        """
        Initialize the NAV API client.

        Args:
            credentials: NAV API credentials
            environment: Environment to use (TEST or PRODUCTION). If None, uses environment 
                        variable NAV_ENVIRONMENT or defaults to PRODUCTION
            timeout: Request timeout in seconds
            
        Examples:
            # Use production environment (default)
            client = NavOnlineInvoiceClient(credentials)
            
            # Use test environment
            client = NavOnlineInvoiceClient(credentials, environment=NavEnvironment.TEST)
            
            # Use environment variable NAV_ENVIRONMENT=test
            os.environ['NAV_ENVIRONMENT'] = 'test'
            client = NavOnlineInvoiceClient(credentials)
        """
        self.validate_credentials(credentials)
        self.credentials = credentials
        
        # Use environment-based URL
        self.environment = environment or get_default_environment()
        self.base_url = ENVIRONMENT_URLS[self.environment]
        
        self.timeout = timeout
        self.http_client = NavHttpClient(self.base_url, timeout)
        
        # Initialize xsdata XML context, serializer, and parser
        self.xml_context = XmlContext()
        self.xml_serializer = XmlSerializer(context=self.xml_context)
        self.xml_parser = XmlParser(context=self.xml_context)
        
        # Log environment information for debugging
        logger.info(f"Initialized NAV client for {self.environment.value} environment: {self.base_url}")

    def validate_credentials(self, credentials: NavCredentials) -> None:
        """
        Validate NAV API credentials.

        Args:
            credentials: NAV API credentials

        Raises:
            NavValidationException: If credentials are invalid
        """
        if not all([credentials.login, credentials.password, credentials.signer_key]):
            raise NavValidationException(
                "Missing required credentials: login, password, or signer_key"
            )

        if not validate_tax_number(credentials.tax_number):
            raise NavValidationException(
                f"Invalid tax number format: {credentials.tax_number}"
            )

    def _create_basic_header(self) -> BasicHeaderType:
        """Create basic header for requests."""
        return BasicHeaderType(
            request_id=generate_custom_id(),
            timestamp=format_timestamp_for_nav(datetime.now()),
            request_version="3.0",
            header_version="1.0"
        )

    def _create_basic_header_with_timestamp(self, timestamp: str) -> BasicHeaderType:
        """Create basic header for requests with a specific timestamp."""
        return BasicHeaderType(
            request_id=generate_custom_id(),
            timestamp=timestamp,
            request_version="3.0",
            header_version="1.0"
        )

    def _create_user_header(self, credentials: NavCredentials, header: BasicHeaderType) -> UserHeaderType:
        """Create user header with authentication data using the provided header."""
        password_hash = generate_password_hash(credentials.password)
        request_signature = calculate_request_signature(
            header.request_id, 
            header.timestamp, 
            credentials.signer_key
        )
        
        return UserHeaderType(
            login=credentials.login,
            password_hash=CryptoType(
                value=password_hash,
                crypto_type="SHA-512"
            ),
            tax_number=credentials.tax_number,
            request_signature=CryptoType(
                value=request_signature,
                crypto_type="SHA3-512"
            )
        )

    def _create_user_header_with_complex_signature(
        self, 
        credentials: NavCredentials, 
        header: BasicHeaderType,
        operation_data: List[Tuple[str, str]]
    ) -> UserHeaderType:
        """Create user header with complex signature for manageInvoice/manageAnnulment operations."""
        password_hash = generate_password_hash(credentials.password)
        request_signature = calculate_complex_request_signature(
            header.request_id, 
            header.timestamp, 
            credentials.signer_key,
            operation_data
        )
        
        return UserHeaderType(
            login=credentials.login,
            password_hash=CryptoType(
                value=password_hash,
                crypto_type="SHA-512"
            ),
            tax_number=credentials.tax_number,
            request_signature=CryptoType(
                value=request_signature,
                crypto_type="SHA3-512"
            )
        )

    def _create_software_info(self, credentials: NavCredentials) -> SoftwareType:
        """Create software information."""
        return SoftwareType(
            software_id=SOFTWARE_ID,
            software_name=SOFTWARE_NAME,
            software_operation=SoftwareOperationType.LOCAL_SOFTWARE,
            software_main_version=SOFTWARE_VERSION,
            software_dev_name=SOFTWARE_DEV_NAME,
            software_dev_contact=SOFTWARE_DEV_CONTACT,
            software_dev_country_code=SOFTWARE_DEV_COUNTRY,
            software_dev_tax_number=credentials.tax_number
        )

    def _serialize_request_to_xml(self, request_obj) -> str:
        """Serialize a request object to XML using xsdata with proper namespace formatting."""
        config = SerializerConfig(
            indent="  ",  # Use indent instead of pretty_print
            xml_declaration=True,
            encoding="UTF-8"
        )
        
        serializer = XmlSerializer(context=self.xml_context, config=config)
        xml_output = serializer.render(request_obj)
        
        # Format with custom namespace prefixes to match NAV expected format
        return self._format_xml_with_custom_namespaces(xml_output)
    
    def _parse_response_from_xml(self, xml_response: str, response_class):
        """
        Generic function for parsing XML responses using xsdata.
        
        This function provides automatic parsing of NAV API responses to typed dataclasses:
        1. Takes raw XML response string
        2. Uses xsdata parser with the provided response class
        3. Returns fully typed response object
        4. Handles parsing errors appropriately
        
        Args:
            xml_response: Raw XML response string from NAV API
            response_class: The dataclass type to parse into (e.g., QueryInvoiceDataResponse)
            
        Returns:
            Parsed response object of the specified type
            
        Raises:
            NavXmlParsingException: If XML parsing fails
            NavApiException: If response contains API errors
        """
        try:
            # Parse XML to response object using xsdata
            response_obj = self.xml_parser.from_string(xml_response, response_class)
            
            # Check for API errors in the response
            if hasattr(response_obj, 'result') and response_obj.result:
                func_code = response_obj.result.func_code
                # Handle both enum and string values
                func_code_value = func_code.value if hasattr(func_code, 'value') else str(func_code)
                
                if func_code_value != 'OK':
                    error_code = getattr(response_obj.result, 'error_code', 'UNKNOWN_ERROR')
                    message = getattr(response_obj.result, 'message', 'No error message provided')
                    raise NavApiException(f"API Error: {error_code} - {message}")
            
            return response_obj
            
        except Exception as e:
            if isinstance(e, NavApiException):
                raise
            logger.error(f"Failed to parse XML response: {e}")
            raise NavXmlParsingException(f"Failed to parse response XML: {e}")
    
    def _format_xml_with_custom_namespaces(self, xml_string: str) -> str:
        """
        Convert xsdata generated XML to match NAV expected format:
        - ns0 -> default namespace
        - ns1 -> common prefix
        """
        # Replace namespace declarations and prefixes
        xml_string = xml_string.replace(
            'xmlns:ns0="http://schemas.nav.gov.hu/OSA/3.0/api"',
            'xmlns="http://schemas.nav.gov.hu/OSA/3.0/api" xmlns:common="http://schemas.nav.gov.hu/NTCA/1.0/common"'
        )
        
        # Remove redundant namespace declarations
        xml_string = xml_string.replace(
            ' xmlns:ns1="http://schemas.nav.gov.hu/NTCA/1.0/common"',
            ''
        )
        
        # Replace element prefixes
        xml_string = xml_string.replace('ns0:', '')  # Remove ns0 prefix (default namespace)
        xml_string = xml_string.replace('ns1:', 'common:')  # Replace ns1 with common
        
        return xml_string

    def _format_annulment_xml_with_custom_namespaces(self, xml_string: str) -> str:
        """
        Convert xsdata generated annulment XML to match NAV expected format.
        Converts from:
        <ns0:InvoiceAnnulment xmlns:ns0="http://schemas.nav.gov.hu/OSA/3.0/annul">
        
        To:
        <InvoiceAnnulment xmlns="http://schemas.nav.gov.hu/OSA/3.0/annul">
        """
        # Replace namespace declarations - convert ns0 to default namespace
        xml_string = xml_string.replace(
            'xmlns:ns0="http://schemas.nav.gov.hu/OSA/3.0/annul"',
            'xmlns="http://schemas.nav.gov.hu/OSA/3.0/annul"'
        )
        
        # Add standalone="yes" attribute to XML declaration if not present
        if 'standalone=' not in xml_string:
            xml_string = xml_string.replace(
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            )
        
        # Remove ns0 prefix from all elements (make them use default namespace)
        xml_string = xml_string.replace('ns0:', '')
        
        return xml_string

    def create_query_invoice_digest_request(
        self, 
        credentials: NavCredentials, 
        page: int,
        invoice_direction: InvoiceDirectionType,
        invoice_query_params: InvoiceQueryParamsType
    ) -> QueryInvoiceDigestRequest:
        """Create a QueryInvoiceDigestRequest using generated models."""
        
        header = self._create_basic_header()
        user = self._create_user_header(credentials, header)
        software = self._create_software_info(credentials)
        
        return QueryInvoiceDigestRequest(
            header=header,
            user=user,
            software=software,
            page=page,
            invoice_direction=invoice_direction,
            invoice_query_params=invoice_query_params
        )

    def create_token_exchange_request(self) -> TokenExchangeRequest:
        """Create a TokenExchangeRequest using generated models."""
        
        header = self._create_basic_header()
        user = self._create_user_header(self.credentials, header)
        software = self._create_software_info(self.credentials)
        
        return TokenExchangeRequest(
            header=header,
            user=user,
            software=software
        )

    def create_query_invoice_data_request(
        self,
        credentials: NavCredentials,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType,
        batch_index: Optional[int] = None,
        supplier_tax_number: Optional[str] = None
    ) -> QueryInvoiceDataRequest:
        """Create a QueryInvoiceDataRequest using generated models."""
        
        header = self._create_basic_header()
        user = self._create_user_header(credentials, header)
        software = self._create_software_info(credentials)
        
        invoice_number_query = InvoiceNumberQueryType(
            invoice_number=invoice_number,
            invoice_direction=invoice_direction,
            batch_index=batch_index,
            supplier_tax_number=supplier_tax_number
        )
        
        return QueryInvoiceDataRequest(
            header=header,
            user=user,
            software=software,
            invoice_number_query=invoice_number_query
        )

    def create_query_invoice_check_request(
        self,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType,
        batch_index: Optional[int] = None,
        supplier_tax_number: Optional[str] = None
    ) -> QueryInvoiceCheckRequest:
        """Create a QueryInvoiceCheckRequest using generated models."""
        
        header = self._create_basic_header()
        user = self._create_user_header(self.credentials, header)
        software = self._create_software_info(self.credentials)
        
        invoice_number_query = InvoiceNumberQueryType(
            invoice_number=invoice_number,
            invoice_direction=invoice_direction,
            batch_index=batch_index,
            supplier_tax_number=supplier_tax_number
        )
        
        return QueryInvoiceCheckRequest(
            header=header,
            user=user,
            software=software,
            invoice_number_query=invoice_number_query
        )

    def create_query_invoice_chain_digest_request(
        self,
        page: int,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType,
        tax_number: Optional[str] = None
    ) -> QueryInvoiceChainDigestRequest:
        """Create a QueryInvoiceChainDigestRequest using generated models."""
        
        header = self._create_basic_header()
        user = self._create_user_header(self.credentials, header)
        software = self._create_software_info(self.credentials)
        
        return QueryInvoiceChainDigestRequest(
            header=header,
            user=user,
            software=software,
            page=page,
            invoice_number=invoice_number,
            invoice_direction=invoice_direction,
            tax_number=tax_number
        )

    def create_query_transaction_status_request(
        self,
        transaction_id: str,
        return_original_request: Optional[bool] = None
    ) -> QueryTransactionStatusRequest:
        """Create a QueryTransactionStatusRequest using generated models."""
        
        header = self._create_basic_header()
        user = self._create_user_header(self.credentials, header)
        software = self._create_software_info(self.credentials)
        
        return QueryTransactionStatusRequest(
            header=header,
            user=user,
            software=software,
            transaction_id=transaction_id,
            return_original_request=return_original_request
        )

    def query_invoice_digest(
        self,
        page: int,
        invoice_direction: InvoiceDirectionType,
        invoice_query_params: InvoiceQueryParamsType
    ) -> QueryInvoiceDigestResponse:
        """
        Query invoice digest using xsdata-generated dataclasses.
        This uses automatic XML serialization and parsing for type-safe API interactions.
        
        Args:
            page: Page number for pagination (1-based)
            invoice_direction: Invoice direction (OUTBOUND/INBOUND)
            invoice_query_params: Query parameters (date range, supplier info, etc.)
            
        Returns:
            QueryInvoiceDigestResponse: Fully parsed response with typed invoice digests
            
        Raises:
            NavValidationException: If parameters are invalid
            NavApiException: If API request fails
            NavXmlParsingException: If XML parsing fails
        """
        if page < 1:
            raise NavValidationException("Page number must be >= 1")

        if not invoice_query_params:
            raise NavValidationException("Invoice query parameters are required")

        try:
            # Create request using xsdata dataclasses
            request = self.create_query_invoice_digest_request(
                credentials=self.credentials,
                page=page,
                invoice_direction=invoice_direction,
                invoice_query_params=invoice_query_params
            )
            
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Make API call
            with self.http_client as client:
                response = client.post("queryInvoiceDigest", xml_request)
                xml_response = response.text
            
            # Parse response using generic parsing function
            parsed_response = self._parse_response_from_xml(xml_response, QueryInvoiceDigestResponse)
            
            logger.info(f"Successfully queried invoice digest for page {page}")
            return parsed_response

        except Exception as e:
            if isinstance(e, (NavValidationException, NavApiException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error querying invoice digest: {e}")
            raise NavApiException(f"Failed to query invoice digest: {e}")
      
    def query_invoice_data(
        self,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType,
        batch_index: Optional[int] = None,
        supplier_tax_number: Optional[str] = None
    ) -> QueryInvoiceDataResponse:
        """
        Query invoice data using xsdata-generated dataclasses.
        This uses automatic XML serialization and parsing for type-safe API interactions.
        
        Args:
            invoice_number: Invoice number to query
            invoice_direction: Invoice direction (OUTBOUND/INBOUND)
            batch_index: Optional batch index for batched invoices
            supplier_tax_number: Optional supplier tax number
            
        Returns:
            QueryInvoiceDataResponse: Fully parsed response with typed invoice data
            
        Raises:
            NavValidationException: If parameters are invalid
            NavInvoiceNotFoundException: If invoice not found
            NavApiException: If API request fails
            NavXmlParsingException: If XML parsing fails
        """
        if not invoice_number:
            raise NavValidationException("Invoice number is required")

        try:
            # Create request using xsdata dataclasses
            request = self.create_query_invoice_data_request(
                credentials=self.credentials,
                invoice_number=invoice_number,
                invoice_direction=invoice_direction,
                batch_index=batch_index,
                supplier_tax_number=supplier_tax_number
            )
            
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Make API call
            with self.http_client as client:
                response = client.post("queryInvoiceData", xml_request)
                xml_response = response.text
            
            # Parse response using generic parsing function
            parsed_response = self._parse_response_from_xml(xml_response, QueryInvoiceDataResponse)
            
            # Check if invoice was found
            if not parsed_response.invoice_data_result or not parsed_response.invoice_data_result.invoice_data:
                raise NavInvoiceNotFoundException(f"Invoice {invoice_number} not found")

            logger.info(f"Successfully queried invoice data for {invoice_number}")
            # Parse the Base64 encoded invoice data
            if parsed_response.invoice_data_result.invoice_data:
                try:
                    # The invoice_data field is already decoded from Base64 by xsdata, 
                    # but it's in bytes format containing XML (possibly compressed)
                    xml_bytes = parsed_response.invoice_data_result.invoice_data
                    
                    # Check if it's already a parsed object
                    if isinstance(xml_bytes, InvoiceData):
                        logger.info(f"Invoice data is already parsed as InvoiceData object")
                        return parsed_response
                    
                    # If it's bytes, check if it's compressed or not
                    if isinstance(xml_bytes, bytes):
                        # Check for gzip compression based on response indicator or magic bytes
                        is_compressed = False
                        if (hasattr(parsed_response.invoice_data_result, 'compressed_content_indicator') and 
                            parsed_response.invoice_data_result.compressed_content_indicator):
                            is_compressed = True
                            logger.debug("Data marked as compressed in response")
                        elif xml_bytes.startswith(b'\x1f\x8b'):  # GZIP magic bytes
                            is_compressed = True
                            logger.debug("Data appears to be gzipped (magic bytes detected)")
                        
                        # Decompress if needed
                        if is_compressed:
                            try:
                                xml_bytes = gzip.decompress(xml_bytes)
                                logger.debug(f"Successfully decompressed data, new length: {len(xml_bytes)}")
                            except Exception as decomp_error:
                                logger.error(f"Failed to decompress data: {decomp_error}")
                                raise NavXmlParsingException(f"Failed to decompress invoice data: {decomp_error}")
                        
                        # Try UTF-8 first, then fall back to other encodings
                        try:
                            xml_content = xml_bytes.decode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                # Try latin-1 which can handle any byte sequence
                                xml_content = xml_bytes.decode('latin-1')
                            except UnicodeDecodeError:
                                # Last resort - decode with error replacement
                                xml_content = xml_bytes.decode('utf-8', errors='replace')
                        
                        # Parse the decoded XML into InvoiceData object
                        parsed_invoice_data = self._parse_response_from_xml(xml_content, InvoiceData)
                        # Replace the bytes with the parsed object
                        parsed_response.invoice_data_result.invoice_data = parsed_invoice_data
                        logger.info(f"Successfully parsed invoice data XML for {invoice_number}")
                    else:
                        # If it's not bytes, log what it is and keep it
                        logger.warning(f"Invoice data is not bytes, it's {type(xml_bytes)}. Keeping as-is.")
                    
                except Exception as e:
                    logger.warning(f"Failed to parse invoice data XML: {e}")
                    # Keep the original bytes data if parsing fails
            
            logger.info(f"Successfully queried invoice data for {invoice_number}")
            return parsed_response

        except Exception as e:
            if isinstance(e, (NavValidationException, NavInvoiceNotFoundException, NavApiException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error querying invoice data: {e}")
            raise NavApiException(f"Failed to query invoice data: {e}")

    def query_invoice_check(
        self, request: QueryInvoiceCheckRequest
    ) -> QueryInvoiceCheckResponse:
        """
        Check if an invoice exists using xsdata-generated dataclasses.
        This uses automatic XML serialization and parsing for type-safe API interactions.

        Args:
            request: QueryInvoiceCheckRequest with proper API structure

        Returns:
            QueryInvoiceCheckResponse: Fully parsed response with typed check results

        Raises:
            NavValidationException: If request validation fails
            NavApiException: If API call fails
            NavXmlParsingException: If XML parsing fails
        """
        try:
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Make API call
            with self.http_client as client:
                response = client.post("queryInvoiceCheck", xml_request)
                xml_response = response.text

            # Parse response using generic parsing function
            parsed_response = self._parse_response_from_xml(xml_response, QueryInvoiceCheckResponse)
            
            logger.info(f"Successfully checked invoice: {request.invoice_number_query.invoice_number}")
            return parsed_response

        except Exception as e:
            if isinstance(e, (NavApiException, NavValidationException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error in query_invoice_check: {e}")
            raise NavApiException(f"Failed to check invoice: {str(e)}")

    def query_invoice_chain_digest(
        self, request: QueryInvoiceChainDigestRequest
    ) -> QueryInvoiceChainDigestResponse:
        """
        Query invoice chain digests using xsdata-generated dataclasses.
        This uses automatic XML serialization and parsing for type-safe API interactions.

        Args:
            request: QueryInvoiceChainDigestRequest with proper API structure

        Returns:
            QueryInvoiceChainDigestResponse: Fully parsed response with typed chain digest data

        Raises:
            NavValidationException: If request validation fails
            NavApiException: If API call fails
            NavXmlParsingException: If XML parsing fails
        """
        try:
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Make API call
            with self.http_client as client:
                response = client.post("queryInvoiceChainDigest", xml_request)
                xml_response = response.text

            # Parse response using generic parsing function
            parsed_response = self._parse_response_from_xml(xml_response, QueryInvoiceChainDigestResponse)
            
            logger.info(f"Successfully queried invoice chain digest for: {request.invoice_number}")
            return parsed_response

        except Exception as e:
            if isinstance(e, (NavApiException, NavValidationException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error in query_invoice_chain_digest: {e}")
            raise NavApiException(f"Failed to query invoice chain digest: {str(e)}")

    def query_transaction_status(
        self,
        transaction_id: str,
        return_original_request: Optional[bool] = None
    ) -> QueryTransactionStatusResponse:
        """
        Query transaction status using xsdata-generated dataclasses.
        This uses automatic XML serialization and parsing for type-safe API interactions.

        Args:
            transaction_id: The transaction ID to query status for
            return_original_request: Whether to return the original request data

        Returns:
            QueryTransactionStatusResponse: Fully parsed response with processing results

        Raises:
            NavValidationException: If parameters are invalid
            NavApiException: If API call fails
            NavXmlParsingException: If XML parsing fails
        """
        if not transaction_id or not transaction_id.strip():
            raise NavValidationException("Transaction ID is required and cannot be empty")

        if len(transaction_id) > 30:
            raise NavValidationException("Transaction ID cannot be longer than 30 characters")

        try:
            # Create request using helper method
            request = self.create_query_transaction_status_request(
                transaction_id=transaction_id,
                return_original_request=return_original_request
            )
            
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Make API call
            with self.http_client as client:
                response = client.post("queryTransactionStatus", xml_request)
                xml_response = response.text

            # Parse response using generic parsing function
            parsed_response = self._parse_response_from_xml(xml_response, QueryTransactionStatusResponse)
            
            logger.info(f"Successfully queried transaction status for: {transaction_id}")
            return parsed_response

        except Exception as e:
            if isinstance(e, (NavApiException, NavValidationException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error in query_transaction_status: {e}")
            raise NavApiException(f"Failed to query transaction status: {str(e)}")

    def get_token(self) -> TokenExchangeResponse:
        """
        Get exchange token from NAV API using xsdata-generated dataclasses.
        This uses automatic XML serialization and parsing for type-safe API interactions.

        Returns:
            TokenExchangeResponse: Complete response with token and validity information

        Raises:
            NavValidationException: If credentials are invalid
            NavApiException: If API call fails
            NavXmlParsingException: If XML parsing fails
        """
        try:
            # Create request using helper method
            request = self.create_token_exchange_request()
            
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Make API call
            with self.http_client as client:
                response = client.post("tokenExchange", xml_request)
                xml_response = response.text

            # Parse response using generic parsing function
            parsed_response = self._parse_response_from_xml(xml_response, TokenExchangeResponse)
            
            logger.info("Successfully obtained exchange token")
            return parsed_response

        except Exception as e:
            if isinstance(e, (NavApiException, NavValidationException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error in get_token: {e}")
            raise NavApiException(f"Failed to get token: {str(e)}")

    def get_invoice_chain_digest(
        self,
        page: int,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType = InvoiceDirectionType.OUTBOUND,
        tax_number: Optional[str] = None
    ) -> QueryInvoiceChainDigestResponse:
        """
        Convenience method to get invoice chain digest with automatic request creation.
        
        Args:
            page: Page number for pagination
            invoice_number: Invoice number to query
            invoice_direction: Direction of the invoice (default: OUTBOUND)
            tax_number: Optional tax number filter
        
        Returns:
            QueryInvoiceChainDigestResponse: Complete response with chain digest data
        """
        request = self.create_query_invoice_chain_digest_request(
            page=page,
            invoice_number=invoice_number,
            invoice_direction=invoice_direction,
            tax_number=tax_number
        )
        return self.query_invoice_chain_digest(request)

    def get_invoice_data(
        self,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType = InvoiceDirectionType.OUTBOUND,
        batch_index: Optional[int] = None,
        supplier_tax_number: Optional[str] = None
    ) -> InvoiceData:
        """
        Get invoice data and return a fully parsed InvoiceData dataclass.
        
        This function provides a high-level interface that:
        1. Uses query_invoice_data to get the API response
        2. Extracts and decodes the base64 invoice data
        3. Returns a typed InvoiceData dataclass
        
        Args:
            invoice_number: Invoice number to query
            invoice_direction: Invoice direction (default: OUTBOUND)
            batch_index: Optional batch index for batched invoices
            supplier_tax_number: Optional supplier tax number
            
        Returns:
            InvoiceData: Fully parsed invoice data as a dataclass
            
        Raises:
            NavValidationException: If parameters are invalid
            NavInvoiceNotFoundException: If invoice not found
            NavApiException: If API request fails
            NavXmlParsingException: If XML parsing fails
        """
        try:
            # Use query_invoice_data to get the full API response
            response = self.query_invoice_data(
                invoice_number=invoice_number,
                invoice_direction=invoice_direction,
                batch_index=batch_index,
                supplier_tax_number=supplier_tax_number
            )
            
            # Extract the already-parsed invoice data from the response
            if not response.invoice_data_result or not response.invoice_data_result.invoice_data:
                raise NavInvoiceNotFoundException(f"No invoice data found for invoice {invoice_number}")
            
            # query_invoice_data already parsed the XML into an InvoiceData object
            invoice_data = response.invoice_data_result.invoice_data
            
            # Ensure it's an InvoiceData object (should be after query_invoice_data processing)
            if not isinstance(invoice_data, InvoiceData):
                raise NavXmlParsingException(f"Expected InvoiceData object, got {type(invoice_data)}")
            
            logger.info(f"Successfully extracted invoice data for {invoice_number}")
            return invoice_data

        except Exception as e:
            if isinstance(e, (NavApiException, NavValidationException, NavInvoiceNotFoundException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error in get_invoice_data: {e}")
            raise NavApiException(f"Failed to get invoice data: {str(e)}")

    def get_exchange_token(self) -> str:
        """
        Convenience method to get and decode the exchange token string.
        
        Returns:
            str: The decoded exchange token
        """
        response = self.get_token()
        return decode_exchange_token(response.encoded_exchange_token, self.credentials.exchange_key)

    def check_invoice_exists(
        self,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType = InvoiceDirectionType.OUTBOUND,
        batch_index: Optional[int] = None,
        supplier_tax_number: Optional[str] = None
    ) -> bool:
        """
        Check if an invoice exists with a simplified interface.
        
        This function provides a high-level interface that:
        1. Creates the request using the provided parameters
        2. Calls query_invoice_check to get the API response
        3. Returns a simple boolean result
        
        Args:
            invoice_number: Invoice number to check
            invoice_direction: Invoice direction (default: OUTBOUND)
            batch_index: Optional batch index for batched invoices
            supplier_tax_number: Optional supplier tax number
            
        Returns:
            bool: True if invoice exists, False otherwise
            
        Raises:
            NavValidationException: If parameters are invalid
            NavApiException: If API request fails
            NavXmlParsingException: If XML parsing fails
        """
        try:
            # Create request using xsdata dataclasses
            request = self.create_query_invoice_check_request(
                invoice_number=invoice_number,
                invoice_direction=invoice_direction,
                batch_index=batch_index,
                supplier_tax_number=supplier_tax_number
            )
            
            # Get full response
            response = self.query_invoice_check(request)
            
            # Extract boolean result
            return response.invoice_check_result or False

        except Exception as e:
            if isinstance(e, (NavApiException, NavValidationException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error in check_invoice_exists: {e}")
            raise NavApiException(f"Failed to check if invoice exists: {str(e)}")

    def get_all_invoice_data_for_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        invoice_direction: InvoiceDirectionType = InvoiceDirectionType.OUTBOUND,
    ) -> List[tuple[InvoiceData, ManageInvoiceOperationType]]:
        """
        Get all invoice data for a given date range by first querying invoice digests
        and then fetching detailed data for each invoice.

        Args:
            start_date: Start date for the query range
            end_date: End date for the query range
            invoice_direction: Invoice direction to query (default: OUTBOUND)

        Returns:
            List[tuple[InvoiceData, ManageInvoiceOperationType]]: List of tuples containing 
            complete invoice data objects and their operation types

        Raises:
            NavValidationException: If parameters are invalid
            NavApiException: If API requests fail
        """
        if start_date >= end_date:
            raise NavValidationException("Start date must be before end date")

        # Validate date range is not too large
        date_diff = (end_date - start_date).days
        if date_diff > MAX_DATE_RANGE_DAYS:
            raise NavValidationException(
                f"Date range too large. Maximum allowed: {MAX_DATE_RANGE_DAYS} days"
            )

        all_invoice_data = []
        processed_count = 0

        try:
            logger.info(
                f"Starting comprehensive invoice data retrieval for date range: {start_date.date()} to {end_date.date()}"
            )

            # Step 1: Query invoice digests to get all invoices in the date range
            page = 1
            total_found = 0

            while True:
                logger.info(f"Querying invoice digests - page {page}")
                # Create invoice query params
                invoice_query_params = InvoiceQueryParamsType(
                    mandatory_query_params=MandatoryQueryParamsType(
                        invoice_issue_date=DateIntervalParamType(
                            date_from=start_date.strftime("%Y-%m-%d"),
                            date_to=end_date.strftime("%Y-%m-%d"),
                        )
                    )
                )

                # Query invoice digests
                digest_response = self.query_invoice_digest(
                    page=page,
                    invoice_direction=invoice_direction,
                    invoice_query_params=invoice_query_params
                )

                if not digest_response.invoice_digest_result or not digest_response.invoice_digest_result.invoice_digest:
                    logger.info(f"No more invoices found on page {page}")
                    break

                invoice_digests = digest_response.invoice_digest_result.invoice_digest
                total_found += len(invoice_digests)
                logger.info(
                    f"Found {len(invoice_digests)} invoices on page {page} (total so far: {total_found})"
                )

                # Step 2: Get detailed data for each invoice digest
                for digest in invoice_digests:
                    try:
                        logger.info(
                            f"Fetching details for invoice: {digest.invoice_number}"
                        )

                        # Create detailed data request
                        # For OUTBOUND invoices, don't include supplier_tax_number as it causes API error
                        # For INBOUND invoices, include supplier_tax_number if available
                        supplier_tax_for_request = None
                        if invoice_direction == InvoiceDirectionType.INBOUND:
                            supplier_tax_for_request = digest.supplier_tax_number

                        # Get detailed invoice data using the get_invoice_data method
                        # which returns the parsed InvoiceData object directly
                        invoice_data = self.get_invoice_data(
                            invoice_number=digest.invoice_number,
                            invoice_direction=invoice_direction,
                            batch_index=digest.batch_index,
                            supplier_tax_number=supplier_tax_for_request
                        )

                        if invoice_data:
                            # Combine invoice data with operation type from digest
                            all_invoice_data.append((invoice_data, digest.invoice_operation))
                            processed_count += 1

                            if processed_count % 10 == 0:
                                logger.info(
                                    f"Processed {processed_count} invoices so far..."
                                )
                        else:
                            logger.warning(
                                f"No detail data found for invoice: {digest.invoice_number}"
                            )

                    except NavInvoiceNotFoundException:
                        logger.warning(
                            f"Invoice details not found for: {digest.invoice_number}"
                        )
                        continue
                    except Exception as e:
                        logger.error(
                            f"Error processing invoice {digest.invoice_number}: {str(e)}"
                        )
                        # Continue with next invoice rather than failing completely
                        continue

                # Check if there are more pages
                if (
                    digest_response.invoice_digest_result.available_page is None
                    or page >= digest_response.invoice_digest_result.available_page
                ):
                    logger.info("All pages processed")
                    break

                page += 1

            logger.info(
                f"Completed invoice data retrieval. Total processed: {processed_count} invoices"
            )
            return all_invoice_data

        except (NavValidationException, NavApiException):
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in get_all_invoice_data_for_date_range: {str(e)}"
            )
            raise NavApiException(
                f"Unexpected error during comprehensive data retrieval: {str(e)}"
            )

    def create_manage_annulment_request(
        self,
        exchange_token: str,
        annulment_operations: List[Tuple[InvoiceAnnulment, int]],
        header_timestamp: Optional[str] = None
    ) -> ManageAnnulmentRequest:
        """
        Create a ManageAnnulmentRequest using generated models.
        
        Args:
            exchange_token: Decoded exchange token from /tokenExchange
            annulment_operations: List of tuples containing (InvoiceAnnulment, index)
            header_timestamp: Optional pre-generated timestamp to ensure consistency
            
        Returns:
            ManageAnnulmentRequest: Complete request ready for submission
        """
        # Create header with consistent timestamp
        if header_timestamp:
            header = self._create_basic_header_with_timestamp(header_timestamp)
        else:
            header = self._create_basic_header()
        software = self._create_software_info(self.credentials)
        
        # Create annulment operation list and prepare operation data for signature
        operations = []
        operation_data = []
        
        for annulment_data, index in annulment_operations:
            # Encode annulment data to base64 for signature calculation
            base64_data = encode_annulment_data_to_base64(annulment_data)
            
            # For the actual request, we need the raw XML bytes (xsdata will base64-encode it)
            xml_data = serialize_annulment_data_to_xml(annulment_data)
            
            # Log the annulment XML data being sent
            print("\n" + "="*80)
            print(f"🚫 ANNULMENT XML DATA (Index: {index})")
            print("="*80)
            print(xml_data)
            print("="*80)
            print(f"📋 Base64 Data Length: {len(base64_data)} characters")
            print("="*80 + "\n")
            
            operation = AnnulmentOperationType(
                index=index,
                annulment_operation=ManageAnnulmentOperationType.ANNUL,
                invoice_annulment=xml_data.encode('utf-8')  # Raw XML bytes for xsdata
            )
            operations.append(operation)
            
            # Prepare operation data for complex signature calculation
            # According to NAV API docs: annulmentOperation + base64 content
            operation_data.append(("ANNUL", base64_data))
        
        # Create user header with complex signature calculation
        user = self._create_user_header_with_complex_signature(
            self.credentials, 
            header, 
            operation_data
        )
        
        annulment_operation_list = AnnulmentOperationListType(
            annulment_operation=operations
        )
        
        return ManageAnnulmentRequest(
            header=header,
            user=user,
            software=software,
            exchange_token=exchange_token,
            annulment_operations=annulment_operation_list
        )

    def manage_annulment(
        self, request: ManageAnnulmentRequest
    ) -> ManageAnnulmentResponse:
        """
        Submit technical annulment request using xsdata-generated dataclasses.
        
        This operation is used to technically annul previously submitted invoices.
        Technical annulment can only be submitted for invoices that have DONE status
        and contain only warnings (WARN) or no validation messages.
        
        Args:
            request: ManageAnnulmentRequest with proper API structure
            
        Returns:
            ManageAnnulmentResponse: Fully parsed response with transaction ID
            
        Raises:
            NavValidationException: If request validation fails
            NavApiException: If API call fails
            NavXmlParsingException: If XML parsing fails
        """
        try:
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Log the complete annulment request XML being sent to NAV
            print("\n" + "="*80)
            print("🚫 TECHNICAL ANNULMENT REQUEST XML SENT TO NAV SERVER")
            print("="*80)
            print(xml_request)
            print("="*80 + "\n")
            
            logger.debug(f"Serialized ManageAnnulmentRequest XML: {xml_request}")
            
            # Make API call
            with self.http_client as client:
                response = client.post("manageAnnulment", xml_request)
                xml_response = response.text

            # Parse response using generic parsing function
            parsed_response = self._parse_response_from_xml(xml_response, ManageAnnulmentResponse)
            
            logger.info(f"Successfully submitted technical annulment request. Transaction ID: {parsed_response.transaction_id}")
            return parsed_response

        except Exception as e:
            if isinstance(e, (NavApiException, NavValidationException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error in manage_annulment: {e}")
            raise NavApiException(f"Failed to submit technical annulment: {str(e)}")

    def submit_technical_annulment(
        self,
        invoice_references: List[Tuple[str, AnnulmentCodeType, str]],
        exchange_key: str
    ) -> ManageAnnulmentResponse:
        """
        High-level method to submit technical annulment for invoices.
        
        This method handles the complete workflow:
        1. Get exchange token
        2. Decode exchange token
        3. Create annulment data
        4. Submit annulment request
        
        Args:
            invoice_references: List of tuples (invoice_number, annulment_code, reason)
            exchange_key: Technical user's exchange key for token decoding
            
        Returns:
            ManageAnnulmentResponse: API response with transaction details
            
        Raises:
            NavValidationException: If parameters are invalid
            NavApiException: If API call fails
        """
        try:
            # Generate single timestamp for consistency across request
            request_timestamp = format_timestamp_for_nav()
            
            # Step 1: Get exchange token
            logger.info("Requesting exchange token for technical annulment")
            token_response = self.get_token()
            
            # Step 2: Decode exchange token
            logger.info("Decoding exchange token")
            decoded_token = decode_exchange_token(
                token_response.encoded_exchange_token, 
                exchange_key
            )
            
            # Step 3: Create annulment operations using the same timestamp
            annulment_operations = []
            for index, (invoice_ref, code, reason) in enumerate(invoice_references, 1):
                annulment_data = InvoiceAnnulment(
                    annulment_reference=invoice_ref,
                    annulment_timestamp=request_timestamp,  # Use consistent timestamp
                    annulment_code=code,
                    annulment_reason=reason
                )
                annulment_operations.append((annulment_data, index))
            
            # Step 4: Create and submit request with consistent timestamp
            logger.info(f"Creating annulment request for {len(invoice_references)} invoices")
            request = self.create_manage_annulment_request(
                exchange_token=decoded_token,
                annulment_operations=annulment_operations,
                header_timestamp=request_timestamp  # Use same timestamp for header
            )
            
            # Submit the request
            response = self.manage_annulment(request)
            
            logger.info(f"Technical annulment submitted successfully. Transaction ID: {response.transaction_id}")
            return response
            
        except Exception as e:
            if isinstance(e, (NavValidationException, NavApiException, NavXmlParsingException)):
                raise
            logger.error(f"Failed to submit technical annulment: {e}")
            raise NavApiException(f"Technical annulment failed: {e}")

    def create_manage_invoice_request(
        self,
        exchange_token: str,
        invoice_operations: List[Tuple[InvoiceData, ManageInvoiceOperationType, int]],
        header_timestamp: Optional[str] = None
    ) -> ManageInvoiceRequest:
        """
        Create a manage invoice request with proper structure and complex signature.
        
        Args:
            exchange_token: Decoded exchange token from NAV
            invoice_operations: List of tuples (invoice_data, operation_type, index)
            header_timestamp: Optional timestamp for consistent request timing
            
        Returns:
            ManageInvoiceRequest: Properly structured request for NAV API
            
        Raises:
            NavValidationException: If parameters are invalid
        """
        from nav_online_szamla.utils import (
            serialize_invoice_data_to_xml, 
            encode_invoice_data_to_base64,
            calculate_complex_request_signature
        )
        
        if not exchange_token:
            raise NavValidationException("Exchange token is required")
        if not invoice_operations:
            raise NavValidationException("At least one invoice operation is required")
        
        # Use provided timestamp or generate new one for consistency
        if header_timestamp is None:
            header_timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'
        
        # Create invoice operation list
        invoice_operation_list = []
        index_hash_inputs = []  # For complex signature calculation
        
        for invoice_data, operation_type, index in invoice_operations:
            # Serialize and encode invoice data
            xml_data = serialize_invoice_data_to_xml(invoice_data)
            
            # Log the XML data being sent
            print("\n" + "="*80)
            print(f"📋 INVOICE XML DATA (Operation: {operation_type.value}, Index: {index})")
            print("="*80)
            print(xml_data)
            print("="*80)
            
            base64_data = encode_invoice_data_to_base64(xml_data)
            
            # Calculate electronic invoice hash for electronic invoices
            # According to NAV docs, this is required when completenessIndicator is true
            electronic_hash = calculate_electronic_invoice_hash(base64_data)
            electronic_invoice_hash = CryptoType(
                value=electronic_hash,
                crypto_type="SHA3-512"
            )
            
            print(f"📋 Electronic Invoice Hash: {electronic_hash}")
            print(f"📋 Base64 Data Length: {len(base64_data)} characters")
            print("="*80 + "\n")
            
            # Create invoice operation
            operation = InvoiceOperationType(
                index=index,
                invoice_operation=operation_type,
                invoice_data=base64_data,
                electronic_invoice_hash=electronic_invoice_hash
            )
            invoice_operation_list.append(operation)
            
            # Collect data for complex signature calculation
            index_hash_inputs.append((operation_type.value, base64_data))
        
        # Create invoice operations list
        operations_list = InvoiceOperationListType(
            compressed_content=False,
            invoice_operation=invoice_operation_list
        )
        
        # Create basic header first to get request_id and timestamp
        header = self._create_basic_header()
        
        # Create user header with complex signature calculation
        user_header = self._create_user_header_with_complex_signature(
            self.credentials,
            header,
            index_hash_inputs
        )
        
        # Create complete request
        request = ManageInvoiceRequest(
            header=header,
            user=user_header,
            software=self._create_software_info(self.credentials),
            exchange_token=exchange_token,
            invoice_operations=operations_list
        )
        
        return request

    def manage_invoice(self, request: ManageInvoiceRequest) -> ManageInvoiceResponse:
        """
        Submit invoice data using xsdata-generated dataclasses.
        
        This operation is used to submit new invoices, modifications, or storno operations.
        
        Args:
            request: ManageInvoiceRequest with proper API structure
            
        Returns:
            ManageInvoiceResponse: Fully parsed response with transaction ID
            
        Raises:
            NavValidationException: If request validation fails
            NavApiException: If API call fails
            NavXmlParsingException: If XML parsing fails
        """
        if not request:
            raise NavValidationException("Request is required")
        
        try:
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Log the complete request XML being sent to NAV
            print("\n" + "="*80)
            print("🚀 COMPLETE REQUEST XML SENT TO NAV SERVER")
            print("="*80)
            print(xml_request)
            print("="*80 + "\n")
            
            # Make API call
            with self.http_client as client:
                response = client.post("manageInvoice", xml_request)
                xml_response = response.text
                
            # Log the response for debugging
            logger.info(f"Received response from manageInvoice API")
            logger.debug(f"Raw response XML: {xml_response[:1000]}...")

            # Parse response
            parsed_response = self._parse_response_from_xml(xml_response, ManageInvoiceResponse)
            
            return parsed_response
            
        except Exception as e:
            if isinstance(e, (NavValidationException, NavApiException, NavXmlParsingException)):
                raise
            logger.error(f"Failed to manage invoice: {e}")
            raise NavApiException(f"Invoice management failed: {e}")

    def submit_invoice(
        self,
        invoice_data: InvoiceData,
        operation_type: ManageInvoiceOperationType = ManageInvoiceOperationType.CREATE,
        exchange_key: str = None
    ) -> ManageInvoiceResponse:
        """
        High-level method to submit a single invoice to NAV.
        
        This method handles the complete workflow:
        1. Get exchange token
        2. Decode exchange token  
        3. Create invoice request
        4. Submit invoice
        
        Args:
            invoice_data: InvoiceData object to submit
            operation_type: Type of operation (CREATE, MODIFY, STORNO)
            exchange_key: Technical user's exchange key for token decoding
            
        Returns:
            ManageInvoiceResponse: API response with transaction details
            
        Raises:
            NavValidationException: If parameters are invalid
            NavApiException: If API call fails
        """
        if not invoice_data:
            raise NavValidationException("Invoice data is required")
        
        # Use provided exchange key or fall back to credentials
        if exchange_key is None:
            if hasattr(self.credentials, 'exchange_key'):
                exchange_key = self.credentials.exchange_key
            else:
                raise NavValidationException("Exchange key is required for invoice submission")
        
        try:
            # Generate consistent timestamp for the entire operation
            request_timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'
            
            # Step 1: Get exchange token
            logger.info("Requesting exchange token for invoice submission")
            token_response = self.get_token()
            
            # Step 2: Decode exchange token
            logger.info("Decoding exchange token")
            decoded_token = decode_exchange_token(
                token_response.encoded_exchange_token, 
                exchange_key
            )
            
            # Step 3: Create invoice operations
            invoice_operations = [(invoice_data, operation_type, 1)]
            
            # Step 4: Create and submit request
            logger.info(f"Creating invoice request with operation: {operation_type.value}")
            request = self.create_manage_invoice_request(
                exchange_token=decoded_token,
                invoice_operations=invoice_operations,
                header_timestamp=request_timestamp
            )
            
            # Submit the request
            response = self.manage_invoice(request)
            
            logger.info(f"Invoice submitted successfully. Transaction ID: {response.transaction_id}")
            return response
            
        except Exception as e:
            if isinstance(e, (NavValidationException, NavApiException, NavXmlParsingException)):
                raise
            logger.error(f"Failed to submit invoice: {e}")
            raise NavApiException(f"Invoice submission failed: {e}")

    def submit_multiple_invoices(
        self,
        invoice_operations: List[Tuple[InvoiceData, ManageInvoiceOperationType]],
        exchange_key: str = None
    ) -> ManageInvoiceResponse:
        """
        High-level method to submit multiple invoices in a single batch to NAV.
        
        Args:
            invoice_operations: List of tuples (invoice_data, operation_type)
            exchange_key: Technical user's exchange key for token decoding
            
        Returns:
            ManageInvoiceResponse: API response with transaction details
            
        Raises:
            NavValidationException: If parameters are invalid
            NavApiException: If API call fails
        """
        if not invoice_operations:
            raise NavValidationException("At least one invoice operation is required")
        
        if len(invoice_operations) > 100:
            raise NavValidationException("Maximum 100 invoice operations allowed per batch")
        
        # Use provided exchange key or fall back to credentials
        if exchange_key is None:
            if hasattr(self.credentials, 'exchange_key'):
                exchange_key = self.credentials.exchange_key
            else:
                raise NavValidationException("Exchange key is required for invoice submission")
        
        try:
            # Generate consistent timestamp for the entire operation
            request_timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'
            
            # Step 1: Get exchange token
            logger.info("Requesting exchange token for batch invoice submission")
            token_response = self.get_token()
            
            # Step 2: Decode exchange token
            logger.info("Decoding exchange token")
            decoded_token = decode_exchange_token(
                token_response.encoded_exchange_token, 
                exchange_key
            )
            
            # Step 3: Add index to each operation
            indexed_operations = []
            for index, (invoice_data, operation_type) in enumerate(invoice_operations, 1):
                indexed_operations.append((invoice_data, operation_type, index))
            
            # Step 4: Create and submit request
            logger.info(f"Creating batch invoice request with {len(invoice_operations)} operations")
            request = self.create_manage_invoice_request(
                exchange_token=decoded_token,
                invoice_operations=indexed_operations,
                header_timestamp=request_timestamp
            )
            
            # Submit the request
            response = self.manage_invoice(request)
            
            logger.info(f"Batch invoice submitted successfully. Transaction ID: {response.transaction_id}")
            return response
            
        except Exception as e:
            if isinstance(e, (NavValidationException, NavApiException, NavXmlParsingException)):
                raise
            logger.error(f"Failed to submit batch invoice: {e}")
            raise NavApiException(f"Batch invoice submission failed: {e}")

    def get_environment_info(self) -> dict:
        """
        Get information about the current environment configuration.
        
        Returns:
            dict: Environment information including URLs and settings
        """
        info = {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "environment": self.environment.value
        }
        
        info.update({
            "is_test_environment": self.environment == NavEnvironment.TEST,
            "is_production_environment": self.environment == NavEnvironment.PRODUCTION
        })
        
        return info
    
    def is_test_environment(self) -> bool:
        """Check if the client is configured for the test environment."""
        return self.environment == NavEnvironment.TEST
    
    def is_production_environment(self) -> bool:
        """Check if the client is configured for the production environment."""
        return self.environment == NavEnvironment.PRODUCTION

    def close(self):
        """Close the HTTP client."""
        self.http_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
