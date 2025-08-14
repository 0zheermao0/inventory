from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

def test_chinese_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # 测试中文显示 - 使用标准字体
    p.setFont("Helvetica", 16)
    p.drawString(50, height - 50, "中文测试报表")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, "商品名称: 测试商品")
    p.drawString(50, height - 120, "操作类型: 入库")
    p.drawString(50, height - 140, "数量: 10")
    p.drawString(50, height - 160, "单价: 100.00")
    p.drawString(50, height - 180, "总价: 1000.00")
    
    # 测试中文商品名称
    p.drawString(50, height - 220, "中文商品名称测试: 电视机")
    p.drawString(50, height - 240, "商品编号: TV-001")
    
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="chinese_test.pdf"'
    
    return response