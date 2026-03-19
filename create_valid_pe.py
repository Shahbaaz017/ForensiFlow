#!/usr/bin/env python3
"""
Create a minimal valid PE file for capa testing
"""
import struct
import os

def create_minimal_pe(filename):
    """Create a minimal but valid PE executable"""
    
    # DOS Header (64 bytes)
    dos_header = bytearray(64)
    dos_header[0:2] = b'MZ'  # Signature
    dos_header[0x3c:0x40] = struct.pack('<I', 64)  # Offset to PE header
    
    # DOS Stub (minimal)
    dos_stub = b'\x0e\x1f\xba\x0e\x00\xb4\x09\xcd\x21\xb8\x01\x4c\xcd\x21'
    dos_stub += b'This program cannot be run in DOS mode.\r\r\n$\x00\x00\x00\x00'
    dos_stub = dos_stub.ljust(64, b'\x00')
    
    # PE Signature
    pe_sig = b'PE\x00\x00'
    
    # COFF Header (20 bytes)
    coff_header = bytearray(20)
    coff_header[0:2] = struct.pack('<H', 0x014c)      # Machine (i386)
    coff_header[2:4] = struct.pack('<H', 1)           # Number of sections
    coff_header[4:8] = struct.pack('<I', 0)           # TimeDateStamp
    coff_header[8:12] = struct.pack('<I', 0)          # PointerToSymbolTable
    coff_header[12:16] = struct.pack('<I', 0)         # NumberOfSymbols
    coff_header[16:18] = struct.pack('<H', 224)       # SizeOfOptionalHeader
    coff_header[18:20] = struct.pack('<H', 0x0102)    # Characteristics (executable, 32-bit)
    
    # Optional Header (224 bytes for PE32)
    opt_header = bytearray(224)
    opt_header[0:2] = struct.pack('<H', 0x010b)       # Magic (PE32)
    opt_header[2:3] = bytes([0x0a])                   # MajorLinkerVersion
    opt_header[3:4] = bytes([0x00])                   # MinorLinkerVersion
    opt_header[4:8] = struct.pack('<I', 0x1000)       # SizeOfCode
    opt_header[8:12] = struct.pack('<I', 0)           # SizeOfInitializedData
    opt_header[12:16] = struct.pack('<I', 0)          # SizeOfUninitializedData
    opt_header[16:20] = struct.pack('<I', 0x1000)     # AddressOfEntryPoint
    opt_header[20:24] = struct.pack('<I', 0x1000)     # BaseOfCode
    opt_header[24:28] = struct.pack('<I', 0x2000)     # BaseOfData
    opt_header[28:32] = struct.pack('<I', 0x400000)   # ImageBase
    opt_header[32:36] = struct.pack('<I', 0x1000)     # SectionAlignment
    opt_header[36:40] = struct.pack('<I', 0x200)      # FileAlignment
    opt_header[40:42] = struct.pack('<H', 0x06)       # MajorOperatingSystemVersion
    opt_header[42:44] = struct.pack('<H', 0x00)       # MinorOperatingSystemVersion
    opt_header[44:46] = struct.pack('<H', 0x00)       # MajorImageVersion
    opt_header[46:48] = struct.pack('<H', 0x00)       # MinorImageVersion
    opt_header[48:50] = struct.pack('<H', 0x06)       # MajorSubsystemVersion
    opt_header[50:52] = struct.pack('<H', 0x00)       # MinorSubsystemVersion
    opt_header[52:56] = struct.pack('<I', 0)          # Win32VersionValue
    opt_header[56:60] = struct.pack('<I', 0x2000)     # SizeOfImage
    opt_header[60:64] = struct.pack('<I', 0x400)      # SizeOfHeaders
    opt_header[64:68] = struct.pack('<I', 0)          # CheckSum
    opt_header[68:70] = struct.pack('<H', 3)          # Subsystem (Windows CUI)
    opt_header[70:72] = struct.pack('<H', 0x8140)     # DllCharacteristics
    opt_header[72:76] = struct.pack('<I', 0x100000)   # SizeOfStackReserve
    opt_header[76:80] = struct.pack('<I', 0x1000)     # SizeOfStackCommit
    opt_header[80:84] = struct.pack('<I', 0x100000)   # SizeOfHeapReserve
    opt_header[84:88] = struct.pack('<I', 0x1000)     # SizeOfHeapCommit
    opt_header[88:92] = struct.pack('<I', 0)          # LoaderFlags
    opt_header[92:96] = struct.pack('<I', 16)         # NumberOfRvaAndSizes
    
    # Data Directories (16 entries, 8 bytes each)
    data_dirs = bytearray(16 * 8)
    
    # Section Header (.text section, 40 bytes)
    section_header = bytearray(40)
    section_header[0:8] = b'.text\x00\x00\x00'
    section_header[8:12] = struct.pack('<I', 0x1000)   # VirtualSize
    section_header[12:16] = struct.pack('<I', 0x1000)  # VirtualAddress
    section_header[16:20] = struct.pack('<I', 0x200)   # SizeOfRawData
    section_header[20:24] = struct.pack('<I', 0x400)   # PointerToRawData
    section_header[36:40] = struct.pack('<I', 0x60000020)  # Characteristics (CODE, EXECUTE, READ)
    
    # Assemble the PE file
    pe_data = dos_header + dos_stub + pe_sig + bytes(coff_header) + bytes(opt_header) + bytes(data_dirs) + section_header
    
    # Pad to file alignment
    while len(pe_data) < 0x400:
        pe_data += b'\x00'
    
    # Add minimal code section (simple x86 return)
    code = b'\xc3'  # ret instruction
    code = code.ljust(0x200, b'\x00')
    pe_data += code
    
    # Write to file
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(pe_data)
    
    print(f"Created valid PE file: {filename} ({len(pe_data)} bytes)")

if __name__ == "__main__":
    create_minimal_pe("evidence/valid_test.exe")
