"""
NeT2i Converter Module 
Converts CSV data to images by encoding different data types as RGB pixels.
"""

import pandas as pd
import numpy as np
import re
import struct
import json
import shutil
import os
import csv
from typing import List, Tuple, Dict
from PIL import Image
import ipaddress
from dateutil import parser


# --- Default datetime values ---
DEFAULT_DATE = "1970-01-01"
DEFAULT_TIME = "00:00:00"
# -----------------------------

# --- Global configuration ---
_CONFIG = {
    'output_dir': 'data',
    'image_size': 150,
    'types_file': 'data_types.json',
    'types_file_ipv6': 'data_types_ipv6.json',
    'decoded_file': 'from_image.csv',
    'clean_existing': True
}
# -----------------------------


def set_config(output_dir: str = None,
               image_size: int = None,
               types_file: str = None,
               types_file_ipv6: str = None,
               decoded_file: str = None,
               clean_existing: bool = None):
   
    global _CONFIG
    if output_dir is not None:
        _CONFIG['output_dir'] = output_dir
    if image_size is not None:
        _CONFIG['image_size'] = image_size
    if types_file is not None:
        _CONFIG['types_file'] = types_file
    if types_file_ipv6 is not None:
        _CONFIG['types_file_ipv6'] = types_file_ipv6
    if decoded_file is not None:
        _CONFIG['decoded_file'] = decoded_file
    if clean_existing is not None:
        _CONFIG['clean_existing'] = clean_existing


def parse_timestamp(text):
    #Parse a string into date and time components. Returns (date_str, time_str) or defaults if invalid.

    text = str(text).strip()
    if not text or len(text) < 6:
        return DEFAULT_DATE, DEFAULT_TIME

    # Remove fractional seconds and UTC. """Future work to use fractional seconds"""
    cleaned = re.sub(r'\.\d{1,9}', '', text)
    cleaned = re.sub(r'\s*UTC$', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()

    try:
        parsed = parser.parse(cleaned, fuzzy=False)
        if 1900 <= parsed.year <= 2100:
            return parsed.strftime("%Y-%m-%d"), parsed.strftime("%H:%M:%S")
    except Exception:
        pass

    # Handle Unix timestamps
    if text.isdigit():
        if len(text) == 13:  # Milliseconds
            try:
                dt = pd.to_datetime(int(text) / 1000, unit='s')
                return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
            except:
                pass
        elif len(text) == 10:  # Seconds
            try:
                dt = pd.to_datetime(int(text), unit='s')
                return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
            except:
                pass

    return DEFAULT_DATE, DEFAULT_TIME  # Fallback


def extract_datetime_from_row(row):

    for i, cell in enumerate(row):
        if pd.isna(cell) or not isinstance(cell, str):
            continue
        cell = cell.strip()
        if len(cell) < 6:
            continue
        # Try to parse — but return index regardless if it looks like a timestamp
        date_val, time_val = parse_timestamp(cell)
        return date_val, time_val, i  # Always return first match index
    return DEFAULT_DATE, DEFAULT_TIME, None


class NeT2iConverter:
    def __init__(self, config: dict):
        self.output_dir = config['output_dir']
        self.image_size = config['image_size']
        self.types_file = config['types_file']
        self.types_file_ipv6 = config['types_file_ipv6']
        self.decoded_file = config['decoded_file']
        self.clean_existing = config['clean_existing']
        # Data storage
        self.df = None
        self.original_types = []
        self.final_types = []
        self.processed_data = []

    def _clean_existing_files(self):
        if not self.clean_existing:
            return
        files_to_remove = [self.types_file, self.types_file_ipv6, self.decoded_file]
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        for file_path in ['ipv4_rows.csv', 'ipv6_rows.csv']:
            if os.path.exists(file_path):
                os.remove(file_path)

    def _is_ipv6(self, ip_string: str) -> bool:
        try:
            return isinstance(ipaddress.ip_address(ip_string.strip()), ipaddress.IPv6Address)
        except ValueError:
            return False

    def _is_ipv4(self, ip_string: str) -> bool:
        try:
            return isinstance(ipaddress.ip_address(ip_string.strip()), ipaddress.IPv4Address)
        except ValueError:
            return False

    def _detect_ip_columns(self, df: pd.DataFrame) -> List[int]:
        ip_columns = []
        for col_idx in range(len(df.columns)):
            column_data = df.iloc[:, col_idx].astype(str)
            ip_count = 0
            total_count = 0
            for value in column_data[:min(100, len(column_data))]:
                value = str(value).strip()
                if value in ['nan', '']:
                    continue
                total_count += 1
                if self._is_ipv4(value) or self._is_ipv6(value):
                    ip_count += 1
            if total_count > 0 and (ip_count / total_count) > 0.5:
                ip_columns.append(col_idx)
        return ip_columns

    def _split_ipv4_ipv6_data(self, csv_path: str) -> Tuple[str, str, bool, bool]:
        ipv4_output = 'ipv4_rows.csv'
        ipv6_output = 'ipv6_rows.csv'
        has_ipv4_data = False
        has_ipv6_data = False

        temp_df = pd.read_csv(csv_path, header=None, nrows=100, dtype=str)
        ip_columns = self._detect_ip_columns(temp_df)

        with open(csv_path, 'r', newline='', encoding='utf-8') as infile, \
             open(ipv4_output, 'w', newline='', encoding='utf-8') as ipv4_file, \
             open(ipv6_output, 'w', newline='', encoding='utf-8') as ipv6_file:

            reader = csv.reader(infile)
            ipv4_writer = csv.writer(ipv4_file)
            ipv6_writer = csv.writer(ipv6_file)

            for row in reader:
                if not row:
                    continue
                has_ipv6_in_row = any(col < len(row) and self._is_ipv6(row[col]) for col in ip_columns)
                if has_ipv6_in_row:
                    ipv6_writer.writerow(row)
                    has_ipv6_data = True
                else:
                    ipv4_writer.writerow(row)
                    has_ipv4_data = True

        return ipv4_output, ipv6_output, has_ipv4_data, has_ipv6_data

    def _detect_column_types(self, df: pd.DataFrame, is_ipv6: bool = False) -> List[str]:
        final_types = []
        for col_idx in range(len(df.columns)):
            column_data = df.iloc[:, col_idx].astype(str)
            has_float = False
            has_ipv4 = False
            has_ipv6 = False
            has_mac = False
            has_numeric = False

            for value in column_data:
                value = str(value).strip()
                if value in ['nan', '']:
                    continue
                if self._is_ipv4(value):
                    has_ipv4 = True
                elif self._is_ipv6(value):
                    has_ipv6 = True
                elif re.match(r'^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$', value):
                    has_mac = True
                elif re.fullmatch(r'-?\d+\.\d+', value):
                    has_numeric = True
                    has_float = True
                elif re.fullmatch(r'-?\d+$', value):
                    has_numeric = True

            if has_ipv6:
                final_types.append("IPv6 Address")
            elif has_ipv4:
                final_types.append("IPv4 Address")
            elif has_mac:
                final_types.append("MAC Address")
            elif has_numeric:
                final_types.append("Float")
            else:
                final_types.append("String")
        return final_types

    def _ipv6_to_rgb_pixels(self, ipv6_str: str) -> List[Tuple[int, int, int]]:
        try:
            ip = ipaddress.IPv6Address(ipv6_str.strip())
            data = list(ip.packed) + [0, 0]  # 16 bytes + 2 padding = 18 bytes
            return [tuple(data[i:i+3]) for i in range(0, 18, 3)]
        except Exception:
            return [(0, 0, 0)] * 6

    def _float_to_two_rgb_pixels(self, float_val: float) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        try:
            packed_bytes = struct.pack('!f', float_val)
            r1, g1, b1 = packed_bytes[0], packed_bytes[1], packed_bytes[2]
            r2, g2, b2 = packed_bytes[3], 0, 0
            return (r1, g1, b1), (r2, g2, b2)
        except Exception:
            return (0, 0, 0), (0, 0, 0)

    def _replace_datetime_in_row(self, row: List[str]) -> List[str]:
    #Replace first detected datetime with 6 components: Year, Month, Day, Hour, Minute, Second.
        values = [str(v) if pd.notna(v) else "" for v in row]
        date_val, time_val, idx = extract_datetime_from_row(values)

        # Always replace if a timestamp-like cell was found (even if parsing failed)
        if idx is not None:
            try:
                dt = pd.to_datetime(f"{date_val} {time_val}")
                year = str(dt.year)
                month = f"{dt.month:02d}"
                day = f"{dt.day:02d}"
                hour = f"{dt.hour:02d}"
                minute = f"{dt.minute:02d}"
                second = f"{dt.second:02d}"
            except:
                # Fallback values
                year, month, day, hour, minute, second = "1970", "01", "01", "00", "00", "00"

            return values[:idx] + [year, month, day, hour, minute, second] + values[idx + 1:]

        return values  # No datetime found

    def _process_data(self, source_out: List[List], is_ipv6: bool = False) -> List[List[Tuple[int, int, int]]]:
        processed = []
        for row in source_out:
            new_row = []
            for val, dtype in zip(row, self.final_types):
                try:
                    if dtype == "IPv6 Address":
                        new_row.extend(self._ipv6_to_rgb_pixels(str(val)))
                    elif dtype == "IPv4 Address":
                        octet_val = int(val)
                        rgb_pixel1, rgb_pixel2 = self._float_to_two_rgb_pixels(float(octet_val))
                        new_row.extend([rgb_pixel1, rgb_pixel2])
                    elif dtype == "MAC Address":
                        mac = str(val).replace(":", "").replace("-", "").upper()
                        if len(mac) >= 6:
                            mac_int = int(mac[:6], 16)
                        else:
                            mac_int = 0
                        rgb_pixel1, rgb_pixel2 = self._float_to_two_rgb_pixels(float(mac_int))
                        new_row.extend([rgb_pixel1, rgb_pixel2])
                    elif dtype == "Float":
                        float_val = float(val)
                        rgb_pixel1, rgb_pixel2 = self._float_to_two_rgb_pixels(float_val)
                        new_row.extend([rgb_pixel1, rgb_pixel2])
                    else:  # String
                        hash_val = abs(hash(str(val))) % 16777215
                        rgb_pixel1, rgb_pixel2 = self._float_to_two_rgb_pixels(float(hash_val))
                        new_row.extend([rgb_pixel1, rgb_pixel2])
                except Exception as e:
                    print(f"Error processing {val} as {dtype}: {e}")
                    if dtype == "IPv6 Address":
                        new_row.extend([(0, 0, 0)] * 6)
                    else:
                        new_row.extend([(0, 0, 0), (0, 0, 0)])
            processed.append(new_row)
        return processed

    def _save_type_information(self, is_ipv6: bool = False):
        types_file = self.types_file_ipv6 if is_ipv6 else self.types_file
        type_info = {
            "ip_version": "IPv6" if is_ipv6 else "IPv4",
            "original_types": self.original_types,
            "final_types": self.final_types,
            "encoding_info": {
                "description": f"Data type mapping for decoding - {'IPv6' if is_ipv6 else 'IPv4'} version",
                "float_encoding": "Each float becomes 2 RGB pixels (6 bytes total)",
                "mac_encoding": "MAC address split into 2 hex chunks",
                "ipv4_encoding": "IPv4 address split into 4 octets, each becomes 2 RGB pixels",
                "ipv6_encoding": "IPv6 address becomes 6 RGB pixels (16 bytes + 2 padding)",
                "integer_note": "All integers converted to floats before encoding",
                "string_encoding": "Hashed to integer, converted to float, then 2 RGB pixels",
                "datetime_handling": "Every timestamp-like cell is replaced with 6 columns: Y,M,D,H,M,S (fallback: 1970-01-01 00:00:00)"
            },
            "original_columns": len(self.original_types),
            "final_columns": len(self.final_types)
        }
        with open(types_file, 'w') as f:
            json.dump(type_info, f, indent=2)

    def _create_image_from_line(self, line: List[Tuple[int, int, int]], image_id: int, prefix: str = ""):
        array = np.zeros((self.image_size, self.image_size, 3), dtype=np.uint8)
        
        if len(line) == 0:
            array = np.full((self.image_size, self.image_size, 3), 128, dtype=np.uint8)
        else:
            rows_per_color = max(1, self.image_size // len(line))
            current_row = 0
            
            for rgb in line:
                r, g, b = map(lambda x: max(0, min(255, int(x))), rgb)
                for _ in range(rows_per_color):
                    if current_row < self.image_size:
                        array[current_row, :] = [r, g, b]
                        current_row += 1
            
            if current_row < self.image_size and len(line) > 0:
                last_rgb = line[-1]
                r, g, b = map(lambda x: max(0, min(255, int(x))), last_rgb)
                while current_row < self.image_size:
                    array[current_row, :] = [r, g, b]
                    current_row += 1
        
        filename = f"{prefix}{image_id}.png"
        Image.fromarray(array).save(os.path.join(self.output_dir, filename))

    def _create_all_images(self, prefix: str = ""):
        os.makedirs(self.output_dir, exist_ok=True)
        for i, line in enumerate(self.processed_data):
            self._create_image_from_line(line, i, prefix)

    def _split_mac(self, data: List[List[str]], types_list: List[str]) -> Tuple[List[List[str]], List[str]]:
        #Split MAC addresses into two 6-character hex parts. Each part is treated as a separate field.
        new_data = []
        new_types = []
        for row in data:
            new_row = []
            for val, dtype in zip(row, types_list):
                if dtype == "MAC Address":
                    mac = str(val).replace(":", "").replace("-", "").upper()
                    if len(mac) >= 12:
                        new_row.extend([mac[:6], mac[6:12]])
                        new_types.extend(["MAC Address", "MAC Address"])
                    else:
                        padded = (mac + '000000')[:6]
                        new_row.append(padded)
                        new_types.append("MAC Address")
                else:
                    new_row.append(val)
                    new_types.append(dtype)
            new_data.append(new_row)
        return new_data, new_types

    def _split_ip(self, data: List[List[str]], types_list: List[str]) -> Tuple[List[List[str]], List[str]]:
        """
        Split IPv4 into 4 octets. IPv6 remains as one field.
        """
        new_data = []
        new_types = []
        for row in data:
            new_row = []
            for val, dtype in zip(row, types_list):
                if dtype == "IPv4 Address":
                    octets = str(val).split('.')
                    if len(octets) == 4 and all(o.isdigit() and 0 <= int(o) <= 255 for o in octets):
                        new_row.extend(octets)
                        new_types.extend(["IPv4 Address"] * 4)
                    else:
                        new_row.append(val)
                        new_types.append("String")
                elif dtype == "IPv6 Address":
                    new_row.append(val)
                    new_types.append("IPv6 Address")
                else:
                    new_row.append(val)
                    new_types.append(dtype)
            new_data.append(new_row)
        return new_data, new_types

    def _process_single_dataset(self, csv_path: str, is_ipv6: bool = False, prefix: str = "") -> Dict[str, any]:
        #  Load raw CSV
        self.df = pd.read_csv(csv_path, header=None, dtype=str)
        source_out = self.df.values.tolist()
        pre_expand_shape = self.df.shape

        #  Expand datetime in each row
        updated_rows = []
        datetime_detected = 0
        for i, row in enumerate(source_out):
            new_row = self._replace_datetime_in_row(row)
            if len(new_row) != len(row):
                datetime_detected += 1
            updated_rows.append(new_row)

        
        temp_df = pd.DataFrame(updated_rows)
        #print(f" Datetime expanded in {datetime_detected} rows")

        #  Detect types on expanded data
        self.original_types = self._detect_column_types(temp_df, is_ipv6)
        source_out = temp_df.astype(str).values.tolist()

        #  Split MAC and IP
        source_out, updated_types = self._split_mac(source_out, self.original_types)
        source_out, self.final_types = self._split_ip(source_out, updated_types)

        # Save metadata
        self._save_type_information(is_ipv6)

        #  Convert to pixels
        self.processed_data = self._process_data(source_out, is_ipv6)

        #  Generate images
        self._create_all_images(prefix)

        return {
            "input_file": csv_path,
            "ip_version": "IPv6" if is_ipv6 else "IPv4",
            "original_shape": pre_expand_shape,
            "expanded_shape": temp_df.shape,
            "original_types": self.original_types,
            "final_types": self.final_types,
            "num_images": len(self.processed_data),
            "datetime_columns_inserted": 6 if datetime_detected > 0 else 0
        }

    def convert(self, csv_path: str, **kwargs) -> Dict[str, any]:
        """
        Main entry point: split, process, and convert CSV to images.
        """
        self._clean_existing_files()
        ipv4_file, ipv6_file, has_ipv4, has_ipv6 = self._split_ipv4_ipv6_data(csv_path)
        
        results = {
            "input_file": csv_path,
            "output_dir": self.output_dir,
            "image_size": self.image_size,
            "has_ipv4": has_ipv4,
            "has_ipv6": has_ipv6,
            "ipv4_results": None,
            "ipv6_results": None
        }

        if has_ipv4:
            results["ipv4_results"] = self._process_single_dataset(ipv4_file, is_ipv6=False, prefix="ipv4_")

        if has_ipv6:
            results["ipv6_results"] = self._process_single_dataset(ipv6_file, is_ipv6=True, prefix="ipv6_")

        total_images = sum([
            results["ipv4_results"]["num_images"] if has_ipv4 else 0,
            results["ipv6_results"]["num_images"] if has_ipv6 else 0
        ])

        results["total_images"] = total_images
        print(f"Conversion completed successfully!\nTotal images generated: {total_images}")
        return results


def encode(csv_path: str, output_dir: str = None, image_size: int = None, **kwargs) -> Dict[str, any]:
    """
    High-level function to encode CSV to images.
    """
    config = _CONFIG.copy()
    if output_dir:
        config['output_dir'] = output_dir
    if image_size:
        config['image_size'] = image_size

    converter = NeT2iConverter(config)
    return converter.convert(csv_path, **kwargs)


def load_csv(csv_path: str, **kwargs) -> str:
    """
    Utility to verify CSV exists.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    return csv_path


__all__ = ['encode', 'load_csv', 'set_config']