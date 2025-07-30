# Original transformation
damping_level = 80  # Example integer within the range
byte_string = damping_level.to_bytes(2, byteorder='big')
print("Byte string:", byte_string)

# Inverse transformation
byte_string = b'\x00\xa0'
recovered_damping_level = int.from_bytes(byte_string, byteorder='big')
print("Recovered integer:", recovered_damping_level)