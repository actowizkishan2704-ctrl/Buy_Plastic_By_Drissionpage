from DrissionPage import ChromiumPage
from DrissionPage.common import Keys
import time
import json
import os

Browser=ChromiumPage()
page=Browser.latest_tab
os.makedirs("saved_pages/home", exist_ok=True)
os.makedirs("saved_pages/categories", exist_ok=True)
os.makedirs("saved_pages/products", exist_ok=True)
os.makedirs("saved_pages/combinations", exist_ok=True)
page.get('https://buyplastic.com/materials/')
with open("saved_pages/home/home.html", "w", encoding="utf-8") as f:
    f.write(page.html)
all_combination_details=[]
category_cards=page.eles("xpath://article[@class='material-card material-category-card']/a/@href").get.links()
for cat_no,product in enumerate(category_cards,1):
    print(product,"scrapping.........")
    new_page=Browser.new_tab()
    new_page.get(product)
    with open(f"saved_pages/categories/category_{cat_no}.html","w",encoding="utf-8") as f:
        f.write(new_page.html)
    new_page.set.activate()
    
    
    products_cards=new_page.eles("xpath://ul[@class='productGrid']//li//h3/a/@href").get.links()
    for prod_no,card in enumerate(products_cards,1):
        print(card,"________________")
        prod_page=Browser.new_tab()
        prod_page.get(card)
        with open(f"saved_pages/products/product_{cat_no}_{prod_no}.html","w",encoding="utf-8") as f:
            f.write(prod_page.html)
        prod_page.set.activate()
        product_data=[]
        product_title = ''.join(prod_page.ele("xpath://h1[contains(@class, 'productView-title')]").texts())

        radios=prod_page.eles("xpath://div[@role='radiogroup']")
        combination_details=[]
        combo_no=1
        if len(radios)>=1:
            radio_1=radios[0].eles("xpath://div[contains(@class, 'form-option-wrapper')]//input")
            for color in radio_1:
                color.click()
                if len(radios)>=2:    
                    radio_2=radios[1].eles("xpath://div[contains(@class, 'form-option-wrapper')]//input")
                    for thick in radio_2:
                        thick.click()
                        if len(radios)>=3:
                            radio_3=radios[2].eles("xpath://div[contains(@class, 'form-option-wrapper')]//input")
                            for size in radio_3:
                                size.click() 
                                with open(f"saved_pages/combinations/product_{cat_no}_{prod_no}_combo_{combo_no}.html","w",encoding="utf-8") as f:
                                    f.write(prod_page.html)

                                combo_no += 1                       
                                sku_id=''.join(prod_page.ele("xpath://dd[@data-product-sku]").texts())
                                prices=''.join(prod_page.ele("xpath://div[@class='productView-product']//span[@data-product-price-without-tax]").texts())
                                current_stock = ''.join(prod_page.ele("xpath://span[@data-product-stock]").texts())                            
                                combination_details.append({
                                    "sku_id":sku_id,
                                    "prices":prices,
                                    "stocks_count":current_stock
                                })
                        else:
                            
                            with open(f"saved_pages/combinations/product_{cat_no}_{prod_no}_combo_{combo_no}.html","w",encoding="utf-8") as f:
                                f.write(prod_page.html)

                            combo_no += 1  
                            sku_id = ''.join(prod_page.ele("xpath://dd[@data-product-sku]").texts())
                            prices = ''.join(prod_page.ele("xpath://div[@class='productView-product']//span[@data-product-price-without-tax]").texts())
                            current_stock = ''.join(prod_page.ele("xpath://span[@data-product-stock]").texts())                          
                            combination_details.append({
                                "sku_id":sku_id,
                                "prices":prices,
                                "stocks_count":current_stock
                            })
                else:
                    with open(f"saved_pages/combinations/product_{cat_no}_{prod_no}_combo_{combo_no}.html","w",encoding="utf-8") as f:
                        f.write(prod_page.html)

                    combo_no += 1 
                    sku_id = ''.join(prod_page.ele("xpath://dd[@data-product-sku]").texts())
                    prices = ''.join(prod_page.ele("xpath://div[@class='productView-product']//span[@data-product-price-without-tax]").texts())
                    current_stock = ''.join(prod_page.ele("xpath://span[@data-product-stock]").texts())                           
                    combination_details.append({
                                    "sku_id":sku_id,
                                    "prices":prices,
                                    "stocks_count":current_stock
                                })
        product_data.append({
            "product_name":product_title,
            "product_details":combination_details
        })
        all_combination_details.extend(product_data)
        prod_page.close()
    new_page.close()
Browser.close()

with open("product_details.json",'w',encoding='utf-8')as f:
    json.dump(all_combination_details,f,indent=4)
   