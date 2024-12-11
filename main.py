from scapy.all import rdpcap
import os
from colorama import init, Fore, Back, Style
from typing import List, Tuple
import argparse
import sys

init()

def validate_pcap_file(filepath: str) -> bool:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"El archivo {filepath} no existe")
    if not os.path.isfile(filepath):
        raise ValueError(f"{filepath} no es un archivo")
    if not filepath.lower().endswith(('.pcap', '.pcapng', '.cap')):
        raise ValueError(f"El archivo debe tener extensión .pcap, .pcapng o .cap")
    return True

def hex_to_rgb(hex_val: int) -> Tuple[int, int, int]:
    if hex_val == 0: return (0, 0, 0)
    elif hex_val == 15: return (255, 255, 255)
    r = int((hex_val & 0b1100) >> 2) * 85
    g = int((hex_val & 0b0010) >> 1) * 170
    b = int(hex_val & 0b0001) * 255
    return (r, g, b)

def pcap_to_bytes(pcap_file: str) -> List[int]:
    packets = rdpcap(pcap_file)
    raw_bytes = []
    for packet in packets:
        raw_bytes.extend(bytes(packet))
    return [x >> 4 for x in raw_bytes]  # Convertir a valores 0-F

def create_legend() -> str:
    legend = ['<div style="margin: 20px 0;">',
              '<h2 style="color: white;">Leyenda de Colores</h2>',
              '<div style="display: flex; flex-wrap: wrap; gap: 10px;">']
    
    for i in range(16):
        r, g, b = hex_to_rgb(i)
        legend.append(
            f'<div style="display: flex; align-items: center; gap: 5px;">'
            f'<div style="width: 20px; height: 20px; background: rgb({r},{g},{b});"></div>'
            f'<span style="color: white;">0x{i:X}</span>'
            '</div>'
        )
    
    legend.extend(['</div></div>'])
    return '\n'.join(legend)

def to_html_with_legend(data: List[int], width: int, scale: int = 1, show_hex: bool = False) -> str:
    html = ['<!DOCTYPE html><html><head><style>',
            '.pixel{display:inline-block;margin:0;padding:0;}',
            '.row{height:fit-content;margin:0;padding:0;display:flex;align-items:center;}',
            '.hex-value{color:#666;margin-left:10px;font-family:monospace;}',
            '</style></head><body style="background:black;margin:0;padding:10px">']
    
    # Agregar leyenda
    html.append(create_legend())
    
    height = len(data) // width
    if len(data) % width != 0:
        height += 1
        
    for y in range(height):
        html.append('<div class="row">')
        for x in range(width):
            idx = y * width + x
            if idx < len(data):
                r, g, b = hex_to_rgb(data[idx])
                html.append(
                    f'<div class="pixel" style="width:{scale*2}px;'
                    f'height:{scale}px;background:rgb({r},{g},{b})"></div>'
                )
        
        if show_hex:
            hex_values = ' '.join([f'{data[y*width + x]:X}' for x in range(width) 
                                 if y*width + x < len(data)])
            html.append(f'<span class="hex-value">{hex_values}</span>')
            
        html.append('</div>')
    
    html.append('</body></html>')
    return '\n'.join(html)

def to_html(data: List[int], width: int, scale: int = 1) -> str:
    html = ['<!DOCTYPE html><html><head><style>',
            '.pixel{display:inline-block;margin:0;padding:0;}',
            '.row{height:fit-content;margin:0;padding:0;}',
            '</style></head><body style="background:black;margin:0;padding:10px">']
    
    height = len(data) // width
    if len(data) % width != 0:
        height += 1
        
    for y in range(height):
        html.append('<div class="row">')
        for x in range(width):
            idx = y * width + x
            if idx < len(data):
                r, g, b = hex_to_rgb(data[idx])
                html.append(
                    f'<div class="pixel" style="width:{scale*2}px;'
                    f'height:{scale}px;background:rgb({r},{g},{b})"></div>'
                )
        html.append('</div>')
    
    html.append('</body></html>')
    return '\n'.join(html)

def main():
    parser = argparse.ArgumentParser(description='PCAP to Color Visualization')
    parser.add_argument('pcap_file', help='Path to input PCAP file')
    parser.add_argument('--output-dir', '-o', default='output', help='Output directory')
    parser.add_argument('--width', '-w', type=int, default=32, help='Width of visualization')
    parser.add_argument('--scale', '-s', type=int, default=5, help='Pixel scale factor')
    parser.add_argument('--show-hex', action='store_true', help='Show hex values')
    
    args = parser.parse_args()
    
    try:
        validate_pcap_file(args.pcap_file)
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
        
        data = pcap_to_bytes(args.pcap_file)
        output_file = os.path.join(args.output_dir, 
                                os.path.basename(args.pcap_file) + '.html')
        
        with open(output_file, 'w') as f:
            f.write(to_html_with_legend(data, args.width, args.scale, args.show_hex))
        
        print(f'Visualization saved to: {output_file}')
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print(Fore.GREEN + "PCAP to Color Visualization" + Style.RESET_ALL)
    main()