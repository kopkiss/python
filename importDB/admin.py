from django.contrib import admin
from .models import Get_db
from .models import Get_db_oracle
from .models import Prpm_v_grt_project_eis
from .models import PRPM_v_grt_pj_team_eis
from .models import PRPM_v_grt_pj_budget_eis
from .models import PRPM_ranking
from .models import PRPM_r_fund_type
from .models import PRPM_ranking_cited_isi




# Register your models here.
admin.site.register(Get_db)
class ora(admin.ModelAdmin):  
    list_display = ['customer_id', 'fullname','email','budget']   # ใส่ชื่อ ฟิวล์ ที่ต้องการแสดง
    list_filter = ['customer_id']  # สามารถเพิ่ม ตัว filter ได้
    list_editable = ['fullname','budget']  # สามารถ เพิ่ม การแก้ไข ฟิวล์ได้ 

admin.site.register(Get_db_oracle,ora)
admin.site.register(Prpm_v_grt_project_eis)
admin.site.register(PRPM_v_grt_pj_team_eis)
admin.site.register(PRPM_v_grt_pj_budget_eis)

# ตัวอย่าง ถ้าต้องการให้แสดง ตาราง ในหน้า admin 
class ranking(admin.ModelAdmin):  
    list_display = ['year', 'sco', 'isi', 'tci']   # ใส่ชื่อ ฟิวล์ ที่ต้องการแสดง
    list_filter = ['year']  # สามารถเพิ่ม ตัว filter ได้
    list_editable = ['sco','tci']  # สามารถ เพิ่ม การแก้ไข ฟิวล์ได้ 

admin.site.register(PRPM_ranking, ranking )

admin.site.register(PRPM_r_fund_type)
admin.site.register(PRPM_ranking_cited_isi)



