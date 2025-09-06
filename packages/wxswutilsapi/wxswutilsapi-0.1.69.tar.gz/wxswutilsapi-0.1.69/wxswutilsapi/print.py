import win32print
import win32ui
import math

def print_text_lines_win32(lines, printer_name, font_name="Courier New"):
    # 打开打印机
    hprinter = win32print.OpenPrinter(printer_name)

    # 创建设备上下文
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)

    # 页面可打印区域（像素）
    printable_area = hdc.GetDeviceCaps(8), hdc.GetDeviceCaps(10)  # HORZRES, VERTRES
    margin_left = 100
    margin_top = 100

    printable_width = printable_area[0] - margin_left * 2
    printable_height = printable_area[1] - margin_top * 2

    # 固定每页行数（行数可以根据需要调整）
    lines_per_page = 80

    # 计算每行高度，保证铺满可打印高度
    line_height = printable_height / lines_per_page
    font_height = int(line_height * 0.8)  # 字体高度略小于行高，防止挤压

    # 创建字体
    font = win32ui.CreateFont({
        "name": font_name,
        "height": -font_height,  # 字体高度用负数表示点大小
        "weight": 400
    })
    hdc.SelectObject(font)

    # 开始打印文档
    hdc.StartDoc("Text Document")

    total_lines = len(lines)
    total_pages = math.ceil(total_lines / lines_per_page)

    for page_index in range(total_pages):
        hdc.StartPage()

        start_line = page_index * lines_per_page
        end_line = min(start_line + lines_per_page, total_lines)

        # 打印文本行
        for i in range(start_line, end_line):
            x = margin_left
            y = margin_top + (i - start_line) * line_height
            hdc.TextOut(x, int(y), lines[i])

        # 打印页码，位置在页面底部（可以根据需要调整偏移量）
        page_info = f"第 {page_index + 1} / {total_pages} 页"
        x_page = margin_left
        y_page = margin_top + printable_height + 10  # 页底稍微偏下一点打印页码
        hdc.TextOut(x_page, int(y_page), page_info)

        hdc.EndPage()

    hdc.EndDoc()
    hdc.DeleteDC()
    win32print.ClosePrinter(hprinter)

def list_printers():
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    printer_name = win32print.GetDefaultPrinter()
    return  {"print_list":[p for p in [printer[2] for printer in printers]],"defalut_print":printer_name}

def get_printer_status(printer_name):
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        printer_info = win32print.GetPrinter(hPrinter, 2)
        status = printer_info['Status']
        printer_info['Status'] = decode_printer_status(status)
        serializable_info = {
            key: value
            for key, value in printer_info.items()
            if isinstance(value, (str, int, float, bool, type(None)))
        }
        # 打印详细信息
        return serializable_info
    finally:
        win32print.ClosePrinter(hPrinter)

def decode_printer_status(status):
    status_map = {
        0x00000000: "空闲",
        0x00000001: "暂停",
        0x00000002: "出错",
        0x00000004: "正在删除",
        0x00000008: "正在打印",
        0x00000010: "准备接收",
        0x00000020: "离线",
        0x00000040: "未响应",
        0x00000080: "纸张缺失",
        0x00000100: "门开",
        0x00000200: "墨盒/色带问题",
        0x00000400: "纸张堵塞",
        0x00000800: "用户干预",
        0x00001000: "正在初始化",
        0x00002000: "正在清洗",
        0x00004000: "正在等待",
        0x00008000: "处理",
        0x00040000: "忙碌",
        0x00400000: "输出托盘满",
    }
    if status == 0:
        return "空闲"
    readable_status = []
    for code, msg in status_map.items():
        if status & code:
            readable_status.append(msg)
    return "，".join(readable_status) if readable_status else "未知状态"

def calculate_total_pages(lines, lines_per_page=60):
    """
    返回根据总行数和每页行数计算出的总页数。
    """
    total_lines = len(lines)
    return math.ceil(total_lines / lines_per_page)