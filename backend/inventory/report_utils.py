import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter, legal, A3, A5
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from django.http import HttpResponse
from inventory.models import InventoryTransaction, StoreInfo
import datetime

# 纸张规格定义
PAPER_SIZES = {
    'A4': A4,
    'A5': A5,
    'A3': A3,
    'Letter': letter,
    'Legal': legal
}

def generate_inventory_report(transactions, report_type="inventory_transactions", paper_size="A4"):
    buffer = io.BytesIO()
    
    # 获取纸张尺寸
    page_size = PAPER_SIZES.get(paper_size, A4)
    width, height = page_size
    
    # 注册系统中文字体
    try:
        # 尝试注册多种中文字体
        font_options = ['STSong-Light', 'STHeiti', 'STKaiti']
        font_name = 'Helvetica'  # 默认字体
        
        for font in font_options:
            try:
                pdfmetrics.registerFont(UnicodeCIDFont(font))
                font_name = font
                break
            except:
                continue
                
        # 如果以上字体都不可用，尝试使用默认的Unicode字体
        if font_name == 'Helvetica':
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            font_name = 'STSong-Light'
    except:
        # 如果所有中文字体都不可用，使用默认字体
        font_name = 'Helvetica'
    
    # 获取店铺信息（如果有）
    store_info = StoreInfo.objects.first()
    
    # 设置页面边距（根据纸张尺寸调整）
    if paper_size == 'A5':
        margin_left = margin_right = 20 * mm
        margin_top = margin_bottom = 15 * mm
    elif paper_size == 'A3':
        margin_left = margin_right = 30 * mm
        margin_top = margin_bottom = 20 * mm
    else:  # A4, Letter, Legal
        margin_left = margin_right = 25 * mm
        margin_top = margin_bottom = 20 * mm
    
    usable_width = width - margin_left - margin_right
    usable_height = height - margin_top - margin_bottom
    
    # 创建PDF文档
    from reportlab.platypus import SimpleDocTemplate
    
    doc = SimpleDocTemplate(buffer, pagesize=page_size, 
                           leftMargin=margin_left, 
                           rightMargin=margin_right, 
                           topMargin=margin_top, 
                           bottomMargin=margin_bottom)
    
    # 根据纸张尺寸设置样式
    base_font_size = 12
    if paper_size == 'A5':
        base_font_size = 10
    elif paper_size == 'A3':
        base_font_size = 14
    
    # 设置样式
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=base_font_size + 4,
        leading=base_font_size + 6,
        alignment=1,  # 居中
        fontName=font_name if font_name != 'Helvetica' else 'Helvetica',
        spaceAfter=6
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=base_font_size - 2,
        leading=base_font_size,
        fontName=font_name if font_name != 'Helvetica' else 'Helvetica'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=base_font_size - 3,
        leading=base_font_size - 1,
        fontName=font_name if font_name != 'Helvetica' else 'Helvetica'
    )
    
    # 构建文档内容
    story = []
    
    # 添加店铺信息
    if store_info:
        # 店铺名称
        store_name = Paragraph(f"<b>{store_info.name}</b>", title_style)
        story.append(store_name)
        
        # 店铺联系信息
        contact_info = []
        if store_info.phone:
            contact_info.append(f"电话: {store_info.phone}")
        if store_info.address:
            contact_info.append(f"地址: {store_info.address}")
        
        if contact_info:
            contact_para = Paragraph("  ".join(contact_info), header_style)
            story.append(contact_para)
            story.append(Spacer(1, 6))
    
    # 添加报表标题
    transaction_types = list(set(t.transaction_type for t in transactions)) if transactions else []
    if len(transaction_types) == 1:
        title = "入库单" if transaction_types[0] == "IN" else "出库单"
    else:
        title = "出入库记录报表"
    
    title_para = Paragraph(f"<b>{title}</b>", title_style)
    story.append(title_para)
    story.append(Spacer(1, 6))
    
    # 添加单据信息（如果有交易记录）
    if transactions:
        first_transaction = transactions[0]
        
        # 单据信息行
        doc_info = []
        doc_info.append(f"单据号码: {first_transaction.document_number}")
        doc_info.append(f"制单日期: {first_transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 客户信息（如果有）
        if first_transaction.customer:
            doc_info.append(f"客户: {first_transaction.customer.name}")
            if first_transaction.customer.phone:
                doc_info.append(f"客户电话: {first_transaction.customer.phone}")
        
        doc_info_para = Paragraph("  ".join(doc_info), header_style)
        story.append(doc_info_para)
        story.append(Spacer(1, 6))
    
    # 准备表格数据
    headers = ['商品编码', '商品名称', '规格', '单位', '数量', '单价', '金额', '备注']
    data = [headers]
    
    total_amount = 0
    
    for transaction in transactions:
        # 获取商品规格和单位
        specification = getattr(transaction.product, 'specification', '')
        unit = getattr(transaction.product, 'unit', '')
        
        row = [
            transaction.product.product_id,
            transaction.product.name,
            specification,
            unit,
            str(transaction.quantity),
            f"{transaction.unit_price:.2f}",
            f"{transaction.total_price:.2f}",
            transaction.remarks if transaction.remarks else ""
        ]
        data.append(row)
        total_amount += float(transaction.total_price)
    
    # 添加合计行
    data.append(["", "", "", "", "", "合计:", f"{total_amount:.2f}", ""])
    
    # 添加人民币大写金额
    def to_chinese_currency(amount):
        """将数字金额转换为中文大写金额"""
        units = ["", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"]
        digits = ["", "拾", "佰", "仟"]
        big_units = ["", "万", "亿"]
        
        if amount == 0:
            return "零元整"
            
        # 分离整数和小数部分
        integer_part = int(amount)
        decimal_part = round((amount - integer_part) * 100)
        
        if integer_part == 0:
            result = "零"
        else:
            result = ""
            str_int = str(integer_part)
            zero_flag = False
            
            # 处理整数部分
            for i, digit in enumerate(reversed(str_int)):
                n = int(digit)
                if n == 0:
                    zero_flag = True
                else:
                    if zero_flag and result:
                        result = "零" + result
                    result = units[n] + digits[i % 4] + result
                    zero_flag = False
                    
                # 添加万、亿单位
                if (i + 1) % 4 == 0 and (i + 1) // 4 < len(big_units):
                    if any(int(d) != 0 for d in str_int[-(i+1):-i-5:-1]) or (i + 1) == 4:
                        result += big_units[(i + 1) // 4]
                        
            result += "元"
            
        # 处理小数部分
        if decimal_part > 0:
            jiao = decimal_part // 10
            fen = decimal_part % 10
            if jiao > 0:
                result += units[jiao] + "角"
            if fen > 0:
                result += units[fen] + "分"
        else:
            result += "整"
            
        return result
    
    # 添加大写金额行
    data.append(["", "", "", "", "", "大写:", to_chinese_currency(total_amount), ""])
    
    # 根据纸张尺寸调整列宽
    if paper_size == 'A5':
        col_widths = [40, 70, 30, 25, 30, 40, 40, 50]
    elif paper_size == 'A3':
        col_widths = [80, 120, 50, 40, 50, 60, 60, 90]
    else:  # A4, Letter, Legal
        col_widths = [60, 90, 40, 30, 40, 50, 50, 70]
    
    # 创建表格
    table = Table(data, colWidths=col_widths, repeatRows=1)  # repeatRows=1使表头在每页重复
    
    # 设置表格样式
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name if font_name != 'Helvetica' else 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), base_font_size - 3),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), base_font_size - 4),
        # 合计行和大写金额行加粗
        ('FONTNAME', (0, -2), (-1, -1), font_name if font_name != 'Helvetica' else 'Helvetica-Bold'),
        ('FONTSIZE', (0, -2), (-1, -1), base_font_size - 3),
    ]
    
    # 如果使用中文字体，设置所有单元格的字体
    if font_name != 'Helvetica':
        table_style.append(('FONTNAME', (0, 1), (-1, -2), font_name))
    
    table.setStyle(TableStyle(table_style))
    story.append(table)
    
    # 添加签名行（在最后一页底部）
    story.append(Spacer(1, 12))
    signature_text = f"制单人: __________    审核人: __________    经手人: __________    收货人: __________"
    signature_para = Paragraph(signature_text, normal_style)
    story.append(signature_para)
    
    # 构建PDF
    doc.build(story)
    
    # 获取BytesIO缓冲区的值
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{paper_size}.pdf"'
    
    return response