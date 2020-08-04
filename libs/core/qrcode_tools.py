from PIL import Image

class QrcodeTools(object):

    def qrcode_to_str(self,qrcode_path):
        image = Image.open(qrcode_path)
        width = image.width
        height = image.height
        cell = self.get_cell(image,width,height)
        self.get_qrcode(cell,image,width,height)

    #计算每个方块的大小像素
    def get_cell_size(self,image,x,y,x2,y2):
        for j in range(x,x2):
            for i in range(y,y2):
                pix = image.getpixel((j,i))
                if pix[:3]==(255,255,255):
                    return j - x  #每个黑色格子的像素点大小
                    
    def get_cell(self,image,width,height):
        flag = 0
        for y in range(height):
            for x in range(width):
                print(x,y)
                pix = image.getpixel((x,y))
                print(pix)
                if pix[:3]==(0,0,0) and flag==0: #出现第一个黑色像素
                    x1=x
                    flag = 1
                    
                if pix[:3]==(255,255,255) and flag ==1 : #出现第一个白色像素（意味着左上角的标记方块横向结束）
                    flag = 2
                    cell = self.get_cell_size(image,x1,x1,x,x)
                    return cell
                    
    def get_qrcode(self,cell,image,width,height):
        height = int(height/cell)
        width = int(width/cell)
        code=''
        for y in range(height):
            
            for x in range(width):
                pix = image.getpixel((x*cell,y*cell))
                if pix[:3]==(0,0,0):
                    code += '▇'
                if pix[:3]==(255,255,255):
                    code += '　'
            code += '\n'
        print(code)