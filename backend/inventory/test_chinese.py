import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from django.http import HttpResponse

def test_chinese_pdf_cids(request):
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
    p.drawString(50, height - 50, "中文测试报表")
    
    # 添加详细信息
    p.setFont(font_name, 12)
    p.drawString(50, height - 100, "商品名称: 测试商品")
    p.drawString(50, height - 120, "操作类型: 入库")
    p.drawString(50, height - 140, "数量: 10")
    p.drawString(50, height - 160, "单价: 100.00")
    p.drawString(50, height - 180, "总价: 1000.00")
    
    # 测试中文商品名称
    p.drawString(50, height - 220, "中文商品名称测试: 电视机")
    p.drawString(50, height - 240, "商品编号: TV-001")
    
    # 显示使用的字体信息
    p.setFont(font_name, 10)
    font_info = f"使用字体: {font_name}"
    p.drawString(50, height - 280, font_info)
    
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="chinese_test_cids.pdf"'
    
    return response