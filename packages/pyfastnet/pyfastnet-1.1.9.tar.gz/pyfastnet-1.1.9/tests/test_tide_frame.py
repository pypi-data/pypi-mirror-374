import unittest
from fastnet_decoder.decode_fastnet import decode_frame

class TestCustomFrame(unittest.TestCase):
    def test_custom_frame(self):
        """
        Test decoding a custom frame using the provided hex string.
        """
        # Hex string provided by the user
        #hex_string = "ff121601d84661003cba0600627200b406bee8e80006060062720061"
        hex_string = "ff600a019684070066010e8383bb023d"
        
        # Convert hex string to bytes
        frame_data = bytes.fromhex(hex_string)

        # Decode the frame
        decoded = decode_frame(frame_data)

        # Validate the output
        self.assertIsInstance(decoded, dict, "Decoded frame should return a dictionary")
        self.assertIn("command", decoded, "Decoded frame should have a command field")
        self.assertIn("values", decoded, "Decoded frame should have a values dictionary")

        # Print decoded contents for debugging
        print("Decoded frame contents:")
        for key, value in decoded.items():
            print(f"{key}: {value}")

        # Example assertion: Ensure no error in decoding
        self.assertNotIn("error", decoded, "Frame should not return an error during decoding")

if __name__ == "__main__":
    unittest.main()
