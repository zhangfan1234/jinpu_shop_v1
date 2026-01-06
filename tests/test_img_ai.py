from utils import api_requests as api


img_path = r"C:\Users\mac\Desktop\jinpu_shop\jinpu_shop\商品主图\e4s9p1801\1.jpg"
prompt = "这个商品是什么材质的"

print(api.alybl_img_ai(img_path, prompt))