import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from django.http import HttpResponse
from inventory.models import InventoryTransaction

def generate_inventory_report(transactions, report_type="inventory"):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
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
    
    # 添加标题
    p.setFont(font_name, 16)
    title = "库存记录报表" if report_type == "inventory" else "出入库记录报表"
    p.drawString(50, height - 50, title)
    
    # 添加日期
    p.setFont(font_name, 12)
    from datetime import datetime
    date_text = f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    p.drawString(50, height - 70, date_text)
    
    # 画线
    p.line(50, height - 80, width - 50, height - 80)
    
    # 准备表格数据
    headers = ['商品编号', '商品名称', '操作类型', '数量', '单价', '总价', '操作时间']
    data = [headers]
    
    total_in = 0
    total_out = 0
    
    for transaction in transactions:
        transaction_type = "入库" if transaction.transaction_type == "IN" else "出库"
            
        if transaction.transaction_type == "IN":
            total_in += float(transaction.total_price)
        else:
            total_out += float(transaction.total_price)
            
        row = [
            transaction.product.product_id,
            transaction.product.name,
            transaction_type,
            str(transaction.quantity),
            str(transaction.unit_price),
            str(transaction.total_price),
            transaction.transaction_date.strftime('%Y-%m-%d %H:%M')
        ]
        data.append(row)
    
    # 添加汇总
    data.append(["", "", "", "", "入库总计:", str(round(total_in, 2)), ""])
    data.append(["", "", "", "", "出库总计:", str(round(total_out, 2)), ""])
    data.append(["", "", "", "", "净总计:", str(round(total_in - total_out, 2)), ""])
    
    # 创建表格
    table = Table(data, colWidths=[60, 100, 60, 60, 60, 60, 100])
    
    # 设置表格样式
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name if font_name != 'Helvetica' else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]
    
    # 如果使用中文字体，设置所有单元格的字体
    if font_name != 'Helvetica':
        table_style.append(('FONTNAME', (0, 1), (-1, -1), font_name))
    
    table.setStyle(TableStyle(table_style))
    
    # 绘制表格
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, height - 300)
    
    # 关闭PDF对象
    p.showPage()
    p.save()
    
    # 获取BytesIO缓冲区的值
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
    
    return response