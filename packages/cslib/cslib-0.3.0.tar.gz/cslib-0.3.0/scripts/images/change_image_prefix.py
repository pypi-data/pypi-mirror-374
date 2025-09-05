import os
import click
from PIL import Image

__all__ = ["change_image_prefix"]

@click.command()
@click.option('--src', '-s', default=f'/Volumes/Charles/data/vision/torchvision/llvip/fused/crossfuse', help='源文件夹路径')
@click.option('--des', '-d', default=f'/Volumes/Charles/data/vision/torchvision/llvip/fused/crossfuse1', help='目标文件夹路径')
@click.option('--format', '-f', default='jpeg', help='输出图像格式')
@click.option('--delete', is_flag=False, help='是否删除源文件')
@click.option('--supported-extensions', '-e', default='tif,jpg,bmp,png', help='支持转换的源文件扩展名，用逗号分隔，默认：tif,jpg,bmp')
def run(src, des, format, delete, supported_extensions):
    change_image_prefix(src, des, format, delete, supported_extensions)

def change_image_prefix(src, des, format, delete=False, supported_extensions='tif,jpg,bmp,png'):
    """
    将源文件夹中的图像文件转换为指定格式并保存到目标文件夹。
    
    示例用法:
    python change_image_prefix.py --src /path/to/source --des /path/to/destination --format jpg
    """
    # 确保目标文件夹存在
    os.makedirs(des, exist_ok=True)
    
    # 解析支持的文件扩展名
    supported_exts = [ext.strip().lower() for ext in supported_extensions.split(',')]
    supported_exts = ['.' + ext if not ext.startswith('.') else ext for ext in supported_exts]
    
    # 遍历源文件夹中的所有文件
    for filename in os.listdir(src):
        # 获取文件的完整路径
        file_path = os.path.join(src, filename)
        
        # 跳过文件夹
        if os.path.isdir(file_path):
            continue
        
        # 检查文件扩展名是否受支持
        if any(filename.lower().endswith(ext) for ext in supported_exts):
            # try:
            # 打开图像
            image = Image.open(file_path)
            
            # 构造新的文件名
            base_name = os.path.splitext(filename)[0]
            new_filename = f"{base_name}.{format.lower()}"
            new_file_path = os.path.join(des, new_filename)
            
            # 保存为指定格式
            # try:
            image.save(new_file_path, format.upper())
            # except (ValueError, IOError):
            #     # 如果指定格式不支持，尝试使用默认保存
            #     image.save(new_file_path)
            click.echo(f"已转换: {filename} -> {new_filename}")
            
            # 如果设置了删除源文件，则删除
            if delete:
                os.remove(file_path)
                click.echo(f"已删除源文件: {filename}")
            # except Exception as e:
            #     click.echo(f"处理文件 {filename} 时出错: {str(e)}", err=True)
    
    click.echo(f"转换完成！所有图像已保存到: {des}")


if __name__ == "__main__":
    run()