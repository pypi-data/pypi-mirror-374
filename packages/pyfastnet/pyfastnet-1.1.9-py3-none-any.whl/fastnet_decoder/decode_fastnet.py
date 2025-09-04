import datetime
from .utils import calculate_checksum, convert_segment_b_to_char, convert_segment_a_to_char
from .mappings import  ADDRESS_LOOKUP, COMMAND_LOOKUP,  CHANNEL_LOOKUP, FORMAT_SIZE_MAP
from .logger import logger



def decode_frame(frame: bytes) -> dict:
    try:
        logger.debug(f"Starting frame decoding. Frame length: {len(frame)}, Frame contents: {frame.hex()}")

        # Parse the header
        to_address     = frame[0]
        from_address   = frame[1]
        body_size      = frame[2]
        command        = frame[3]
        header_checksum= frame[4]
        body           = frame[5:-1]
        body_checksum  = frame[-1]

        logger.debug(
            f"Parsed header: to_address=0x{to_address:02X}, from_address=0x{from_address:02X}, "
            f"body_size={body_size}, command=0x{command:02X}, header_checksum=0x{header_checksum:02X}"
        )

        # Validate checksums
        if calculate_checksum(frame[:4]) != header_checksum:
            logger.info(f"Header checksum mismatch. Frame dropped: {frame.hex()}")
            return {"error": "Header checksum mismatch"}

        if calculate_checksum(body) != body_checksum:
            logger.info(f"Body checksum mismatch. Frame dropped: {frame.hex()}")
            return {"error": "Body checksum mismatch"}

        # Validate body size explicitly
        if len(body) < 2 or len(body) != body_size:
            logger.info(
                f"Invalid body size: Expected {body_size}, Actual {len(body)}. Frame: {frame.hex()}"
            )
            return {"error": "Invalid body size"}

        logger.debug("Header and body checksums are valid.")

        decoded_data = {
            "to_address": ADDRESS_LOOKUP.get(to_address, f"Unknown (0x{to_address:02X})"),
            "from_address": ADDRESS_LOOKUP.get(from_address, f"Unknown (0x{from_address:02X})"),
            "command":     COMMAND_LOOKUP.get(command,     f"Unknown (0x{command:02X})"),
            "values":     {}
        }

        # Decode body
        index = 0
        while index < len(body):
            # Make sure we have at least channel ID + format byte
            if index + 1 >= len(body):
                logger.info(
                    f"Insufficient bytes to decode channel ID and format byte at index {index}. "
                    f"Remaining length: {len(body) - index}"
                )
                return {"error": "Insufficient bytes for channel header"}

            channel_id  = body[index]
            format_byte = body[index + 1]
            index      += 2

            # Determine how many data bytes this format expects
            data_length = FORMAT_SIZE_MAP.get(format_byte & 0x0F, 0)
            if index + data_length > len(body):
                logger.info(
                    f"Incomplete data for channel 0x{channel_id:02X}. "
                    f"Expected length: {data_length}, Available: {len(body) - index}"
                )
                return {"error": f"Incomplete data for channel 0x{channel_id:02X}"}

            data_bytes = body[index:index + data_length]
            index     += data_length

            # Decode the actual value
            decoded_value = decode_format_and_data(channel_id, format_byte, data_bytes)
            channel_name  = CHANNEL_LOOKUP.get(channel_id, f"Unknown (0x{channel_id:02X})")

            decoded_data["values"][channel_name] = decoded_value
            logger.debug(f"Decoded value for channel {channel_name}: {decoded_value}")

        return decoded_data

    except Exception as e:
        logger.error(f"Unexpected error during frame decoding: {e}. Frame contents: {frame.hex()}")
        return {"error": "Decoding failure"}



# def decode_frame(frame: bytes) -> dict:
#     try:
#         logger.debug(f"Starting frame decoding. Frame length: {len(frame)}, Frame contents: {frame.hex()}")

#         # Parse the header
#         to_address = frame[0]
#         from_address = frame[1]
#         body_size = frame[2]
#         command = frame[3]
#         header_checksum = frame[4]
#         body = frame[5:-1]
#         body_checksum = frame[-1]

#         logger.debug(f"Parsed header: to_address=0x{to_address:02X}, from_address=0x{from_address:02X}, "
#                      f"body_size={body_size}, command=0x{command:02X}, header_checksum=0x{header_checksum:02X}")

#         # Validate checksums
#         if calculate_checksum(frame[:4]) != header_checksum:
#             logger.info(f"Header checksum mismatch. Frame dropped: {frame.hex()}")
#             return {"error": "Header checksum mismatch"}

#         if calculate_checksum(body) != body_checksum:
#             logger.info(f"Body checksum mismatch. Frame dropped: {frame.hex()}")
#             return {"error": "Body checksum mismatch"}

#         # Validate body size explicitly
#         if len(body) < 2 or len(body) != body_size:
#             logger.info(f"Invalid body size: Expected {body_size}, Actual {len(body)}. Frame: {frame.hex()}")
#             return {"error": "Invalid body size"}

#         logger.debug("Header and body checksums are valid.")

#         # Decode frame...
#         decoded_data = {
#             "to_address": ADDRESS_LOOKUP.get(to_address, f"Unknown (0x{to_address:02X})"),
#             "from_address": ADDRESS_LOOKUP.get(from_address, f"Unknown (0x{from_address:02X})"),
#             "command": COMMAND_LOOKUP.get(command, f"Unknown (0x{command:02X})"),
#             "values": {}
#         }

#         # Decode body
#         index = 0
#         while index < len(body):
#             if index + 1 >= len(body):
#                 raise ValueError(f"Insufficient bytes to decode channel ID and format byte at index {index}. Remaining length: {len(body) - index}")

#             channel_id = body[index]
#             format_byte = body[index + 1]
#             index += 2

#             data_length = FORMAT_SIZE_MAP.get(format_byte & 0x0F, 0)
#             if index + data_length > len(body):
#                 raise ValueError(f"Incomplete data for channel 0x{channel_id:02X}. Expected length: {data_length}, Available: {len(body) - index}")

#             data_bytes = body[index:index + data_length]
#             index += data_length

#             decoded_value = decode_format_and_data(channel_id, format_byte, data_bytes)
#             channel_name = CHANNEL_LOOKUP.get(channel_id, f"Unknown (0x{channel_id:02X})")

#             decoded_data["values"][channel_name] = decoded_value
#             logger.debug(f"Decoded value for channel {channel_name}: {decoded_value}")

#         return decoded_data

#     except Exception as e:
#         logger.error(f"Error during frame decoding: {e}. Frame contents: {frame.hex()}")
#         return None








        

def decode_ascii_frame(frame: bytes) -> dict:
    """
    Decodes an ASCII FastNet frame and returns interpreted values.
    
    Args:
        frame (bytes): The full ASCII frame (header + body).
        
    Returns:
        dict: Decoded data including addresses, command, and channel values.
    """
    try:
        to_address = frame[0]
        from_address = frame[1]
        body_size = frame[2]
        command = frame[3]
        header_checksum = frame[4]
        body = frame[5:-1]  # Body starts after header checksum
        body_checksum = frame[-1]

        channel_id = body[0]
        format_byte = body[1]
        data_bytes = body[2:]

        channel_name = CHANNEL_LOOKUP.get(channel_id, f"Unknown (0x{channel_id:02X})")

        try:
            ascii_text = data_bytes.decode("ascii").strip()
            interpreted_value = ascii_text
            raw_value = ascii_text
        except UnicodeDecodeError as decode_error:
            logger.error(f"Failed to decode ASCII text: {decode_error}")
            return {"error": "ASCII decode failed"}

        decoded_data = {
            "to_address": ADDRESS_LOOKUP.get(to_address, f"Unknown (0x{to_address:02X})"),
            "from_address": ADDRESS_LOOKUP.get(from_address, f"Unknown (0x{from_address:02X})"),
            "command": COMMAND_LOOKUP.get(command, f"Unknown (0x{command:02X})"),
            "values": {
                channel_name: {
                    "channel_id": f"0x{channel_id:02X}",
                    "format_byte": f"0x{format_byte:02X}",
                    "data_bytes": data_bytes.hex(),
                    "raw": raw_value,
                    "interpreted": interpreted_value
                }
            }
        }

        return decoded_data

    except Exception as e:
        logger.error(f"Error decoding ASCII frame: {e}")
        return {"error": str(e)}

def decode_format_and_data(channel_id, format_byte, data_bytes):
    """
    Decodes the format byte and interprets the data accordingly.

    Args:
        channel_id (int): Channel ID (from `CHANNEL_LOOKUP`).
        format_byte (int): The format byte indicating divisor, digits, and data interpretation.
        data_bytes (bytes): The raw data to decode.

    Returns:
        dict: Decoded results including format details and the final interpreted value.
    """
    try:
        logger.debug(f"Decoding channel ID: 0x{channel_id:02X}, format byte: 0x{format_byte:02X}, data: {data_bytes.hex()}")

        # Extract format information from the format byte
        divisor_bits = (format_byte >> 6) & 0b11  # First two bits
        digits_bits = (format_byte >> 4) & 0b11   # Next two bits
        format_bits = format_byte & 0b1111        # Last four bits

        # Map divisor and digits bits to actual values
        divisor_map = {0b00: 1, 0b01: 10, 0b10: 100, 0b11: 1000}
        digits_map = {0b00: 1, 0b01: 2, 0b10: 3, 0b11: 4}

        divisor = divisor_map.get(divisor_bits, 1)
        digits = digits_map.get(digits_bits, 1)

        if len(data_bytes) == 0:
            logger.warning("decode_format_and_data: Empty data bytes; cannot decode.")
            return None

        # Decode based on format bits
        if format_bits == 0x01:  # 16-bit signed integer
            if len(data_bytes) != 2:
                logger.warning("Data length mismatch for 16-bit signed integer (expected 2 bytes).")
                return None
            raw_value = int.from_bytes(data_bytes, byteorder="big", signed=True)
            interpreted_value = raw_value / divisor

        elif format_bits == 0x02:  # 6-bit segment + 10-bit unsigned value
            if len(data_bytes) != 2:
                logger.warning("Data length mismatch for 6-bit segment + 10-bit unsigned (expected 2 bytes).")
                return None
            segment_code = (data_bytes[0] >> 2) & 0b111111  # 6-bit segment code
            unsigned_value = ((data_bytes[0] & 0b11) << 8) | data_bytes[1]  # 10-bit unsigned value
            interpreted_value = unsigned_value / divisor
            raw_value = {"segment_code": segment_code, "unsigned_value": unsigned_value}

        elif format_bits == 0x03:  
            if len(data_bytes) != 2:
                logger.warning("Data length mismatch for 7-bit segment + 9-bit unsigned (expected 2 bytes).")
                return None
            # 7-bit segment + 9-bit unsigned - think this is wrong, believe to be  8+8 as per below
            #segment_code = (data_bytes[0] >> 1) & 0b01111111  # 7-bit segment
            #unsigned_value = ((data_bytes[0] & 0b1) << 8) | data_bytes[1]  # 9-bit unsigned value
            segment_code = data_bytes[0]
            unsigned_value = data_bytes[1]

            layout = convert_segment_a_to_char(segment_code)
            if layout == "-[data]" or layout == "=[data]":
                signed_value = -unsigned_value 
            else:
                signed_value = unsigned_value
            interpreted_value = signed_value / divisor
            raw_value = {"segment_code": hex(segment_code), "segment_code_bin": bin(segment_code), "unsigned_value": unsigned_value, "layout": layout}

        elif format_bits == 0x04:  # 8-bit segment + 24-bit unsigned value
            if len(data_bytes) != 4:
                logger.warning("Data length mismatch for 8-bit + 24-bit unsigned (expected 4 bytes).")
                return None
            segment_code = data_bytes[0]  # 8-bit segment code
            unsigned_value = int.from_bytes(data_bytes[1:], byteorder="big", signed=False)  # 24-bit unsigned value
            interpreted_value = unsigned_value / divisor
            raw_value = {"segment_code": segment_code, "unsigned_value": unsigned_value}

        elif format_bits == 0x05:  # Timer format (XX YY ZZ WW)
            if len(data_bytes) != 4:
                logger.warning("Data length mismatch for timer format (expected 4 bytes).")
                return None
            useless = data_bytes[0]  # Useless byte (can be ignored)
            hours = data_bytes[1]  # Hours (may exceed 24)
            minutes = data_bytes[2]  # Minutes
            seconds = data_bytes[3]  # Seconds
            interpreted_value = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
            raw_value = {"useless": useless, "hours": hours, "minutes": minutes, "seconds": seconds}

        elif format_bits == 0x06:  # 7-segment display text
            if len(data_bytes) != 4:
                logger.warning("Data length mismatch for 7-segment display text (expected 4 bytes).")
                return None
            segment_text = "".join(convert_segment_b_to_char(byte) for byte in data_bytes)
            logger.debug(f"Decoded 7-segment text: {segment_text}")
            raw_value = [f"{byte:02X}" for byte in data_bytes]  # Raw bytes as hex strings
            interpreted_value = segment_text

        elif format_bits == 0x07:  # 15-bit unsigned value with 4-byte input
            if len(data_bytes) != 4:
                logger.warning("Data length mismatch for 15-bit unsigned (expected 4 bytes).")
                return None
            # unused - SegCodeA - 7bit MSB, 8 bit LSB
            segment_code = data_bytes[1]
            msb = (data_bytes[2] >> 1) & 0b01111111  # 7 bits from third byte
            lsb = data_bytes[3]  # Full 8 bits from fourth byte
            unsigned_value = (msb << 8) | lsb  # Combine MSB and LSB into 15-bit value

            layout = convert_segment_a_to_char(segment_code)
            if layout == "H[data]" or layout == "-[data]":
                signed_value = -unsigned_value 
            else:
                signed_value = unsigned_value
            
            interpreted_value = signed_value / divisor
            
            raw_value = {"segment_code": hex(segment_code), "segment_code_bin": bin(segment_code), "unsigned_value": unsigned_value, "layout": layout}


        #elif format_bits == 0x07:  # 15-bit unsigned value with 4-byte input
        #    if len(data_bytes) != 4:
        #        logger.warning("Data length mismatch for 15-bit unsigned (expected 4 bytes).")
        #        return None
        #    msb = (data_bytes[2] >> 1) & 0b01111111  # 7 bits from third byte
        #    lsb = data_bytes[3]  # Full 8 bits from fourth byte
        #    unsigned_value = (msb << 8) | lsb  # Combine MSB and LSB into 15-bit value
        #    interpreted_value = unsigned_value / divisor
        #    raw_value = unsigned_value


        elif format_bits == 0x08:  # 7-bit segment + 9-bit unsigned (0x08 format)
            if len(data_bytes) != 2:
                logger.warning("decode_format_and_data: Data length mismatch for 0x08 (7-bit segment + 9-bit unsigned).")
                return None
            segment_code = (data_bytes[0] >> 1) & 0b01111111  # 7-bit segment
            unsigned_value = ((data_bytes[0] & 0b1) << 8) | data_bytes[1]  # 9-bit unsigned value
            interpreted_value = unsigned_value / divisor
            raw_value = {"segment_code": segment_code, "unsigned_value": unsigned_value}

        elif format_bits == 0x0A:  # 16-bit signed + 16-bit signed
            if len(data_bytes) != 4:
                logger.warning("Data length mismatch for 16-bit + 16-bit signed (expected 4 bytes).")
                return None
            first_value = int.from_bytes(data_bytes[:2], byteorder="big", signed=True)  # First 16-bit signed integer
            second_value = int.from_bytes(data_bytes[2:], byteorder="big", signed=True)  # Second 16-bit signed integer
            interpreted_first_value = first_value / divisor
            interpreted_second_value = second_value / divisor
            interpreted_value = interpreted_first_value
            raw_value = {"first": interpreted_first_value, "second": interpreted_second_value}


        else:
            logger.warning(f"Unsupported format: 0x{format_bits:02X}.")
            return None

        # Return the result
        result = {
            "channel_id": f"0x{channel_id:02X}",
            "format_byte": f"0x{format_byte:02X}",
            "data_bytes": data_bytes.hex(),
            "divisor": divisor,
            "digits": digits,
            "format_bits": format_bits,
            "raw": raw_value,
            "interpreted": interpreted_value
        }
        #ogger.debug(f"Decoded value for channel 0x{channel_id:02X}: {interpreted_value}")
        return result

    except Exception as e:
        logger.error(f"Error decoding channel 0x{channel_id:02X}: {e}")
        return None