import pandas as pd
from products.models import Product
from inventory.models import Customer, InventoryTransaction, TransactionItem
from django.http import HttpResponse
import io
import re

def export_products_to_excel():
    """导出商品信息到Excel"""
    products = Product.objects.all().values(
        'product_id', 'name', 'specification', 'unit', 'price', 'stock_quantity', 'description'
    )
    
    df = pd.DataFrame(products)
    df.columns = ['型号', '商品名称', '规格', '单位', '单价', '库存数量', '商品描述']
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='商品信息', index=False)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=products.xlsx'
    return response

def parse_price(price_value):
    """解析价格值，处理包含非数字字符的情况"""
    if pd.isna(price_value):
        return 0.0
    
    # 如果是数字类型，直接返回
    if isinstance(price_value, (int, float)):
        return float(price_value)
    
    # 转换为字符串并提取数字
    price_str = str(price_value)
    
    # 使用正则表达式提取第一个数字（包括小数）
    match = re.search(r'(\d+(?:\.\d+)?)', price_str)
    if match:
        return float(match.group(1))
    
    # 如果没有找到数字，返回0
    return 0.0

def import_products_from_excel(file):
    """从Excel导入商品信息"""
    # 读取Excel文件，跳过前两行空行
    df = pd.read_excel(file, skiprows=2, header=None)
    
    # 检查是否有数据
    if df.empty or len(df) < 2:
        raise ValueError("Excel文件中没有足够的数据")
    
    # 使用第二行作为列名（索引为1）
    df.columns = df.iloc[1]
    # 删除前两行（空行和表头行）
    df = df.drop(df.index[0:2])
    # 重置索引
    df = df.reset_index(drop=True)
    
    # 打印列名以帮助调试
    print("实际列名:", df.columns.tolist())
    
    # 检查必要的列是否存在
    required_columns = ['型号', '单价元/个']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"缺少必要的列: {col}")
    
    created_count = 0
    updated_count = 0
    errors = []
    
    for index, row in df.iterrows():
        try:
            # 跳过空行
            if pd.isna(row['型号']) or row['型号'] == '':
                continue
                
            # 解析价格
            price = parse_price(row['单价元/个'])
                
            product, created = Product.objects.update_or_create(
                product_id=row['型号'],
                defaults={
                    'name': row['名称'] if '名称' in df.columns and pd.notna(row['名称']) else '',
                    'specification': '',  # 如果需要可以从其他列获取规格信息
                    'unit': '',  # 如果需要可以从其他列获取单位信息
                    'price': price,
                    'stock_quantity': 0,  # Excel中没有库存数量列，设置默认值为0
                    'description': row['备注'] if '备注' in df.columns and pd.notna(row['备注']) else ''
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        except Exception as e:
            errors.append(f"第{index+1}行出现错误: {str(e)}")
    
    return {
        'created_count': created_count,
        'updated_count': updated_count,
        'errors': errors
    }

def export_customers_to_excel():
    """导出客户资料到Excel"""
    customers = Customer.objects.all().values(
        'name', 'contact_person', 'phone', 'email', 'address', 'remarks'
    )
    
    df = pd.DataFrame(customers)
    df.columns = ['客户名称', '联系人', '联系电话', '邮箱', '地址', '备注']
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='客户资料', index=False)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=customers.xlsx'
    return response

def import_customers_from_excel(file):
    """从Excel导入客户资料"""
    df = pd.read_excel(file)
    
    # 检查必要的列是否存在
    required_columns = ['客户名称']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"缺少必要的列: {col}")
    
    # 处理可选列
    optional_columns = ['联系人', '联系电话', '邮箱', '地址', '备注']
    for col in optional_columns:
        if col not in df.columns:
            df[col] = ''  # 如果列不存在，添加空列
    
    created_count = 0
    updated_count = 0
    errors = []
    
    for index, row in df.iterrows():
        try:
            # 跳过空行
            if pd.isna(row['客户名称']) or row['客户名称'] == '':
                continue
                
            customer, created = Customer.objects.update_or_create(
                name=row['客户名称'],
                defaults={
                    'contact_person': row['联系人'] if pd.notna(row['联系人']) else '',
                    'phone': row['联系电话'] if pd.notna(row['联系电话']) else '',
                    'email': row['邮箱'] if pd.notna(row['邮箱']) else '',
                    'address': row['地址'] if pd.notna(row['地址']) else '',
                    'remarks': row['备注'] if pd.notna(row['备注']) else ''
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        except Exception as e:
            errors.append(f"第{index+1}行出现错误: {str(e)}")
    
    return {
        'created_count': created_count,
        'updated_count': updated_count,
        'errors': errors
    }

def export_inventory_transactions_to_excel():
    """导出出入库订单到Excel"""
    # 获取所有出入库单据及其商品项
    transactions = InventoryTransaction.objects.prefetch_related('items__product', 'customer').all()
    
    data = []
    for transaction in transactions:
        for item in transaction.items.all():
            data.append({
                '单据号码': transaction.document_number,
                '操作类型': '入库' if transaction.transaction_type == 'IN' else '出库',
                '客户名称': transaction.customer.name if transaction.customer else '',
                '客户电话': transaction.customer.phone if transaction.customer else '',
                '商品编号': item.product.product_id,
                '商品名称': item.product.name,
                '规格': item.product.specification,
                '单位': item.product.unit,
                '数量': item.quantity,
                '单价': float(item.unit_price),
                '金额': float(item.total_price),
                '制单日期': transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                '制单人': transaction.preparer,
                '审核人': transaction.auditor,
                '经手人': transaction.handler,
                '收货人': transaction.receiver,
                '单据备注': transaction.remarks,
                '商品备注': item.remarks
            })
    
    df = pd.DataFrame(data)
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='出入库订单', index=False)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=inventory_transactions.xlsx'
    return response

def import_inventory_transactions_from_excel(file):
    """从Excel导入出入库订单"""
    df = pd.read_excel(file)
    
    # 检查必要的列是否存在
    required_columns = ['单据号码', '操作类型', '商品编号', '数量']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"缺少必要的列: {col}")
    
    # 处理可选列
    optional_columns = ['客户名称', '单价', '制单人', '审核人', '经手人', '收货人', '单据备注', '商品备注']
    for col in optional_columns:
        if col not in df.columns:
            df[col] = ''  # 如果列不存在，添加空列
    
    created_count = 0
    updated_count = 0
    errors = []
    
    # 按单据号码分组处理
    for document_number, group in df.groupby('单据号码'):
        try:
            # 获取单据信息（取第一行）
            first_row = group.iloc[0]
            
            # 查找或创建客户
            customer = None
            if pd.notna(first_row['客户名称']) and first_row['客户名称']:
                customer, _ = Customer.objects.get_or_create(
                    name=first_row['客户名称'],
                    defaults={
                        'phone': first_row['客户电话'] if pd.notna(first_row['客户电话']) else ''
                    }
                )
            
            # 创建或更新出入库单据
            transaction_type = 'IN' if first_row['操作类型'] == '入库' else 'OUT'
            transaction, created = InventoryTransaction.objects.update_or_create(
                document_number=document_number,
                defaults={
                    'transaction_type': transaction_type,
                    'customer': customer,
                    'preparer': first_row['制单人'] if pd.notna(first_row['制单人']) else '',
                    'auditor': first_row['审核人'] if pd.notna(first_row['审核人']) else '',
                    'handler': first_row['经手人'] if pd.notna(first_row['经手人']) else '',
                    'receiver': first_row['收货人'] if pd.notna(first_row['收货人']) else '',
                    'remarks': first_row['单据备注'] if pd.notna(first_row['单据备注']) else ''
                }
            )
            
            if created:
                created_count += 1
            
            # 处理商品项
            for _, row in group.iterrows():
                # 查找商品
                try:
                    product = Product.objects.get(product_id=row['商品编号'])
                except Product.DoesNotExist:
                    errors.append(f"单据{document_number}中的商品{row['商品编号']}不存在")
                    continue
                
                # 设置单价（如果未提供，则使用商品默认价格）
                unit_price = row['单价'] if pd.notna(row['单价']) and row['单价'] else product.price
                
                # 创建或更新商品项
                TransactionItem.objects.update_or_create(
                    transaction=transaction,
                    product=product,
                    defaults={
                        'quantity': int(row['数量']) if pd.notna(row['数量']) else 0,
                        'unit_price': unit_price,
                        'remarks': row['商品备注'] if pd.notna(row['商品备注']) else ''
                    }
                )
                
                # 更新总金额
                transaction.total_amount = sum(item.total_price for item in transaction.items.all())
                transaction.save()
                
        except Exception as e:
            errors.append(f"单据{document_number}处理出现错误: {str(e)}")
    
    return {
        'created_count': created_count,
        'updated_count': updated_count,
        'errors': errors
    }