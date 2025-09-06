# YTTP - Custom HTTP Parser

## Project Objective

This project implements a custom HTTP parser that supports messages with or without request lines, unlike h11 which requires request lines.

### Key Features

- **Flexible Message Parsing**: Supports both standard HTTP requests and header-only messages (like LSP/MCP protocols)
- **Event-driven Architecture**: Compatible with h11's interface using Request, Headers, Data, and EndOfMessage events
- **Content-Length Body Parsing**: Handles fixed-length message bodies
- **Chunked Transfer Encoding**: Supports chunked message parsing with hex size indicators
- **Error Handling**: Uses Result[T] pattern for consistent error handling without exceptions

### Technical Implementation

The parser uses a state machine approach:
1. `WANT_REQUEST_OR_HEADERS`: Determines if first line is HTTP request or header
2. `WANT_HEADERS`: Parses header section  
3. `WANT_BODY`: Parses message body based on Content-Length or Transfer-Encoding
4. `COMPLETE`: Message fully parsed

### Use Case

Enables parsing of protocols that send header-only messages without HTTP request lines, which h11 cannot handle due to its strict HTTP compliance requirements.